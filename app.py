from flask import Flask, render_template, request, jsonify
import recipe_app  

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_recipe", methods=["POST"])
def get_recipe():
    ingredients = request.form.get("ingredients")
    ingredients_list = ingredients.split(', ')
    recipes = recipe_app.request_recipe(ingredients_list)
    # 3つのレシピを改行で区切ってまとめる
    result = '\n\n'.join(recipes)
    return result

if __name__ == "__main__":
    app.run(debug=True)
