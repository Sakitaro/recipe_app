from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os
import recipe_app  

app = Flask(__name__)

# データベースの設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

load_dotenv()
secret_key =  os.getenv('SECRET_KEY')
app.secret_key = secret_key

# Flask-Loginの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# UserMixinを継承したUserクラスを作成します
# ユーザーモデルの定義
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# データベースの初期化コマンド
@app.cli.command("init-db", help="Initialize the database.")
def init_db():
    db.create_all()
    print("Database initialized.")


# ユーザーをロードするためのコールバック関数を設定します
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# サインアップ
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Check if email already exists in the users list
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # Show an error message and redirect to the signup page
            flash('This email is already registered. Please use a different email.', category='error')
            return redirect(url_for('signup'))

        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        # Log in the user after successful registration
        login_user(new_user)
        return redirect(url_for('index'))

    return render_template('signup.html')


# ログインページ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Invalid email or password'
    return render_template('login.html')

# ログアウトページ
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/get_recipe", methods=["POST"])
@login_required
def get_recipe():
    ingredients = request.form.get("ingredients")
    ingredients_list = ingredients.split(', ')
    recipes = recipe_app.request_recipe(ingredients_list)
    # 3つのレシピを改行で区切ってまとめる
    result = '\n\n'.join(recipes)
    return result

if __name__ == "__main__":
    app.run(debug=True)
