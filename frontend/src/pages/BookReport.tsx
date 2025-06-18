import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, CircularProgress } from '@mui/material';
import { BookReport } from '../types';
import { api } from '../api/apiClient';
import { API_PATHS } from '../utils/apiPaths';

export default function BookReportPage() {
  const navigate = useNavigate();
  const [bookReports, setBookReports] = React.useState<BookReport[]>();
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    api.get(API_PATHS.BOOK_REPORT)
      .then(response => {
        console.log(response.report);
        setBookReports(response.report);
      })
      .catch(error => {
        console.error(error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <CircularProgress />;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Book Report
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Book Title</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Borrower</TableCell>
              <TableCell>Borrowed Date</TableCell>
              <TableCell>Due Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {bookReports?.map(bookReport => (
              <TableRow key={bookReport.book_id}>
                <TableCell>
                  <Typography 
                    component={Link} 
                    to={`/books/${bookReport.book_id}`}
                    sx={{
                      color: 'primary.main',
                      textDecoration: 'none',
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                      display: 'inline-block',
                      cursor: 'pointer'
                    }}
                  >
                    {bookReport.book_title}
                  </Typography>
                </TableCell>
                <TableCell>{bookReport.book_status}</TableCell>
                <TableCell>{bookReport.borrower}</TableCell>
                <TableCell>{new Intl.DateTimeFormat('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(bookReport.borrowed_date))}</TableCell>
                <TableCell>{new Intl.DateTimeFormat('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(bookReport.due_date))}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
