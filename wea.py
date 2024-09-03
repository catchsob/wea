import json

import requests
from bs4 import BeautifulSoup
from haversine import haversine

class WeaG:

    _URL_RAIN = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001'
    _URL_STMAP = 'https://www.cwa.gov.tw/Data/js/Observe/OSM/C/STMap.json'
    _URL_WEB = 'https://www.cwa.gov.tw/V8/C/W/Observe/MOD/24hr/SITEID.html'
    
    def __init__(self, env_json='env.json'):
        """
        env_json - environment variables JSON file name , two parameters would be handled:
                   1. 'CWA_KEY', will grab rainfall information if key is assigned
                   2. 'VERBOSE', will dump more message if true is assigned
        """
        # init env
        try:
            with open(env_json, 'r', encoding='utf-8') as f:
                env = json.load(f)
        except Exception as e:
            env = {}
            print(f'handle {env_json} got Exception:', e)
        self.env = {'CWA_KEY': env.get('CWA_KEY'),
                    'VERBOSE': env.get('VERBOSE', False)}
        
        # siteids = {'46694': {'name': '基隆', 'src': 'web', 'coors': (25.13331389, 121.740475)},
        #            'C1F87': {'name': '上谷關', 'src': 'C1F871', 'coors': (121.01865, 24.203484)}}
        self.siteids = {}
        self._init_web()
        if self.env['CWA_KEY']:
            self._init_rain()

    def _init_web(self):
        r = requests.get(__class__._URL_STMAP)
        if r.status_code == 200:
            for i in r.json():
                self.siteids[i['ID']] = {'name': i['STname'],
                                         'src': 'web',
                                         'coors': (float(i['Lat']), float(i['Lon']))}
            if self.env['VERBOSE']:
                print(f'_init_web() update {len(r.json())} sites')
        else:
            print('_init_web() got', r.status_code)
    
    def _init_rain(self):
        params = {'Authorization': self.env['CWA_KEY']}
        r = requests.get(__class__._URL_RAIN, params=params)
        if r.status_code == 200:
            count = 0
            for i in r.json()['records']['Station']:
                i_id = i['StationId'][:-1]
                if i_id not in self.siteids:
                    self.siteids[i_id] = {'name': i['StationName'],
                                          'src': i['StationId'],
                                          'coors': (i['GeoInfo']['Coordinates'][1]['StationLatitude'],
                                                    i['GeoInfo']['Coordinates'][1]['StationLongitude'])
                                         }
                    count += 1
            if self.env['VERBOSE']:
                print(f'_init_rain() update {count} sites')
        else:
            print('_init_rain() got', r.status_code)

    def grab(self, site, n=1):
        """grab weather information of specific site name, or of nereast site coorindate
        site   - site name of str or site coordinate of tuple(latitude, longitude)
        n      - site number of weather information to be grabbed, must be between 1 ~ 5 of int
        return - weather information in dict or list, ex:
                 n == 1
                 {'R': 0.0, 'H': 0.84, 'T': 28.5, 'O': '09/03 21:30', 'C': (23.97512778, 121.613275)}
                 n > 1
                 [{'O': '09/03 21:30', 'R': 0.0, 'H': 0.84, 'T': 28.5, 'C': (23.97512778, 121.613275)},
                  {'O': '2024-09-03 21:40:00', 'R': 0.0, 'C': (23.972935, 121.60599)}]     
        """
        n = max(1, min(5, type(n) == int and n))  # size should be between 1 ~ 5
        
        # search siteid by name
        if type(site) == str:
            info = []
            for siteid in self.siteids:
                if self.siteids[siteid]['name'] == site:
                    src = self.siteids[siteid]['src']
                    if r := self._grab_web(siteid) if src == 'web' else self._grab_rain(src):
                        info.append(r)
                        if len(info) == n:
                            break
            if n == 1:
                return info[0] if info else {}
            return info
        
        # search siteid by coordinates
        elif type(site) == tuple and len(site) == 2 and all(isinstance(v, float) for v in site):
            ds = [(haversine(self.siteids[s]['coors'], site), s) for s in self.siteids]
            info = []
            for i in sorted(ds)[:n]:
                siteid = i[1]
                src = self.siteids[siteid]['src']
                if r := self._grab_web(siteid) if src == 'web' else self._grab_rain(src):
                    r['S'] = self.siteids[siteid]['name']
                    info.append(r)
            if n == 1:
                return info[0] if info else {}
            return info

        return {}

    def _grab_rain(self, siteid):
        params = {'Authorization': self.env['CWA_KEY'],
                  'RainfallElement': 'Now',
                  'StationId': siteid}
        info = {}
        r = requests.get(__class__._URL_RAIN, params=params)
        if r.status_code == 200:
            if r.json()['records']['Station']:
                a = r.json()['records']['Station'][0]
                info['O'] = a['ObsTime']['DateTime'].replace('+08:00', '').replace('T', ' ')
                info['R'] = float(a['RainfallElement']['Now']['Precipitation'])
                info['C'] = self.siteids[siteid[:-1]]['coors']
        return info
        
    def _grab_web(self, siteid):
        info = {}
        r = requests.get(__class__._URL_WEB.replace('SITEID', siteid))
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            if a := soup.find(headers="rain"):
                info['R'] = float(a.text)
            if a := soup.find(headers="hum"):
                info['H'] = float(a.text)/100
            if a := soup.find(class_="tem-C"):
                info['T'] = float(a.text)
            if a := soup.find(headers="time"):
                info['O'] = a.text
            info['C'] = self.siteids[siteid]['coors']
        return info

    @staticmethod
    def tostr(info, sep=', '):
        """translate grabbed weather information to readble str
        info - grabbed weather information of dict
        sep  - separator of each weather information
        """
        if not info or type(info) != dict:
            return '無此站'
        
        r = []
        if 'S' in info:
            r.append(f'測站: {info["S"]}')
        if 'O' in info:
            r.append(f'時間: {info["O"]}')
        if 'T' in info:
            r.append(f'溫度: {info["T"]:.1f}℃')
        if 'H' in info:
            r.append(f'濕度: {info["H"]:.1%}')
        if 'R' in info:
            r.append(f'雨量: {info["R"]:.1f}mm')

        return (type(sep) == str and sep or ', ').join(r)
    
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('site', help='site name')
    parser.add_argument('--env', '-e', default='env.json',
                        help='environment file in json, default env.json')
    parser.add_argument('--size', '-n', type=int, default=1,
                        help='max number of sites would be grabbed, default 1')

    args = parser.parse_args()

    w = WeaG(args.env)
    r = w.grab(args.site, args.size)
    if type(r) == dict:
        print(w.tostr(r))
    elif type(r) == list:
        for i in r:
            print(w.tostr(i))
