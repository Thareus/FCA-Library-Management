import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Button, TextField, Typography, Alert } from '@mui/material';
import { api, setAuthToken } from '../api/apiClient';
import { API_PATHS } from '../utils/apiPaths';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const data = await api.post<{ token: string }>(API_PATHS.LOGIN, { email, password });
      setAuthToken(data.token);
      navigate('/books');
    } catch (error: any) {
      let errorMessage = 'Login failed';
      if (error.response) {
        errorMessage = 'Request failed';
        console.error('Response error:', error.response.data);
      } else if (error.request) {
        errorMessage = 'No response from server. Please try again.';
        console.error('No response:', error.request);
      } else {
        errorMessage = error.message || 'Request setup failed';
        console.error('Request error:', error.message);
      }
      setError(errorMessage);
    }
  };

  return (
    <Box maxWidth={400} mx="auto">
      <Typography variant="h4" mb={2}>Login</Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <form onSubmit={handleSubmit}>
        <TextField label="Email" fullWidth margin="normal" value={email} onChange={e => setEmail(e.target.value)} required />
        <TextField label="Password" type="password" fullWidth margin="normal" value={password} onChange={e => setPassword(e.target.value)} required />
        <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>Login</Button>
      </form>
    </Box>
  );
}
