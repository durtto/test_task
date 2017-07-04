import requests
from lxml import html

url = 'http://sports.williamhill.com/bet/en-gb/results///E/11336004/thisDate/2017/07/03/17:00:00//5%3a00+Pontefract.html'


def parse():
    page = requests.get(url)
    if page.status_code != 200:
        return False
    tree = html.fromstring(page.content)
    horses = tree.xpath(
        '//table[@class="md_runnerDetails md_rd_template5"]//td[@class="md_runner"]/text()')
    scores = tree.xpath(
        '//table[@id="meetingData_results"]//td[@class="md_column5"]/strong/text()')
    horses = [h.strip() for h in horses if h.strip()]
    scores = [h.strip() for h in scores]
    return zip(horses, scores)


r = parse()
for horse, score in iter(r):
    print '%s - %s' % (horse, score)
