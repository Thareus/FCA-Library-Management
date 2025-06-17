import csv
from rest_framework import serializers, viewsets, status, permissions, filters
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
import pandas as pd

from .models import Author, Book, BookInstance
from .serializers import (
    BookSerializer, BookSearchSerializer, BookBorrowSerializer,
    AmazonIDUpdateSerializer, AuthorSerializer
)
from .tasks import process_csv_task

from users.models import UserWishlist
from users.serializers import UserWishlistSerializer

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
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def borrow(self, request):
        """
        Borrow a book.
        """
        serializer = BookBorrowSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        book = serializer.validated_data['book']
        user = request.user
    
        # Get Available Book Instances
        book_instances = BookInstance.objects.filter(book=book, status='A')

        if not book_instances.exists():
            return Response({'error': 'Book is not available for borrowing'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Borrow Book Instance
        book_instance = book_instances.first()
        book_instance.status = 'B'
        book_instance.borrower = user
        book_instance.save()

        # Delete UserWishlist instance
        UserWishlist.objects.filter(book=book, user=user).delete()
        return Response({'message': 'Book borrowed successfully!'}, status=status.HTTP_200_OK)

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
            wishlists = UserWishlist.objects.filter(book=book).select_related('user')
            serializer = UserWishlistSerializer(wishlists, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Error retrieving wishlists', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def update_amazon_ids(self, request):
        """
        Update Amazon IDs for books in bulk.
        """
        serializer = AmazonIDUpdateSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        updated_books = []
        for item in serializer.validated_data:
            try:
                book = Book.objects.get(id=item['book_id'])
                book.amazon_id = item['amazon_id']
                book.save()
                updated_books.append(book)
            except Book.DoesNotExist:
                continue
        
        return Response({
            'message': f'Successfully updated {len(updated_books)} books',
            'updated_books': BookSerializer(updated_books, many=True).data
        })