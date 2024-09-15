from flask import Flask, jsonify, request
from blueprints.books import books_bp
from flask_cors import CORS
from blueprints.exchange_bp import exchange_bp
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import cross_origin
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
# Set the secret key
app.config['SECRET_KEY'] = 'b4f308c7eee4457bd087fabb550688e4'

# Register the books blueprint
app.register_blueprint(exchange_bp)
app.register_blueprint(books_bp)

# Connect to MongoDB Atlas
#mongodb+srv://mriduaayu123:xhiUSnVjZEGIH22n@cluster0.uc4f1.mongodb.net/
uri = "mongodb+srv://mriduaayu123:xhiUSnVjZEGIH22n@cluster0.uc4f1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

#client = MongoClient('mongodb+srv://mriduaayu123:xhiUSnVjZEGIH22n@cluster0.uc4f1.mongodb.net/swap_book')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['swap_book']  
profiles_collection = db['profile']
books_collection=db['BookDataset']
user_library=db['user_library']

# Test MongoDB connection
@app.route('/test_db_connection', methods=['GET'])
def test_db_connection():
    try:
        # The 'ping' command is used to check the connection to the server
        client.admin.command('ping')
        return jsonify({'message': 'MongoDB connection successful'}), 200
    except ConnectionFailure:
        return jsonify({'error': 'MongoDB connection failed'}), 500


def get_uuid_from_request():
    return request.args.get('uuid')

#Create  user profile
#Function will be called after the person registers as before login profile should exists
@cross_origin()
@app.route('/create_profile', methods=['POST'])
def create_profile():
    data = request.get_json()
    user_uuid = data.get('uuid')

    if not user_uuid:
        return jsonify({'error': 'UUID is required'}), 400

    profile_data = {
        ##profile data, bio data
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'latitude': data.get('latitude'),
        'longitude': data.get('longitude'),
        'email': data.get('email'),
        'phone': data.get('phone'),
        'bio':data.get('bio', ''),
        'given_list': [],
        'taken_list': [],
        'library': []
    }

    # Upsert the profile (insert if doesn't exist, otherwise update)
    profiles_collection.update_one({'uuid': user_uuid}, {'$set': profile_data}, upsert=True)

    return jsonify({'message': 'Profile created successfully'}), 200


# Configure the upload folder and allowed extensions
# UPLOAD_FOLDER = 'uploads/'
# ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/create_profile', methods=['POST'])
# @cross_origin()
# def create_profile():
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file part in the request'}), 400
        
#         file = request.files['file']
#         user_uuid = request.form.get('uuid')

#         if not user_uuid:
#             return jsonify({'error': 'UUID is required'}), 400

#         # Handle file upload
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             profile_picture = file_path  # Store the path to the uploaded file
#         else:
#             profile_picture = ''

#         profile_data = {
#             'first_name': request.form.get('first_name'),
#             'last_name': request.form.get('last_name'),
#             'latitude': request.form.get('latitude'),
#             'longitude': request.form.get('longitude'),
#             'email': request.form.get('email'),
#             'phone': request.form.get('phone'),
#             'bio': request.form.get('bio', ''),  # Add bio field
#             'profile_picture': profile_picture,  # Store the profile picture path
#             'given_list': [],
#             'taken_list': [],
#             'library': []
#         }

#         # Upsert the profile (insert if doesn't exist, otherwise update)
#         profiles_collection.update_one({'uuid': user_uuid}, {'$set': profile_data}, upsert=True)

#         return jsonify({'message': 'Profile created successfully'}), 200
#     except Exception as e:
#         # Log the error and return a generic error response
#         print(f"Error in create_profile: {str(e)}")
#         return jsonify({'error': 'An internal error occurred', 'details': str(e)}), 500

# Function to check if a profile exists
@app.route('/check_profile/<string:uuid>', methods=['GET'])
def check_profile(uuid):
    if not uuid:
        return jsonify({'error': 'UUID is required'}), 400

    profile = profiles_collection.find_one({'uuid': uuid})
    if profile:
        return jsonify({'exists': True, 'message': 'Profile exists'}), 200
    else:
        return jsonify({'exists': False, 'message': 'Profile does not exist'}), 404


##get profile
#Function to get the user's profile
@app.route('/get_profile/<string:profile_id>', methods=['GET'])
def get_profile(profile_id):
    # Query the database using profile_id
    profile = profiles_collection.find_one({'uuid': profile_id}, {'_id': 0})
    
    if profile:
        return jsonify({'profile': profile}), 200
    else:
        return jsonify({'error': 'Profile not found'}), 404

##update profile
# Function to update the user's profile
@app.route('/update_profile/<profile_id>', methods=['PUT'])
def update_profile():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({'error': 'Invalid JSON format'}), 400

    user_uuid = get_uuid_from_request()
    if not user_uuid:
        return jsonify({'error': 'UUID is required'}), 400

    # Check if the profile exists
    existing_profile = profiles_collection.find_one({'uuid': user_uuid})
    if not existing_profile:
        return jsonify({'error': 'Profile does not exist. Create a profile first.'}), 404

    # Data to be updated in the profile
    profile_data = {
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'email': data.get('email'),
        'phone': data.get('phone'),
    }

    # Remove None values (fields the user doesn't want to update)
    profile_data = {k: v for k, v in profile_data.items() if v is not None}

    if not profile_data:
        return jsonify({'error': 'No data provided for update'}), 400

    # Update the profile
    result = profiles_collection.update_one({'uuid': user_uuid}, {'$set': profile_data})

    if result.matched_count > 0:
        return jsonify({'message': 'Profile updated successfully'}), 200
    else:
        return jsonify({'error': 'Profile update failed'}), 500

# Function to insert a book if it does not exist
# def insert_book_if_not_exists(book_title):
#     try:
#         # Generate a new book_id for the book
#         new_book_id = books_collection.count_documents({}) + 1  # Simple incremental ID generation
        
#         # Insert the book into the BOOKDataset collection
#         books_collection.insert_one({'book_id': new_book_id, 'title': book_title})
#         return new_book_id
#     except Exception as e:
#         print(f"Error inserting book: {str(e)}")
#         return None

# API to add a book to the user's library
# @app.route('/add_to_library', methods=['POST'])
# def add_to_library():
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Invalid JSON format'}), 400
        
#         # Extract book title and user UUID from the request payload
#         book_title = data.get('book_title')
#         user_uuid = data.get('user_uuid')
        
#         if not book_title:
#             return jsonify({'error': 'Book title is required'}), 400
#         if not user_uuid:
#             return jsonify({'error': 'UUID is required'}), 400

#         # Check if the book exists in the BOOKDataset collection
#         book = books_collection.find_one({'title': book_title})
        
#         if not book:
#             # If the book does not exist, insert it and get the new book_id
#             new_book_id = insert_book_if_not_exists(book_title)
#             if new_book_id is None:
#                 return jsonify({'error': 'Failed to insert book'}), 500
#         else:
#             new_book_id = book['book_id']
        
#         # Add the book_id to the user's library
#         user_library.update_one(
#             {'user_uuid': user_uuid},
#             {'$addToSet': {'library': new_book_id}},
#             upsert=True
#         )
        
#         return jsonify({'message': 'Book added to library successfully'}), 200
#     except Exception as e:
#         # Log the error and return a generic error response
#         print(f"Error in add_to_library: {str(e)}")
#         return jsonify({'error': 'An internal error occurred', 'details': str(e)}), 500

# Function to insert a book if it does not exist
def insert_book_if_not_exists(book_title):
    try:
        # Generate a new book_id for the book (incremental ID)
        new_book_id = books_collection.count_documents({}) + 1
        
        # Insert the book into the BOOKDataset collection
        books_collection.insert_one({'book_id': new_book_id, 'title': book_title})
        return new_book_id
    except Exception as e:
        print(f"Error inserting book: {str(e)}")
        return None


# API to add a book to the user's library
@app.route('/add_to_library', methods=['POST'])
def add_to_library():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON format'}), 400

        # Extract book title and user UUID from the request payload
        book_title = data.get('book_title')
        user_uuid = data.get('user_uuid')

        if not book_title:
            return jsonify({'error': 'Book title is required'}), 400
        if not user_uuid:
            return jsonify({'error': 'User UUID is required'}), 400

        # Check if the user exists in the profiles_collection
        user_profile = profiles_collection.find_one({'uuid': user_uuid})
        if not user_profile:
            return jsonify({'error': 'User not found'}), 404

        # Check if the book exists in the BOOKDataset collection
        book = books_collection.find_one({'title': book_title})

        if not book:
            # If the book does not exist, insert it and get the new book_id
            new_book_id = insert_book_if_not_exists(book_title)
            if new_book_id is None:
                return jsonify({'error': 'Failed to insert book'}), 500
        else:
            # Get the existing book ID
            new_book_id = book['book_id']

        # Add the book_id to the user's library if it's not already there
        result = profiles_collection.update_one(
            {'uuid': user_uuid},
            {'$addToSet': {'library': new_book_id}}  # $addToSet ensures no duplicates
        )

        if result.modified_count > 0:
            return jsonify({'message': 'Book added to library successfully'}), 200
        else:
            return jsonify({'message': 'Book already in library or no changes made'}), 200

    except Exception as e:
        # Log the error and return a generic error response
        print(f"Error in add_to_library: {str(e)}")
        return jsonify({'error': 'An internal error occurred', 'details': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
