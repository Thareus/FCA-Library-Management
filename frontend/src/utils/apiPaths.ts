// Utility function to ensure all API paths are prefixed with /api
const apiPath = (path: string): string => {
  // Remove leading slashes to avoid double slashes
  const cleanPath = path.startsWith('/') ? path.substring(1) : path;
  
  // Don't add /api if it's already there or if it's a full URL
  if (cleanPath.startsWith('api/') || cleanPath.startsWith('http')) {
    return `/${cleanPath}`;
  }
  
  return `/api/${cleanPath}`;
};

export const API_PATHS = {
  // Auth
  LOGIN: apiPath('auth/login/'),
  LOGOUT: apiPath('auth/logout/'),
  REGISTER: apiPath('auth/registration/'),
  
  // Users
  USER_PROFILE: apiPath('users/profile/'),
  CURRENT_USER: apiPath('users/me/'),
  
  // Books
  BOOKS: apiPath('books/'),
  BOOK_DETAIL: (id: string | number) => apiPath(`books/${id}/`),
  BORROW_BOOK: apiPath('books/borrow/'),
  RETURN_BOOK: apiPath('books/return/'),
  WISHLIST_ADD: apiPath('books/wishlist/'),
  BOOK_WISHLISTS: (id: string | number) => apiPath(`books/${id}/wishlists_on/`),
  
  // Search
  SEARCH: (query: string) => apiPath(`books/search/?query=${encodeURIComponent(query)}`),
};

export default API_PATHS;
