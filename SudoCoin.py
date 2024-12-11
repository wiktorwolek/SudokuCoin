import hashlib
import time
import json
from SudokuHasher import *
import threading
class Block:

    def __init__(self, index, proof_no, prev_hash, data, timestamp=None):
        self.index = index
        self.proof_no = proof_no
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = timestamp or time.time()

    @property
    def calculate_hash(self):
        block_of_string = sudoku_hash("{}{}{}{}{}".format(self.index, self.proof_no,
                                              self.prev_hash, self.data,
                                              self.timestamp))

        return sudoku_hash(block_of_string)
    def __repr__(self):
        return "{} - {} - {} - {} - {}".format(self.index, self.proof_no,
                                               self.prev_hash, self.data,
                                               self.timestamp)
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    @staticmethod
    def fromJSON(data):
        # Load a Block from a JSON string
        #data = json.loads(json_str)
        return Block(
            index=int(data['index']),
            proof_no=data['proof_no'],
            prev_hash=data['prev_hash'],
            data=data['data'],
            timestamp=data['timestamp']
        )

class BlockChain:
    def toJSON(self):
        # Convert the entire blockchain to JSON format
        return json.dumps(
            [block.__dict__ for block in self.chain]
        )
    @staticmethod
    def fromJSON(json_str):
        # Load a BlockChain from a JSON string
        data = json.loads(json_str)
        blockchain = BlockChain()
        for block_data in data:
            block = Block.fromJSON(block_data)
            blockchain.chain.append(block)

        return blockchain
    def __init__(self):
        self.chain = []
        self.current_data = []
       # self.construct_genesis()

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
    def  check_chain_validity(self):
        for i in range(1,len(self.chain)):
            if not BlockChain.check_validity(self.chain[i],self.chain[i-1]):
                return False
        return True
    @staticmethod
    def check_validity(block, prev_block):
        if prev_block.index + 1 != block.index:
            print("bad index")
            return False

        elif prev_block.calculate_hash != block.prev_hash:
            print("bad prev hash")
            return False

        elif not BlockChain.verifying_proof(block.proof_no,
                                            prev_block.proof_no):
            print("bad proof")
            return False

        elif block.timestamp <= prev_block.timestamp:
            print("bad timestamp")
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
    def proof_of_work(last_proof,stop_event):
        '''this simple algorithm identifies a number f' such that hash(ff') contain 4 leading zeroes
         f is the previous f'
         f' is the new proof
        '''
        proof_no = random.randint(0,10000)
        while BlockChain.verifying_proof(proof_no, last_proof) is False:
            if stop_event.is_set():
                return
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
        return sudoku_hash_value[:2]=="12"

    @property
    def latest_block(self):
        return self.chain[-1]

    def block_mining(self, details_miner,stop_event):

        self.new_data(
            sender="0",  
            recipient=details_miner,
            quantity=
            1, 
        )

        last_block = self.latest_block

        last_proof_no = last_block.proof_no
        proof_no = self.proof_of_work(last_proof_no,stop_event)
        if stop_event.is_set():
            return;
        last_hash = last_block.calculate_hash
        block = self.construct_block(proof_no, last_hash)
        print_sudoku_hash(block.calculate_hash)
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