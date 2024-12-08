import hashlib
import random

def shuffle_list_with_seed(lst):
    random.shuffle(lst)
    return lst
def print_sudoku_hash(hash):
    for i in range(9):
        for j in range(9):
            print (hash[i*9+j], end = " "),
        print ()
    print("sha-256 hash "+hash[81:])
def print_grid(arr):
    for i in range(9):
        for j in range(9):
            print (arr[i][j], end = " "),
        print ()

def find_empty_location(arr, l,rows,cols):
    for row in rows:
        for col in cols:
            if(arr[row][col]== 0):
                l[0]= row
                l[1]= col
                return True
    return False


def used_in_row(arr, row, num):
    for i in range(9):
        if(arr[row][i] == num):
            return True
    return False

def used_in_col(arr, col, num):
    for i in range(9):
        if(arr[i][col] == num):
            return True
    return False

def used_in_box(arr, row, col, num):
    for i in range(3):
        for j in range(3):
            if(arr[i + row][j + col] == num):
                return True
    return False


def check_location_is_safe(arr, row, col, num):
    

    return (not used_in_row(arr, row, num) and 
           (not used_in_col(arr, col, num) and 
           (not used_in_box(arr, row - row % 3, 
                           col - col % 3, num))))

def solve_sudoku(arr,cols,rows):
    l =[0, 0]
     
    if(not find_empty_location(arr, l,rows,cols)):
        return True
    
    row = l[0]
    col = l[1]
    
    for num in range(1, 10):
        
        if(check_location_is_safe(arr, 
                          row, col, num)):
            
            arr[row][col]= num

            if(solve_sudoku(arr,rows,cols)):
                return True

            arr[row][col] = 0
                   
    return False 

def initialize_empty_grid():
    return [[0 for _ in range(9)] for _ in range(9)]


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
def fill_quadrant(grid,list,block):
    rows = [block[0] * 3 + i for i in range(3)]
    cols = [block[1] * 3 + i for i in range(3)]
    a =0;
    for row in rows:
        for col in cols:
            grid[row][col]=list[a]
            a += 1

# Main function to generate a "Sudoku hash"
def sudoku_hash(input_string):

    shahash = hashlib.sha256(input_string.encode())
    # Step 1: Convert input to numerical representation
    input_numbers = string_to_numbers(shahash.hexdigest())

    # Step 2: Initialize an empty 9x9 Sudoku grid and solve it
    sudoku_grid = initialize_empty_grid()

    random.seed(shahash.hexdigest())
    rowRange =shuffle_list_with_seed( list(range(9)))
    colRange = shuffle_list_with_seed(list(range(9)))
    quadrant1 = shuffle_list_with_seed(list(range(1,10)))
    quadrant2 = shuffle_list_with_seed(list(range(1,10)))
    quadrant3 = shuffle_list_with_seed(list(range(1,10)))
    fill_quadrant(sudoku_grid,quadrant1,[1,1])
    fill_quadrant(sudoku_grid,quadrant2,[2,2])
    fill_quadrant(sudoku_grid,quadrant3,[0,0])
    solve_sudoku(sudoku_grid,rowRange,colRange)  # This fills the grid with a valid Sudoku solution

    # Step 3: Permute the grid based on the input numbers
    sudoku_grid = permute_grid(sudoku_grid, input_numbers)
    #print_grid(sudoku_grid)
    # Step 4: Extract a hash-like string from the grid
    return extract_hash_from_grid(sudoku_grid) + shahash.hexdigest()


