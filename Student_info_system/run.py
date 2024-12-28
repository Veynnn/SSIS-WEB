from blueprint import create_app
from flask import Flask
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv(".env")

app = create_app()
if __name__ == '__main__':
    app.run(debug=True)