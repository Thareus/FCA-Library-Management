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
  BOOK_CREATE_NEW_INSTANCE: (id: string | number | undefined) => apiPath(`books/${id}/create_new_copy/`),
  BOOKS_CSV_UPLOAD: apiPath('books/upload_csv/'),
  BORROW_BOOK: apiPath('books/borrow/'),
  RETURN_BOOK: apiPath('books/return_book/'),
  WISHLIST_ADD: (id: string | number | undefined) => apiPath(`books/${id}/wishlist/`),
  BOOK_WISHLISTS: (id: string | number | undefined) => apiPath(`books/${id}/wishlists_on/`),
  BOOK_REPORT: apiPath('books/report/'),
  GET_AMAZON_ID: (id: string | number | undefined) => apiPath(`books/${id}/get_amazon_id/`),
  UPDATE_AMAZON_IDS: apiPath('books/update_amazon_ids/'),
};

export default API_PATHS;
