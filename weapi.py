# pip install Flask

# version 0.1.0: support multi-site

from flask import Flask, request
from wea import WeaG

__version__ = '0.1.0'

app = Flask('weapi-'+__version__)

w = WeaG()

@app.route('/obs', methods=['POST'])
def obs():
    if request.args and 'site' in request.args:
        rs = {}
        j = {'success': False}
        for site in request.args.getlist('site'):
            r = w.grab(site)
            rs[site] = r if r else None
            if r:
                j['success'] = True
        j.update(rs)
    else:
        j = {'success': False, 'reason': 'query got no site'}
    print(j)
    return j


if __name__ == '__main__':
    app.run()
