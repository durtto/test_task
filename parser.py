import json
import re
import time

import requests
from lxml import html

import config

odds = {name: {} for name in config.EVENTS}


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


def __dict__(self):
    return {'name': self.name, 'value': self.value,
            'print_value': self.print_value,
            'probability': self.probability}


class BaseMarketParser:
    name = ""

    def parse(self, url):
        """
        :return dict {Odd.name: Odd}
        """
        return {}


def calculate_probabilities(odds):
    sum = 0
    for odd in odds:
        sum += 1 / odd['value']
    for odd in odds:
        odd['probability'] = 1 / odd['value'] / sum


# Parsers impl
class SkyBet(BaseMarketParser):
    name = "SkyBet"


class Bet365(BaseMarketParser):
    name = "Bet365"

    def parse(self, url):
        page = requests.get(url)
        if page.status_code != 200:
            return {}
        result = {}
        for m in re.findall('NA=([^;]*);OD=([^;]*);',
                            page.text.replace('\n', '')):
            horse = m[0]
            print_value = m[1]
            if print_value == 'SP':
                continue
            odd, to = print_value.split('/')
            value = float(odd) / int(to)
            result[horse] = Odd(horse, value, print_value, 0).to_dict()
        calculate_probabilities(result.values())


class PaddyPower(BaseMarketParser):
    name = "PaddyPower"

    def parse(self, url):
        page = requests.get(url)
        if page.status_code != 200:
            return {}
        m = re.search('hr_ev_init\((.*),"",\'!!!!!!!!!',
                      page.text.replace('\n', ''))
        if not m:
            return {}
        found = m.group(1)
        found = "[%s]" % found
        js = json.loads(found)
        result = {}
        for odd in js[3]:
            if not odd['lp_den']: continue
            horse = odd['names']['en']
            odd, to = int(odd['lp_num']), int(odd['lp_den'])
            print_value = '%s/%s' % (odd, to)
            value = float(odd) / to
            result[horse] = Odd(horse, value, print_value, 0)
        calculate_probabilities(result.values())


class WilliamHill(BaseMarketParser):
    name = "WilliamHill"

    def parse(self, url):
        page = requests.get(url)
        if page.status_code != 200:
            return False
        tree = html.fromstring(page.text)
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


parsers = {}
for parser in BaseMarketParser.__subclasses__():
    instance = parser()
    parsers[instance.name] = instance


def update_odds():
    for event_name, event in config.EVENTS.items():
        update_event_odds(event_name, event)


def update_event_odds(event, sites):
    for parser_name, url in sites.items():
        site_odds = parsers[parser_name].parse(url)
        for odd, value in site_odds.items():
            if not odds.get(odd):
                odds[event][odd] = {parser.name: value}
            else:
                odds[event][odd][parser.name] = value
    return odds


def parse_loop():
    while True:
        update_odds()
        with open(config.ODDS_FILE, 'w') as f:
            json.dump(odds, f)
        # ignore time spent for parsing
        time.sleep(config.INTERVAL)


if __name__ == '__main__':
    parse_loop()
