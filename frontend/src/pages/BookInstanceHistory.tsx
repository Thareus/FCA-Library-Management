import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import { BookInstanceHistory } from '@/types';
import { api } from '../api/apiClient';

export default function BookInstanceHistoryPage() {
    const { bookId } = useParams<{ bookId: string }>();
    const { bookInstanceId } = useParams<{ bookInstanceId: string }>();
    const [bookInstanceHistory, setBookInstanceHistory] = React.useState<BookInstanceHistory[] | null>(null);
    const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    api
      .get<BookInstanceHistory[]>(`/books/${bookId}/book-instances/${bookInstanceId}/`)
      .then(data => {
        setBookInstanceHistory(data);
      })
      .catch(error => {
        setError(error.response?.data?.error || 'Failed to load book instance history');
      });
  }, [bookId, bookInstanceId]);

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!bookInstanceHistory) {
    return <CircularProgress />;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Book Instance History
      </Typography>
      {bookInstanceHistory?.map(history => (
        <Box key={history.id} mb={2}>
          <Typography variant="body1" gutterBottom>
            {history.status} on {history.borrowed_date}
          </Typography>
        </Box>
      ))}
    </Box>
  );
}
