# [START app]
import logging
from flask import Flask, request, redirect
import requests

from hcssupdater import HCSSUpdater

app = Flask(__name__)

BOT_ID = "33284e04361b09285e04b5beb1"
BOT_URL = 'https://api.groupme.com/v3/bots/post'
SHEET_ID = '1U-wAQAXaDFYZ2uQvPtxL5kSDOss8kMPRRpyb6OgRbKs'


def report_command(data):
    try:
        value = data['text'].split()[1]
    except IndexError:
        requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text':"Sorry %s! I don't know what went wrong!" % data['name']})
        return
    updater = HCSSUpdater(SHEET_ID)
    updater.update_score(data['name'], value, data['created_at'])
    requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text': "Okay %s! I added %s to the sheeeeet!" % (data['name'], value)})


def echo_command(data):
    requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text':" ".join(data['text'].split()[1:])})

commands = {
    '/report': report_command,
    '/echo': echo_command
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
