from flask import Blueprint, request, jsonify
import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

books_bp = Blueprint('books_bp', __name__)
uri = "mongodb+srv://mriduaayu123:xhiUSnVjZEGIH22n@cluster0.uc4f1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

#client = MongoClient('mongodb+srv://mriduaayu123:xhiUSnVjZEGIH22n@cluster0.uc4f1.mongodb.net/swap_book')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['swap_book']  
books_collection=db['BookDataset']
# MongoDB collections
profiles_collection = db['profile']  # Ensure this is set to your actual collection name
## seach by author
@books_bp.route('/search', methods=['POST'])
def search_books():
    data = request.get_json()

    # Extract the author name from the JSON request
    author = data.get('author')
    if not author:
        return jsonify({'error': 'Author name is required'}), 400

    # Use Google Books API to search for books by author
    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': f'inauthor:{author}',
        'maxResults': 25,  # Adjust as needed
        'printType': 'books'
    }
    
    response = requests.get(GOOGLE_BOOKS_API, params=params)
    
    if response.status_code == 200:
        books = response.json().get('items', [])
        
        # Prepare the JSON response
        result = []
        for book in books:
            book_info = book.get('volumeInfo', {})
            
            # Extracting required details
            description = book_info.get('description', 'No Description')
            categories = book_info.get('categories', ['No Categories'])
            content_version = book_info.get('contentVersion', 'No Version')
            image_links = book_info.get('imageLinks', {})
            industry_identifiers = book_info.get('industryIdentifiers', [])
            isbn = industry_identifiers[0].get('identifier') if industry_identifiers else 'No ISBN'
            page_count = book_info.get('pageCount', 'No Page Count')
            title = book_info.get('title', 'No Title')
            lang=book_info.get('language', 'No Language')

            # Append the filtered details to the result
            result.append({
                'title':title,
                'description': description,
                'categories': categories,
                'content_version': content_version,
                'image_links': image_links,
                'isbn': isbn,
                'page_count': page_count,
                'lang':lang

            })
        
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Failed to fetch books'}), 500


##Search by isbn number
@books_bp.route('/search_by_isbn', methods=['POST'])
def search_books_by_isbn():
    data = request.get_json()

    # Extract the ISBN number from the JSON request
    isbn = data.get('isbn')
    if not isbn:
        return jsonify({'error': 'ISBN number is required'}), 400

    # Use Google Books API to search for books by ISBN
    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': f'isbn:{isbn}',
        'maxResults': 1,  # Adjust as needed
        'printType': 'books'
    }
    
    response = requests.get(GOOGLE_BOOKS_API, params=params)
    
    if response.status_code == 200:
        books = response.json().get('items', [])
        
        # Prepare the JSON response
        result = []
        for book in books:
            book_info = book.get('volumeInfo', {})
            title = book_info.get('title', 'No title')

            # The 'authors' field is a list, so we need to join the list to a string
            authors = book_info.get('authors', ['No author'])
            author = ', '.join(authors)  # Join the list into a string

            # Extracting required details
            description = book_info.get('description', 'No Description')
            categories = book_info.get('categories', ['No Categories'])
            content_version = book_info.get('contentVersion', 'No Version')
            image_links = book_info.get('imageLinks', {})
            industry_identifiers = book_info.get('industryIdentifiers', [])
            isbn_number = industry_identifiers[0].get('identifier') if industry_identifiers else 'No ISBN'
            page_count = book_info.get('pageCount', 'No Page Count')
            language = book_info.get('language', 'No Language Specified')

            # Append the filtered details to the result
            result.append({
                'title': title,
                'author': author,
                'description': description,
                'categories': categories,
                'content_version': content_version,
                'image_links': image_links,
                'isbn': isbn_number,
                'page_count': page_count,
                'language': language
            })
        
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Failed to fetch books'}), 500



## search by Title

@books_bp.route('/search_by_title', methods=['POST'])
def search_books_by_title():
    data = request.get_json()

    # Extract the book title from the JSON request
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Book title is required'}), 400

    # Use Google Books API to search for books by title
    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': f'intitle:{title}',
        'maxResults': 22,  # Adjust as needed
        'printType': 'books'
    }
    
    response = requests.get(GOOGLE_BOOKS_API, params=params)
    
    if response.status_code == 200:
        books = response.json().get('items', [])
        
        # Prepare the JSON response
        result = []
        for book in books:
            book_info = book.get('volumeInfo', {})
            
            # Get the authors list and join it into a string
            authors = book_info.get('authors', ['No author'])
            author = ', '.join(authors)

            # Extracting required details
            title = book_info.get('title', 'No Title')
            description = book_info.get('description', 'No Description')
            categories = book_info.get('categories', ['No Categories'])
            content_version = book_info.get('contentVersion', 'No Version')
            image_links = book_info.get('imageLinks', {})
            industry_identifiers = book_info.get('industryIdentifiers', [])
            isbn = industry_identifiers[0].get('identifier') if industry_identifiers else 'No ISBN'
            page_count = book_info.get('pageCount', 'No Page Count')
            language = book_info.get('language', 'No Language Specified')

            # Append the filtered details to the result
            result.append({
                'title': title,
                'author': author,
                'description': description,
                'categories': categories,
                'content_version': content_version,
                'image_links': image_links,
                'isbn': isbn,
                'page_count': page_count,
                'language': language
            })
        
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Failed to fetch books'}), 500

def title(title):
    # Use Google Books API to search for books by title
    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': f'intitle:{title}',
        'maxResults': 1,  # Fetch only one result for simplicity
        'printType': 'books'
    }

    response = requests.get(GOOGLE_BOOKS_API, params=params)
    
    if response.status_code == 200:
        books = response.json().get('items', [])
        if books:
            book_info = books[0].get('volumeInfo', {})

            # Get the authors list and join it into a string
            authors = book_info.get('authors', ['No author'])
            author = ', '.join(authors)

            return {
                'title': book_info.get('title', 'No Title'),
                'author': author,
                'description': book_info.get('description', 'No Description'),
                'categories': book_info.get('categories', []),
                'isbn': book_info.get('industryIdentifiers', [{}])[0].get('identifier', 'No ISBN'),
                'page_count': book_info.get('pageCount', 'No Page Count'),
                'language': book_info.get('language', 'No Language Specified')
            }
    return None



@books_bp.route('/get_user_library', methods=['POST'])
def get_user_library():
    data = request.get_json()

    # Extract the user_uuid from the JSON request
    user_uuid = data.get('user_uuid')
    if not user_uuid:
        return jsonify({'error': 'User UUID is required'}), 400

    # Fetch the user profile from the profile collection
    user_profile = profiles_collection.find_one({'uuid': user_uuid})
    if not user_profile or 'library' not in user_profile:
        return jsonify({'error': 'User profile or library not found'}), 404

    # Extract the list of book_ids from the user's library in the profile
    book_ids = user_profile['library']

    # Prepare the response list with book details from the Google Books API
    result = []
    for book_id in book_ids:
        print(book_id)
        # Fetch the book details from books_collection using book_id
        book = books_collection.find_one({'book_id': book_id})
        print(book)
        if book:
            book_title = book.get('title', 'No Title')
            # Call search_books_by_title to get detailed book info
            book_details = title(book_title)
            if book_details:
                result.append({
                    'book_id': str(book_id),  # Convert ObjectId or integer to string
                    'title': book_details.get('title', 'No Title'),
                    'authors': [book_details.get('author', 'Unknown Author')],
                    'description': book_details.get('description', 'No Description'),
                    'categories': book_details.get('categories', []),
                    'isbn': book_details.get('isbn', 'No ISBN'),
                    'page_count': book_details.get('page_count', 'No Page Count'),
                    'lang': book_details.get('language', 'No Language Specified')

                })

    # Return the result as JSON
    return jsonify({'library': result}), 200

##most popular categories
@books_bp.route('/most_popular_categories', methods=['GET','POST'])
def search_most_popular_categories():
    categories=['Romance','Mystery','Fantasy','Science Fiction','Thrillers','Horror','Children Fiction','Inspirational','Biography','Religious Books']
    return jsonify({"Categories":categories})
@books_bp.route('/search_by_category', methods=['POST'])
def search_books_by_category():
    data = request.get_json()

    # Extract the book category from the JSON request
    category = data.get('categories')
    if not category:
        return jsonify({'error': 'Categories is required'}), 400

    # Use Google Books API to search for books by category
    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': f'subject:{category}',
        'maxResults': 10,  # Adjust as needed
        'printType': 'books'
    }
    
    response = requests.get(GOOGLE_BOOKS_API, params=params)
    
    if response.status_code == 200:
        books = response.json().get('items', [])
        
        # Prepare the JSON response
        result = []
        for book in books:
            book_info = book.get('volumeInfo', {})

            # Get the authors list and join it into a string
            authors = book_info.get('authors', ['Unknown Author'])
            author = ', '.join(authors)
            
            # Extracting required details
            title = book_info.get('title', 'No Title')
            description = book_info.get('description', 'No Description')
            categories = book_info.get('categories', ['No Categories'])
            content_version = book_info.get('contentVersion', 'No Version')
            image_links = book_info.get('imageLinks', {})
            industry_identifiers = book_info.get('industryIdentifiers', [])
            isbn = industry_identifiers[0].get('identifier') if industry_identifiers else 'No ISBN'
            page_count = book_info.get('pageCount', 'No Page Count')
            language = book_info.get('language', 'No Language Specified')

            # Append the filtered details to the result
            result.append({
                'title': title,
                'description': description,
                'author': author,
                'categories': categories,
                'content_version': content_version,
                'image_links': image_links,
                'isbn': isbn,
                'page_count': page_count,
                'language': language
            })
        
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Failed to fetch books'}), 500



@books_bp.route('/search_by_author_and_category', methods=['POST'])
def search_books_by_author_and_category():
    data = request.get_json()

    # Extract author and category from the JSON request
    author = data.get('author')
    category = data.get('category')
    
    if not author or not category:
        return jsonify({'error': 'Author and category are required'}), 400

    # Use Google Books API to search for books by author and category
    GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': f'inauthor:{author}+subject:{category}',
        'maxResults': 25,  # Adjust as needed
        'printType': 'books'
    }

    response = requests.get(GOOGLE_BOOKS_API, params=params)

    if response.status_code == 200:
        books = response.json().get('items', [])

        # Prepare the JSON response
        result = []
        for book in books:
            book_info = book.get('volumeInfo', {})
            
            # Extracting required details
            description = book_info.get('description', 'No Description')
            title = book_info.get('title', 'No Title')
            authors = book_info.get('authors', ['Unknown Author'])
            content_version = book_info.get('contentVersion', 'No Version')
            image_links = book_info.get('imageLinks', {})
            industry_identifiers = book_info.get('industryIdentifiers', [])
            isbn = industry_identifiers[0].get('identifier') if industry_identifiers else 'No ISBN'
            page_count = book_info.get('pageCount', 'No Page Count')
            language = book_info.get('language', 'No Language Specified')
            categories = book_info.get('categories', ['No Categories'])

            # Append the filtered details to the result
            result.append({
                'title': title,
                'description': description,
                'authors': authors,
                'categories': categories,
                'content_version': content_version,
                'image_links': image_links,
                'isbn': isbn,
                'page_count': page_count,
                'language': language
            })

        return jsonify(result), 200
    else:
        return jsonify({'error': 'Failed to fetch books'}), 500





OLA_API_URL = "https://api.olamaps.io/routing/v1/distanceMatrix"  # Replace with actual Ola API URL
OLA_API_KEY = "1VlO_.sdKjsE~4/5uK5BBKz"  # Replace with your actual API key

# @books_bp.route('/calculate_travel_time', methods=['POST'])
# def calculate_travel_time():
#     data = request.get_json()

#     # Extract latitude and longitude for both users
#     user1_lat = data.get('user1_lat')
#     user1_lng = data.get('user1_lng')
#     user2_lat = data.get('user2_lat')
#     user2_lng = data.get('user2_lng')

#     # Validate that all required values are present
#     if not all([user1_lat, user1_lng, user2_lat, user2_lng]):
#         return jsonify({'error': 'All latitude and longitude values are required'}), 400

#     # Prepare parameters for the API request
#     params = {
#         "origins": f"{user1_lat},{user1_lng}",
#         "destinations": f"{user2_lat},{user2_lng}",
#         "key": OLA_API_KEY
#     }

#     # Make the API request
#     response = requests.get(OLA_API_URL, params=params)
    
#     # Handle the API response
#     if response.status_code == 200:
#         travel_data = response.json()
#         return jsonify(travel_data), 200
#     else:
#         return jsonify({'error': 'Failed to fetch travel time data from Ola API'}), 500


@books_bp.route('/calculate_travel_time', methods=['POST'])
def calculate_travel_time():
    data = request.get_json()

    # Get user inputs
    origins = data.get('origins')
    destinations = data.get('destinations')
    mode = data.get('mode', 'driving')  # Default to driving if not provided

    if not origins or not destinations:
        return jsonify({'error': 'Origins and destinations are required'}), 400

    # Construct query parameters
    params = {
        "origins": origins,
        "destinations": destinations,
        "mode": mode,
        "key": OLA_API_KEY
    }
    try:
        # Make the API request
        response = requests.get(OLA_API_URL, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Check if the response contains valid JSON data
        try:
            travel_data = response.json()
        except ValueError:
            return jsonify({'error': 'Invalid JSON response from Ola API'}), 500

        return jsonify(travel_data), 200

    except requests.exceptions.RequestException as e:
        # Capture any request-related errors
        return jsonify({'error': 'Failed to fetch travel time data from Ola API', 'details': str(e)}), 500
