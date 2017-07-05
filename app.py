from threading import Thread
from flask import Flask, render_template
from flask_socketio import SocketIO, send
import parser as parser

app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    sites = [parser.name for parser in parser.parsers]
    return render_template('index.html', odds=parser.odds, sites=sites)


parse_thread = Thread(target=parser.parse_loop)

if __name__ == '__main__':
    parse_thread.start()
    socketio.run(app)
