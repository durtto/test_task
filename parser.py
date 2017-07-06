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
        if odd:
            sum += 1 / odd['value']
    for odd in odds:
        if odd:
            odd['probability'] = 1 / odd['value'] / sum


# Parsers impl
class SkyBet(BaseMarketParser):
    name = "SkyBet"

    def parse(self, url):
        page = requests.get(url)
        if page.status_code != 200:
            return {}
        tree = html.fromstring(page.text)
        horses = tree.xpath(
            '/td[@class="runner-info section-end"]/div[@class="oc-runner '
            'oc-horse"]/h4/text()')
        scores_num = tree.xpath(
            '//td[starts-with(@class,"win text-centre")]/@data-oc-num')
        scores_den = tree.xpath(
            '//td[starts-with(@class,"win text-centre")]/@data-oc-num')
        scores = zip(scores_den, scores_num)
        horses = [h.strip() for h in horses if h.strip()]

        result = {}
        i = 0
        for score in scores:
            horse = horses[i]
            i += 1
            print_value = '%s/%s' % (score[0], score[1])
            value = float(score[0]) / int(score[1])
            result[horse] = Odd(horse, value, print_value, 0).to_dict()
        calculate_probabilities(result.values())
        return result


class Bet365(BaseMarketParser):
    name = "Bet365"

    def parse(self, url):
        page = requests.get(url)
        if page.status_code != 200:
            return {}
        result = {}
        matches = re.findall('NA=([^;]*);OD=([^;]*);',
                             page.text.replace('\n', ''))
        if not matches:
            return {}
        for m in matches:
            horse = m[0]
            print_value = m[1]
            if print_value == 'SP':
                continue
            odd, to = print_value.split('/')
            try:
                value = float(odd) / int(to)
            except TypeError:
                value = None
            result[horse] = Odd(horse, value, print_value, 0).to_dict()
        calculate_probabilities(result.values())
        return result


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
            try:
                value = float(odd) / int(to)
            except TypeError:
                value = None
            result[horse] = Odd(horse, value, print_value, 0).to_dict()
        calculate_probabilities(result.values())
        return result


class WilliamHill(BaseMarketParser):
    name = "WilliamHill"

    def parse(self, url):
        page = requests.get(url)
        if page.status_code != 200:
            return {}
        tree = html.fromstring(page.text)
        horses = tree.xpath(
            '//table[@class="md_runnerDetails md_rd_template2"]//'
            'td[@class="md_runner"]/text()')
        scores = tree.xpath(
            '//td[contains(@class,"racecardBoldCenter")]/a/text()')
        horses = [h.strip() for h in horses if h.strip()]
        scores = [h.strip() for h in scores]

        result = {}
        for horse, value in zip(horses, scores):
            print_value = value
            try:
                odd, to = print_value.split('/')
                real_value = float(odd) / int(to)
            except Exception:
                real_value = None
            result[horse] = Odd(horse, real_value, print_value, 0).to_dict()
        calculate_probabilities(result.values())
        return result


parsers = {}
for p in BaseMarketParser.__subclasses__():
    instance = p()
    parsers[instance.name] = instance


def update_odds():
    for event_name, event in config.EVENTS.items():
        update_event_odds(event_name, event)


def update_event_odds(event, sites):
    for parser_name, url in sites.items():
        parser = parsers[parser_name]
        site_odds = parser.parse(url)
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
