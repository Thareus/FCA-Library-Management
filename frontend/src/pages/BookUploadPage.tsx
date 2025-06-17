import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  Typography, 
  Button, 
  CircularProgress, 
  Alert, 
  Paper,
  Container,
  List,
  ListItem,
  ListItemText,
  Link
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { api } from '../api/apiClient';
import { API_PATHS } from '../utils/apiPaths';

const BookUploadPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setMessage(null);
      setErrors([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    setMessage(null);
    setErrors([]);

    try {
      const response = await api.post(API_PATHS.BOOKS_CSV_UPLOAD, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data) {
        if (response.data.message) {
          setMessage({ type: 'success', text: response.data.message });
        }
        if (response.data.errors && response.data.errors.length > 0) {
          setErrors(response.data.errors);
        }
      } else {
        throw new Error(response.data || 'Failed to upload file');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setErrors([
        error instanceof Error ? error.message : 'An error occurred during upload'
      ]);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Upload Books via CSV
        </Typography>
        
        <Typography variant="body1" paragraph>
          Upload a CSV file containing the following columns: 
        </Typography>
        <List
            sx = {{
            listStyleType: 'disc',
            pl: 2,
            '& .MuiListItem-root': {
            display: 'list-item',
            },
            }}>
            <ListItem >
                <ListItemText primary="Book ID" secondary="Required"/>
                <ListItemText primary="The library ID of the book"/>
            </ListItem>
            <ListItem >
                <ListItemText primary="ISBN" secondary="Required"/>
                <ListItemText primary="The International Standard Book Number of the book" secondary={
                  <Typography variant="body2">
                    You may use <Link href="https://isbnsearch.org/" target="_blank" rel="noopener noreferrer">this website</Link> to find the ISBN of a book
                  </Typography>
                }/>
            </ListItem>
            <ListItem >
                <ListItemText primary="Author(s)" secondary="Required"/>
                <ListItemText primary="All authors should appear as given names followed by surname. If there are multiple authors, they should be separated by a comma. Example: 'John Doe, Jane Doe'"/>
            </ListItem>
            <ListItem >
                <ListItemText primary="Publication Year" secondary="Required"/>
                <ListItemText primary="The year the book was published"/>
            </ListItem>
            <ListItem >
                <ListItemText primary="Title" secondary="Required"/>
                <ListItemText primary="The title of the book"/>
            </ListItem>
            <ListItem >
                <ListItemText primary="Language"/>
                <ListItemText
                  primary="The language of the book in either ISO 639 format or BCP47 format"
                  secondary={
                    <Typography variant="body2">
                      See <Link href="https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes" target="_blank" rel="noopener noreferrer">here</Link> for a list of valid ISO 639 codes
                    </Typography>
                  }
                />
            </ListItem>
        </List>

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
          <Box sx={{ mb: 2 }}>
            <Button
              component="label"
              variant="outlined"
              startIcon={<CloudUploadIcon />}
              disabled={isUploading}
            >
              {file ? file.name : 'Select CSV File'}
              <input
                type="file"
                hidden
                accept=".csv"
                onChange={handleFileChange}
              />
            </Button>
            {file && (
              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </Typography>
            )}
          </Box>

          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={!file || isUploading}
            sx={{ mt: 2 }}
          >
            {isUploading ? (
              <>
                <CircularProgress size={24} sx={{ mr: 1 }} />
                Uploading...
              </>
            ) : (
              'Upload and Process CSV'
            )}
          </Button>
        </Box>

        {message && (
          <Alert severity={message.type} sx={{ mt: 3 }}>
            {message.text}
            {errors.length > 0 && (
              <Box component="div" sx={{ mt: 2 }}>
                <Typography variant="subtitle2">Some errors occurred:</Typography>
                <ul style={{ margin: '4px 0 0 0', paddingLeft: 20 }}>
                  {errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </Box>
            )}
          </Alert>
        )}
      </Paper>
    </Container>
  );
};

export default function BookUploadPageWithProtection() {
  return (
    <ProtectedRoute requireStaff={true}>
      <BookUploadPage />
    </ProtectedRoute>
  );
}