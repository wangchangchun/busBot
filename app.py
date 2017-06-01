import sys
from io import BytesIO

import telegram
from flask import Flask, request, send_file

from fsm import TocMachine



API_TOKEN = '394005589:AAHjLOQJNMHWVDBuatFRLh83xtUi3qILKDM'
WEBHOOK_URL = 'https://7ae31aa4.ngrok.io/hook'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'what_do_you_find',
        'route_pic',
        'time_table',
        'stop_name',
        'which_time_table',
        'which_route_pic',
        'which_bus_line',
        'forward',
        'backward'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'what_do_you_find',
            'dest': 'route_pic',
            'conditions': 'find_route_pic'
        },
        {
            'trigger': 'advance',
            'source': 'what_do_you_find',
            'dest': 'time_table',
            'conditions': 'find_time_table'
        },
        {
            'trigger': 'advance',
            'source': 'what_do_you_find',
            'dest': 'stop_name',
            'conditions': 'find_stop_name'
        },
        {
            'trigger': 'advance',
            'source': 'time_table',
            'dest': 'which_time_table',
            'conditions': 'which_time_table_do_you_need'
        },
        {
            'trigger': 'advance',
            'source': 'stop_name',
            'dest': 'which_bus_line',
            'conditions': 'which_stop_name_do_you_need'
        },
        {
            'trigger': 'advance',
            'source': 'which_time_table',
            'dest': 'forward',
            'conditions': 'go_forward'
        },
        {
            'trigger': 'advance',
            'source': 'which_time_table',
            'dest': 'backward',
            'conditions': 'go_backward'
        },
        {
            'trigger': 'advance',
            'source': 'route_pic',
            'dest': 'which_route_pic',
            'conditions': 'which_route_pic_do_you_need'
        },
        {
            'trigger': 'go_back',
            'source': [
                'which_route_pic',
                'forward',
                'backward',
                'which_time_table',
                'which_bus_line'
            ],
            'dest': 'what_do_you_find'
        }
    ],
    initial='what_do_you_find',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))


@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    machine.advance(update)
    return 'ok'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()
