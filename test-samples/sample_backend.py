"""
Sample Python backend code for testing Code Review Assistant.
"""

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Database connection
def get_db():
    conn = sqlite3.connect('database.db')
    return conn

@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def get_user(user_id):
    """Get user by ID."""
    query = f"SELECT * FROM users WHERE id = {user_id}"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'id': user[0],
        'name': user[1],
        'email': user[2]
    })

@app.route('/users', methods=['POST'])
def create_user():
    """Create new user."""
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO users (name, email) VALUES ('{name}', '{email}')"
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'User created'}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
