start cmd /k python .\SudokuCoinNode.py --port 3001 --peer 127.0.0.1:3010
start cmd /k python .\SudokuCoinNode.py --port 3002 --peer 127.0.0.1:3001 127.0.0.1:3010
start cmd /k python .\SudokuCoinNode.py --port 3003 --peer 127.0.0.1:3002 127.0.0.1:3010