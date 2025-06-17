from rest_framework import serializers
from django.db import transaction
import re
import iso639
import bcp47

from .models import Author, Book, BookInstance

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for the Author model."""
    class Meta:
        model = Author
        fields = [
            'id',
            'given_names',
            'surname'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'surname': {'required': True},
        }

class BookSerializer(serializers.ModelSerializer):
    """Serializer for the Book model."""
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'authors',
            'library_id',
            'isbn',
            'amazon_id',
            'publication_year',
            'language',
            'created_at',
            'updated_at',
            'slug'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug']
        extra_kwargs = {
            'library_id': {'required': True},
            'isbn': {'required': True},
            'title': {'required': True},
        }
    
    def validate_library_id(self, value):
        if not re.match(r'^\w{10}$', value):
            raise serializers.ValidationError("Invalid Library ID format.")
        return value

    def validate_isbn(self, value):
        if not re.match(r'^\w{9}[\wX]$|^\w{13}$', value):
            raise serializers.ValidationError("Invalid ISBN format.")
        
        # # Optional: External validation
        # response = requests.get(f'https://openlibrary.org/api/books?bibkeys=ISBN:{value}&format=json')
        # if not response.ok or not response.json():
        #     raise serializers.ValidationError("ISBN not found in external database.")
        return value

    def validate_language(self, value):
        # Try searching for language using the ISO-639 group of language codes.
        for part in ['part1', 'part2b', 'part2t', 'part3', 'alpha2']:
            try:
                return iso639.languages.get(**{part: value}).name
            except KeyError:
                continue
            except ValueError:
                break   
        # Failing that, try searching with the IETF BCP 47 language codes.
        matching_languages = [k for k, v in bcp47.languages.items() if v == value]
        if len(matching_languages) == 0:
            return 'Unknown'
        if len(matching_languages) == 1:
            return matching_languages[0].__str__()
        if len(matching_languages) > 1:
            raise serializers.ValidationError(f"Found more than one matching language for {value}, {matching_languages}. Maybe try a different code.")
    

class BookImportSerializer(BookSerializer):
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'authors',
            'authors_display',
            'library_id',
            'isbn',
            'amazon_id',
            'publication_year',
            'language',
            'created_at',
            'updated_at',
            'slug'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug']
        extra_kwargs = {
            'library_id': {'required': True},
            'isbn': {'required': True},
            'title': {'required': True},
        }

    authors = serializers.CharField(write_only=True, required=False)
    authors_display = serializers.SerializerMethodField(read_only=True)

    def get_authors_display(self, obj):
        """Return authors as comma-separated string for read operations"""
        return ', '.join([author.name for author in obj.authors.all()])

    def create(self, validated_data):
        authors_string = validated_data.pop('authors', '')
        
        with transaction.atomic():
            book = Book.objects.get_or_create(**validated_data)
            if authors_string:
                self._process_authors(book, authors_string)
            book_instances = book.book_instances.all()
            if not book_instances:
                BookInstance.objects.create(book=book, status='A')
        return book
    
    def update(self, instance, validated_data):
        authors_string = validated_data.pop('authors', None)
        
        with transaction.atomic():
            # Update other fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Handle authors if provided
            if authors_string is not None:
                instance.authors.clear()  # Remove existing relationships
                self._process_authors(instance, authors_string)
        
        return instance
    
    def _process_authors(self, book, authors_string):
        """Parse author string and create/link Author instances"""
        if not authors_string.strip():
            return
            
        author_names = [name.strip() for name in authors_string.split(',')]
        
        for author_name in author_names:
            # Split into given names and surname (assuming last space separates them)
            parts = author_name.strip().rsplit(' ', 1)
            if len(parts) == 2:
                given_names, surname = parts
            else:
                given_names = ""
                surname = parts[0]
            
            # Clean up the names
            given_names = given_names.strip()
            surname = surname.strip()
            
            author, created = Author.objects.get_or_create(
                given_names=given_names,
                surname=surname,
                defaults={'given_names': given_names, 'surname': surname}
            )
            book.authors.add(author)


class BookSearchSerializer(serializers.Serializer):
    """Serializer for book search functionality."""
    query = serializers.CharField(required=True, help_text="Search query (title or author)")

class AmazonIDUpdateSerializer(serializers.Serializer):
    """Serializer for updating Amazon IDs for books."""
    book_id = serializers.IntegerField(required=True)
    amazon_id = serializers.CharField(max_length=10, required=True)