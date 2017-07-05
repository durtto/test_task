import requests
from lxml import html
import json
import re

url = 'http://www.paddypower.com/racing/horse-racing/deauville/11%3a25-STAKES-6f-101yds-12518007.html'


def parse():
    page = requests.get(url)
    if page.status_code != 200:
        return False
    m = re.search('hr_ev_init\((.*),"",\'!!!!!!!!!',
                  page.content.replace('\n', ''))
    if m:
        found = m.group(1)
        found = "[%s]" % found
        js = json.loads(found)
        for odd in js[3]:
            if not odd['lp_den']: continue
            print '%s - %s/%s' % (
                odd['names']['en'], odd['lp_num'], odd['lp_den'])