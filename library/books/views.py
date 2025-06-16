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

from .models import Author, Book
from .serializers import (
    BookSerializer, BookSearchSerializer,
    AmazonIDUpdateSerializer, AuthorSerializer
)
from .tasks import process_csv_task


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
    search_fields = ['title', 'author', 'isbn', 'amazon_id']
    filterset_fields = ['status', 'language', 'category']
    ordering_fields = ['title', 'author', 'publication_date', 'created_at']
    ordering = ['title']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'update_amazon_ids']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return Book.objects.all().annotate(
            available_copies=Count('instances', filter=Q(instances__status='A')),
            total_copies=Count('instances')
        )
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Search for books by title or author.
        """
        serializer = BookSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
        
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
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
        process_csv_task.delay(path)
        return Response({"message": "File successfully uploaded. You will receive an email when this file has finished processing."}, status=202)
    
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


class BookSearchView(APIView):
    """
    API endpoint that allows searching for books by title or author.
    Returns books with their availability status.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        query = request.query_params.get('query', '').strip()
        
        if not query:
            return Response(
                {"error": "Search query parameter 'query' is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Search for books where title or author name contains the query
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__given_names__icontains=query) |
            Q(author__surname__icontains=query)
        ).distinct()
        
        # Annotate each book with its availability status
        book_data = []
        for book in books:
            available_copies = book.instances.filter(status='A').count()
            total_copies = book.instances.count()
            
            book_data.append({
                'id': book.id,
                'title': book.title,
                'authors': [
                    f"{author.given_names} {author.surname}" 
                    for author in book.author.all()
                ],
                'isbn': book.isbn,
                'publisher': book.publisher,
                'publication_year': book.publication_year,
                'language': book.language,
                'available_copies': available_copies,
                'total_copies': total_copies,
                'is_available': available_copies > 0,
                'amazon_id': book.amazon_id
            })
        
        return Response({
            'count': len(book_data),
            'query': query,
            'results': book_data
        })