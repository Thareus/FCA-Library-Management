from rest_framework import serializers
from django.db import transaction
import re
import iso639
import bcp47
import logging
from .models import Author, Book, BookInstance, BookInstanceHistory

logger = logging.getLogger(__name__)

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
            'slug',
            # Method Fields
            'authors_display',
            'total_copies',
            'available_copies',
            'book_instances',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug']
        extra_kwargs = {
            'library_id': {'required': True},
            'isbn': {'required': True},
            'title': {'required': True},
        }
    
    authors = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        many=True,
        write_only=True
    )
    authors_display = serializers.SerializerMethodField(read_only=True)
    total_copies = serializers.SerializerMethodField(read_only=True)
    available_copies = serializers.SerializerMethodField(read_only=True)
    book_instances = serializers.SerializerMethodField(read_only=True)
    
    def get_authors_display(self, obj):
        return (', '.join([f"{author.given_names} {author.surname}" for author in obj.authors.all()]))
    
    def get_total_copies(self, obj):
        return obj.book_instances.count()
    
    def get_available_copies(self, obj):
        return obj.book_instances.filter(status='A').count()

    def get_book_instances(self, obj):
        return BookInstanceSerializer(obj.book_instances.all(), many=True).data
    
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
            'library_id': {'required': True, 'validators': []},
            'isbn': {'required': True, 'validators': []},
            'title': {'required': True},
        }

    # Accommodate authors format    
    authors = serializers.CharField(write_only=True)  # Accepts a CSV string

    def create(self, validated_data):
        print("CREATE BOOK")
        authors_string = validated_data.pop('authors', '')
        
        with transaction.atomic():
            # Get or create the book using the unique fields
            book, created = Book.objects.get_or_create(
                library_id=validated_data.get('library_id'),
                defaults=validated_data
            )
            
            # If the book already exists, update fields
            if not created:
                logger.warning(f"Book with library_id {validated_data['library_id']} already exists. Updating fields.")
                for key, value in validated_data.items():
                    setattr(book, key, value)
                book.save()
            
            # Handle authors if provided
            if authors_string:
                self._process_authors(book, authors_string)
            
            # Create book instance if none exists
            book_instances = book.book_instances.all()
            print("BOOK INSTANCES", book_instances)
            if not book_instances:
                book_instance_serializer = BookInstanceSerializer(data={'book':book.pk, 'status':'A'})
                if book_instance_serializer.is_valid():
                    print("BOOK INSTANCE VALID")
                    book_instance_serializer.save()
                else:
                    print("BOOK INSTANCE INVALID", book_instance_serializer.errors)
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
            
            # Create book instance if none exists
            book_instances = instance.book_instances.all()
            if not book_instances:
                book_instance_serializer = BookInstanceSerializer(data={'book':instance.pk, 'status':'A'})
                if book_instance_serializer.is_valid():
                    print("BOOK INSTANCE VALID")
                    book_instance_serializer.save()
                else:
                    print("BOOK INSTANCE INVALID", book_instance_serializer.errors)
        return instance
    
    def _process_authors(self, book, author_value):
        if not author_value.strip():
            return
            
        author_names = [name.strip() for name in author_value.split(',')]
        
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

class BookBorrowSerializer(serializers.Serializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

class BookWishlistSerializer(serializers.Serializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

class BookSearchSerializer(serializers.Serializer):
    """Serializer for book search functionality."""
    query = serializers.CharField(required=True, help_text="Search query (title or author)")

class BookInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInstance
        fields = [
            'id',
            'book',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        with transaction.atomic():
            instance = BookInstance.objects.create(**validated_data)
            history_serializer = BookInstanceHistorySerializer(data={
                'book_instance':instance.pk, 
                'status':'A', 
                'user':None,
                'borrowed_date':None,
                'due_date':None,
                'returned_date':None,
                'is_returned':True
            })
            if history_serializer.is_valid():
                print("HISTORY VALID")
                history_serializer.save()
            else:
                print("HISTORY INVALID", history_serializer.errors)
        return instance

class BookInstanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInstanceHistory
        fields = [
            'id',
            'book_instance',
            'status',
            'user',
            'borrowed_date',
            'due_date',
            'returned_date',
            'is_returned',
        ]
        read_only_fields = ['id', 'borrowed_date', 'due_date', 'returned_date', 'is_returned']

class AmazonIDUpdateSerializer(serializers.Serializer):
    """Serializer for updating Amazon IDs for books."""
    book_id = serializers.IntegerField(required=True)
    amazon_id = serializers.CharField(max_length=10, required=True)