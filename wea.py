# pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup

class WeaG:
    '''Weather Grabber, to grab observed weather information from official CWA website'''

    def __init__(self):
        '''to initialize the weather sites information'''

        self._url = 'https://www.cwa.gov.tw/V8/C/W/Observe/MOD/24hr/TBD.html'
        self._load()
    
    def grab(self, site):
        '''to grab observed rainfall, temperature, and humidity information from official CWA website
           params - location: name of site, should be same as CWA official website
           return - observation time, rainfall, temperature, and humidity in dict,
                    ex: {'O': '11/02 11:20', 'T': 27.5, 'H': 0.73, 'R': 0.0}
        '''

        rtn = {}
        if site in self.sites:
            url = self._url.replace('TBD', self.sites[site])
            r = requests.get(url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                try:
                    rtn['O'] = soup.find(headers="time").text
                    rtn['T'] = float(soup.find(class_="tem-C").text)
                    rtn['H'] = float(soup.find(headers="hum").text)/100
                    rtn['R'] = float(soup.find(headers="rain").text)
                except:
                    pass
            r.close()
        return rtn
    
    def _load(self):
        url = 'https://www.cwa.gov.tw/Data/js/Observe/OSM/C/STMap.json'
        r = requests.get(url)
        self.sites = {i['STname']: i['ID'] for i in r.json()} if r.status_code == 200 else {}
        r.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('sites', nargs='*', default=['臺北'],
                        help='weather of site to be grabbed, default 臺北')
    args = parser.parse_args()
    
    w = WeaG()
    for site in args.sites:
        r = w.grab(site)
        if r:
            print(r)
            print(f'{site} 觀測時間: {r["O"]} 溫度: {r["T"]:.1f}°C, 濕度: {r["H"]:.0%}, 雨量: {r["R"]:.1f}mm')
        else:
            print(f'{site} 查無此站！')
