from flask import Flask, request, render_template, Response, jsonify
from fetcher import fetch_and_process_file
from db import init_db
import sqlite3
from urllib.parse import urlparse

app = Flask(__name__)

# avatars.githubusercontent : Allows viewing github profile pictures by pasting the image url in the challenge.
# raw.githubusercontent : By creating a gist with the image content (on gist.github.com), and then copying its url and paste it in the challenge.

ALLOWED_DOMAINS = ['raw.githubusercontent.com', 'avatars.githubusercontent.com']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch_file():
    url = request.form.get('url')

    if not url:
        return 'No URL provided!', 400
    
    parsed_url = urlparse(url)

    if parsed_url.scheme != 'https' or parsed_url.netloc not in ALLOWED_DOMAINS or parsed_url.query:
        return jsonify({'error': 'Nope nope nope...'}), 403

    return fetch_and_process_file(url)

# Only admins can view which files have been uploaded
@app.route('/search', methods=['GET'])
def search_file():
    if request.remote_addr not in ['127.0.0.1', '::1']:
        return jsonify({'error': 'Access denied!'}), 403

    search_term = request.args.get('q')

    if not search_term:
        return jsonify({'error': 'No search term provided!'}), 400

    try:
        conn = sqlite3.connect('history.db')
        cursor = conn.cursor()

        query = f"SELECT filename, content_type FROM history WHERE filename LIKE '%{search_term}%' AND LENGTH(filename) > 0"
        cursor.execute(query)

        results = cursor.fetchall()

        conn.close()

        if not results:
            return jsonify({'message': 'No matching filenames found.'}), 404

        response_items = [{'filename': row[0], 'content_type': row[1]} for row in results]
        return jsonify({'matching_items': response_items}), 200

    except sqlite3.Error as e:
        return jsonify({'error': 'An error occurred'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0')
