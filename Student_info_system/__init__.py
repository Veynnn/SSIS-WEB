from flask import Flask
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY  

from views import *

if __name__ == '__main__':
    app.run(debug=True)
