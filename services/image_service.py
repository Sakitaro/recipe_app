from PIL import Image
from werkzeug.utils import secure_filename
import os

class ImageService:
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ImageService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_image(image, upload_folder):
        filename = secure_filename(image.filename)
        image_path = os.path.join(upload_folder, filename)
        image.save(image_path)
        ImageService.resize_image(image_path, (800, 800))
        return filename

    @staticmethod
    def resize_image(image_path, max_size):
        image = Image.open(image_path)
        image.thumbnail(max_size)
        image.save(image_path)
