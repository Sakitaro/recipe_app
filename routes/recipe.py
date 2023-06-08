from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.recipe import Recipe
from urllib.parse import unquote
from recipe_app import request_recipe, request_instructions
from services.image_service import ImageService

recipe_bp = Blueprint('recipe', __name__)

# 画像の保存
UPLOAD_FOLDER = 'static/uploads'

@recipe_bp.route("/get_recipe", methods=["POST"])
def get_recipe():
    ingredients = request.form.get("ingredients")
    ingredients_list = ingredients.split(', ')
    recipes = request_recipe(ingredients_list)
    # 3つのレシピを改行で区切ってまとめる
    result = '\n\n'.join(recipes)
    return result

@recipe_bp.route("/get_instructions", methods=["POST"])
def get_instructions():
    data = request.get_json()
    recipe_name = data.get("recipe_name")
    instructions = request_instructions(recipe_name)
    return instructions

@recipe_bp.route('/post_recipe', methods=['GET', 'POST'])
def post_recipe():
    if request.method == 'POST':
        # 画像ファイルをチェックし、保存
        image = request.files.get('image')
        if not image or not ImageService.allowed_file(image.filename):  # 更新
            flash("Invalid image format. Allowed formats: jpg, jpeg, png, gif", "danger")
            return redirect(url_for('recipe.post_recipe'))

        filename = ImageService.save_image(image, UPLOAD_FOLDER)  # 更新

        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions'].replace('\r\n', '<br>').replace('\n', '<br>')

        recipe_db = Recipe()
        recipe_db.add_recipe(session.get('user_id'), title, ingredients, instructions, filename)
        recipe_db.conn.commit()

        return redirect(url_for('recipe.post_recipe'))

    title = unquote(request.args.get('title', ''))
    ingredients = unquote(request.args.get('ingredients', ''))
    instructions = unquote(request.args.get('instructions', '')).replace('<br>', '\n')

    recipe_db = Recipe()
    recipes = recipe_db.get_all_recipes()
    return render_template('post_recipe.html', recipes=recipes, title=title, ingredients=ingredients, instructions=instructions)

@recipe_bp.route('/new_post', methods=['GET'])
def new_post():
    title = unquote(request.args.get('title', ''))
    ingredients = unquote(request.args.get('ingredients', ''))
    instructions = unquote(request.args.get('instructions', '')).replace('<br>', '\n')
    return render_template('new_recipe.html', title=title, ingredients=ingredients, instructions=instructions)
