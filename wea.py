# pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup

class WeaG:
    '''Weather Grabber, to grab observed weather information from official CWA website'''

    URLS = {'site_obs': 'https://www.cwa.gov.tw/V8/C/W/Observe/MOD/24hr/TBD.html',
            'site_map': 'https://www.cwa.gov.tw/Data/js/Observe/OSM/C/STMap.json'}

    def __init__(self, verbose=False):
        '''to initialize the weather sites information'''

        self.verbose = verbose
        self.sites = self._load_sitemap()
    
    def grab(self, site):
        '''to grab observed temperature, humidity, and rainfall information from official CWA website
           params - location: name of site, should be the same as CWA official website
           return - observation time, temperature, humidity, and rainfall in dict,
                    ex: {'O': '11/02 11:20', 'T': 27.5, 'H': 0.73, 'R': 0.0}
        '''

        obs = {}
        if site in self.sites:
            url = __class__.URLS['site_obs'].replace('TBD', self.sites[site])
            r = requests.get(url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                try:
                    obs['O'] = soup.find(headers="time").text
                    obs['T'] = float(soup.find(class_="tem-C").text)
                    obs['H'] = float(soup.find(headers="hum").text)/100
                    obs['R'] = float(soup.find(headers="rain").text)
                except Exception as e:
                    if self.verbose:
                        print(f'grab {site} got {e}')
            r.close()
        
        if self.verbose:
            print(f'grab {site} got {obs}')
        return obs
    
    def _load_sitemap(self):
        r = requests.get(__class__.URLS['site_map'])
        sites = {i['STname']: i['ID'] for i in r.json()} if r.status_code == 200 else {}
        r.close()
        if self.verbose:
            print(f"{len(sites)} sites are loaded from {__class__.URLS['site_map'].split('/')[-1]}")
        return sites


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('sites', nargs='*', default=['臺北'],
                        help='weather of site to be grabbed, default 臺北')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    
    w = WeaG(args.verbose)
    for site in args.sites:
        if r := w.grab(site):
            print(f'{site} 觀測時間: {r["O"]} 溫度: {r["T"]:.1f}°C, 濕度: {r["H"]:.0%}, 雨量: {r["R"]:.1f}mm')
        else:
            print(f'{site} 查無此站！')
