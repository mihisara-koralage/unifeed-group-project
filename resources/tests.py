"""Backend contract tests; test templates stand in for the frontend handoff."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .forms import ResourceForm
from .models import Resource


TEST_TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {'loaders': [('django.template.loaders.locmem.Loader', {
        'resources/list.html': '{% for resource in resources %}{{ resource.title }}{% endfor %}',
        'resources/submit.html': '<form method="post">{% csrf_token %}{{ form.as_p }}</form>',
        'resources/redirect.html': '{{ resource.url }}',
    })]},
}]


@override_settings(TEMPLATES=TEST_TEMPLATES)
class ResourceBackendTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create(email='resources-student@example.test', role='student')
        cls.other = User.objects.create(email='resources-other@example.test', role='student')
        cls.page = User.objects.create(email='resources-page@example.test', role='page')
        cls.admin = User.objects.create(email='resources-admin@example.test', role='admin')
        cls.notes = Resource.objects.create(
            title='Python Notes', url='https://example.com/notes', category='notes',
            description='Lectures and examples', contributor=cls.other,
        )
        cls.book = Resource.objects.create(
            title='Reference Book', url='https://example.com/book', category='books',
            description='PYTHON reference', contributor=cls.other,
        )
        cls.hidden = Resource.objects.create(
            title='Hidden Python Notes', url='https://example.com/hidden', category='notes',
            description='Python', contributor=cls.other, is_approved=False,
        )

    def setUp(self):
        self.client.force_login(self.student)
        self.data = {'title': 'Study material', 'url': 'https://drive.google.com/file/d/123?usp=sharing',
                     'category': 'notes', 'description': 'A useful resource'}

    def test_all_routes_require_login(self):
        self.client.logout()
        for name, args in [('list', []), ('submit', []), ('open', [self.notes.pk])]:
            with self.subTest(route=name):
                response = self.client.get(reverse('resources:' + name, args=args))
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.url.startswith('/users/login/?next='))

    def test_list_excludes_unapproved_resources(self):
        response = self.client.get(reverse('resources:list'))
        self.assertEqual(list(response.context['resources']), [self.book, self.notes])
        self.assertEqual(response.context['categories'], Resource.Category.choices)

    def test_category_and_keyword_filters_combine_without_leaking_hidden_results(self):
        response = self.client.get(reverse('resources:list'), {'category': 'notes', 'search': ' Python '})
        self.assertEqual(list(response.context['resources']), [self.notes])
        self.assertEqual(response.context['search'], 'Python')
        self.assertEqual(response.context['active_cat'], 'notes')

    def test_search_matches_description_and_title_case_insensitively(self):
        response = self.client.get(reverse('resources:list'), {'search': 'python'})
        self.assertCountEqual(response.context['resources'], [self.notes, self.book])
        self.assertFalse(self.client.get(reverse('resources:list'), {'search': 'not present'}).context['resources'])

    def test_invalid_category_is_ignored(self):
        response = self.client.get(reverse('resources:list'), {'category': 'invalid'})
        self.assertEqual(response.context['active_cat'], '')
        self.assertCountEqual(response.context['resources'], [self.notes, self.book])

    def test_student_submission_sets_contributor_on_server(self):
        response = self.client.post(reverse('resources:submit'), {
            **self.data, 'contributor': self.other.pk, 'is_approved': False,
        })
        self.assertRedirects(response, reverse('resources:list'))
        resource = Resource.objects.get(title=self.data['title'])
        self.assertEqual(resource.contributor, self.student)
        self.assertTrue(resource.is_approved)  # Matches the agreed model default.
        self.assertEqual(resource.url, self.data['url'])

    def test_nonstudents_cannot_submit_or_open_submission_form(self):
        count = Resource.objects.count()
        for user in [self.page, self.admin]:
            self.client.force_login(user)
            for method in [self.client.get, self.client.post]:
                with self.subTest(role=user.role, method=method.__name__):
                    self.assertRedirects(method(reverse('resources:submit'), self.data), reverse('resources:list'))
        self.assertEqual(Resource.objects.count(), count)

    def test_form_rejects_invalid_fields_without_saving(self):
        count = Resource.objects.count()
        for field, value in [('title', ''), ('title', 'x' * 201), ('url', 'javascript:alert(1)'),
                             ('category', 'invalid'), ('description', 'x' * 501)]:
            with self.subTest(field=field, value=value[:25]):
                response = self.client.post(reverse('resources:submit'), {**self.data, field: value})
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context['form'].errors)
        self.assertEqual(Resource.objects.count(), count)

    def test_url_validation_blocks_unsafe_or_malformed_links(self):
        for url in ['javascript:alert(1)', 'data:text/html,test', 'ftp://example.com/file',
                    '//example.com', 'example.com', 'https://', 'https://exa mple.com',
                    'https://example.com/a\nb', 'https://user:secret@example.com/']:
            with self.subTest(url=url):
                form = ResourceForm({**self.data, 'url': url})
                self.assertFalse(form.is_valid())
                self.assertIn('url', form.errors)

    def test_valid_http_https_urls_allow_queries_fragments_and_ports(self):
        for url in ['http://example.com', self.data['url'], 'https://example.com:8443/?q=test#chapter']:
            with self.subTest(url=url):
                form = ResourceForm({**self.data, 'url': url})
                self.assertTrue(form.is_valid(), form.errors)

    def test_model_validation_protects_admin_submission(self):
        self.notes.url = 'ftp://example.com/file'
        with self.assertRaises(ValidationError):
            self.notes.full_clean()

    def test_open_renders_confirmation_instead_of_redirecting_automatically(self):
        response = self.client.get(reverse('resources:open', args=[self.notes.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources/redirect.html')
        self.assertEqual(response.context['resource'], self.notes)
        self.assertNotIn('Location', response)

    def test_open_rejects_unapproved_missing_and_unsafe_legacy_resources(self):
        self.notes.url = 'javascript:alert(1)'
        self.notes.save(update_fields=['url'])
        for pk in [self.hidden.pk, self.notes.pk, 999999]:
            self.assertEqual(self.client.get(reverse('resources:open', args=[pk])).status_code, 404)

    def test_read_routes_do_not_accept_post(self):
        for name, args in [('list', []), ('open', [self.notes.pk])]:
            self.assertEqual(self.client.post(reverse('resources:' + name, args=args)).status_code, 405)

    def test_submission_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        self.assertEqual(client.post(reverse('resources:submit'), self.data).status_code, 403)
        client.get(reverse('resources:submit'))
        token = client.cookies['csrftoken'].value
        self.assertRedirects(client.post(reverse('resources:submit'), self.data,
                                        HTTP_X_CSRFTOKEN=token), reverse('resources:list'))
