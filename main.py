# [START app]
import logging
import logging.handlers

logger = logging.getLogger('Flask')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address='/dev/log')
logger.addHandler(handler)
logger.critical('>>>Start flask app>>>')

from flask import Flask, request, redirect
import requests

from hcssupdater import HCSSUpdater

app = Flask(__name__)
app.config['DEBUG'] = True

TEST_BOT_ID = '33284e04361b09285e04b5beb1'
BOT_ID = '33284e04361b09285e04b5beb1'
#BOT_ID = "9f0b7f63622e7968c464b7ff8d"
BOT_URL = 'https://api.groupme.com/v3/bots/post'
TEST_SHEET_ID = '1U-wAQAXaDFYZ2uQvPtxL5kSDOss8kMPRRpyb6OgRbKs'
SHEET_ID = '15-w7N4Qqw5MnpRmnd7bm2cyqbgWR-JPOT-wnmpMnvNs'
SHEET_LINK = 'https://goo.gl/HTWJLj'


def bot_speak(text):
    requests.post(BOT_URL, data={'bot_id': BOT_ID, 'text': text})


def report_command(data):
    try:
        value = data['text'].split()[1]
    except (TypeError, IndexError, KeyError):
        logger.exception("error in report_command")
        bot_speak("Sorry %s! That didn't work and I don't know what went wrong!" % (data['name'].split() or ['you'])[0])
        return
    updater = HCSSUpdater(SHEET_ID, sheet_name='Points')
    updater.update_score(data['name'], value, data['created_at'])
    bot_speak("Okay %s! I added %s to the spreadsheet!" % ((data['name'].split() or ['you'])[0], value))


def echo_command(data):
    bot_speak(" ".join(data['text'].split()[1:]))


def quote_command(data):
    r = requests.get('http://quotes.rest/qod.json?category=inspire')
    data = r.json()
    try:
        quote = data['contents']['quotes'][0]
        bot_speak('"%s" -%s' % (quote['quote'], quote['author']))
    except (TypeError, IndexError, KeyError):
        logger.exception('quote_commend ran into an error')


def stats_command(data):
    updater = HCSSUpdater(SHEET_ID, sheet_name='Points')
    stats = updater.stats()
    response = []
    for i in range(len(stats[0])):
        response.append("%s: %s" % (stats[0][i], stats[1][i]))
    bot_speak(", ".join(response))


def sheet_command(data):
    bot_speak(BOT_URL)


def help_command(data):
    help = ['Here are the commands: ']
    help.extend("{}{} {}".format(k, " ".join(v[1:-1]), v[-1]) for k, v in commands.items())
    bot_speak("\n".join(help))

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
    command = (data['text'].split() or [None])[0]
    command = short_commands.get(command, command)
    commands.get(command, lambda x: None)(data)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    logger.critical('Hello everyone!')
    return 'Hello everyone!'


@app.route('/groupme', methods=['post', 'get'])
def groupme():
    if request.method == 'POST':
        json = request.get_json()
        logger.critical('DATA: %s' % json)
        process_request({'text': json['text'], 'name': json['name'], 'created_at': json['created_at']})
        return ''
    else:
        return redirect('https://docs.google.com/spreadsheets/d/1U-wAQAXaDFYZ2uQvPtxL5kSDOss8kMPRRpyb6OgRbKs', code=302)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
# [END app]
