import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardActions, 
  Button, 
  TextField, 
  CircularProgress,
  Stack,
  Paper,
  Alert
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import UpdateIcon from '@mui/icons-material/Update';
import ReportIcon from '@mui/icons-material/Report';
import { useAuth } from '../hooks/useAuth';
import {api} from '../api/apiClient';
import { Book } from '../types';
import { API_PATHS } from '../utils/apiPaths';

export default function BookListPage() {
  const [books, setBooks] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const { isStaff, isLoading: isAuthLoading } = useAuth();

  const fetchBooks = async (search = '') => {
    setLoading(true);
    try {
      let results;
      if (search) {
        results = await api.get(API_PATHS.BOOKS_SEARCH(search));
        setBooks(results.results || []);
      } else {
        results = await api.get(API_PATHS.BOOKS);
        setBooks(results.results || results);
      }
    } catch (err) {
      setBooks([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    fetchBooks(query);
  };

  const handleUpdateAmazonIds = async () => {
    setMessage('');
    try {
      await api.post(API_PATHS.UPDATE_AMAZON_IDS);
      setMessage('Amazon IDs updated successfully!');
    } catch (err: any) {
      setMessage(err.response?.data?.detail || 'Failed to update Amazon IDs');
    }
  };

  return (
    <Box>
      <Typography variant="h4">Books</Typography>

      {isStaff && !isAuthLoading && (
        <Box>
          <Button
            variant="contained"
            color="primary"
            component={Link}
            to="/books/upload"
            startIcon={<AddIcon />}
            sx={{ mr: 4 }}
          >
            Upload Books
          </Button>
          <Button
            variant="contained"
            color="primary"
            component={Link}
            to="/books/report"
            startIcon={<ReportIcon />}
            sx={{ mr: 4 }}
          >
            Generate Report
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleUpdateAmazonIds}
            startIcon={<UpdateIcon />}
            sx={{ mr: 4 }}
          >
            Get All Amazon IDs
          </Button>
        </Box>
      )}
      {message && (
        <Alert sx={{ mt: 2 }} severity={message.includes('success') ? 'success' : 'error'}>
          {message}
        </Alert>
      )}
      <Paper component="form" onSubmit={handleSearch} elevation={0} sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <TextField 
            fullWidth
            size="small"
            label="Search by title or author" 
            value={query} 
            onChange={e => setQuery(e.target.value)} 
            variant="outlined"
          />
          <Button 
            variant="contained" 
            type="submit"
            sx={{ whiteSpace: 'nowrap' }}
          >
            Search
          </Button>
        </Stack>
      </Paper>
      {loading ? <CircularProgress /> : (
        <Grid container spacing={2}>
          {books.map((book: Book) => (
            <Grid item xs={12} sm={6} md={4} key={book.id || book.isbn}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{book.title}</Typography>
                  <Typography variant="body2">{book.authors_display}</Typography>
                  <Typography variant="body2">ISBN: {book.isbn}</Typography>
                  <Typography variant="body2">Total Copies: {book.total_copies}</Typography>
                  <Typography variant="body2">Available Copies: {book.available_copies}</Typography>
                </CardContent>
                <CardActions>
                  <Button component={Link} to={`/books/${book.id}`} size="small">Details</Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
