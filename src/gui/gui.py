from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def index():
    param = request.args.get("data", "{}")
    return render_template('index.html', data=param)

if __name__ == '__main__':
    app.run(debug=True)
