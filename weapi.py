# pip install Flask

# version 0.1.0: support multi-site
# version 0.1.1: respond version

from flask import Flask, request
from wea import WeaG

__version__ = '0.1.1'

app = Flask('weapi-'+__version__)

w = WeaG()

@app.route('/obs', methods=['POST'])
def obs():
    j = {'success': False, 'version': __version__}
    if request.args and 'site' in request.args:
        rs = {}
        for site in request.args.getlist('site'):
            r = w.grab(site)
            rs[site] = r if r else None
            if r:
                j['success'] = True
        j.update(rs)
    else:
        j['reason'] = 'query got no site'
    print(j)
    return j


if __name__ == '__main__':
    app.run()
