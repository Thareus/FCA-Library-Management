from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse

class Author(models.Model):
    class Meta:
        ordering = ['surname', 'given_names']
        verbose_name = _('author')
        verbose_name_plural = _('authors')
        default_related_name = 'authors'
        db_table = 'authors'

    given_names = models.CharField(_('given names'), max_length=100)
    surname = models.CharField(_('surname'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=255, unique=True, blank=True)
    
    def __str__(self):
        return f"{self.given_names} {self.surname}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.given_names} {self.surname}")
        super().save(*args, **kwargs)
    

class Book(models.Model):
    class Meta:
        ordering = ['title']
        verbose_name = _('book')
        verbose_name_plural = _('books')
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
            models.Index(fields=['amazon_id']),
        ]
    
    # Book details
    title = models.CharField(_('title'), max_length=200)
    authors = models.ManyToManyField(Author, related_name='books')
    publication_year = models.IntegerField(help_text="Use negative numbers for BC years, positive for AD.", null=True, blank=True)
    language = models.CharField(_('language'), max_length=50, default='English')
    
    # Book identification
    library_id = models.CharField(_('Library ID'), max_length=10, unique=True)
    isbn = models.CharField(_('ISBN'), max_length=13, unique=True)
    amazon_id = models.CharField(_('Amazon ID'), max_length=10, blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    slug = models.SlugField(_('slug'), max_length=255, unique=True, blank=True)

    @property
    def total_copies(self):
        return self.book_instance.count()

    @property
    def available_copies(self):
        return self.book_instance.filter(status=BookStatus.AVAILABLE).count()

    def __str__(self):
        return f"{self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title} {self.isbn}")
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('books:book-detail', kwargs={'slug': self.slug})
    

class BookStatus(models.TextChoices):
    AVAILABLE = 'A', _('Available')
    BORROWED = 'B', _('Borrowed')
    RESERVED = 'R', _('Reserved')
    MISSING = 'M', _('Missing')

class BookInstance(models.Model):
    class Meta:
        verbose_name = _('book instance')
        verbose_name_plural = _('book instances')
        default_related_name = 'book_instances'
        db_table = 'book_instances'
    
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE)
    
    status = models.CharField(
        _('status'),
        max_length=2,
        choices=BookStatus.choices,
        default=BookStatus.AVAILABLE
    )

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    @property
    def is_available(self):
        return self.status == BookStatus.AVAILABLE
    
    def __str__(self):
        return f"{self.book.title} - {self.status}"


class BookInstanceHistory(models.Model):
    class Meta:
        verbose_name = _('book instance history')
        verbose_name_plural = _('book instance histories')
        default_related_name = 'book_instance_history'
        db_table = 'book_instance_history'
        ordering = ['-borrowed_date']
    
    book_instance = models.ForeignKey(
        'books.BookInstance',
        on_delete=models.CASCADE,
        related_name='book_instance_history',
        verbose_name=_('book instance')
    )
    status = models.CharField(
        _('status'),
        max_length=2,
        choices=BookStatus.choices,
        default=BookStatus.AVAILABLE
    )
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='book_history',
        verbose_name=_('user')
    )
    borrowed_date = models.DateTimeField(_('borrowed date'), auto_now_add=True)
    due_date = models.DateTimeField(_('due date'))
    returned_date = models.DateTimeField(_('returned date'), null=True, blank=True)
    is_returned = models.BooleanField(_('is returned'), default=False)

    
    def __str__(self):
        return f"{self.book_instance.book.title} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.book.status = BookStatus.AVAILABLE
            self.book.save()
        elif self.is_returned and not self.returned_date:
            self.returned_date = timezone.now()
            self.book.status = BookStatus.AVAILABLE
            self.book.save()
        super().save(*args, **kwargs)