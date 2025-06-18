export interface Author {
    id: number;
    given_names: string;
    surname: string;
}

export interface Book {
  id: number;
  title: string;
  authors: Author[];
  authors_display: string;
  isbn: string;
  amazon_id: string;
  publication_year: number;
  language: string;
  available_copies: number;
  total_copies: number;
  book_instances: BookInstance[];
}

export enum BookStatus {
    A = 'Available',
    B = 'Borrowed',
    R = 'Reserved',
    L = 'Lost',
    D = 'Damaged'
}

export interface BookInstance {
    id: number;
    book: Book;
    status: string;
    created_at: string;
    updated_at: string;
    history: BookInstanceHistory[];
    most_recent_history: BookInstanceHistory;
}

export interface BookInstanceHistory {
    id: number;
    book_instance: BookInstance;
    status: string;
    borrower: User;
    borrowed_date: string;
    due_date: string;
    returned_date: string;
    is_returned: boolean;
}

export interface BookReport {
    book_title: string,
    book_id: number,
    bookinstance_id: number,
    book_status: string,
    borrower: string,
    borrowed_date: string,
    due_date: string,
}

export interface User {
  id: number;
  username: string;
  email: string;
  wishlist: Book[];
}

export interface UserWishlist {
    id: number;
    user: User;
    book: Book;
    created_at: string;
    username: string;
}
