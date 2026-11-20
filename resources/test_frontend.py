from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Resource


class ResourceFrontendTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create(email='shelf@example.test', first_name='Alex')
        cls.page = User.objects.create(email='society-shelf@example.test', role='page')
        cls.resource = Resource.objects.create(
            title='Useful <script>alert(1)</script> notes',
            description='A helpful <img src=x onerror=alert(1)> tutorial',
            category='notes', contributor=cls.student,
            url='https://example.com/study?q=notes&section=1',
        )

    def setUp(self):
        self.client.force_login(self.student)

    def test_directory_uses_real_template_and_navigation(self):
        response = self.client.get(reverse('resources:list'))
        self.assertTemplateUsed(response, 'resources/list.html')
        self.assertContains(response, 'Good things to learn')
        self.assertContains(response, 'Share a resource')
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, reverse('resources:open', args=[self.resource.pk]))
        self.assertContains(self.client.get(reverse('feed:home')), reverse('resources:list'))

    def test_search_is_encoded_in_category_links(self):
        search = 'notes & category=books'
        response = self.client.get(reverse('resources:list'), {'search': search, 'category': 'notes'})
        self.assertContains(response, 'category=books&amp;search=notes%20%26%20category%3Dbooks')
        self.assertContains(response, 'name="category" value="notes"')
        self.assertContains(response, 'Nothing on this shelf just yet.')

    def test_page_account_can_browse_but_cannot_see_share_buttons(self):
        self.client.force_login(self.page)
        response = self.client.get(reverse('resources:list'))
        self.assertContains(response, 'View resource')
        self.assertNotContains(response, f'href="{reverse("resources:submit")}"')

    def test_empty_directory_has_first_share_action(self):
        Resource.objects.all().delete()
        response = self.client.get(reverse('resources:list'))
        self.assertContains(response, 'A shared shelf starts with one link.')
        self.assertContains(response, 'Share the first resource')

    def test_invalid_submission_shows_all_errors_and_preserves_values(self):
        response = self.client.post(reverse('resources:submit'), {
            'title': 'My study notes', 'url': 'not-a-url', 'category': 'bogus',
            'description': 'x' * 501,
        })
        self.assertContains(response, 'A little adjustment needed.')
        for name in ['url', 'category', 'description']:
            self.assertContains(response, f'id="resource-{name}-error"')
        self.assertContains(response, 'value="My study notes"')
        self.assertContains(response, 'value="not-a-url"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'for="id_url"')

    def test_submit_then_follow_directory_and_confirmation(self):
        response = self.client.post(reverse('resources:submit'), {
            'title': 'A new resource', 'url': 'https://example.com/learn',
            'category': 'tutorials', 'description': 'An introduction',
        }, follow=True)
        self.assertContains(response, 'Resource submitted successfully!')
        self.assertContains(response, 'A new resource')
        resource = Resource.objects.get(title='A new resource')
        confirmation = self.client.get(reverse('resources:open', args=[resource.pk]))
        self.assertContains(confirmation, 'https://example.com/learn')

    def test_external_confirmation_is_explicit_escaped_and_opener_safe(self):
        response = self.client.get(reverse('resources:open', args=[self.resource.pk]))
        self.assertContains(response, 'href="https://example.com/study?q=notes&amp;section=1"')
        self.assertContains(response, 'target="_blank" rel="noopener noreferrer"')
        self.assertContains(response, '(opens in a new tab)')
        self.assertContains(response, '&lt;img src=x onerror=alert(1)&gt;')
        self.assertNotContains(response, '<img src=x onerror=alert(1)>')
        self.assertNotContains(response, 'http-equiv="refresh"')
        self.assertNotContains(response, 'window.location')

    def test_unapproved_resource_is_hidden_from_actual_pages(self):
        self.resource.is_approved = False
        self.resource.save(update_fields=['is_approved'])
        self.assertNotContains(self.client.get(reverse('resources:list')), 'Useful &lt;script&gt;')
        self.assertEqual(self.client.get(reverse('resources:open', args=[self.resource.pk])).status_code, 404)
