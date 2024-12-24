from blueprint import create_app
from flask import Flask

app = Flask(__name__)
app.secret_key = '123456'

app = create_app()
if __name__ == '__main__':
    app.run(debug=True)