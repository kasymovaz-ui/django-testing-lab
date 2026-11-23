
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from captcha.models import CaptchaStore


class RegistrationTests(TestCase):

    def test_registration_page_opens(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_successful_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })

        self.assertTrue(
            User.objects.filter(username='testuser').exists()
        )
        self.assertRedirects(response, reverse('login'))


class AuthenticationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123!'
        )

    def get_captcha_data(self):
        key = CaptchaStore.generate_key()
        captcha = CaptchaStore.objects.get(hashkey=key)

        return {
            'captcha_0': key,
            'captcha_1': captcha.response,
        }

    def test_login_page_opens(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_correct_captcha(self):
        data = {
            'username': 'testuser',
            'password': 'StrongPass123!',
        }
        data.update(self.get_captcha_data())

        response = self.client.post(reverse('login'), data)

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(
            '_auth_user_id' in self.client.session
        )

    def test_login_with_wrong_captcha(self):
        data = {
            'username': 'testuser',
            'password': 'StrongPass123!',
            'captcha_0': CaptchaStore.generate_key(),
            'captcha_1': 'wronganswer',
        }

        response = self.client.post(reverse('login'), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            '_auth_user_id' in self.client.session
        )

    def test_login_without_captcha(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'StrongPass123!',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            '_auth_user_id' in self.client.session
        )

    def test_login_with_wrong_password(self):
        data = {
            'username': 'testuser',
            'password': 'WrongPassword123!',
        }
        data.update(self.get_captcha_data())

        response = self.client.post(reverse('login'), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            '_auth_user_id' in self.client.session
        )


class DashboardTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='StrongPass123!'
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}"
        )

    def test_dashboard_opens_for_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Личный кабинет')

    def test_logout(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertNotIn(
            '_auth_user_id',
            self.client.session
        )
