from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def index():
    target = app.config.get('TARGET')
    data = app.config.get('ENC_DATA')
    network_routers = app.config.get('NETWORK_ROUTERS_JSON')

    return render_template('index.html', target=target, data=data, network_routers=network_routers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

