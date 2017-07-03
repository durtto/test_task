import json
from threading import Thread
import requests
import lxml
from lxml import html
from io import StringIO
from lxml import etree
from flask import Flask, render_template
from flask_socketio import SocketIO, send


class Odd():
    def __init__(self, name, value, print_value, probability):
        self.name = name
        self.value = value  # example: 1.4, 1.5
        self.print_value = print_value  # example: 1/4, 2/7
        self.probability = probability


class BaseMarketParser:
    url = None

    @property
    def name(self):
        return ""

    def parse(self):
        """
        :return dict {Odd.name: Odd}
        """
        raise NotImplementedError


def calculate_probabilities(odds):
    sum = reduce(lambda odd: 1 / odd.value, odds)
    for odd in odds:
        odd.probability = 1 / odd.value / sum


# Parsers impl
class SkyBet(BaseMarketParser):
    pass


class Bet365(BaseMarketParser):
    url = 'https://www.bet365.com/?lng=1&amp;cb=105812028182#/AC/B2/C101/' \
          'D20170703/E20537844/F65742225/G1/P11/'

    def parse(self):
        page = requests.get(self.url)
        if page.status_code != 200:
            return False
        tree = html.fromstring(page.content)
        horses = tree.xpath(
            '//span[@class="rl-HorseTrainerJockey_Horse"]/text()')
        print horses


class PaddyPower(BaseMarketParser):
    pass


class WilliamHill(BaseMarketParser):
    pass


parsers = [SkyBet(), Bet365(), PaddyPower(), WilliamHill()]


def get_odds():
    odds = {}
    for parser in parsers:
        site_odds = parser.parse()
        for odd, value in site_odds:
            if not odds.get(odd):
                odds[odd] = {parser.name: value}
            else:
                odds[odd][parser.name] = value
    return odds


def parse_loop():
    while True:
        new_data = get_odds()
        send(json.dumps(new_data), json=True, namespace='/update')


app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    odds = get_odds()
    sites = [parser.name for parser in parsers]
    return render_template('index.html', odds=odds, sites=sites)


parse_thread = Thread(target=parse_loop)

if __name__ == '__main__':
    # parse_thread.start()
    socketio.run(app)
