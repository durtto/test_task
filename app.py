import json
import time
from threading import Thread
import requests
from lxml import html
from flask import Flask, render_template
from flask_socketio import SocketIO, send

odds = {}
interval = 1


class Odd():
    def __init__(self, name, value, print_value, probability):
        self.name = name
        self.value = value  # example: 1.4, 1.5
        self.print_value = print_value  # example: 1/4, 2/7
        self.probability = probability

    def to_dict(self):
        return {'name': self.name, 'value': self.value,
                'print_value': self.print_value,
                'probability': self.probability}


class BaseMarketParser:
    url = None

    @property
    def name(self):
        return ""

    def parse(self):
        """
        :return dict {Odd.name: Odd}
        """
        return {}


def calculate_probabilities(odds):
    sum = reduce(lambda sum, odd: 1 / odd['value'], odds)
    for odd in odds:
        odd['probability'] = 1 / odd['value'] / sum


# Parsers impl
class SkyBet(BaseMarketParser):
    @property
    def name(self):
        return "SkyBet"


class Bet365(BaseMarketParser):
    url = 'https://www.bet365.com/?lng=1&amp;cb=105812028182#/AC/B2/C101/' \
          'D20170703/E20537844/F65742225/G1/P11/'

    @property
    def name(self):
        return "Bet365"


class PaddyPower(BaseMarketParser):
    @property
    def name(self):
        return "PaddyPower"


class WilliamHill(BaseMarketParser):
    url = 'http://sports.williamhill.com/bet/en-gb/results///E/11336004/' \
          'thisDate/2017/07/03/17:00:00//5%3a00+Pontefract.html'

    @property
    def name(self):
        return "WilliamHill"

    def parse(self):
        page = requests.get(self.url)
        if page.status_code != 200:
            return False
        tree = html.fromstring(page.content)
        horses = tree.xpath(
            '//table[@class="md_runnerDetails md_rd_template5"]//'
            'td[@class="md_runner"]/text()')
        scores = tree.xpath(
            '//table[@id="meetingData_results"]//td[@class="md_column5"]/'
            'strong/text()')
        horses = [h.strip() for h in horses if h.strip()]
        scores = [h.strip() for h in scores]
        result = {}
        for horse, value in zip(horses, scores):
            print_value = value
            odd, to = print_value.split('/')
            real_value = float(odd) / int(to)
            result[horse] = Odd(horse, real_value, print_value, 0).to_dict()
        calculate_probabilities(result.values())
        return result


parsers = [SkyBet(), Bet365(), PaddyPower(), WilliamHill()]


def get_odds():
    odds = {}
    for parser in parsers:
        site_odds = parser.parse()
        for odd, value in site_odds.items():
            if not odds.get(odd):
                odds[odd] = {parser.name: value}
            else:
                odds[odd][parser.name] = value
    return odds


def parse_loop():
    global odds
    while True:
        odds = get_odds()
        #send(json.dumps(odds), json=True, namespace='/update', broadcast=True)
        time.sleep(interval)


app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    sites = [parser.name for parser in parsers]
    return render_template('index.html', odds=odds, sites=sites)


parse_thread = Thread(target=parse_loop)

if __name__ == '__main__':
    parse_thread.start()
    socketio.run(app)
