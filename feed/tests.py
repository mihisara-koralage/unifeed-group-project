from io import BytesIO
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image


class FeedFrontendTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create(email='student@example.test', role='student')
        cls.other = User.objects.create(email='other@example.test', role='student')
        cls.page = User.objects.create(email='society@example.test', role='page')

    def setUp(self):
        self.client.force_login(self.student)

    def test_feed_requires_sign_in(self):
        self.client.logout()
        self.assertRedirects(self.client.get(reverse('feed:home')), '/users/login/?next=/')

    def test_empty_feed_and_navigation(self):
        response = self.client.get(reverse('feed:home'))
        self.assertContains(response, 'Every community starts with a hello.')
        self.assertContains(response, 'data-composer')
        self.assertContains(response, reverse('messaging:inbox'))

    def test_posts_hashtags_and_message_button(self):
        from .models import Post
        self.client.post(reverse('feed:home'), {'content':'Hello #Campus <script>alert(1)</script>'})
        Post.objects.create(author=self.other, content='A question about #Campus')
        response = self.client.get(reverse('feed:home'))
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, reverse('messaging:conversation', args=[self.other.pk]))
        self.assertNotContains(response, f'href="{reverse("messaging:conversation", args=[self.student.pk])}"')
        response = self.client.get(reverse('feed:hashtag', args=['campus']))
        self.assertContains(response, '#campus')
        self.assertContains(response, 'A question about')

    def test_invalid_post_preserves_errors(self):
        response = self.client.post(reverse('feed:home'), {'content':''})
        self.assertContains(response, 'This field is required.')

    def test_like_toggle_enforces_csrf_and_updates_rendered_state(self):
        from .models import Post
        post = Post.objects.create(author=self.other, content='A campus moment')
        url = reverse('feed:toggle_like', args=[post.pk])
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        self.assertEqual(client.post(url).status_code, 403)
        client.get(reverse('feed:home'))
        token = client.cookies['csrftoken'].value
        self.assertJSONEqual(client.post(url, HTTP_X_CSRFTOKEN=token).content, {'liked':True,'like_count':1})
        self.assertContains(client.get(reverse('feed:home')), 'aria-pressed="true"')
        self.assertJSONEqual(client.post(url, HTTP_X_CSRFTOKEN=token).content, {'liked':False,'like_count':0})

    def test_page_account_can_browse_and_message_but_not_post_or_like(self):
        from .models import Post
        post = Post.objects.create(author=self.other, content='Hello campus')
        self.client.force_login(self.page)
        response = self.client.get(reverse('feed:home'))
        self.assertNotContains(response, 'data-composer')
        self.assertNotContains(response, 'data-like-url=')
        self.assertContains(response, reverse('messaging:conversation', args=[self.other.pk]))
        self.assertEqual(self.client.post(reverse('feed:toggle_like', args=[post.pk])).status_code, 403)

    def test_post_image_is_saved_and_rendered(self):
        from .models import Post
        with tempfile.TemporaryDirectory() as folder, override_settings(MEDIA_ROOT=folder):
            stream = BytesIO()
            Image.new('RGB',(20,20),'#183f35').save(stream,'PNG')
            upload = SimpleUploadedFile('campus.png',stream.getvalue(),content_type='image/png')
            self.client.post(reverse('feed:home'), {'content':'Campus photo','image':upload})
            post = Post.objects.get()
            self.assertContains(self.client.get(reverse('feed:home')), post.image.url)
