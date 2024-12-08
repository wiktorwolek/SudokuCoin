from SudoCoin import BlockChain;
import json
from SudokuHasher import print_sudoku_hash
blockchain = BlockChain()
print("***Mining fccCoin about to start***")
print(blockchain.chain)

blockchain.new_data(
    sender="Telimena",  
    recipient="Pan Tadeusz",  
    quantity= 1, 
)

blockchain.block_mining("Jan Paweł")
blockchain.new_data(
    sender="Pan Tadeusz",  
    recipient="Telimena",  
    quantity= 1, 
)
blockchain.block_mining("Jan Paweł")
blockchain.new_data(
    sender="Pan Tadeusz",  
    recipient="Telimena",  
    quantity= 1, 
)
blockchain.block_mining("Jan Paweł")
print("***Mining fccCoin has been successful***")
print(blockchain.chain)
print('last hash')
print_sudoku_hash(blockchain.latest_block.calculate_hash)
print('blockchain validity ' + str(blockchain.check_chain_validity()))
json = blockchain.toJSON()

