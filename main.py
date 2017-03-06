# [START app]
import logging
from flask import Flask, request, redirect
import requests

from hcssupdater import HCSSUpdater

app = Flask(__name__)

TEST_BOT_ID = '33284e04361b09285e04b5beb1'
BOT_ID = "9f0b7f63622e7968c464b7ff8d"
BOT_URL = 'https://api.groupme.com/v3/bots/post'
TEST_SHEET_ID = '1U-wAQAXaDFYZ2uQvPtxL5kSDOss8kMPRRpyb6OgRbKs'
SHEET_ID = '15-w7N4Qqw5MnpRmnd7bm2cyqbgWR-JPOT-wnmpMnvNs'
SHEET_LINK = 'https://goo.gl/HTWJLj'


def report_command(data):
    try:
        value = data['text'].split()[1]
    except (TypeError, IndexError, KeyError):
        logging.exception("error in report_command")
        requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text': "Sorry %s! That didn't work and I don't know what went wrong!" % (data['name'].split() or ['you'])[0]})
        return
    updater = HCSSUpdater(SHEET_ID, sheet_name='Points')
    updater.update_score(data['name'], value, data['created_at'])
    requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text': "Okay %s! I added %s to the spreadsheet! %s" % ((data['name'].split() or ['you'])[0], value, SHEET_LINK)})


def echo_command(data):
    requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text': " ".join(data['text'].split()[1:])})


def quote_command(data):
    r = requests.get('http://quotes.rest/qod.json?category=inspire')
    data = r.json()
    try:
        quote = data['contents']['quotes'][0]
        requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text': '"%s" -%s' % (quote['quote'], quote['author'])})
    except (TypeError, IndexError, KeyError):
        logging.exception('quote_commend ran into an error')


def stats_command(data):
    updater = HCSSUpdater(SHEET_ID, sheet_name='Points')
    stats = updater.stats()
    response = []
    for i in range(len(stats[0])):
        response.append("%s: %s" % (stats[0][i], stats[1][i]))
    requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text': ", ".join(response)})


commands = {
    '/report': report_command,
    '/echo': echo_command,
    '/quote': quote_command,
    '/stats': stats_command
}


def process_request(data):
    commands.get((data['text'].split() or [None])[0], lambda x: None)(data)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello everyone!'


@app.route('/groupme', methods=['post', 'get'])
def groupme():
    if request.method == 'POST':
        json = request.get_json()
        process_request({'text': json['text'], 'name': json['name'], 'created_at': json['created_at']})
        return ''
    else:
        return redirect('https://docs.google.com/spreadsheets/d/1U-wAQAXaDFYZ2uQvPtxL5kSDOss8kMPRRpyb6OgRbKs', code=302)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
# [END app]
