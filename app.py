from threading import Thread

from flask import Flask, render_template

import parser as bet_parser

app = Flask(__name__, template_folder='.')
app.config.from_pyfile('config.py')


@app.route('/')
def index():
    sites = [parser for parser in bet_parser.parsers]
    return render_template('index.html', odds=bet_parser.odds, sites=sites)


parse_thread = Thread(target=bet_parser.parse_loop)

if __name__ == '__main__':
    parse_thread.start()
    app.run()
