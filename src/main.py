from Crypto.PublicKey import RSA
import hashlib
import requests
import threading
import jsonpickle
from src import Article
from src import Block
from src import Blockchain
from src import Handler
from src import Miner

PORT = 5000

stop_mining_flag = False
chain = Blockchain.Blockchain()
peer_addresses = []
current_articles = []


def get_latest_blockchain():
    return Blockchain.Blockchain()


if __name__ == '__main__':

    '''
    peer_addresses = requests.get('http://127.0.0.1:5000/get_peer_addresses?n=2').json()
    if len(peer_addresses) == 0:
        chain = Blockchain.Blockchain()
    else:
        chain = get_latest_blockchain()
    '''

    #chain = Blockchain.Blockchain()

    handler_thread = threading.Thread(target=Handler.handler_loop())
    miner_thread = threading.Thread(target=Miner.miner_loop())
    handler_thread.start()
    miner_thread.start()
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


