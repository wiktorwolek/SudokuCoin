import hashlib
from SudokuHasher import *
import time
start_time = time.time()
input_string = ""
for i in range(0,1000):
    input_string +="1"
    shahash = hashlib.sha256(input_string.encode())
print(time.time()-start_time)
input_string = ""
start_time = time.time()
for i in range(0,1000):
    input_string +="1"
    shahash = sudoku_hash(input_string)
print(time.time()-start_time)