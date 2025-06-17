import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Button, CircularProgress, Alert } from '@mui/material';
import axios from 'axios';
import { Book } from '@/types';
import {api} from '../api/apiClient';

export default function BookDetailPage() {
  const { id } = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [borrowMsg, setBorrowMsg] = useState('');

  useEffect(() => {
    const fetchBook = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/books/${id}/`);
        setBook(res.data);
      } catch (err) {
        setError('Book not found');
      }
      setLoading(false);
    };
    fetchBook();
  }, [id]);

  const handleBorrow = async () => {
    setBorrowMsg('');
    try {
      const token = localStorage.getItem('token');
      await api.post('/books/borrow/', { book: id }, { headers: { Authorization: `Token ${token}` } });
      setBorrowMsg('Book borrowed successfully!');
    } catch (err: any) {
      setBorrowMsg(err.response?.data?.detail || 'Could not borrow book');
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box>
      <Typography variant="h4" mb={2}>{book.title}</Typography>
      <Typography variant="subtitle1">{book.authors ? book.authors.join(', ') : book.author}</Typography>
      <Typography variant="body1">ISBN: {book.isbn}</Typography>
      <Typography variant="body1">Publisher: {book.publisher}</Typography>
      <Typography variant="body1">Year: {book.publication_year}</Typography>
      <Typography variant="body1">Language: {book.language}</Typography>
      <Typography variant="body1">Available Copies: {book.available_copies}</Typography>
      <Typography variant="body1">{book.is_available ? 'Available' : 'Not Available'}</Typography>
      <Button variant="contained" color="primary" sx={{ mt: 2 }} onClick={handleBorrow} disabled={!book.is_available}>
        Borrow
      </Button>
      {borrowMsg && <Alert sx={{ mt: 2 }} severity={borrowMsg.includes('success') ? 'success' : 'error'}>{borrowMsg}</Alert>}
    </Box>
  );
}
