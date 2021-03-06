#! /usr/bin/env python3
from collections import deque
from operator import eq
import random
import copy
import time
import image_grid
import statistics




#
# BFS search (for connected pieces)
#

def get_all_nodegroups(gameboard, valid_moves_only=True):
	'''
			Returns an array of arrays, where each subarray contains a
			group of connected nodes (i.e. a move).

			With valid_moves_only = True, this will not return groups
			of size 1.
	'''
	visited_nodes = []
	nodegroups = []

	for x in range(len(gameboard)):
		for y in range(len(gameboard[0])):
			start = x, y

			if get_item(gameboard, start) == 0 or start in visited_nodes:
				continue

			new_nodegroup = get_connected_nodes(gameboard, start)
			visited_nodes += new_nodegroup

			if valid_moves_only and len(new_nodegroup) <= 1:
				continue

			nodegroups.append(new_nodegroup)

	return nodegroups


def get_connected_nodes(array, start) -> list:
	"""Run either a BFS or DFS algorithm to get connected nodes"""
	match = get_item(array, start)
	visited = {start}
	visit = deque(visited)
	nodes_found = []

	while visit:
		node = deque.popleft(visit)

		for offset in ((-1, 0), (1, 0), (0, -1), (0, 1)):
			test_node = get_next(node, offset)
			if test_node in visited or not is_valid_index(array, test_node):
				continue

			visited.add(test_node)
			value = get_item(array, test_node)
			if eq(value, match):
				visit.append(test_node)

		nodes_found.append(node)

	return nodes_found


def get_item(array, index):
	"""Access the data structure based on the given position information."""
	row, column = index
	return array[row][column]


def get_next(node, offset):
	"""Find the next location based on an offset from the current location."""
	row, column = node
	row_offset, column_offset = offset
	return row + row_offset, column + column_offset


def is_valid_index(array, index):
	"""Verify that the index is in range of the data structure's contents."""
	row, column = index
	return 0 <= row < len(array) and 0 <= column < len(array[row])





#
# Gameboard Operations
#

def get_zeroes(array) -> list:
	zeroes = []
	for x in range(len(array)):
		for y in range(len(array[0])):
			if array[x][y] == 0:
				return get_connected_nodes(array, (x, y))
	return []


def get_largest_nodegroup(gameboard, valid_moves_only=True):
	all_nodegroups = get_all_nodegroups(gameboard, valid_moves_only)

	if len(all_nodegroups) == 0:
		return []

	largest_group = all_nodegroups[0]
	largest_len = len(all_nodegroups[0])

	for group in all_nodegroups[1:]:
		group_len = len(group)

		if group_len > largest_len:
			largest_group = group
			largest_len = group_len

	return largest_group


def modify_gameboard(gameboard, nodes_to_remove):
	'''
	Simulates a move in the game. It expects nodes_to_remove to
	be a list of positions to be removed, and then this function
	handles the shifting around.

	gameboard IS modified. If you need a copy, do copy.deepcopy()
	before passing it as an argument.
	'''
	if len(nodes_to_remove) < 2:
		return gameboard

	# Remove nodes
	for node in nodes_to_remove:
		x, y = node
		gameboard[x][y] = 0

	# Next, collapse each column down
	# so that all the 0s are on top
	for col in range(9):
		blank_square_row = 8

		for row in range(8, -1, -1):
			if gameboard[row][col] == 0:
				continue
			piece_value = gameboard[row][col]
			gameboard[row][col] = 0
			gameboard[blank_square_row][col] = piece_value

			blank_square_row -= 1

	# Then shift any empty columns to the left
	leftmost_col = 0

	for col in range(9):
		# don't shift empty columns
		if gameboard[8][col] == 0:
			continue

		# shift this column if columns to the left have been shifted
		if col != leftmost_col:
			for row in range(9):
				gameboard[row][leftmost_col] = gameboard[row][col]
				gameboard[row][col] = 0

		leftmost_col += 1

	return gameboard


def print_gameboard(gameboard, highlight_pieces = []):
	symbols = [' ', '$', '^', '@', '+', '=', '*', 'V', ';', '&']

	# gameboard assumed to be 9x9
	for row in range(9):
		print(row, end='')
		print(' | ', end='')

		for col, num in enumerate(gameboard[row]):
			charStr = str(symbols[num])
			if (row, col) in highlight_pieces:
				# surround the charStr in characters to make it highlight
				charStr = '\033[2;31;43m' + charStr + '\033[0;0m'

			print(charStr + ' ', end='')

		print()
	print('   --------------------')
	print(' 0 1 2 3 4 5 6 7 8 ')



#
# Searches
#


def random_search(gameboard):
	possible_moves = get_all_nodegroups(gameboard)

	gameboard_original = copy.deepcopy(gameboard)
	gameboard = copy.deepcopy(gameboard)

	cords_used = []
	dead_end_counter = 0
	possibilities_counter = 0

	best_num_zeroes = -1
	
	while (gameboard[8][0] != 0): # gameboard[8][0] == 0   <=>  gameboard is solved
		possibilities_counter += 1

		random_path, modified_gameboard = follow_random_path(gameboard)
		for move in random_path:
			cords_used.append(move)
		num_zeroes = len(get_zeroes(modified_gameboard))

		#Keep track of execution
		if dead_end_counter%10000 == 0:
			print(dead_end_counter)

		# 81 zeroes = game is won
		if num_zeroes == 81:
			break
		else:
			dead_end_counter += 1
		
		if num_zeroes > best_num_zeroes:
			best_num_zeroes = num_zeroes
			dead_ends_to_get_here = dead_end_counter
			dead_end_counter = 0
			print()
			print("Best: ", best_num_zeroes, "\n", 
				# "Coordinates: ", cords_used, "\n", 
				"Num moves: ", len(cords_used), "\n",
				"Dead Ends: ", dead_ends_to_get_here)
			print("Coordinates: ", cords_used)
		
		if dead_end_counter > dead_end_counter_limit:
			print(" > dead_end_counter_limit exceeded, starting new path")
			dead_end_counter = 0
			best_num_zeroes = -1
			cords_used = []
			gameboard = copy.deepcopy(gameboard_original)
			continue
		
		# go backwards some # steps from already generated dead-end sequence.
		generator = []
		for i in range(len(cords_used)):
			generator += [i]*(100-(2*i))
		'''generator  = [1]*5 + [2]*15+ [3] * 15 + [4]*15 + [5] * 15\
				+ [6]*15 + [7] * 5  +[8] * 5 + [9] *5 + [10] *5 + [11]*5 \
				+ [12]*5+ [13]*5 + [14] *5 + [15]*5+ [16]*5+ [17] *5 \
				+ [18]*5 + [19] *5 +[20] *5 +[21] *5 + [22]*5+ [23] *5\
				+[24]*5 + [25]*5 + [26]*5 + [27]*5+ [28]*5+[29]*5+[30]*5 +[31]*5 +[32]*5'''

		go_back_by = len(cords_used) - min(random.choice(generator), len(cords_used)-1)
		cords_used = cords_used[:go_back_by]
		gameboard = copy.deepcopy(gameboard_original)
		for move in cords_used:
			modify_coords = get_connected_nodes(gameboard, move)
			gameboard = modify_gameboard(gameboard, modify_coords)
		#print(cords_used)
	
	print()
	print()
	print("== Automatic search complete ==")
	print()
	print(cords_used)
	print()
	print("Searched: ", possibilities_counter, "possibilities")



def follow_random_path(gameboard):
	'''
	Returns a list of valid but random moves, as well as
	the gameboard at the end of the sequence.

	(cords_used, gameboard)
	'''
	coordinates_used = []
	largest_group = get_largest_nodegroup(gameboard)

	if len(largest_group) > 0:
		info = largest_group[0]

		while True:
			all_possible_moves = get_all_nodegroups(gameboard)
			possible_choices = [group[0] for group in all_possible_moves]
			weights = [len(group) for group in all_possible_moves]

			if(len(possible_choices) > 0):
				#choose randomly with weight on size of group.
				generator = []
				for i in range(len(possible_choices)):
					strategy = random.randint(0,3)
					if(strategy<3):
						generator += [i]*25*(max(weights)-weights[i]+1)
					elif(strategy ==3):
						generator += [i] * weights[i]
					#generator += [i] * 10*(abs(int(statistics.median(weights))-weights[i])+1)
					#print(generator)

				if(generator):
					random_choice = random.choice(generator)
				else:
					random_choice = random.randint(0, len(possible_choices)-1)

				x, y = possible_choices[random_choice]
				start = (x, y)

				modify_coords = get_connected_nodes(gameboard, start)
				gameboard = modify_gameboard(gameboard, modify_coords)
				coordinates_used.append(start)

			else:
				break

	return coordinates_used, gameboard


total_configurations = 0
total_non_winning = 0
total_non_winning_roots = 0
total_non_winning_roots_by_depth = [0, 0, 0, 0, 0, 0, 0]

def exhaustive_search(gameboard, depth, prev_moves, stop_at_win=True):
	'''
	Recursively searches through all possible moves.

	If stop_at_win is true, this will stop once the board is empty
	'''
	global total_configurations, total_non_winning, total_non_winning_roots
	possible_moves = get_all_nodegroups(gameboard)

	if len(possible_moves) == 0:
		total_configurations += 1
		num_zeroes = len(get_zeroes(gameboard))

		if num_zeroes < 81:
			total_non_winning += 1

		return num_zeroes

	best_numzeroes = -1

	below_nonwinning = 0

	for move in possible_moves:
		dummy_gameboard = copy.deepcopy(gameboard)
		dummy_gameboard = modify_gameboard(dummy_gameboard, move)

		if depth == 0:
			print("=======")
			print("Making move : " + str(move[0]))
			print("=======")

		new_prev_move = prev_moves.copy()
		new_prev_move += [move[0]]

		numzeroes = exhaustive_search(dummy_gameboard, depth + 1, new_prev_move, stop_at_win)
		if numzeroes < 81:
			below_nonwinning += 1
		if numzeroes > best_numzeroes:
			best_numzeroes = numzeroes
		if stop_at_win and numzeroes == 81:
			return 81

	if best_numzeroes == 81:
		total_non_winning_roots += below_nonwinning

		if depth < 6:
			total_non_winning_roots_by_depth[depth] += below_nonwinning
	elif depth <= 3:
		print("[[unsolvable]]")
		print("Depth | " + str(depth))
		print("Moves | " + str(prev_moves))
		print_gameboard(gameboard)

	return best_numzeroes




#
# Manual Search

def manual_search(gameboard):
	while(True):
		testing_gameboard = copy.deepcopy(gameboard)
		possible_moves = get_all_nodegroups(testing_gameboard)

		print()
		print()
		print()
		print_gameboard(testing_gameboard, [x[0] for x in possible_moves])
		print()

		largest_group = get_largest_nodegroup(testing_gameboard)
		greedy_move = largest_group[0]
		x, y = greedy_move
		print("Largest group at " + str(greedy_move))
		print("Group size: " + str(len(largest_group)))
		print("Zeroes: ", len(get_zeroes(gameboard)))
		print()

		x_coord = int(input("Enter x "))
		y_coord = int(input("Enter y "))
		start = x_coord, y_coord

		modify_coords = get_connected_nodes(gameboard, start)
		gameboard = modify_gameboard(gameboard, modify_coords)







#
# Main
#


# Note: Solution (x,y) starts at top left corner, which is (0,0) and x corresponds to vertical direction, y corresponds to horizontal.

dead_end_counter_limit = 15000

def main():
	"""Show how to search for similar neighbors in a 2D array structure."""
	gameboard = image_grid.main_process()

	random_search(gameboard)
	'''best_score = exhaustive_search(gameboard, 0, [], False)
	print("best score | " + str(best_score))
	print("total non-winning | " + str(total_non_winning))
	print("total end-states  | " + str(total_configurations))
	print("total non-winning-roots | " + str(total_non_winning_roots))
	print("total non-winning-roots-by-depth | " + str(total_non_winning_roots_by_depth))'''







if __name__ == '__main__':
	start_time = time.time()
	main()
	print("Execution time --- %s seconds ---" % (time.time() - start_time))
