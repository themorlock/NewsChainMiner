from Crypto.PublicKey import RSA
import hashlib
import json
import flask
import requests
import threading
import time
import jsonpickle
import Article
import Block
import Blockchain

CENTRAL_SERVER_ADDRESS = '35.225.55.196'
PING_CENTRAL_SERVER_DELAY = 60

PORT = 5000

NUM_ARTICLES_PER_BLOCK = 2
stop_mining_flag = False
chain = Blockchain.Blockchain()
peer_addresses = []
current_articles = []

app = flask.Flask(__name__)


@app.route('/new_article', methods=['POST'])
def new_article():
    json_dict = json.loads(flask.request.data.decode('utf-8'))
    json_dict.update({'py/object':'Article.Article'})
    article = jsonpickle.loads(json.dumps(json_dict))
    for current_article in current_articles:
        if article.get_hash() == current_article.get_hash():
            return 'Recieved'
    if article.verify():
        current_articles.append(article)
        for peer_address in peer_addresses:
            requests.post('http://' + peer_address + ':' + str(PORT)
                          + '/new_article', data=jsonpickle.encode(article))
    return 'Recieved'


@app.route('/new_block', methods=['POST'])
def new_block():
    json_dict = json.loads(flask.request.data.decode('utf-8'))
    json_dict.update({'py/object':'Block.Block'})
    block = jsonpickle.loads(json.dumps(json_dict))
    if chain.add_block(block):
        for article in block.articles:
            for curr_article in current_articles:
                if article.get_hash() == curr_article.get_hash():
                    current_articles.remove(curr_article)
        stop_mining_flag = True
        for peer_address in peer_addresses:
            requests.post('http://' + peer_address + ':' + str(PORT)
                          + '/new_block', data=jsonpickle.encode(block))
    return 'Recieved'


@app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    return jsonpickle.encode(chain)


def handler_loop():
    app.run(host='0.0.0.0')


def broadcast_new_block(new_block):
    global peer_addresses
    for peer_address in peer_addresses:
        requests.post('http://' + peer_address + ':' + str(PORT)
                      + '/new_block', data=jsonpickle.encode(new_block))


def miner_loop():
    global chain
    global NUM_ARTICLES_PER_BLOCK
    global stop_mining_flag
    while True:
        if len(current_articles) >= NUM_ARTICLES_PER_BLOCK:
            articles_for_block = current_articles[:NUM_ARTICLES_PER_BLOCK]
            new_block = Block.Block(chain.get_previous_hash(),
                                    chain.get_previous_block_number() + 1, articles_for_block)
            print('---Mining Block---')
            mined = new_block.try_new_nonce()
            while not mined and not stop_mining_flag:
                mined = new_block.try_new_nonce()
            if stop_mining_flag:
                print('---Halting Mining---')
                stop_mining_flag = False
                continue
            print('---Mined Block---')
            chain.add_block(new_block)
            print('---Broadcasting Mined Block---')
            broadcast_new_block(new_block)
            del current_articles[:NUM_ARTICLES_PER_BLOCK]


def get_peer_addresses():
    global peer_addresses
    global CENTRAL_SERVER_ADDRESS
    global PORT
    peer_addresses = requests.get('http://' + CENTRAL_SERVER_ADDRESS + ':' + str(PORT) + '/get_peer_addresses').json()


def get_peer_addresses_loop():
    global PING_CENTRAL_SERVER_DELAY
    while True:
        time.sleep(PING_CENTRAL_SERVER_DELAY)
        print('---Pinging Central Server For Peer Addresses---')
        get_peer_addresses()


def get_latest_blockchain():
    print('---Looking for Current Blockchain---')
    for peer_address in peer_addresses:
        try:
            json_dict = json.loads(requests.get('http://' + peer_address + ':' + str(PORT) + '/get_blockchain').text.decode('utf-8'))
            json_dict.update({'py/object':'Blockchain.Blockchain'})
            temp_chain = jsonpickle.loads(json.dumps(json_dict))
            print('---Downloading Latest Blockchain---')
            return temp_chain
        except:
            continue
    print("---Couldn't Find a Copy of Blockchain, Creating Genesis Block---")
    return Blockchain.Blockchain()


if __name__ == '__main__':
    get_peer_addresses()
    chain = get_latest_blockchain()
    miner_thread = threading.Thread(target=miner_loop, daemon=True)
    handler_thread = threading.Thread(target=handler_loop, daemon=True)
    get_peer_addresses_thread = threading.Thread(target=get_peer_addresses_loop, daemon=True)
    miner_thread.start()
    handler_thread.start()
    get_peer_addresses_thread.start()
    miner_thread.join()
    handler_thread.join()
    get_peer_addresses_thread.join()
