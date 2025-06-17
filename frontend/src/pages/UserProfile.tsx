import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  CircularProgress, 
  Alert,
  Paper,
  Avatar,
  Divider,
  Button
} from '@mui/material';
import axios from 'axios';
import { User } from '../types';
import { useAuth } from '../hooks/useAuth';
import { api } from '../api/apiClient';

export default function UserProfile() {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [user, setUser] = useState<User | null>(null);
  const { isStaff, isLoading: isAuthLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.log('No authentication token found. Please log in.');
          throw new Error('No authentication token found. Please log in.');
        }

        const user = await api.get<User>('/users/profile/', {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
          },
          withCredentials: true
        });
        
        setUser(user);
      } catch (error: any) {
        let errorMessage = 'Failed to load user profile';
        
        if (axios.isAxiosError(error)) {
          errorMessage = error.response?.data?.message || error.message || errorMessage;
          
          // If unauthorized, redirect to login
          if (error.response?.status === 401) {
            setTimeout(() => {
              window.location.href = '/login';
            }, 2000);
            return; // Exit early to prevent state updates after redirect
          }
        } else if (error instanceof Error) {
          errorMessage = error.message;
        }
        
        console.error('Error fetching user profile:', errorMessage);
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!user) return <Alert severity="info">User not found</Alert>;

  return (
    <>
    <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={() => navigate('/books')}>
      Back to Books
    </Button>
    {loading && <CircularProgress />}
    <Box sx={{ maxWidth: 800, margin: '0 auto', p: 3 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box display="flex" alignItems="center" mb={3}>
          <Avatar sx={{ width: 80, height: 80, mr: 3 }}>
            {user.username.charAt(0).toUpperCase()}
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1">
              {user.username} {isStaff && ' (Admin)'}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {user.email}
            </Typography>
          </Box>
        </Box>
      </Paper>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Notifications
        </Typography>
        <Divider sx={{ mb: 2 }} />
        {user.notifications.length > 0 ? (
          <List>
            {user.notifications.map((notification) => (
              <ListItem 
                key={notification.id} 
                component={Link} 
                to={`/books/${notification.book.id}`}
                sx={{
                  textDecoration: 'none',
                  color: 'inherit',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemText 
                  primary={notification.message}
                  primaryTypographyProps={{
                    fontWeight: notification.notified ? 'normal' : 'bold'
                  }}
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body1" color="text.secondary" sx={{ py: 2 }}>
            You have no notifications.
          </Typography>
        )}
      </Paper>

      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          My Wishlist
        </Typography>
        <Divider sx={{ mb: 2 }} />
        {user.wishlist.length > 0 ? (
          <List>
            {user.wishlist.map((book) => (
              <ListItem 
                key={book.id} 
                component={Link} 
                to={`/books/${book.id}`}
                sx={{
                  textDecoration: 'none',
                  color: 'inherit',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemText 
                  primary={book.title} 
                  secondary={book.authors.join(', ')}
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body1" color="text.secondary" sx={{ py: 2 }}>
            Your wishlist is empty. Start adding books!
          </Typography>
        )}
      </Paper>
    </Box>
    </> 
  );      
};