import os
import webbrowser
import requests
from colorama import Fore, Style, init

# Initialize Colorama for Windows
init(autoreset=True)

def get_book_info_by_isbn(isbn):
    """Get book information from Google Books API using ISBN."""
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            book = data["items"][0]["volumeInfo"]
            title = book.get("title", "N/A")
            return title, isbn
    return None, None

def get_book_info_by_title(title):
    """Get book information from Google Books API using Title."""
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            book = data["items"][0]["volumeInfo"]
            isbn = book.get("industryIdentifiers", [{}])[0].get("identifier", "N/A")
            return title, isbn
    return None, None

def search_libgen(isbn):
    """Search book on LibGen."""
    libgen_url = f"http://libgen.is/search.php?req={isbn}"
    response = requests.get(libgen_url)
    if response.status_code == 200 and "No files were found" not in response.text:
        return libgen_url
    return None

def main():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, "bulksearch.txt")
    
    # Create the file with the format header if it doesn't exist
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write("Format: ISBN, Title\n")
        print(f"Created {file_path}. Please enter ISBN and Title data following the format and rerun the script.")
        return

    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    if len(lines) <= 1:
        print(f"No ISBN and Title data found in {file_path}. Please follow the format and enter the data.")
        return

    isbn_title_list = lines[1:]  # Skip the first line which is the format header

    book_details = []
    not_found_books = []

    for item in isbn_title_list:
        if not item.strip():
            continue
        parts = item.split(',')
        if len(parts) < 2:
            print(f"Skipping invalid line: {item.strip()}")
            continue
        isbn = parts[0].strip()
        title = ','.join(parts[1:]).strip()
        title_by_isbn, valid_isbn = get_book_info_by_isbn(isbn)
        title_by_title, isbn_by_title = get_book_info_by_title(title)
        
        if title_by_isbn and valid_isbn:
            book_details.append((title_by_isbn, valid_isbn))
            print(f"Retrieved by ISBN: **{title_by_isbn}** (ISBN: {valid_isbn})")
        elif title_by_title and isbn_by_title:
            book_details.append((title_by_title, isbn_by_title))
            print(f"Retrieved by Title: **{title_by_title}** (ISBN: {isbn_by_title})")
        else:
            not_found_books.append((title, isbn))

    print("\nBooks retrieved:")
    for i, (title, isbn) in enumerate(book_details):
        print(f"{i + 1}. **{title}** (ISBN: {isbn})")

    if not_found_books:
        print("\nBooks not retrieved:")
        for i, (title, isbn) in enumerate(not_found_books):
            print(f"{Fore.RED}{i + 1}. **{title}** (ISBN: {isbn}){Style.RESET_ALL}")

    while True:
        choice = input("\nEnter the number(s) of the book(s) to open (comma-separated), 'all' to open all, 'libgen' to search on LibGen, or 'exit' to quit: ").strip().lower()
        
        if choice == 'all':
            for _, isbn in book_details:
                libgen_url = search_libgen(isbn)
                if libgen_url:
                    webbrowser.open(libgen_url)
            break
        
        elif choice == 'libgen':
            for _, isbn in book_details:
                libgen_url = search_libgen(isbn)
                if libgen_url:
                    webbrowser.open(libgen_url)
            break
        
        elif choice == 'exit':
            break
        
        else:
            try:
                indices = [int(i) - 1 for i in choice.split(",")]
                for index in indices:
                    if 0 <= index < len(book_details):
                        _, isbn = book_details[index]
                        libgen_url = search_libgen(isbn)
                        if libgen_url:
                            webbrowser.open(libgen_url)
                    elif 0 <= index < len(not_found_books):
                        _, isbn = not_found_books[index]
                        libgen_url = search_libgen(isbn)
                        if libgen_url:
                            webbrowser.open(libgen_url)
                    else:
                        print(f"Invalid index: {index + 1}")
                break
            except ValueError:
                print("Invalid input. Please enter valid numbers.")

if __name__ == "__main__":
    main()
