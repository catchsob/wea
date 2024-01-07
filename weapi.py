# pip install Flask

from flask import Flask, request
from wea import WeaG

app = Flask(__name__)

w = WeaG()

@app.route('/obs', methods=['POST'])
def obs():
    if request.args and 'site' in request.args:
        site = request.args['site']
        r = w.grab(site)
        j = {'success': True, site: r} if r else {'success': False, 'reason': 'no such site'}
    else:
        j = {'success': False, 'reason': 'query got no site'}
    print(j)
    return j


if __name__ == '__main__':
    app.run()
