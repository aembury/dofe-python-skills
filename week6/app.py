from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello! This is my Flask website."

@app.route('/about')
def about():
    return "This is the about page."

@app.route('/contact')
def contact():
    return "Email me at ..."

if __name__ == '__main__':
    app.run(debug=True)