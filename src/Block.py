import random
import hashlib

LEADING_MASK = "000"


class Block:
    def __init__(self, prev_hash, block_number, articles):
        self.prev_hash = prev_hash
        self.block_number = block_number
        self.articles = articles
        self.nonce = random.randint(0, 1048576)

    def get_articles_string(self):
        articles_string = ""
        for article in self.articles:
            articles_string += article.get_hash()

    def get_hash(self):
        block_string = "{}{}{}{}".format(self.prev_hash, self.block_number, self.get_articles_string(), self.nonce)
        block_hash = hashlib.sha256(str.encode(block_string)).hexdigest()
        return block_hash

    def verify(self):
        return self.get_hash()[:len(LEADING_MASK)] == LEADING_MASK

    def try_new_nonce(self):
        self.nonce += 1
        return self.verify()
