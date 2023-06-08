from flask import Flask, render_template
from dotenv import load_dotenv
import os

from routes.auth import auth_bp
from routes.recipe import recipe_bp

app = Flask(__name__)

# loading secret key
load_dotenv()
secret_key = os.getenv('SECRET_KEY')
app.secret_key = secret_key

# registering blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(recipe_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
