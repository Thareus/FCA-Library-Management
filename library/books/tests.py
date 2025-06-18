from django.test import TestCase
from .models import Author, Book, BookInstance, BookStatus


class AuthorModelTests(TestCase):
    """Tests for the Author model."""

    def test_slug_is_generated(self):
        author = Author.objects.create(given_names="John", surname="Doe")
        self.assertTrue(author.slug)


class BookModelTests(TestCase):
    """Tests for the Book model and related models."""

    def setUp(self):
        self.author = Author.objects.create(given_names="Jane", surname="Austen")

    def test_slug_is_generated(self):
        book = Book.objects.create(
            title="Pride and Prejudice",
            library_id="LIB0000001",
            isbn="1234567890123",
        )
        book.authors.add(self.author)
        self.assertTrue(book.slug)

    def test_total_and_available_copies(self):
        book = Book.objects.create(
            title="Emma",
            library_id="LIB0000002",
            isbn="1234567890124",
        )
        book.authors.add(self.author)

        bi_available = BookInstance.objects.create(book=book, status=BookStatus.AVAILABLE)
        bi_borrowed = BookInstance.objects.create(book=book, status=BookStatus.BORROWED)

        self.assertEqual(book.total_copies, 2)
        self.assertEqual(book.available_copies, 1)

        # Ensure the BookInstance.is_available property mirrors the history logic
        self.assertFalse(bi_borrowed.is_available)
        self.assertTrue(bi_available.is_available)

class BookModelAdditionalTests(TestCase):
    """Additional tests for Book model."""

    def setUp(self):
        self.author = Author.objects.create(given_names="Mark", surname="Twain")

    def test_get_absolute_url_contains_slug(self):
        book = Book.objects.create(
            title="Adventures",
            library_id="LIB0000003",
            isbn="1234567890125",
        )
        book.authors.add(self.author)
        self.assertIn(book.slug, book.get_absolute_url())

class BookSerializerValidationTests(TestCase):
    """Tests for BookSerializer field validations."""

    def setUp(self):
        self.author = Author.objects.create(given_names="Leo", surname="Tolstoy")

    def test_invalid_library_id(self):
        from .serializers import BookSerializer
        serializer = BookSerializer(data={
            'title': 'War and Peace',
            'authors': [self.author.id],
            'library_id': 'BADID',
            'isbn': '1234567890126'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('library_id', serializer.errors)

    def test_invalid_isbn(self):
        from .serializers import BookSerializer
        serializer = BookSerializer(data={
            'title': 'Anna Karenina',
            'authors': [self.author.id],
            'library_id': 'LIB0000004',
            'isbn': 'BADISBN'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('isbn', serializer.errors)

