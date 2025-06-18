import pytest

pytest.importorskip("django")

from django.utils.text import slugify
from books.models import (
    Author,
    Book,
    BookInstance,
    BookInstanceHistory,
    BookStatus,
)
from users.models import CustomUser

@pytest.mark.django_db
def test_book_slug_created_automatically():
    author = Author.objects.create(given_names="John", surname="Doe")
    book = Book.objects.create(
        title="My Book",
        library_id="1234567890",
        isbn="0123456789123",
        language="en",
    )
    book.authors.add(author)
    expected_slug = slugify(f"{book.title} {book.isbn}")
    assert book.slug == expected_slug

@pytest.mark.django_db
def test_bookinstance_is_available_property():
    author = Author.objects.create(given_names="Jane", surname="Smith")
    book = Book.objects.create(
        title="Another Book",
        library_id="0987654321",
        isbn="9876543210123",
        language="en",
    )
    book.authors.add(author)
    instance = BookInstance.objects.create(book=book)
    user = CustomUser.objects.create_user(username="tester", email="t@example.com", password="pass")
    history = BookInstanceHistory.objects.create(
        book_instance=instance,
        status=BookStatus.AVAILABLE,
        user=user,
        due_date="2100-01-01T00:00:00Z",
    )
    assert instance.is_available is True
    history.status = BookStatus.BORROWED
    history.save()
    assert instance.is_available is False
