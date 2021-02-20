from Crypto.PublicKey import RSA
import hashlib
import json
import flask
import requests
import threading
import jsonpickle
import Article
import Block
import Blockchain

PORT = 5000

NUM_ARTICLES_PER_BLOCK = 1
stop_mining_flag = False
chain = Blockchain.Blockchain()
peer_addresses = []
current_articles = []

app = flask.Flask(__name__)


@app.route('/new_article', methods=['POST'])
def new_article():
    json_dict = json.loads(flask.request.data.decode("utf-8"))
    json_dict.update({"py/object":"Article.Article"})
    article = jsonpickle.loads(json.dumps(json_dict))
    #article = jsonpickle.decode(flask.request.data.decode("utf-8"), classes=Article.Article)
    if article.verify():
        current_articles.append(article)
        for peer_address in peer_addresses:
            requests.post('http://' + peer_address + ':' + str(PORT)
                          + '/new_article', data=jsonpickle.encode(article))
    return 'Recieved'


@app.route('/new_block', methods=['POST'])
def new_block():
    json_dict = json.loads(flask.request.data.decode("utf-8"))
    json_dict.update({"py/object":"Block.Block"})
    block = jsonpickle.loads(json.dumps(json_dict))
    #block = jsonpickle.decode(flask.request.data.decode("utf-8"), classes=Block.Block)
    if chain.add_block(block):
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
    print('Starting miner loop')
    while True:
        if len(current_articles) >= NUM_ARTICLES_PER_BLOCK:
            articles_for_block = current_articles[:NUM_ARTICLES_PER_BLOCK]
            new_block = Block.Block(chain.get_previous_hash(),
                                    chain.get_previous_block_number() + 1, articles_for_block)
            mined = new_block.try_new_nonce()
            while not mined:
                mined = new_block.try_new_nonce()
                if stop_mining_flag:
                   break 
            if stop_mining_flag:
                del current_articles[:NUM_ARTICLES_PER_BLOCK]
                stop_mining_flag = False
                continue
            chain.add_block(new_block)
            broadcast_new_block(new_block)
            del current_articles[:NUM_ARTICLES_PER_BLOCK]


def get_latest_blockchain():
    for peer_address in peer_addresses:
        try:
            json_dict = json.loads(requests.get('http://' + peer_address + ':' + str(PORT) + '/get_blockchain').text.decode("utf-8"))
            json_dict.update({"py/object":"Blockchain.Blockchain"})
            temp_chain = jsonpickle.loads(json.dumps(json_dict))
            return temp_chain
        except:
            continue
    return Blockchain.Blockchain()


if __name__ == '__main__':
    key_pair = RSA.generate(bits=1024)

    msg1 = "abc"
    signature = pow(int.from_bytes(hashlib.sha512(str.encode(msg1)).digest(), byteorder='big'), key_pair.d, key_pair.n)
    a1 = Article.Article(msg1, signature, key_pair.e, key_pair.n)
    #print(a1.verify())
    requests.post('http://' + '34.66.161.128' + ':' + str(PORT)
                  + '/new_article', data=jsonpickle.encode(a1))
    '''
    peer_addresses = requests.get('http://35.225.55.196:5000/get_peer_addresses?n=16').json()
    chain = get_latest_blockchain()

    miner_thread = threading.Thread(target=miner_loop, daemon=True)
    handler_thread = threading.Thread(target=handler_loop, daemon=True)
    miner_thread.start()
    handler_thread.start()
    miner_thread.join()
    handler_thread.join()
    '''
    '''
    key_pair = RSA.generate(bits=1024)

    msg1 = "abc"
    signature = pow(int.from_bytes(hashlib.sha512(str.encode(msg1)).digest(), byteorder='big'), key_pair.d, key_pair.n)
    a1 = Article.Article(msg1, signature, key_pair.e, key_pair.n)

    msg2 = "abcd"
    signature = pow(int.from_bytes(hashlib.sha512(str.encode(msg2)).digest(), byteorder='big'), key_pair.d, key_pair.n)
    a2 = Article.Article(msg2, signature, key_pair.e, key_pair.n)

    msg3 = "abcde"
    signature = pow(int.from_bytes(hashlib.sha512(str.encode(msg3)).digest(), byteorder='big'), key_pair.d, key_pair.n)
    a3 = Article.Article(msg3, signature, key_pair.e, key_pair.n)
    chain1 = Blockchain.Blockchain()
    b1 = Block.Block(chain1.get_previous_hash(), chain1.get_previous_block_number() + 1, [a1, a2, a3])
    t = b1.try_new_nonce()
    while not t:
        t = b1.try_new_nonce()
    chain1.add_block(b1)
    print(jsonpickle.encode(chain1))
    '''


