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
  Paper
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useAuth } from '../hooks/useAuth';
import axios from 'axios';
import { Book } from '../types';

export default function BookListPage() {
  const [books, setBooks] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const { isStaff, isLoading: isAuthLoading } = useAuth();

  const fetchBooks = async (search = '') => {
    setLoading(true);
    try {
      let res;
      if (search) {
        res = await axios.get(`/api/books/search/?query=${encodeURIComponent(search)}`);
        setBooks(res.data.results || []);
      } else {
        res = await axios.get('/api/books/books/');
        setBooks(res.data.results || res.data);
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

  return (
    <Box>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Books</Typography>
        {isStaff && !isAuthLoading && (
          <Button
            variant="contained"
            color="primary"
            component={Link}
            to="/books/upload"
            startIcon={<AddIcon />}
          >
            Upload Books
          </Button>
        )}
      </Stack>
      
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
                  <Typography variant="body2">{book.authors ? book.authors.join(', ') : book.authors}</Typography>
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
