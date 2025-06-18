import requests
import urllib
from django.conf import settings
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.storage import default_storage
from django.db.models import Q, OuterRef, Subquery
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
import logging

from .models import Author, Book, BookStatus, BookInstance, BookInstanceHistory
from .serializers import (
    BookSerializer, BookSearchSerializer, BookBorrowSerializer,
    AuthorSerializer
)
from .tasks import process_csv_task

from users.models import UserWishlist
from users.serializers import UserWishlistSerializer

logger = logging.getLogger(__name__)

class AuthorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing authors.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['given_names', 'surname']
    filterset_fields = ['given_names', 'surname']
    ordering_fields = ['given_names', 'surname']
    ordering = ['given_names', 'surname']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'update_amazon_ids']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'authors', 'isbn', 'amazon_id']
    filterset_fields = ['language']
    ordering_fields = ['title', 'authors', 'publication_date', 'created_at']
    ordering = ['title']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'update_amazon_ids']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
        
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for books by title or authors.
        """
        serializer = BookSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(authors__given_names__icontains=query) | Q(authors__surname__icontains=query)
        )
        
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], parser_classes=[JSONParser, FormParser, MultiPartParser])
    def borrow(self, request):
        """
        Borrow a book.
        """
        logger.info(f"Borrow request received. Data: {request.data}")
        
        try:
            serializer = BookBorrowSerializer(data=request.data) # Operates on BookInstance
            if not serializer.is_valid():
                logger.error(f"Validation error in borrow request: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            book_instance = serializer.validated_data['book_instance']
            logger.info(f"Processing borrow request for book instance: {book_instance.id}")
            
            # Check if book is already borrowed
            if book_instance.status == BookStatus.BORROWED:
                logger.warning(f"Book instance {book_instance.id} is already borrowed")
                return Response(
                    {'error': 'This book is already borrowed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update Book Instance
            book_instance.status = BookStatus.BORROWED
            
            try:
                # Create new entry in BookInstanceHistory
                history = BookInstanceHistory(
                    book_instance=book_instance,
                    status=BookStatus.BORROWED,
                    user=request.user,
                    borrowed_date=timezone.now(),
                    due_date=timezone.now() + timedelta(days=14),
                    is_returned=False
                )
                history.save()
                book_instance.save()
                logger.info(f"Successfully updated book instance {book_instance.id} and created history entry")
            except Exception as e:
                logger.error(
                    f"Error updating book instance {book_instance.id} or creating history: {str(e)}",
                    exc_info=True
                )
                return Response(
                    {'error': 'Failed to update book status'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Delete UserWishlist instance if it exists
            try:
                deleted_count, _ = UserWishlist.objects.filter(
                    book=book_instance.book, 
                    user=request.user
                ).delete()
                if deleted_count > 0:
                    logger.info(f"Removed {deleted_count} items from user's wishlist")
            except Exception as e:
                logger.error(
                    f"Error removing book from user's wishlist: {str(e)}",
                    exc_info=True
                )
                # Don't fail the request if wishlist cleanup fails
            
            logger.info(f"Successfully processed borrow request for book instance {book_instance.id}")
            return Response(
                {'message': 'Book borrowed successfully!'}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(
                f"Unexpected error in borrow endpoint: {str(e)}",
                exc_info=True
            )
            return Response(
                {'error': 'An unexpected error occurred'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], parser_classes=[JSONParser, FormParser, MultiPartParser])
    def return_book(self, request):
        """
        Return a book.
        """
        try:
            
            serializer = BookBorrowSerializer(data=request.data) # Operates on BookInstance
            if not serializer.is_valid():
                logger.error(f"Validation error in borrow request: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            book_instance = serializer.validated_data['book_instance']

            book = book_instance.book
            available_copies = book.available_copies

            book_instance.status = BookStatus.AVAILABLE
            book_instance.save()

            # Update Book Instance History
            try:
                history = BookInstanceHistory.objects.create(
                    book_instance=book_instance,
                    status=BookStatus.AVAILABLE,
                    user=request.user,
                    returned_date=timezone.now(),
                    is_returned=True
                )
                history.save()
            except Exception as e:
                logger.error(
                    f"Error updating book instance history: {str(e)}",
                    exc_info=True
                )
                return Response(
                    {'error': 'Failed to update book instance history'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # If available copies was 0, and is now 1, send email to next user on wishlist
            if available_copies == 0 and book.available_copies == 1:
                UserWishlist.objects.filter(book=book).first().user.send_wishlist_email(book)

            return Response({'message': 'Book returned successfully!'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(
                f"Error returning book: {str(e)}",
                exc_info=True
            )
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_csv(self, request):
        """
        Upload a CSV file containing book data.
        Expected CSV format: id,title,authors,isbn,publication year,language
        """
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            return Response({'error': 'File is not a CSV'}, status=status.HTTP_400_BAD_REQUEST)

        path = default_storage.save(f'uploads/{file.name}', file)
        process_csv_task.delay(path, 'test@email.com')
        return Response({"message": "File successfully uploaded. You will receive an email when this file has finished processing."}, status=202)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def update_amazon_ids(self, request):
        """
        Update Amazon IDs for books in bulk.
        """
        task_id = process_amazon_ids_task.delay()
        return Response({'task_id': task_id}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'], url_path='report', url_name='generate_borrowed_report', permission_classes=[permissions.IsAdminUser])
    def generate_borrowed_report(self, request):
        """
        Generate a report on all bookinstances that are currently borrowed.
        """
        borrowed_bookinstances = BookInstance.objects.filter(status=BookStatus.BORROWED).select_related('book')
        
        report = []
        for bookinstance in borrowed_bookinstances:
            history = bookinstance.history.order_by('-borrowed_date').first()
            report.append({
                'book_title': bookinstance.book.title,
                'book_id': bookinstance.book.id,
                'bookinstance_id': bookinstance.id,
                'book_status': bookinstance.status,
                'borrower': history.user.username,
                'borrowed_date': history.borrowed_date,
                'due_date': history.due_date,
            })
        
        return Response({
            'message': 'Report generated',
            'report': report
        })

    @action(detail=True, methods=['post'])
    def create_new_copy(self, request, pk=None):
        """
        Create a new copy of a book.
        """
        try:
            book = self.get_object()
            new_copy = BookInstance.objects.create(book=book, status='A')
            return Response({"message": "New copy created successfully!"}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='wishlist', url_name='add_to_wishlist')
    def add_to_wishlist(self, request, pk=None):
        """
        Add a book to the user's wishlist.
        """
        user = request.user.id
        book = self.get_object().id
        serializer = UserWishlistSerializer(
            data={
                'user': user,
                'book': book
            }
        )
        if UserWishlist.objects.filter(user=user, book=book).exists():
            return Response({'error': 'This book is already in your wishlist.'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Book added to wishlist successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def wishlists_on(self, request, pk=None):
        """
        Get all wishlists that include this book.
        
        Returns a list of UserWishlist objects where each contains:
        - id: Wishlist entry ID
        - user: User who wishlisted the book
        - created_at: When the book was wishlisted
        """
        try:
            book = self.get_object()
            wishlists = UserWishlist.objects.filter(book=book).prefetch_related('user')
            serializer = UserWishlistSerializer(wishlists, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Error retrieving wishlists', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='get_amazon_id', url_name='get_amazon_id')
    def get_amazon_id(self, request, pk=None):
        """
        Get the Amazon ID for a book from https://openlibrary.org/dev/docs/api/search.
        """
        try:
            book = self.get_object()
            response = requests.get(f'https://openlibrary.org/search.json?title={urllib.parse.quote(book.title)}&fields=isbn')

            if response.status_code != 200:
                return Response({'error': 'Failed to get Amazon ID'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            data = response.json()
            if len(data.get('docs', [])) > 0:
                isbn = data['docs'][0].get('isbn')[0]
                amazon_id = f"http://www.amazon.co.uk/dp/{isbn}/ref=nosim?tag={settings.AWS_ASSOCIATE_ID}"
                book.amazon_id = amazon_id
                book.isbn = isbn
                book.save()
                return Response({'amazon_id': amazon_id}, status=status.HTTP_200_OK)
            return Response({'error': 'Failed to get Amazon ID'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response(
                {'error': 'Error retrieving Amazon ID', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
