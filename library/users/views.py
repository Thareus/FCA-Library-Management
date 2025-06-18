from rest_framework import serializers, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from .models import CustomUser, UserWishlist
from .serializers import (
    UserSerializer,
    UserProfileSerializer, 
    UserRegistrationSerializer,
    CustomTokenSerializer,
    UserWishlistSerializer,
)

class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create token for the new user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response(
            {
                'user': UserSerializer(user, context=self.get_serializer_context()).data,
                'token': token.key
            },
            status=status.HTTP_201_CREATED
        )


class CustomAuthToken(ObtainAuthToken):
    """
    Custom token-based authentication view that extends ObtainAuthToken.
    Returns user data along with the token.
    """
    serializer_class = CustomTokenSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class LogoutView(APIView):
    """
    Logout a user by deleting their auth token.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete the user's token to force logout
        request.user.auth_token.delete()
        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK
        )


class CurrentUserView(APIView):
    """
    Get the current authenticated user's information.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user = CustomUser.objects.prefetch_related('wishlist', 'notifications').get(username=self.request.user.username)
        
        return user

class UserWishlistViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user wishlists.
    """
    serializer_class = UserWishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserWishlist.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def post(self, request):
        """
        Add a book to the user's wishlist.
        """
        serializer = UserWishlistSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        book = serializer.validated_data['book']
        user = request.user
        
        # Add Book to User's Wishlist
        wishlist = UserWishlist.objects.create(user=user, book=book)
        
        return Response({'message': 'Book added to wishlist successfully!', 'wishlist': UserWishlistSerializer(wishlist).data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def get_for_user(self, request, pk=None):
        """
        Get all wishlists that include this book.
        
        Returns a list of UserWishlist objects where each contains:
        - id: Wishlist entry ID
        - user: User who wishlisted the book
        - created_at: When the book was wishlisted
        """
        try:
            user = self.request.user
            wishlists = UserWishlist.objects.filter(user=user).select_related('book')
            serializer = UserWishlistSerializer(wishlists, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Error retrieving wishlists', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def get_for_book(self, request, pk=None):
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