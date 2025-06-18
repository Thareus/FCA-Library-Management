import pytest

pytest.importorskip("django")

from django.utils import timezone
from users.models import CustomUser, UserNotification
from books.models import Book, Author
from users.serializers import UserRegistrationSerializer

@pytest.mark.django_db
def test_user_registration_serializer_creates_user():
    data = {
        "email": "new@example.com",
        "username": "newuser",
        "password": "StrongPass123",
        "password2": "StrongPass123",
    }
    serializer = UserRegistrationSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    user = serializer.save()
    assert CustomUser.objects.filter(username="newuser").exists()
    assert user.check_password("StrongPass123")

@pytest.mark.django_db
def test_user_registration_password_mismatch():
    data = {
        "email": "err@example.com",
        "username": "erruser",
        "password": "pass1",
        "password2": "pass2",
    }
    serializer = UserRegistrationSerializer(data=data)
    assert not serializer.is_valid()
    assert "password" in serializer.errors

@pytest.mark.django_db
def test_user_notification_mark_as_notified():
    author = Author.objects.create(given_names="Ann", surname="Lee")
    book = Book.objects.create(title="Notif Book", library_id="1111111111", isbn="1111111111111", language="en")
    book.authors.add(author)
    user = CustomUser.objects.create_user(username="notif", email="notif@example.com", password="pass")
    notification = UserNotification.objects.create(user=user, book=book, message="Check book")
    assert not notification.notified
    notification.mark_as_notified()
    notification.refresh_from_db()
    assert notification.notified
    assert notification.notified_at is not None
    assert notification.notified_at <= timezone.now()
