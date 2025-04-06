#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/clear', methods=['DELETE'])
def clear_session():
    session['page_views'] = None
    session['user_id'] = None
    return {}, 204

@app.route('/articles', methods=['GET'])
def index_article():
    articles = [article.to_dict() for article in Article.query.all()]
    return articles, 200

@app.route('/articles/<int:id>', methods=['GET'])
def show_article(id):
    session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
    session['page_views'] += 1

    if session['page_views'] <= 3:
        article = Article.query.filter(Article.id == id).first()
        article_json = jsonify(article.to_dict())
        return make_response(article_json, 200)

    return {'message': 'Maximum pageview limit reached'}, 401

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    user = User.query.filter_by(username=username).first()
    if not user:
        return {'message': 'User not found'}, 404
    
    session['user_id'] = user.id
    return user.to_dict(), 200

@app.route('/logout', methods=['DELETE'])
def logout():
    session['user_id'] = None
    return {}, 204

@app.route('/check_session', methods=['GET'])
def check_session():
    user_id = session.get('user_id')
    if not user_id:
        return {}, 401
    
    user = db.session.get(User, user_id)
    return user.to_dict(), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
