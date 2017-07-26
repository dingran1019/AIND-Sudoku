assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    display(values)
    twin_list = []
    for unit in unitlist:
        len_unit = len(unit)
        for i in range(len_unit):
            if len(values[unit[i]]) == 2:  # only compare for len==2 units
                for j in range(i + 1, len_unit):  # one-way comparison
                    if values[unit[i]] == values[unit[j]]:
                        twin_list.append([unit[i], unit[j], values[unit[i]], set(unit) - {unit[i], unit[j]}])
    # print(twin_list)

    # Eliminate the naked twins as possibilities for their peers
    for tw in twin_list:
        for box in tw[3]:
            new_val = ''.join(sorted(list(set(values[box]) - set(
                tw[2]))))  # using set operationg to remove digits appeared in naked twins from other boxes
            assign_value(values, box, new_val)

    display(values)
    return values


def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return [s + t for s in A for t in B]


rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diag_units = [[s + t for (s, t) in list(zip(rows, cols))],
              [s + t for (s, t) in list(zip(rows, cols[::-1]))]]  # define diagonal units
unitlist = row_units + column_units + square_units + diag_units  # adding diagonal units into the unitlist so it will be used as a new constraint
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """

    assert len(grid) == 81
    new_grid = []
    for i in grid:
        if i == '.':
            new_grid.append('123456789')
        else:
            new_grid.append(i)

    return dict(zip(boxes, new_grid))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for key, value in values.items():
        if len(value) == 1:
            for u in unitlist:
                if key in u:
                    for box in u:
                        if box != key:
                            # values[box] = values[box].replace(value, "")
                            assign_value(values, box, values[box].replace(value, ""))
    return values


def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for u in unitlist:
        for i in '123456789':
            i_apperance = [box for box in u if i in values[box]]
            if len(i_apperance) == 1:
                # values[i_apperance[0]] = i
                assign_value(values, i_apperance[0], i)

    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked Twin Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """
    Using depth-first search and propagation, try all possible values.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    unsolved_boxes = [b for b in values.keys() if len(values[b]) > 1]
    min_b = None
    min_len = 10
    for b in unsolved_boxes:
        if len(values[b]) < min_len:
            min_len = len(values[b])
            min_b = b

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for i in values[min_b]:
        new_values = values.copy()
        new_values[min_b] = i
        result = search(new_values)
        if result:
            return result


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments

        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
