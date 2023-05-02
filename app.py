from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, g
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import os
from recipe_app import request_recipe, request_instructions
import sqlite3

class User:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS recipes
                       (id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        ingredients TEXT NOT NULL,
                        instructions TEXT NOT NULL,
                        user_id INTEGER,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
        self.conn.commit()

    def add_user(self, username, email, password):
        self.cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        self.conn.commit()

    def get_user(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()
        return user

    def add_recipe(self, user_id, title, ingredients, instructions):
        self.cursor.execute("INSERT INTO recipes (user_id, title, ingredients, instructions) VALUES (?, ?, ?, ?)", (user_id, title, ingredients, instructions))
        self.conn.commit()

    def get_all_recipes(self):
        self.cursor.execute("""SELECT recipes.id, recipes.title, recipes.ingredients, recipes.instructions, users.username
                             FROM recipes
                             JOIN users ON recipes.user_id = users.id""")
        recipes = self.cursor.fetchall()
        return recipes


    def close(self):
        self.conn.close()

app = Flask(__name__)

load_dotenv()
secret_key = os.getenv('SECRET_KEY')
app.secret_key = secret_key

@app.before_request
def before_request():
    g.user_db = User()

@app.teardown_request
def teardown_request(exception):
    g.user_db.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_recipe", methods=["POST"])
def get_recipe():
    ingredients = request.form.get("ingredients")
    ingredients_list = ingredients.split(', ')
    recipes = request_recipe(ingredients_list)
    # 3つのレシピを改行で区切ってまとめる
    result = '\n\n'.join(recipes)
    return result

@app.route("/get_instructions", methods=["POST"])
def get_instructions():
    data = request.get_json()
    recipe_name = data.get("recipe_name")
    instructions = request_instructions(recipe_name)
    return instructions

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = g.user_db.get_user(username)
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        try:
            g.user_db.add_user(username, email, password)
            flash('Registered successfully.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'danger')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/post_recipe', methods=['GET', 'POST'])
def post_recipe():
    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']

        g.user_db.add_recipe(session.get('user_id'), title, ingredients, instructions)
        g.user_db.conn.commit()

        return redirect(url_for('index'))

    recipes = g.user_db.get_all_recipes()
    return render_template('post_recipe.html', recipes=recipes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

