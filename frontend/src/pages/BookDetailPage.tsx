import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Box, Typography, Button, CircularProgress, Alert, Paper, List, ListItem, ListItemText } from '@mui/material';
import { Book, BookStatus, UserWishlist } from '../types';
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

  const handleGetAmazonId = async () => {
    setMessage('');
    try {
      await api.get(API_PATHS.GET_AMAZON_ID(id));
      setMessage('Amazon ID retrieved successfully!');
      window.location.reload();
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Could not retrieve Amazon ID');
    }
  };

  const handleCreateNewCopy = async () => {
    setMessage('');
    try {
      await api.post(API_PATHS.BOOK_CREATE_NEW_INSTANCE(id));
      setMessage('New copy created successfully!');
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Could not create new copy');
    }
  };

  const handleReturn = async (id: number) => {
    setMessage('');
    try {
      await api.post(API_PATHS.RETURN_BOOK, {book_instance: id.toString()});
      setMessage('Book returned successfully!');
      window.location.reload();
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Could not return book');
    }
  };

  const handleBorrow = async (id: number) => {
    setMessage('');
    try {
      await api.post(API_PATHS.BORROW_BOOK, {book_instance: id.toString()});
      setMessage('Book borrowed successfully!');
      window.location.reload();
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Could not borrow book');
    }
  };

  const handleWishlist = async () => {
    setMessage('');
    try {
      await api.post(API_PATHS.WISHLIST_ADD(id));
      setMessage('Book added to wishlist successfully!');
      window.location.reload();
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Could not add book to wishlist');
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button variant="contained" color="primary" sx={{ mt: 2, }} onClick={() => navigate('/books')}>
          Back to Books
        </Button>
        <Box>
          <Button variant="contained" color="error" sx={{ mt: 2, mr: 4}} onClick={() => navigate(`/books/${id}/delete`)}>
            Delete Book
          </Button>
          {book?.amazon_id ? (
            <Button variant="contained" color="primary" sx={{ mt: 2 }} target="_blank" href={book.amazon_id}>
              Buy on Amazon
            </Button>
          ) : (
            <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={() => handleGetAmazonId(id)}>
              Get Amazon ID
            </Button>
          )}
        </Box>
      </Box>
      {loading && <CircularProgress />}
      {book && (
        <>
        <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
          <Typography variant="h4" mb={2}>{book.title}</Typography>
          <Typography variant="subtitle1">{book.authors_display}</Typography>
          <Typography variant="body1">ISBN: {book.isbn}</Typography>
          <Typography variant="body1">Year: {book.publication_year}</Typography>
          <Typography variant="body1">Language: {book.language}</Typography>
        </Paper>
        <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
          <Typography variant="body1">Total Copies: {book.total_copies}</Typography>
          <Typography variant="body1">Available Copies: {book.available_copies}</Typography>
          {isAvailable(book) ? (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', alignItems: 'left' }}>
              <Typography variant="h5" sx={{ mr: 3, alignContent: 'center' }}>
                Available
              </Typography>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', alignItems: 'left' }}>
              <Typography variant="h5" sx={{ mr: 3, alignContent: 'center' }}>
                Currently Unavailable
              </Typography> 
              <Button variant="outlined" color="primary" onClick={handleWishlist}>
                Add to Wishlist
              </Button>  
            </Box>
          )}
          {message && <Alert sx={{ mt: 2 }} severity={message.includes('success') ? 'success' : 'error'}>{message}</Alert>}
          <List>
            <ListItem>
              <ListItemText primary="Copies" />
              <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={() => handleCreateNewCopy}>
                Add new copy
              </Button>
            </ListItem>
            {book.book_instances.map((instance) => (
              <ListItem key={instance.id}>
                <ListItemText primary="Status" secondary={BookStatus[instance.status as keyof typeof BookStatus]}/>

                {instance.status === 'A' && <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={() => handleBorrow(instance.id)}>
                  Borrow
                </Button>}
                {instance.status === 'B' && <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={() => handleReturn(instance.id)}>
                  Return
                </Button>}
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
                <ListItemText primary="Wishlisted On:" secondary={new Intl.DateTimeFormat('en-GB', {dateStyle: 'long', timeStyle: 'short'}).format(new Date(wishlist.created_at))} />
              </ListItem>
            </List>
          ))}
          </Paper>
        </>
      )}
    </Box>
  );
}