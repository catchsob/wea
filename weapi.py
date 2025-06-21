# dependencies: flask, wea, requests, bs4


__version__ = '0.2.0'


import flask
import wea


print(f'[weapi-{__version__} (wea-{wea.__version__})]', flush=True)


app = flask.Flask(__name__)

@app.route('/', methods=['POST'])
def do_wea():
    if ((d := flask.request.form) and (site := d.get('site'))) or \
        ((d := flask.request.get_json()) and (site := d.get('site'))):
        r = wea.grab(site)
        return r if d.get('raw') == True else wea.tostr(r)
    return 400

if __name__ == '__main__':
    app.run()
