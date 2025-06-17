// Utility function to ensure API paths start with /api
const apiPath = (path: string): string => {
  // Remove any leading slashes so we can safely build the URL
  const cleanPath = path.startsWith('/') ? path.substring(1) : path;

  // Skip prefixing when the path already begins with /api or is a full URL
  if (cleanPath.startsWith('api/') || cleanPath.startsWith('http')) {
    return `/${cleanPath}`;
  }

  return `/api/${cleanPath}`;
};

export const API_PATHS = {
  // Auth
  LOGIN: apiPath('users/login/'),
  LOGOUT: apiPath('users/logout/'),
  REGISTER: apiPath('users/register/'),
  
  // Users
  USER_PROFILE: apiPath('users/profile/'),
  CURRENT_USER: apiPath('users/me/'),
  
  // Books
  BOOKS: apiPath('books/'),
  BOOKS_SEARCH: (query: string) => apiPath(`books/search/?query=${encodeURIComponent(query)}`),
  BOOK_DETAIL: (id: string | number | undefined) => apiPath(`books/${id}/`),

  BOOKS_CSV_UPLOAD: apiPath('books/upload_csv/'),
  BORROW_BOOK: apiPath('books/borrow/'),
  RETURN_BOOK: apiPath('books/return/'),
  WISHLIST_ADD: apiPath('books/wishlist/'),
  BOOK_WISHLISTS: (id: string | number | undefined) => apiPath(`books/${id}/wishlists_on/`),
};

export default API_PATHS;
