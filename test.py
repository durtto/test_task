import re
import requests

url = 'https://www.bet365.com/SportsBook.API/web?lid=1&zid=9&pd=%23AC%23B2%23C101%23D20170706%23E20538211%23F65791671%23K20538211%23M65791671%23P11%23%3A%23AC%23B2%23C101%23D20170706%23E20538211%23F65791673%23K20538211%23M65791673%23P11%23%3A%23AC%23B2%23C101%23D20170706%23E20538211%23F65791676%23K20538211%23M65791676%23P11%23%3A%23AC%23B2%23C101%23D20170706%23E20538211%23F65791677%23K20538211%23M65791677%23P11%23%3A%23AC%23B2%23C101%23D20170706%23E20538211%23F65791678%23K20538211%23M65791678%23P11%23%3A%23AC%23B2%23C101%23D20170706%23E20538211%23F65791680%23K20538211%23M65791680%23P11%23%3A%23AC%23B2%23C101%23D20170706%23E20538211%23F65791683%23K20538211%23M65791683%23P11%23%3A&cid=195&cg=0'
page = requests.get(url)
for m in re.findall('NA=([^;]*);OD=([^;]*);', page.text.replace('\n', '')):
    print(m)
