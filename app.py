from flask import Flask
from flask import request, render_template, send_file, request
import config
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from utils import bdb_donate, bdb_pay, add_transaction_to_collection, get_transactions
from pymongo import MongoClient
import json

app = Flask(__name__)
blockchain_db = BigchainDB(config.BLOCKCHAIN_URL)
client = MongoClient(config.MONGO_HOST, 27017).bitdonate
user = generate_keypair()

@app.route('/')
def index():
    return "Hello, world"

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    """
    Take a donater name and an amount and put a transaction into the blockchain
    """
    if request.method == 'GET':
        return render_template('donate.html')
    elif request.method == 'POST':
        donater_name = request.form.get('donater_name')
        amount = request.form.get('amount')
        sent_txid = bdb_donate(blockchain_db, user, donater_name, amount)
        add_transaction_to_collection(client, 'donate', sent_txid)
        return "Transaction {} sent".format(sent_txid)


@app.route('/pay', methods=['GET', 'POST'])
def pay():
    """
    Take a vendor name and an amount and put that expenditure transaction into the blockchain
    """
    if request.method == 'GET':
        return render_template('pay.html')
    elif request.method == 'POST':
        vendor_name = request.form.get('vendor_name')
        amount = request.form.get('amount')
        sent_txid = bdb_pay(blockchain_db, user, vendor_name, amount)
        add_transaction_to_collection(client, 'pay', sent_txid)
        print("added transaction id to mongo")
        return "Transaction {} sent".format(sent_txid)

@app.route('/donate_transactions', methods=['GET'])
def donate_transactions():
    """
    Shows all the donations made to the charity
    """
    collection = client.donate_transactions
    return render_template(
        'donate_transactions.html',
        tx_list=get_transactions(client, blockchain_db, 'donate')
    )


if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=3031,
    )
