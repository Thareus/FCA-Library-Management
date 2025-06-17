import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, Button, CircularProgress, Alert, Paper, Avatar, List, ListItem, ListItemText, CardActions } from '@mui/material';
import axios from 'axios';
import { Book, UserWishlist } from '@/types';
import { api } from '../api/apiClient';
import { API_PATHS } from '../utils/apiPaths';

export default function BookDetailPage() {
  const { id } = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [wishlists_on, setWishlistsOn] = useState<UserWishlist[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const isAvailable = (book: Book) => book?.available_copies > 0;

  useEffect(() => {
    const fetchBook = async () => {
      setLoading(true);
      try {
        const res = await api.get<Book>(API_PATHS.BOOK_DETAIL(id));
        setBook(res);
      } catch (err) {
        setError('Book not found');
      }
      setLoading(false);
    };
    fetchBook();
  }, [id]);

  useEffect(() => {
    const fetchWishlistsOn = async () => {
      setLoading(true);
      try {
        const res = await api.get<UserWishlist[]>(API_PATHS.BOOK_WISHLISTS(id));
        setWishlistsOn(res);
      } catch (err) {
        setError('Wishlists not found');
      }
      setLoading(false);
    };
    fetchWishlistsOn();
  }, [id]);

  const handleReturn = async () => {
    setMessage('');
    try {
      await api.post(API_PATHS.RETURN_BOOK, { book: id });
      setMessage('Book returned successfully!');
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Could not return book');
    }
  };

  const handleBorrow = async () => {
    setMessage('');
    try {
      await api.post(API_PATHS.BORROW_BOOK, { book: id });
      setMessage('Book borrowed successfully!');
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Could not borrow book');
    }
  };

  const handleWishlist = async () => {
    setMessage('');
    try {
      await api.post(API_PATHS.WISHLIST_ADD, { book: id });
      setMessage('Book added to wishlist successfully!');
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Could not add book to wishlist');
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={() => navigate('/books')}>
        Back to Books
      </Button>
      {loading && <CircularProgress />}
      {book && (
        <>
        <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
          <Typography variant="h4" mb={2}>{book.title}</Typography>
          <Typography variant="subtitle1">{book.authors ? book.authors.join(', ') : book.authors}</Typography>
          <Typography variant="body1">ISBN: {book.isbn}</Typography>
          <Typography variant="body1">Year: {book.publication_year}</Typography>
          <Typography variant="body1">Language: {book.language}</Typography>
        </Paper>
        <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
          <Typography variant="body1">Total Copies: {book.total_copies}</Typography>
          <Typography variant="body1">Available Copies: {book.available_copies}</Typography>
          {isAvailable(book) ? (
            <>
              <Typography sx={{ mr: 3 }}>
                Available
              </Typography>
              <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={handleBorrow}>
                Borrow
              </Button>
            </>
          ) : (
            <>
              <Button variant="outlined" color="primary" sx={{ mt: 2 }} onClick={handleWishlist}>
                Wishlist
              </Button>
              <Typography sx={{ mr: 3 }}>
                Currently Unavailable
              </Typography>   
            </>
          )}
          {message && <Alert sx={{ mt: 2 }} severity={message.includes('success') ? 'success' : 'error'}>{message}</Alert>}
          <List>
            {book.book_instances.map((instance) => (
              <ListItem key={instance.id}>
                <ListItemText primary={instance.is_available ? 'Available' : 'Not Available'} />
              </ListItem>
            ))}
          </List>
          </Paper>
          <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
            <Typography variant="body1">Wishlisted By:</Typography>
            {wishlists_on?.map((wishlist: UserWishlist) => (
            <List>
              <ListItem>
                <ListItemText primary={wishlist.user.username} />
                <ListItemText primary="Wishlisted On:" secondary={wishlist.created_at} />
              </ListItem>
            </List>
          ))}
          </Paper>
        </>
      )}
    </Box>
  );
}