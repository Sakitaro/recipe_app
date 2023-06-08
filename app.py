from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, g
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
from urllib.parse import unquote

import os
from recipe_app import request_recipe, request_instructions
import sqlite3

class User:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                       (id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
        self.conn.commit()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS recipes
                       (id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        ingredients TEXT NOT NULL,
                        instructions TEXT NOT NULL,
                        user_id INTEGER,
                        image_filename TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
        self.conn.commit()

        # Check if the image_filename column exists
        self.cursor.execute("PRAGMA table_info(recipes)")
        columns = self.cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # If the image_filename column does not exist, add it
        if 'image_filename' not in column_names:
            self.cursor.execute("ALTER TABLE recipes ADD COLUMN image_filename TEXT")
            self.conn.commit()

    def add_user(self, username, email, password):
        self.cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        self.conn.commit()

    def get_user(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()
        return user

    def add_recipe(self, user_id, title, ingredients, instructions, image_filename):
        self.cursor.execute("INSERT INTO recipes (user_id, title, ingredients, instructions, image_filename) VALUES (?, ?, ?, ?, ?)", (user_id, title, ingredients, instructions, image_filename))
        self.conn.commit()

    def get_all_recipes(self):
        self.cursor.execute("""SELECT recipes.id, recipes.title, recipes.ingredients, recipes.instructions, users.username, recipes.image_filename
                            FROM recipes
                            JOIN users ON recipes.user_id = users.id
                            ORDER BY recipes.created_at DESC""")
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
    if hasattr(g, 'user_db'):
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

# 画像の保存
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size):
    image = Image.open(image_path)
    image.thumbnail(max_size)
    image.save(image_path)

@app.route('/post_recipe', methods=['GET', 'POST'])
def post_recipe():
    if request.method == 'POST':
        # 画像ファイルをチェックし、保存
        image = request.files.get('image')
        if not image or not allowed_file(image.filename):
            flash("Invalid image format. Allowed formats: jpg, jpeg, png, gif", "danger")
            return redirect(url_for('post_recipe'))

        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        resize_image(image_path, (800, 800))

        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions'].replace('\r\n', '<br>').replace('\n', '<br>')

        g.user_db.add_recipe(session.get('user_id'), title, ingredients, instructions, filename)
        g.user_db.conn.commit()

        return redirect(url_for('post_recipe'))

    title = unquote(request.args.get('title', ''))
    ingredients = unquote(request.args.get('ingredients', ''))
    instructions = unquote(request.args.get('instructions', '')).replace('<br>', '\n')

    recipes = g.user_db.get_all_recipes()
    return render_template('post_recipe.html', recipes=recipes, title=title, ingredients=ingredients, instructions=instructions)

@app.route('/new_post', methods=['GET'])
def new_post():
    title = unquote(request.args.get('title', ''))
    ingredients = unquote(request.args.get('ingredients', ''))
    instructions = unquote(request.args.get('instructions', '')).replace('<br>', '\n')
    return render_template('new_recipe.html', title=title, ingredients=ingredients, instructions=instructions)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

