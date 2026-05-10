from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message = None
    if request.method == 'POST':
        # You can access POST data using request.form.get('message')
        message = "Thank you for reaching out! We've successfully received your message."
        
    return render_template('contact.html', message=message)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
