from flask import Blueprint

user_bp = Blueprint('user_bp', __name__, url_prefix='/user', template_folder="/templates")

from root.user import routes
