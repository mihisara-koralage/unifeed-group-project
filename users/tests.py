import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image


class UsersFrontendTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = 'Campus-test-password-42!'
        cls.student = get_user_model()(email='student@example.test', role='student')
        cls.student.set_password(cls.password)
        cls.student.save()

    def test_auth_pages_render_without_an_account(self):
        for name in ['users:login', 'users:register']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'name="csrfmiddlewaretoken"')
            self.assertContains(response, '/static/css/users.css')
            self.assertContains(response, '/static/js/users.js')
            self.assertNotContains(response, 'data-like-url')

    def test_registration_uses_committed_backend_and_does_not_elevate_role(self):
        response = self.client.post(reverse('users:register'), {
            'email':'new@example.test', 'password1':self.password,
            'password2':self.password, 'role':'admin', 'is_superuser':True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:profile'))
        new_user = get_user_model().objects.get(email='new@example.test')
        self.assertEqual(new_user.role, 'student')
        self.assertFalse(new_user.is_superuser)
        self.assertContains(self.client.get(reverse('users:profile')), 'new@example.test')

    def test_registration_validation_errors_are_visible(self):
        response = self.client.post(reverse('users:register'), {
            'email':'student@example.test', 'password1':self.password, 'password2':'different',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-errors')
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_email_login_and_invalid_password_feedback(self):
        response = self.client.post(reverse('users:login'), {'username':self.student.email, 'password':'incorrect'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password.')
        response = self.client.post(reverse('users:login'), {'username':self.student.email, 'password':self.password})
        self.assertRedirects(response, reverse('users:profile'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.student.pk)
        self.assertEqual(self.client.get(reverse('users:profile')).status_code, 200)

    def test_signed_in_auth_pages_redirect_to_profile(self):
        self.client.force_login(self.student)
        for route in ['users:login', 'users:register']:
            self.assertRedirects(self.client.get(reverse(route)), reverse('users:profile'))

    def test_profile_requires_login(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/login/?next=/users/profile/')

    def test_profile_bio_save_escaping_and_assigned_role(self):
        self.client.force_login(self.student)
        self.client.post(reverse('users:profile'), {'bio':'Hello <script>alert(1)</script>'})
        response = self.client.get(reverse('users:profile'))
        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertContains(response, 'Student')
        self.assertNotContains(response, 'name="role"')

    def test_avatar_upload_uses_existing_profile_form(self):
        self.client.force_login(self.student)
        with tempfile.TemporaryDirectory() as folder, override_settings(MEDIA_ROOT=folder):
            image = BytesIO()
            Image.new('RGB', (12,12), '#183f35').save(image, 'PNG')
            upload = SimpleUploadedFile('avatar.png', image.getvalue(), content_type='image/png')
            self.client.post(reverse('users:profile'), {'bio':'Campus life', 'avatar':upload})
            self.student.refresh_from_db()
            self.assertTrue(self.student.avatar.name.startswith('profile_pics/'))
            self.assertContains(self.client.get(reverse('users:profile')), self.student.avatar.url)

    def test_logout_form_includes_csrf_and_ends_session(self):
        secure_client = Client(enforce_csrf_checks=True)
        secure_client.force_login(self.student)
        self.assertEqual(secure_client.post(reverse('users:logout')).status_code, 403)
        response = secure_client.get(reverse('users:profile'))
        self.assertContains(response, 'action="/users/logout/" method="post"')
        token = secure_client.cookies['csrftoken'].value
        response = secure_client.post(reverse('users:logout'), HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', secure_client.session)
