from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class CustomUser(AbstractUser):
    class Meta:
        ordering = ['username']
        verbose_name = _('user')
        verbose_name_plural = _('users')
        default_related_name = 'users'
        db_table = 'users'
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return self.username

class UserWishlist(models.Model):
    """Model for users to add books to their wishlist."""
    class Meta:
        verbose_name = _('user wishlist')
        verbose_name_plural = _('user wishlists')
        default_related_name = 'wishlist'
        db_table = 'user_wishlist'
        unique_together = ('user', 'book')
        ordering = ['-created_at']
    
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='wishlist',
        verbose_name=_('user')
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        verbose_name=_('book')
    )
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist: {self.book.title}"

class UserNotification(models.Model):
    """Model to track notifications for when a book becomes available."""
    class Meta:
        verbose_name = _('user notification')
        verbose_name_plural = _('user notifications')
        unique_together = ('user', 'book')
        ordering = ['-created_at']
        db_table = 'user_notifications'
        default_related_name = 'notifications'

    message = models.CharField(max_length=255)
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('user')
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('book')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    notified = models.BooleanField(_('notification sent'), default=False)
    notified_at = models.DateTimeField(_('notification sent at'), null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.book.title}"
    
    def mark_as_notified(self):
        """Mark this notification as sent."""
        self.notified = True
        self.notified_at = timezone.now()
        self.save(update_fields=['notified', 'notified_at'])