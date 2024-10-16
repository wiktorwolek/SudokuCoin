import hashlib
import time
import json
from SudokuHasher import *

class Block:

    def __init__(self, index, proof_no, prev_hash, data, timestamp=None):
        self.index = index
        self.proof_no = proof_no
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = timestamp or time.time()

    @property
    def calculate_hash(self):
        block_of_string = "{}{}{}{}{}".format(self.index, self.proof_no,
                                              self.prev_hash, self.data,
                                              self.timestamp)

        return sudoku_hash(block_of_string)
    def __repr__(self):
        return "{} - {} - {} - {} - {}".format(self.index, self.proof_no,
                                               self.prev_hash, self.data,
                                               self.timestamp)
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    @staticmethod
    def fromJSON(json_str):
        # Load a Block from a JSON string
        data = json.loads(json_str)
        return Block(
            index=data['index'],
            proof_no=data['proof_no'],
            prev_hash=data['prev_hash'],
            data=data['data'],
            timestamp=data['timestamp']
        )

class BlockChain:
    def toJSON(self):
        # Convert the entire blockchain to JSON format
        return json.dumps({
            'chain': [block.toJSON() for block in self.chain]
        })
    @staticmethod
    def fromJSON(json_str):
        # Load a BlockChain from a JSON string
        data = json.loads(json_str)
        blockchain = BlockChain()
        # Recreate the blocks
        for block_data in data['chain']:
            block = Block.fromJSON(block_data)
            blockchain.chain.append(block)

        return blockchain
    def __init__(self):
        self.chain = []
        self.current_data = []
        self.construct_genesis()

    def construct_genesis(self):
        self.construct_block(proof_no=0, prev_hash=0)

    def construct_block(self, proof_no, prev_hash):
        block = Block(
            index=len(self.chain),
            proof_no=proof_no,
            prev_hash=prev_hash,
            data=self.current_data)
        self.current_data = []

        self.chain.append(block)
        return block

    @staticmethod
    def check_validity(block, prev_block):
        if prev_block.index + 1 != block.index:
            return False

        elif prev_block.calculate_hash != block.prev_hash:
            return False

        elif not BlockChain.verifying_proof(block.proof_no,
                                            prev_block.proof_no):
            return False

        elif block.timestamp <= prev_block.timestamp:
            return False

        return True

    def new_data(self, sender, recipient, quantity):
        self.current_data.append({
            'sender': sender,
            'recipient': recipient,
            'quantity': quantity
        })
        return True

    @staticmethod
    def proof_of_work(last_proof):
        '''this simple algorithm identifies a number f' such that hash(ff') contain 4 leading zeroes
         f is the previous f'
         f' is the new proof
        '''
        proof_no = 0
        while BlockChain.verifying_proof(proof_no, last_proof) is False:
            proof_no += 1
        print(f'iterations {proof_no}')
        return proof_no

    @staticmethod
    def verifying_proof(last_proof, proof):
        #verifying the proof: does hash(last_proof, proof) is in n numbers from being sutable sudoku sollution

        guess = str(f'{last_proof}{proof}'.encode())
        #guess_hash = hashlib.sha256(guess).hexdigest()
        input_string = guess
        sudoku_hash_value = sudoku_hash(input_string)
        return sudoku_hash_value[:3]=="123"

    @property
    def latest_block(self):
        return self.chain[-1]

    def block_mining(self, details_miner):

        self.new_data(
            sender="0",  #it implies that this node has created a new block
            receiver=details_miner,
            quantity=
            1,  #creating a new block (or identifying the proof number) is awarded with 1
        )

        last_block = self.latest_block

        last_proof_no = last_block.proof_no
        proof_no = self.proof_of_work(last_proof_no)

        last_hash = last_block.calculate_hash
        block = self.construct_block(proof_no, last_hash)

        return vars(block)

    @staticmethod
    def obtain_block_object(block_data):
        #obtains block object from the block data

        return Block(
            block_data['index'],
            block_data['proof_no'],
            block_data['prev_hash'],
            block_data['data'],
            timestamp=block_data['timestamp'])