from flask import Flask, render_template, request

app = Flask(__name__, static_folder='static')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hobbies')
def hobbies():
    my_hobbies = ["Coding", "Gaming", "Reading", "Dancing"]
    return render_template('hobbies.html', hobbies=my_hobbies)

@app.route('/contact')
def contact():
    return render_template('contact.html')

import os

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('username', 'Anonymous')

    # Save to message log file under week8 folder
    messages_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'messages.txt')
    with open(messages_path, 'a', encoding='utf-8') as f:
        f.write(f"{name}\n")

    print(f"Message received from: {name}")  # Prints to VS Code terminal
    return f"Thanks for the message, {name}!"

if __name__ == '__main__':
    app.run(debug=True)