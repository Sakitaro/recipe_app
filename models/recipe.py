import sqlite3

class Recipe:
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
