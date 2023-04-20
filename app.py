from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from recipe_app import request_recipe, request_instructions


app = Flask(__name__)

load_dotenv()
secret_key = os.getenv('SECRET_KEY')
app.secret_key = secret_key

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


if __name__ == "__main__":
    app.run(debug=True)
