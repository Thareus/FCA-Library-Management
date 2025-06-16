export interface Author {
    id: number;
    given_names: string;
    surname: string;
}

export interface Book {
  id: number;
  title: string;
  authors: Author[];
  isbn: string;
  amazon_id: string;
  publication_year: number;
  language: string;
  available_copies: number;
  total_copies: number;
}

export interface Notification {
    id: number;
    message: string;
    user: User;
    book: Book;
    created_at: string;
    notified: boolean;
    notified_at: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  wishlist: Book[];
  notifications: Notification[];
}
