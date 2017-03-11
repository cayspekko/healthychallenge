# [START app]
import logging
import requests

from flask import Flask, request, redirect
from hcssupdater import HCSSUpdater

app = Flask(__name__)
app.config['DEBUG'] = True
logging.critical('-->APP START')

BOT_URL = 'https://api.groupme.com/v3/bots/post'
TEST_SHEET_ID = '1U-wAQAXaDFYZ2uQvPtxL5kSDOss8kMPRRpyb6OgRbKs'
SHEET_ID = '15-w7N4Qqw5MnpRmnd7bm2cyqbgWR-JPOT-wnmpMnvNs'
SHEET_LINK = 'https://goo.gl/HTWJLj'

BOTS = {
    '28874652': '33284e04361b09285e04b5beb1',  # Test room
    '27099638': '9f0b7f63622e7968c464b7ff8d'  # Main room
}


def bot_speak(group_id, text):
    if BOTS.get(group_id):
        requests.post(BOT_URL, data={'bot_id': BOTS[group_id], 'text': text})


def report_command(data):
    try:
        value = data['text'].split()[1]
    except (TypeError, IndexError, KeyError):
        logging.exception("error in report_command")
        bot_speak(data['group_id'], "Sorry %s! That didn't work and I don't know what went wrong!" % (data['name'].split() or ['you'])[0])
        return
    updater = HCSSUpdater(SHEET_ID, sheet_name='Points')
    updater.update_score(data['name'], value, data['created_at'])
    bot_speak(data['group_id'], "Okay %s! I added %s to the spreadsheet!" % ((data['name'].split() or ['you'])[0], value))


def echo_command(data):
    bot_speak(data['group_id'], " ".join(data['text'].split()[1:]))


def quote_command(data):
    r = requests.get('http://quotes.rest/qod.json?category=inspire')
    quote_data = r.json()
    try:
        quote = quote_data['contents']['quotes'][0]
        bot_speak(data['group_id'], '"%s" -%s' % (quote['quote'], quote['author']))
    except (TypeError, IndexError, KeyError):
        logging.exception('quote_commend ran into an error')


def stats_command(data):
    updater = HCSSUpdater(SHEET_ID, sheet_name='Points')
    logging.critical('Read updater %s' % bool(updater))
    stats = updater.stats()
    logging.critical('stats %s' % stats)
    response = []
    for i in range(len(stats[0])):
        response.append("%s: %s" % (stats[0][i], stats[1][i]))

    bot_speak(data['group_id'], ", ".join(response))


def sheet_command(data):
    bot_speak(data['group_id'], "Here's the link: %s" % SHEET_LINK)


def help_command(data):
    help = ['Here are the commands: ']
    help.extend("{}\t{} {}".format(k, " ".join(v[1:-1]), v[-1]) for k, v in commands.items())
    bot_speak(data['group_id'], "\n".join(help))

commands = {
    '/report': (report_command, '[number]', 'also /r [number]. Report [number] to the spreadsheet.'),
    '/echo': (echo_command, '[text]', 'Repeats [text].'),
    '/quote': (quote_command, 'Gets the quote of the day courtesy theysaidso.com'),
    '/stats': (stats_command, 'Gets the current report stats'),
    '/sheet': (sheet_command, 'Prints the url of the spreadsheet'),
    '/help': (help_command, 'Prints this help command')
}

short_commands = {
    '/r': '/report'
}


def process_request(data):
    try:
        command = (data['text'].split() or [None])[0]
        command = short_commands.get(command, command)
        commands.get(command, (lambda x: None,))[0](data)
    except Exception as e:
        logging.exception("Command %s failed" % command)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    logging.critical('Hello everyone!')
    return 'Hello everyone!'


@app.route('/groupme', methods=['post', 'get'])
def groupme():
    if request.method == 'POST':
        json = request.get_json()
        logging.critical('DATA: %s' % json)
        if json.get('sender_type') == 'user':  # ignore non-humans
            process_request({'text': json['text'], 'name': json['name'], 'created_at': json['created_at'], 'group_id': json['group_id']})
        return ''
    else:
        return redirect('https://docs.google.com/spreadsheets/d/1U-wAQAXaDFYZ2uQvPtxL5kSDOss8kMPRRpyb6OgRbKs', code=302)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
# [END app]
