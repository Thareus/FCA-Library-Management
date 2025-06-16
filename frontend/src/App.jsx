import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import BookListPage from './pages/BookListPage';
import BookDetailPage from './pages/BookDetailPage';
import UserProfile from './pages/UserProfile';
import BookUploadPage from './pages/BookUploadPage';
import Navbar from './components/Navbar';

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Navbar />
      <Container sx={{ mt: 4 }}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/books" element={<BookListPage />} />
          <Route path="/books/upload" element={<BookUploadPage />} />
          <Route path="/books/:id" element={<BookDetailPage />} />
          <Route path="/profile" element={<UserProfile />} />
          <Route path="*" element={<Navigate to="/books" />} />
        </Routes>
      </Container>
    </ThemeProvider>
  );
}

export default App;
