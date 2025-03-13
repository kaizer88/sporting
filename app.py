from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Flask app
app = Flask(__name__)


# Setup PostgreSQL connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('PG_HOST'),
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD'),
        database=os.getenv('PG_DATABASE')
    )
    return conn


# API endpoint to add a user
@app.route('/add-user', methods=['POST'])
def add_user():
    # Get data from the POST request
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert user into the database
        cursor.execute(
            'INSERT INTO users (username, email) VALUES (%s, %s) RETURNING *',
            (username, email)
        )
        new_user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(
            {"message": "User added", "user": {"id": new_user[0], "username": new_user[1], "email": new_user[2]}}), 201

    except Exception as e:
        return jsonify({"error": f"Failed to add user: {str(e)}"}), 500

# API endpoint to list all users
@app.route('/users', methods=['GET'])
def get_users():

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        users_list = [{"id": user[0], "username": user[1], "email": user[2]} for user in users]

        return jsonify({"users": users_list}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to retrieve users: {str(e)}"}), 500


# API endpoint to update a user by ID
@app.route('/update-user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET username = %s, email = %s WHERE id = %s RETURNING *',
            (username, email, user_id)
        )
        updated_user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if updated_user:
            return jsonify({"message": "User updated", "user": {"id": updated_user[0], "username": updated_user[1],
                                                                "email": updated_user[2]}}), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
