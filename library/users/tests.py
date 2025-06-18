from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from books.models import Author, Book


class UserRegistrationTests(APITestCase):
    """Tests for the user registration endpoint."""

    def test_user_can_register(self):
        url = reverse('users:register')
        payload = {
            'email': 'test@example.com',
            'username': 'tester',
            'password': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.count(), 1)

class UserModelTests(APITestCase):
    """Tests for custom user model methods."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='alice', email='alice@example.com', password='pass1234'
        )
        self.author = Author.objects.create(given_names='Greg', surname='Bear')
        self.book = Book.objects.create(
            title='Eon',
            library_id='LIB0000005',
            isbn='1234567890127',
        )
        self.book.authors.add(self.author)

    def test_send_wishlist_email(self):
        from unittest.mock import patch
        with patch('django.core.mail.send_mail') as mock_send_mail:
            self.user.send_wishlist_email(self.book)
            mock_send_mail.assert_called_once()

