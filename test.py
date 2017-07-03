import requests
from lxml import html

url = 'https://www.bet365.com/?lng=1&amp;cb=105812028182#/AC/B73/C104/' \
      'D20170703/E20537884/F65746428/G1/P11/'


def parse():
    page = requests.get(url)
    if page.status_code != 200:
        return False
    tree = html.fromstring(page.content)
    horses = tree.xpath('//span[@class="rl-HorseTrainerJockey_Horse"]')
    print horses


parse()


