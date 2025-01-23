start cmd /k python .\SudokuCoinNode.py --port 3001 --password 123
start cmd /k python .\SudokuCoinNode.py --port 3002 --peer 127.0.0.1:3001 --password 123
start cmd /k python .\SudokuCoinNode.py --port 3003 --peer 127.0.0.1:3001 127.0.0.1:3002 --password 123
start cmd /k python .\SudokuCoinNode.py --port 3004 --peer 127.0.0.1:3001 127.0.0.1:3002 127.0.0.1:3003 --password 123 --isEvil True