# API Documentation

This document provides a detailed overview of the API endpoints for the Library Management System.

---

## Authentication

The API uses token-based authentication. Include the token in the `Authorization` header for all protected endpoints: `Authorization: Token <your_token>`.

### Auth Endpoints (`dj_rest_auth`)

These endpoints are provided by the `dj_rest_auth` library.

#### Login
*   **URL:** `/api/auth/login/`
*   **Method:** `POST`
*   **Description:** Authenticates a user and returns an authentication token.
*   **Data:**
    ```json
    {
        "email": "user@example.com",
        "password": "your_password"
    }
    ```

#### Logout
*   **URL:** `/api/auth/logout/`
*   **Method:** `POST`
*   **Description:** Logs out the user and invalidates their token.
*   **Headers:** `Authorization: Token <your_token>`

#### User
*   **URL:** `/api/auth/user/`
*   **Method:** `GET`
*   **Description:** Retrieves the details of the currently authenticated user.
*   **Headers:** `Authorization: Token <your_token>`

#### Password Reset
*   **URL:** `/api/auth/password/reset/`
*   **Method:** `POST`
*   **Description:** Requests a password reset email.
*   **Data:**
    ```json
    {
        "email": "user@example.com"
    }
    ```

### Custom User Endpoints

#### Register
*   **URL:** `/api/users/register/`
*   **Method:** `POST`
*   **Description:** Registers a new user.
*   **Data:**
    ```json
    {
        "email": "newuser@example.com",
        "password": "strong_password",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "1234567890",
        "address": "123 Main St"
    }
    ```

#### Profile
*   **URL:** `/api/users/profile/`
*   **Method:** `GET`, `PUT`, `PATCH`
*   **Description:** View or update the authenticated user's profile.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for PUT/PATCH):**
    ```json
    {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "1234567890",
        "address": "123 Main St"
    }
    ```

#### Me
*   **URL:** `/api/users/me/`
*   **Method:** `GET`
*   **Description:** An alternative endpoint to retrieve the current user's details.
*   **Headers:** `Authorization: Token <your_token>`

#### Wishlist

*   **URL:** `/api/users/wishlist/`
*   **Method:** `GET`, `POST`
*   **Description:**
    *   `GET`: Lists all books in the user's wishlist.
    *   `POST`: Adds a book to the user's wishlist.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for POST):**
    ```json
    {
        "book": 1
    }
    ```

#### Wishlist Item
*   **URL:** `/api/users/wishlist/<wishlist_item_id>/`
*   **Method:** `GET`, `DELETE`
*   **Description:**
    *   `GET`: Retrieves a specific item from the wishlist.
    *   `DELETE`: Removes a book from the user's wishlist.
*   **Headers:** `Authorization: Token <your_token>`

#### Wishlist Item - For User
*   **URL:** `/api/users/wishlist/<wishlist_item_id>/get_for_user/`
*   **Method:** `GET`
*   **Description:** Returns all wishlist entries for the authenticated user.
*   **Headers:** `Authorization: Token <your_token>`

#### Wishlist Item - For Book
*   **URL:** `/api/users/wishlist/<wishlist_item_id>/get_for_book/`
*   **Method:** `GET`
*   **Description:** Lists all users who have wishlisted the associated book.
*   **Headers:** `Authorization: Token <your_token>`

---

## Books

#### Book List
*   **URL:** `/api/books/`
*   **Method:** `GET`, `POST`
*   **Description:**
    *   `GET`: Lists all available books.
    *   `POST`: Creates a new book.
*   **Data (for POST):**
    ```json
    {
        "title": "New Book Title",
        "authors": [1, 2],
        "publication_year": 2024,
        "language": "English",
        "library_id": "000000001",
        "isbn": "9783161484100"
    }
    ```

#### Book
*   **URL:** `/api/books/<book_id>/`
*   **Method:** `GET`, `PUT`, `PATCH`, `DELETE`
*   **Description:**
    *   `GET`: Retrieves a specific book.
    *   `PUT`/`PATCH`: Updates a book's details.
    *   `DELETE`: Deletes a book.

#### Search
*   **URL:** `/api/books/search/`
*   **Method:** `GET`
*   **Description:** Search for books by title or author name using the `query` parameter.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for GET):**
    ```json
    {
        "query": "search query"
    }
    ```

#### Borrow
*   **URL:** `/api/books/borrow/`
*   **Method:** `POST`
*   **Description:** Borrows a book.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for POST):**
    ```json
    {
        "book_instance": 1
    }
    ```

#### Return
*   **URL:** `/api/books/return_book/`
*   **Method:** `POST`
*   **Description:** Marks a borrowed book as returned.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for POST):**
    ```json
    {
        "book_instance": 1
    }
    ```

#### Upload CSV
*   **URL:** `/api/books/upload_csv/`
*   **Method:** `POST`
*   **Description:** Uploads a CSV file of books.
    Expected columns: `id,title,authors,isbn,publication year,language`.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for POST):** file object

#### Get Amazon ID
*   **URL:** `/api/books/<book_id>/get_amazon_id/`
*   **Method:** `GET`
*   **Description:** Fetches an Amazon ID from the Open Library API and stores it on the specified book.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for GET):**
    ```json
    {
        "book": 1
    }
    ```

#### Update Amazon IDs
*   **URL:** `/api/books/update_amazon_ids/`
*   **Method:** `POST`
*   **Description:** Launches a task to update all the Amazon IDs of books that are missing them.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for POST):** None

#### Generate Borrowed Report
*   **URL:** `/api/books/report/`
*   **Method:** `GET`
*   **Description:** Lists all `BookInstance` records currently marked as borrowed.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for GET):** None

#### Create New Copy
*   **URL:** `/api/books/<book_id>/create_new_copy/`
*   **Method:** `POST`
*   **Description:** Creates a new `BookInstance` entry for the selected book.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for POST):**
    ```json
    {
        "book": 1
    }
    ```

#### Add to Wishlist
*   **URL:** `/api/books/<book_id>/wishlist/`
*   **Method:** `POST`
*   **Description:** Adds the specified book to the authenticated user's wishlist.
*   **Headers:** `Authorization: Token <your_token>`
*   **Data (for POST):**
    ```json
    {
        "book": 1
    }
    ```

#### Wishlists On
*   **URL:** `/api/books/<book_id>/wishlists_on/`
*   **Method:** `GET`
*   **Description:** Lists all wishlist entries that include the specified book.
*   **Headers:** `Authorization: Token <your_token>`

---

## Authors

#### Author List
*   **URL:** `/api/authors/`
*   **Method:** `GET`, `POST`
*   **Description:**
    *   `GET`: Lists all authors.
    *   `POST`: Creates a new author.
*   **Data (for POST):**
    ```json
    {
        "given_names": "John",
        "surname": "Doe"
    }
    ```

#### Author
*   **URL:** `/api/authors/<author_id>/`
*   **Method:** `GET`, `PUT`, `PATCH`, `DELETE`
*   **Description:**
    *   `GET`: Retrieves a specific author.
    *   `PUT`/`PATCH`: Updates an author's details.
    *   `DELETE`: Deletes an author.
