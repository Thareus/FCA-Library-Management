from django.test import TestCase
from .models import Author, Book, BookInstance, BookStatus
from django.urls import reverse


class AuthorModelTests(TestCase):
    """Tests for the Author model."""

    def test_slug_is_generated(self):
        author = Author.objects.create(given_names="John", surname="Doe")
        self.assertTrue(author.slug)

    def test_str_representation(self):
        author = Author.objects.create(given_names="Emily", surname="Bronte")
        self.assertEqual(str(author), "Emily Bronte")


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

    def test_get_absolute_url_contains_id(self):
        book = Book.objects.create(
            title="Adventures",
            library_id="LIB0000003",
            isbn="1234567890125",
        )
        book.authors.add(self.author)
        self.assertIn(str(book.id), book.get_absolute_url())

    def test_get_absolute_url_missing_id(self):
        book = Book(title="Draft", library_id="LIB0000009", isbn="1234567890999")
        # Not saved, so no id
        with self.assertRaises(Exception):
            book.get_absolute_url()

class BookInstanceModelTests(TestCase):
    """Tests for the BookInstance model."""

    def setUp(self):
        self.author = Author.objects.create(given_names="Agatha", surname="Christie")
        self.book = Book.objects.create(title="Poirot", library_id="LIB0000010", isbn="1234567890110")
        self.book.authors.add(self.author)

    def test_instance_creation_and_str(self):
        instance = BookInstance.objects.create(book=self.book, status=BookStatus.AVAILABLE)
        self.assertEqual(str(instance), f"{self.book.title} - {BookStatus.AVAILABLE}")

    def test_is_available_property(self):
        instance = BookInstance.objects.create(book=self.book, status=BookStatus.AVAILABLE)
        instance2 = BookInstance.objects.create(book=self.book, status=BookStatus.BORROWED)
        self.assertTrue(instance.is_available)
        self.assertFalse(instance2.is_available)

    def test_status_choices(self):
        self.assertIn(BookStatus.AVAILABLE, BookStatus.values)
        self.assertIn(BookStatus.BORROWED, BookStatus.values)

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

