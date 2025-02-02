import os
from flask import Flask
from .colleges import colleges_bp
from .courses import courses_bp
from .students import students_bp
from .index import index_bp
from config import SECRET_KEY,CLOUD_NAME,API_KEY,API_SECRET
import cloudinary
def create_app():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    template_path = os.path.join(project_root, 'templates')
    static_path = os.path.join(project_root, 'static')
    
    cloudinary.config( 
    cloud_name = CLOUD_NAME, 
    api_key = API_KEY, 
    api_secret = API_SECRET,
    secure=True
    )
    

    app = Flask(__name__, 
                template_folder=template_path,
                
                static_folder=static_path)
    
    app.secret_key = SECRET_KEY  


    
    app.register_blueprint(colleges_bp, url_prefix='/colleges')
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(students_bp, url_prefix='/students')
    app.register_blueprint(index_bp)  
    
    return app