from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def index():
    data = request.args.get('data')
    network_routers = request.args.get('network_routers') 
    return render_template('index.html', data=data, network_routers=network_routers)


if __name__ == '__main__':
    app.run(debug=True)
