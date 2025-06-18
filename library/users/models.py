from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

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

    def send_wishlist_email(self, book):
        """Send an email to the user when a book they have on their wishlist becomes available."""
        try:
            # Create the email message
            subject = 'Your wishlist book is available!'
            message = f"Hello {self.username},\n\nYour wishlist book {book.title} is now available for borrowing.\n\nBest regards,\nLibrary Team"
            from_email = 'library@example.com'
            recipient_list = [self.email]
            
            # Send the email
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )            
            # Log the email sending
            logger.info(f"Sent wishlist email to {self.email}")

        except Exception as e:
            logger.error(
                f"Failed to send wishlist email to {self.email}: {str(e)}",
                exc_info=True
            )
            

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
        related_name='wishlists_on',
        verbose_name=_('book')
    )
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)