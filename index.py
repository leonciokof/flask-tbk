import datetime as dt

from flask import Flask, redirect, request
from getenv import env
from tbk.webpay.commerce import Commerce
from tbk.webpay.confirmation import Confirmation
from tbk.webpay.payment import Payment
import dotenv
import requests

dotenv.load_dotenv('.env')
app = Flask(__name__)
commerce = Commerce(testing=True)
port = env('PORT', 80)


@app.route('/')
def index():
    ip = requests.get('http://ip.42.pl/raw').text
    hostname = env('HOSTNAME', 'http://localhost')
    session_id = dt.datetime.now().strftime('%Y%m%d%H%M%S')
    amount = 10000
    order_id = 1
    payment = Payment(
        request_ip=request.remote_addr,
        commerce=commerce,
        success_url='%s:%s/webpay/success' % (hostname, port),
        confirmation_url='%s:%s/webpay/confirmation' % (ip, port),
        failure_url='%s:%s/webpay/failure' % (hostname, port),
        session_id=session_id,
        amount=amount,
        order_id=order_id,
    )

    return redirect(payment.redirect_url, code=302)


@app.route('/webpay/success', methods=['POST'])
def success():
    return 'success'


@app.route('/webpay/failure', methods=['POST'])
def failure():
    return 'failure'


@app.route('/webpay/confirmation', methods=['POST'])
def confirmation():
    confirmation = Confirmation(
        commerce=commerce,
        request_ip=request.remote_addr,
        data=request.form
    )

    # validate_confirmation validate if order_id and amount are valid.
    if confirmation.is_success():
        return commerce.acknowledge

    return commerce.reject

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
