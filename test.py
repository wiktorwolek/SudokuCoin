from SudoCoin import BlockChain;
import json
blockchain = BlockChain()
print("***Mining fccCoin about to start***")
print(blockchain.chain)

last_block = blockchain.latest_block
last_proof_no = last_block.proof_no
proof_no = blockchain.proof_of_work(last_proof_no)

blockchain.new_data(
    sender="0",  
    recipient="Quincy Larson",  
    quantity=
    1, 
)

last_hash = last_block.calculate_hash
block = blockchain.construct_block(proof_no, last_hash)

print("***Mining fccCoin has been successful***")
print(blockchain.chain)
print('last hash')
print(block.calculate_hash)
json = blockchain.toJSON()

