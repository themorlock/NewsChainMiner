import socket
import jsonpickle
import requests
from src import Block
from src import Blockchain
from src import main


def broadcast_new_block(new_block):
    for peer_address in main.peer_addresses:
        requests.post('http://' + peer_address + ':' + str(main.PORT)
                      + '/new_block', data=jsonpickle.encode(new_block))
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(jsonpickle.encode(new_block), (peer_address, main.PORT))
        '''


def miner_loop():
    while True:
        if len(main.current_articles) >= Block.NUM_ARTICLES_PER_BLOCK:
            articles_for_block = main.current_articles[:Block.NUM_ARTICLES_PER_BLOCK]
            new_block = Block.Block(main.chain.get_previous_hash(),
                                    main.chain.get_previous_block_number() + 1, articles_for_block)
            mined = new_block.try_new_nonce()
            while not mined:
                mined = new_block.try_new_nonce()
                if main.stop_mining_flag:
                    break
            if main.stop_mining_flag:
                main.stop_mining_flag = False
                continue
            main.chain.add_block(new_block)
            broadcast_new_block(new_block)
            del main.current_articles[:Block.NUM_ARTICLES_PER_BLOCK]



