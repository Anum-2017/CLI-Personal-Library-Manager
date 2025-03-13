import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ Connect to MySQL Database
def connect_db():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"❌ Database Connection Error: {e}")
        return None

# ✅ Load Books from MySQL
def load_library():
    conn = connect_db()
    if not conn:
        return []
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT title, author, year, genre, read_status FROM books")
            books = cursor.fetchall()
    finally:
        conn.close()

    return books

# ✅ Add a Book to MySQL
def add_book():
    conn = connect_db()
    if not conn:
        print("❌ Database connection failed.")
        return

    title = input("Enter book title: ").strip()
    author = input("Enter author: ").strip()
    year = input("Enter publication year: ").strip()
    genre = input("Enter genre: ").strip()
    read_status = input("Have you read it? (yes/no): ").strip().lower() == "yes"

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO books (title, author, year, genre, read_status) VALUES (%s, %s, %s, %s, %s)",
                (title, author, year, genre, read_status)
            )
        conn.commit()
        print(f'✅ Book "{title}" added successfully.')
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

# ✅ Remove a Book from MySQL
def remove_book():
    conn = connect_db()
    if not conn:
        print("❌ Database connection failed.")
        return

    title = input("Enter the title of the book to remove: ").strip().lower()

    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM books WHERE LOWER(title) = %s", (title,))
            conn.commit()

            if cursor.rowcount > 0:
                print(f'🗑️ Book "{title}" removed successfully.')
            else:
                print(f'❌ Book "{title}" not found.')
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

# ✅ Search Books in MySQL
def search_library():
    conn = connect_db()
    if not conn:
        print("❌ Database connection failed.")
        return

    search_by = input("Search by (title/author): ").strip().lower()
    if search_by not in ["title", "author"]:
        print("❌ Invalid search type. Use 'title' or 'author'.")
        return

    search_term = input(f"Enter {search_by}: ").strip().lower()

    try:
        with conn.cursor(dictionary=True) as cursor:
            query = f"SELECT title, author, year, genre, read_status FROM books WHERE LOWER({search_by}) LIKE %s"
            cursor.execute(query, (f"%{search_term}%",))
            results = cursor.fetchall()

        if results:
            print("\n📖 Search Results:")
            for book in results:
                status = "✅ Read" if book["read_status"] else "❌ Not Read"
                print(f'📚 {book["title"]} by {book["author"]} ({book["year"]}) - {status}')
        else:
            print(f'❌ No books found matching "{search_term}".')
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

# ✅ Display All Books
def display_books():
    books = load_library()

    if not books:
        print("📭 The library is empty.")
        return

    print("\n📖 Library Collection:")
    print("=" * 40)
    for book in books:
        status = "✅ Read" if book["read_status"] else "❌ Not Read"
        print(f'📘 {book["title"]} by {book["author"]} ({book["year"]}) - {status}')
    print("=" * 40)

# ✅ Display Statistics
def display_statistics():
    conn = connect_db()
    if not conn:
        print("❌ Database connection failed.")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM books")
            total_books = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM books WHERE read_status = TRUE")
            read_books = cursor.fetchone()[0]

        perc_read = (read_books / total_books) * 100 if total_books > 0 else 0

        print("\n📊 Library Statistics")
        print("=" * 30)
        print(f'📚 Total books: {total_books:,}')
        print(f'📖 Books read: {read_books:,}')
        print(f'📈 Percentage read: {perc_read:.2f}%')
        print("=" * 30)

    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

# ✅ Main Function
def main():
    while True:
        print("\n📚 Library Menu:")
        print("1. 📖 Add a book")
        print("2. ❌ Remove a book")
        print("3. 🔎 Search for a book")
        print("4. 📚 Display All Books")
        print("5. 📊 Display Statistics")
        print("6. 🚪 Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_book()
        elif choice == "2":
            remove_book()
        elif choice == "3":
            search_library()
        elif choice == "4":
            display_books()
        elif choice == "5":
            display_statistics()
        elif choice == "6":
            print("📚 Library saved to database. 👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

        input("\nPress Enter to continue...")

# ✅ Run the Program
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Exiting Library Manager. Goodbye!")
