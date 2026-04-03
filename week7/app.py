from flask import Flask, render_template

app = Flask(__name__, static_folder='static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hobbies')
def hobbies():
    my_hobbies = ["Coding", "Gaming", "Reading", "Dancing"]
    return render_template('hobbies.html', hobbies=my_hobbies)

if __name__ == '__main__':
    app.run(debug=True)