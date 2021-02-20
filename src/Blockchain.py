from src import Article
from src import Block


class Blockchain:
    def __init__(self):
        genesis_block = Block.Block(0, 0, [])
        mined = genesis_block.try_new_nonce()
        while not mined:
            mined = genesis_block.try_new_nonce()
        self.blocks = []
        self.blocks.append(genesis_block)

    def get_previous_hash(self):
        return self.blocks[-1].get_hash()

    def get_previous_block_number(self):
        return self.blocks[-1].block_number

    def add_block(self, new_block):
        if new_block.prev_hash == self.get_previous_hash() \
                and new_block.block_number == self.get_previous_block_number() + 1 \
                and new_block.verify():
            self.blocks.append(new_block)
            return True
        return False
