from flask import Blueprint, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import math

exchange_bp = Blueprint('exchange_bp', __name__)
uri = "mongodb+srv://mriduaayu123:xhiUSnVjZEGIH22n@cluster0.uc4f1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

#client = MongoClient('mongodb+srv://mriduaayu123:xhiUSnVjZEGIH22n@cluster0.uc4f1.mongodb.net/swap_book')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['swap_book']  
books_collection=db['BookDataset']
# MongoDB collections
profiles_collection = db['profile']  # Ensure this is set to your actual collection name
@exchange_bp.route('/exchange_books', methods=['POST'])
def exchange_books():
    data = request.get_json()
    
    # Extract book titles and user IDs from the request
    book_title_1 = data.get('book_title_1')
    book_title_2 = data.get('book_title_2')
    user_id_1 = data.get('user_id_1')
    user_id_2 = data.get('user_id_2')
    
    # Validate required parameters
    if not all([book_title_1, book_title_2, user_id_1, user_id_2]):
        return jsonify({'error': 'All parameters (book_title_1, book_title_2, user_id_1, user_id_2) are required'}), 400

    # Check if user_id_1 and user_id_2 exist in the profiles collection
    user_1_exists = profiles_collection.find_one({'uuid': user_id_1})
    user_2_exists = profiles_collection.find_one({'uuid': user_id_2})

    if not user_1_exists or not user_2_exists:
        return jsonify({'error': 'One or both user IDs do not exist'}), 404

    # Look up book_id for book_title_1
    book_1 = books_collection.find_one({'title': book_title_1})
    if not book_1:
        return jsonify({'error': f'Book with title "{book_title_1}" not found'}), 404
    book_id_1 = book_1['book_id']
    
    # Look up book_id for book_title_2
    book_2 = books_collection.find_one({'title': book_title_2})
    if not book_2:
        return jsonify({'error': f'Book with title "{book_title_2}" not found'}), 404
    book_id_2 = book_2['book_id']

    # Add book_id_1 to user_id_2's taken_list and book_id_2 to user_id_1's given_list
    profiles_collection.update_one(
        {'uuid': user_id_1},
        {'$addToSet': {'given_list': book_id_2}}
    )
    
    profiles_collection.update_one(
        {'uuid': user_id_2},
        {'$addToSet': {'taken_list': book_id_1}}
    )
    
    # Add book_id_2 to user_id_1's taken_list and book_id_1 to user_id_2's given_list
    profiles_collection.update_one(
        {'uuid': user_id_1},
        {'$addToSet': {'taken_list': book_id_2}}
    )
    
    profiles_collection.update_one(
        {'uuid': user_id_2},
        {'$addToSet': {'given_list': book_id_1}}
    )

    return jsonify({'message': 'Books exchanged successfully'}), 200

@exchange_bp.route('/get_taken_list/<string:user_id>', methods=['GET'])
def get_taken_list(user_id):
    # Fetch the user profile from the database
    user_profile = profiles_collection.find_one({'uuid': user_id})
    
    if not user_profile:
        return jsonify({'error': 'User not found'}), 404

    # Get the taken_list (book IDs)
    taken_list_ids = user_profile.get('taken_list', [])

    # Fetch corresponding book titles from the BookDataset collection
    book_titles = []
    if taken_list_ids:
        books = books_collection.find({'book_id': {'$in': taken_list_ids}})
        for book in books:
            book_titles.append(book.get('title'))

    return jsonify({'taken_list': book_titles}), 200


# @exchange_bp.route('/get_given_list/<string:user_id>', methods=['GET'])
# def get_given_list(user_id):
#     # Fetch the user profile from the database
#     user_profile = profiles_collection.find_one({'uuid': user_id})
    
#     if not user_profile:
#         return jsonify({'error': 'User not found'}), 404

#     given_list = user_profile.get('given_list', [])

#     return jsonify({'given_list': given_list}), 200

# @exchange_bp.route('/get_taken_list/<string:user_id>', methods=['GET'])
# def get_taken_list(user_id):
#     # Fetch the user profile from the database
#     user_profile = profiles_collection.find_one({'uuid': user_id})
    
#     if not user_profile:
#         return jsonify({'error': 'User not found'}), 404

#     taken_list = user_profile.get('taken_list', [])

#     return jsonify({'taken_list': taken_list}), 200

@exchange_bp.route('/get_given_list/<string:user_id>', methods=['GET'])
def get_given_list(user_id):
    # Fetch the user profile from the database
    user_profile = profiles_collection.find_one({'uuid': user_id})
    
    if not user_profile:
        return jsonify({'error': 'User not found'}), 404

    # Get the given_list (book IDs)
    given_list_ids = user_profile.get('given_list', [])

    # Fetch corresponding book titles from the BookDataset collection
    book_titles = []
    if given_list_ids:
        books = books_collection.find({'book_id': {'$in': given_list_ids}})
        for book in books:
            book_titles.append(book.get('title'))

    return jsonify({'given_list': book_titles}), 200

import math
from flask import request, jsonify

# Function to calculate the distance between two points using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


@exchange_bp.route('/calculate_distance', methods=['POST'])

def calculate_distance():
    """
    API endpoint to calculate the distance between two points based on latitude and longitude.
    Expects latitude and longitude of both users in the request payload.
    """
    data = request.get_json()
    
    lat1 = data.get('lat1')
    lon1 = data.get('lon1')
    lat2 = data.get('lat2')
    lon2 = data.get('lon2')
    
    # Check if any of the coordinates are missing
    if not lat1 or not lon1 or not lat2 or not lon2:
        return jsonify({'error': 'Latitude and longitude for both users are required.'}), 400
    
    try:
        # Calculate the distance using the Haversine formula
        distance = haversine(lat1, lon1, lat2, lon2)
        return jsonify({'distance_km': distance}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@exchange_bp.route('/explore', methods=['POST'])
def explore_books():
    """
    Explore API to find users within a radius and return the books they have that the requesting user does not.
    """
    data = request.get_json()

    user_id = data.get('user_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius = data.get('radius')  # Radius in kilometers

    # Check if all required parameters are provided
    if not all([user_id, latitude, longitude, radius]):
        return jsonify({'error': 'Missing required parameters.'}), 400

    # Fetch the profile of the requesting user
    requesting_user = profiles_collection.find_one({'uuid': user_id})

    if not requesting_user:
        return jsonify({'error': 'User not found'}), 404

    user_books = set(requesting_user.get('library', []))  # Check the library field for the requesting user
    print(f"Requesting user's books: {user_books}")

    # Find all users within the radius
    nearby_users = profiles_collection.find()

    results = []
    for user in nearby_users:
        if user['uuid'] == user_id:
            continue  # Skip the requesting user themselves

        user_latitude = user.get('latitude')
        user_longitude = user.get('longitude')

        # Check if latitude and longitude are valid
        if user_latitude is None or user_longitude is None:
            continue  # Skip this user if they don't have valid coordinates

        # Calculate the distance between the requesting user and the current user
        distance = haversine(latitude, longitude, user_latitude, user_longitude)
        print(f"Distance to user {user['uuid']}: {distance} km")

        if distance <= radius:
            # Print the full user object to check its structure
            print(f"Current user object: {user}")

            # Filter books the requesting user doesn't have
            other_user_books = set(user.get('library', [])) - user_books
            print(f"Other user's books: {other_user_books}")
            print(f"Requesting user's books: {user_books}")
            print("*********" * 10)
 # Fetch book titles from IDs
            other_user_books = books_collection.find({
                'book_id': {'$in': list(other_user_books)}
            })
            book_titles = [book['title'] for book in other_user_books]
            
            if book_titles:
                results.append({
                    'user_id': user['uuid'],
                    'name': f"{user['first_name']} {user['last_name']}",
                    'books': ', '.join(book_titles)  # Convert list of book titles to comma-separated string
                })


    if results:
        return jsonify(results), 200
    else:
        return jsonify({'message': 'No users found within the specified range'}), 200



# @exchange_bp.route('/get_user_library', methods=['POST'])
# def get_user_library():
#     data = request.get_json()

#     # Extract the user_uuid from the JSON request
#     user_uuid = data.get('user_uuid')
#     if not user_uuid:
#         return jsonify({'error': 'User UUID is required'}), 400

#     # Fetch the user profile from the profile collection
#     user_profile = profiles_collection.find_one({'uuid': user_uuid})
#     print(user_profile)

#     if not user_profile or 'library' not in user_profile:
#         return jsonify({'error': 'User profile or library not found'}), 404

#     # Extract the list of book_ids from the user's library in the profile
#     book_ids = user_profile['library']
#     print(book_ids)

#     # Prepare the response list with full book details
#     for book_id in book_ids:
#         print(book_id)
#     result = []

    
        
#     return result

# @exchange_bp.route('/get_user_library', methods=['POST'])
# def get_user_library():
#     data = request.get_json()

#     # Extract the user_uuid from the JSON request
#     user_uuid = data.get('user_uuid')
#     if not user_uuid:
#         return jsonify({'error': 'User UUID is required'}), 400

#     # Fetch the user profile from the profile collection
#     user_profile = profiles_collection.find_one({'uuid': user_uuid})
#     if not user_profile or 'library' not in user_profile:
#         return jsonify({'error': 'User profile or library not found'}), 404

#     # Extract the list of book_ids from the user's library in the profile
#     book_ids = user_profile['library']

#     # Prepare the response list with full book details
#     result = []
#     for book_id in book_ids:
#         print(book_id)
#         # Fetch the book details from books_collection using book_id
#         book = books_collection.find_one({'book_id': book_id})
#         print(book)
#         if book:
#             result.append({
#                 #'book_id': str(book['_id']),  # Convert ObjectId or integer to string
#                 'book_title': book.get('title', 'No Title'),
#                 'author': book.get('author', 'Unknown Author'),
#                 'isbn': book.get('isbn', 'No ISBN')
#             })

#     # Return the result as JSON
#     return jsonify({'library': result}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

##explore 
##userid 1 , user id 2, book id 1 , book id 2, 