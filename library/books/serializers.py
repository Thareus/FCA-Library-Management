from rest_framework import serializers
from .models import Author, Book
import re
import requests
import pandas as pd
import iso639
import bcp47

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
            'author',
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
            'author': {'required': True},
        }
    
    def validate_library_id(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Invalid Library ID format.")
        return value

    def validate_isbn(self, value):
        if not re.match(r'^\d{9}[\dX]$|^\d{13}$', value):
            raise serializers.ValidationError("Invalid ISBN format.")
        
        # Optional: External validation
        response = requests.get(f'https://openlibrary.org/api/books?bibkeys=ISBN:{value}&format=json')
        if not response.ok or not response.json():
            raise serializers.ValidationError("ISBN not found in external database.")
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
    """Serializer for importing books from a CSV file, with extra handling for authors field."""
    class Meta:
        model = Book
        fields = ['library_id', 'isbn', 'authors', 'publication_year', 'title', 'language']
        extra_kwargs = {
            'library_id': {'required': True},
            'isbn': {'required': True},
            'title': {'required': True},
            'authors': {'required': True},
        }
    
    def create(self, validated_data):
        authors_data = validated_data.pop('authors').split(',')
        for author in authors_data:
            author = author.strip().rsplit(' ', 1)
            if len(author) == 2:
                given_names, surname = author
            else:
                given_names = ""
                surname = author
            author, _ = Author.objects.get_or_create(
                given_names=given_names,
                surname=surname
            )
            book = Book.objects.create(**validated_data)
            book.authors.add(author)
        return book
    

class BookSearchSerializer(serializers.Serializer):
    """Serializer for book search functionality."""
    query = serializers.CharField(required=True, help_text="Search query (title or author)")

class AmazonIDUpdateSerializer(serializers.Serializer):
    """Serializer for updating Amazon IDs for books."""
    book_id = serializers.IntegerField(required=True)
    amazon_id = serializers.CharField(max_length=10, required=True)