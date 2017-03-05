# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging
from flask import Flask, request, current_app
import requests

from hcssupdater import HCSSUpdater

app = Flask(__name__)

BOT_ID = "33284e04361b09285e04b5beb1"
BOT_URL = 'https://api.groupme.com/v3/bots/post'


def report_command(data):
    try:
        value = data['text'].split()[1]
    except IndexError:
        requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text':"Sorry %s! I don't know what went wrong!" % data['name']})
        return
    updater = HCSSUpdater('1U-wAQAXaDFYZ2uQvPtxL5kSDOss8kMPRRpyb6OgRbKs')
    updater.update_score(data['name'], value, data['created_at'])
    requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text':"Okay %s! I added that to the sheeeeet!" % data['name']})


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
    logging.critical("Does this message work or what?")
    return 'IT WOIKS!'


@app.route('/groupme', methods=['post', 'get'])
def groupme():
    logging.critical("-->GROUPME")
    with app.app_context():
        if not hasattr(current_app, 'groupme_data'):
            current_app.groupme_data = []
        groupme_data = current_app.groupme_data

    if request.method == 'POST':
        json = request.get_json()
        logging.critical(json)
        groupme_data.append(json)
        with app.app_context():
            current_app.groupme_data = groupme_data
        process_request({'text': json['text'], 'name': json['name'], 'created_at': json['created_at']})

    logging.critical('<--GROUPME')
    return "<br><br>".join(str(d) for d in groupme_data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
# [END app]
