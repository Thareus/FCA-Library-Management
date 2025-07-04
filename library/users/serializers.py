from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from books.models import Book
from books.serializers import BookSerializer

from .models import UserWishlist

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    Includes all fields except password.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'is_staff', 'is_superuser')
        read_only_fields = ('id',)

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.
    Includes all fields except password.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'wishlist_data')
        read_only_fields = ('id',)
    
    wishlist_data = serializers.SerializerMethodField()

    def get_wishlist_data(self, obj):
        return UserWishlistSerializer(obj.wishlist, many=True).data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles password validation and user creation.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove password2 from the data
        validated_data.pop('password2', None)
        
        # Create user with the validated data
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user


class CustomTokenSerializer(serializers.Serializer):
    """
    Serializer for token authentication.
    """
    email = serializers.EmailField(
        label="Email",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label="Token",
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = User.objects.filter(email=email).first()
            
            if user and user.check_password(password):
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg, code='authorization')
                
                attrs['user'] = user
                return attrs
            else:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

class UserWishlistSerializer(serializers.ModelSerializer):
    """Serializer for the Wishlist model."""
    class Meta:
        model = UserWishlist
        fields = ['id', 'book', 'user', 'created_at', 'username', 'book_title']
        read_only_fields = ['created_at']
    
    username = serializers.SerializerMethodField(read_only=True)
    book_title = serializers.SerializerMethodField(read_only=True)
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_book_title(self, obj):
        return obj.book.title