from asgiref.sync import async_to_sync
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from .models import Conversation, Message
from .routing import websocket_urlpatterns


class MessagingFrontendTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.one = User.objects.create(email='one@example.test')
        cls.two = User.objects.create(email='two@example.test')

    def setUp(self):
        self.client.force_login(self.one)

    def test_empty_inbox_and_protected_routes(self):
        self.assertContains(self.client.get(reverse('messaging:inbox')), 'Good conversations start with hello.')
        self.client.logout()
        response = self.client.get(reverse('messaging:inbox'))
        self.assertEqual(response.status_code,302)

    def test_start_conversation_and_history_escape_text(self):
        response = self.client.get(reverse('messaging:conversation', args=[self.two.pk]))
        self.assertEqual(response.status_code,200)
        conversation = Conversation.objects.get()
        self.assertEqual(conversation.participants.count(),2)
        Message.objects.create(conversation=conversation,sender=self.two,content='<script>alert(1)</script>')
        response = self.client.get(reverse('messaging:conversation',args=[self.two.pk]))
        self.assertContains(response,'&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(response,'<script>alert(1)</script>')
        self.assertContains(response,f'data-ws-path="/ws/chat/{conversation.pk}/"')
        self.assertContains(response,'data-chat-form')
        # The chat queryset is named messages; it must not appear in global flash notices.
        self.assertNotContains(response,'class="notice "')

    def test_inbox_unread_badge_and_opening_marks_messages_read(self):
        conversation = Conversation.get_or_create_between(self.one,self.two)
        message = Message.objects.create(conversation=conversation,sender=self.two,content='A hello from campus')
        response = self.client.get(reverse('messaging:inbox'))
        self.assertContains(response,'A hello from campus')
        self.assertContains(response,'1 unread messages')
        self.client.get(reverse('messaging:conversation',args=[self.two.pk]))
        message.refresh_from_db()
        self.assertTrue(message.is_read)

    def test_hide_for_me_preserves_the_message_for_the_other_participant(self):
        conversation = Conversation.get_or_create_between(self.one,self.two)
        message = Message.objects.create(conversation=conversation,sender=self.one,content='Keep this for the recipient')
        self.client.post(reverse('messaging:delete_message',args=[message.pk]))
        self.assertTrue(Message.objects.filter(pk=message.pk).exists())
        self.assertNotContains(self.client.get(reverse('messaging:conversation',args=[self.two.pk])),message.content)
        self.client.force_login(self.two)
        self.assertContains(self.client.get(reverse('messaging:conversation',args=[self.one.pk])),message.content)
        self.client.post(reverse('messaging:delete_message',args=[message.pk]))
        self.assertNotContains(self.client.get(reverse('messaging:conversation',args=[self.one.pk])),message.content)

    def test_self_message_returns_to_inbox(self):
        self.assertRedirects(self.client.get(reverse('messaging:conversation',args=[self.one.pk])),reverse('messaging:inbox'))
        self.assertEqual(Conversation.objects.count(),0)


@override_settings(CHANNEL_LAYERS={'default':{'BACKEND':'channels.layers.InMemoryChannelLayer'}})
class LiveChatContractTests(TransactionTestCase):
    def setUp(self):
        User = get_user_model()
        self.one = User.objects.create(email='one@example.test')
        self.two = User.objects.create(email='two@example.test')
        self.stranger = User.objects.create(email='stranger@example.test')
        self.conversation = Conversation.get_or_create_between(self.one,self.two)

    def communicator(self,user):
        socket = WebsocketCommunicator(URLRouter(websocket_urlpatterns),f'/ws/chat/{self.conversation.pk}/')
        socket.scope['user'] = user
        return socket

    def test_messages_and_typing_reach_the_other_participant(self):
        async def run():
            one,two = self.communicator(self.one),self.communicator(self.two)
            try:
                self.assertTrue((await one.connect())[0])
                self.assertTrue((await two.connect())[0])
                await one.send_json_to({'type':'typing','is_typing':True})
                self.assertEqual((await two.receive_json_from())['type'],'typing')
                await one.send_json_to({'type':'chat_message','content':'Hello in real time'})
                own,other = await one.receive_json_from(),await two.receive_json_from()
                self.assertEqual(own['message_id'],other['message_id'])
                self.assertEqual(other['content'],'Hello in real time')
                self.assertEqual(other['sender_id'],self.one.pk)
            finally:
                await one.disconnect()
                await two.disconnect()
        async_to_sync(run)()
        self.assertEqual(Message.objects.get().content,'Hello in real time')

    def test_unauthenticated_and_non_participant_connections_are_rejected(self):
        async def run():
            for user in [AnonymousUser(),self.stranger]:
                socket = self.communicator(user)
                self.assertFalse((await socket.connect())[0])
                await socket.disconnect()
        async_to_sync(run)()
