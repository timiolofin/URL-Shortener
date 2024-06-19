from flask import Flask, request, jsonify, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import string
import random
import os

app = Flask(__name__, static_folder='build')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

@app.before_request
def create_tables():
    db.create_all()

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(6))
    link = URL.query.filter_by(short_url=short_url).first()
    if link:
        return generate_short_url()
    return short_url

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data['original_url']
    short_url = generate_short_url()
    new_link = URL(original_url=original_url, short_url=short_url)
    db.session.add(new_link)
    db.session.commit()
    return jsonify({'short_url': request.host_url + short_url}), 201

@app.route('/<short_url>')
def redirect_to_url(short_url):
    link = URL.query.filter_by(short_url=short_url).first_or_404()
    return redirect(link.original_url)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)

