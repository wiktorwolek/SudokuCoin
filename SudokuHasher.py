import hashlib
# Function to check if a number can be placed in the given position (Sudoku rules)
def is_valid(grid, row, col, num):
    for x in range(9):
        if grid[row][x] == num or grid[x][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if grid[i + start_row][j + start_col] == num:
                return False
    return True

# Recursive backtracking function to generate a fully solved Sudoku grid
def solve_sudoku(grid):
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:  # Find empty cell
                for num in range(1, 10):
                    if is_valid(grid, row, col, num):
                        grid[row][col] = num
                        if solve_sudoku(grid):
                            return True
                        grid[row][col] = 0  # Backtrack
                return False
    return True

# Create an empty 9x9 grid
def initialize_empty_grid():
    return [[0 for _ in range(9)] for _ in range(9)]

# Shuffle rows and columns of the Sudoku grid to permute it
def permute_grid(grid, input_numbers):
    for block in range(3):
        rows = [block * 3 + i for i in range(3)]
        for i in input_numbers:
            if i%3==0:
                r = rows[1];
                rows[1] = rows[2]
                rows[2] = r
            elif i%3==1:
                r = rows[1];
                rows[1] = rows[2]
                rows[2] = r
            elif i%3==2:
                r = rows[0];
                rows[0] = rows[1]
                rows[1] = r
        grid[block * 3:block * 3 + 3] = [grid[r] for r in rows]

    # Shuffle columns within each 3-column block
    grid_t = list(zip(*grid))  # Transpose grid to treat columns like rows
    for block in range(3):
        cols = [block * 3 + i for i in range(3)]
        for i in input_numbers:
            if i%3==0:
                r = cols[1];
                cols[1] = cols[2]
                cols[2] = r
            elif i%3==1:
                r = cols[1];
                cols[1] = cols[2]
                cols[2] = r
            elif i%3==2:
                r = cols[0];
                cols[0] = cols[1]
                cols[1] = r
        grid_t[block * 3:block * 3 + 3] = [grid_t[c] for c in cols]

    return [list(row) for row in zip(*grid_t)]  # Transpose back

# Convert the input string to a list of numbers between 1 and 9
def string_to_numbers(input_string):
    return [(ord(char) % 9) + 1 for char in input_string]

# Extract hash-like value from the filled Sudoku grid
def extract_hash_from_grid(grid):
    # Concatenate the grid numbers row by row into a string and return it as a "hash"
    return ''.join(str(grid[row][col]) for row in range(9) for col in range(9))

# Main function to generate a "Sudoku hash"
def sudoku_hash(input_string):

    shahash = hashlib.sha256(input_string.encode())
    # Step 1: Convert input to numerical representation
    input_numbers = string_to_numbers(shahash.hexdigest())

    # Step 2: Initialize an empty 9x9 Sudoku grid and solve it
    sudoku_grid = initialize_empty_grid()
    solve_sudoku(sudoku_grid)  # This fills the grid with a valid Sudoku solution

    # Step 3: Permute the grid based on the input numbers
    sudoku_grid = permute_grid(sudoku_grid, input_numbers)

    # Step 4: Extract a hash-like string from the grid
    return extract_hash_from_grid(sudoku_grid)


