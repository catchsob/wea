'''dependencies: requests beautifulsoup4'''

import threading
from time import time

import requests
from bs4 import BeautifulSoup

class WeaG:
    '''Weather Grabber, to grab observed weather information from official CWA website'''

    URLS = {'site_obs': 'https://www.cwa.gov.tw/V8/C/W/Observe/MOD/24hr/TBD.html',
            'site_map': 'https://www.cwa.gov.tw/Data/js/Observe/OSM/C/STMap.json'}

    def __init__(self, verbose=False):
        '''to initialize the weather sites information'''

        self.verbose = verbose
        self.sites, self.coors = self._load_sitemap()
    
    def grab(self, site):
        '''to grab observed temperature, humidity, and rainfall information from official CWA website
           params - site: name of site, should be the same as CWA official website
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
    
    def grabs(self, *sites, timeout=3):
        '''to grab observed temperature, humidity, and rainfall information from official CWA website of
           multiple sites
           params - sites: names of sites, should be the same as CWA official website
           return - observation time, temperature, humidity, and rainfall in dict of list obey the order
                    of sites, ex: [{'O': '11/02 11:20', 'T': 27.5, 'H': 0.73, 'R': 0.0},
                                   {'O': '11/02 11:20', 'T': 28.1, 'H': 0.65, 'R': 0.5}]
        '''

        if not sites:
            print('grabs got empty sites!')
            return None

        # define the execution target of each thread
        def _grab(site):
            nonlocal obs

            if site in self.sites:
                obs[site] = {}
                url = __class__.URLS['site_obs'].replace('TBD', self.sites[site])
                r = requests.get(url)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    try:
                        obs[site]['O'] = soup.find(headers="time").text
                        obs[site]['T'] = float(soup.find(class_="tem-C").text)
                        obs[site]['H'] = float(soup.find(headers="hum").text)/100
                        obs[site]['R'] = float(soup.find(headers="rain").text)
                    except Exception as e:
                        if self.verbose:
                            print(f'_grab {site} got {e}')
                r.close()
            else:
                obs[site] = None
            
            if self.verbose:
                print(f'grab {site} got {obs[site]}')
        
        # start multi threads
        obs = {}
        ths = []
        for site in sites:
            th = threading.Thread(target=_grab, args=(site,), daemon=True)
            th.start()
            ths.append(th)

        # timeout control of multi threads
        start = time()
        i = 0
        while i < len(ths) and ((timeout_remain := timeout - time() + start) > 0):
            ths[i].join(timeout=timeout_remain)
            i += 1

        return [obs.get(s) for s in sites]

    @classmethod
    def tostr(cls, observation, sep=', '):
        '''convert {'O': '11/02 11:20', 'T': 27.5, 'H': 0.73, 'R': 0.0} to
           觀測時間: 06/07 21:40 溫度: 25.6°C, 濕度: 97%, 雨量: 49.0mm
        '''

        if type(observation) == dict:
            items = [f'觀測時間: {observation.get("O", "N/A")}']
            t = observation.get("T")
            items.append('溫度: ' + ('N/A' if t == None else f'{t:.1f}°C'))
            h = observation.get("H")
            items.append('濕度: ' + ('N/A' if h == None else f'{h:.0%}'))
            r = observation.get("R")
            items.append('雨量: ' + ('N/A' if r == None else f'{r:.1f}mm'))
            return (sep if sep != None and type(sep) == str else ', ').join(items)
        return ''

    def _load_sitemap(self):
        sites, coors = {}, {}

        r = requests.get(__class__.URLS['site_map'])
        if r.status_code == 200:
            for s in r.json():
                sites[s['STname']] = s['ID']
                coors[s['STname']] = {'coor': (float(s['Lat']), float(s['Lon'])), 'addr': s['Addr']}
        r.close()
        if self.verbose:
            print(f"{len(sites)} sites are loaded from {__class__.URLS['site_map'].split('/')[-1]}")
        return sites, coors


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('sites', nargs='*', default=['臺北'],
                        help='weather of site to be grabbed, default 臺北')
    parser.add_argument('-t', '--timeout', type=float, default=3, help='timeout, default 3s')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    
    print('\nby WeaG().grab() in sequence')
    w = WeaG(args.verbose)
    start = time()
    for site in args.sites:
        if r := w.grab(site):
            print(f'{site} {w.tostr(r)}')
        else:
            print(f'{site} 查無此站！')
    print(f'elapsed for {time()-start:.3f}s')

    print('\nby WeaG().grabs() by multi-thread')
    w = WeaG(args.verbose)
    start = time()
    if r := w.grabs(*args.sites, timeout=args.timeout):
        for i, site in enumerate(args.sites):
            if r[i]:
                print(f'{site} {w.tostr(r[i])}')
            else:
                print(f'{site} 查無此站！')
    else:
        print('something wrong!')
    print(f'elapsed for {time()-start:.3f}s')
