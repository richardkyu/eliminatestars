#! /usr/bin/env python3
from collections import deque
from operator import eq
import random
import copy
import time
import image_grid




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


def modify_gameboard(gameboard, to_modify):
	if len(to_modify) < 2:
		'''print("invalid")
		curframe = inspect.currentframe()
		calframe = inspect.getouterframes(curframe, 2)
		print('caller name:', calframe[1][3])'''
		return gameboard
	updated_array = gameboard.copy()

	# Change all elements in connected nodes to 0.
	for element in to_modify:
		updated_array[element[0]][element[1]] = 0

	# Before all shifts
	'''for element in updated_array:
		print(element)
	print("\n")'''

	# move coordinates down if there is a zero.
	for x in range(1, len(updated_array)):
		for y in range(len(updated_array[0])):
			if updated_array[x][y] == 0 and updated_array[x-1][y] != 0:
				for check in range(x, 0, -1):
					updated_array[check][y], updated_array[check -
														   1][y] = updated_array[check-1][y], updated_array[check][y]

	# detect when there are holes at the bottom
	empty_bottom = []
	for y in range(len(updated_array[0])):
		if updated_array[len(updated_array)-1][y] == 0:
			empty_bottom.append(y)

	# print(empty_bottom)
	# Iterate through grid again and collect coordinates to be shifted.
	shifted_coordinates = []
	for x in range(len(updated_array)):
		for y in range(len(updated_array[0])):
			for element in empty_bottom:
				if y > element and updated_array[x][y] != 0:
					shifted_coordinates.append([x, y])

	# print(shifted_coordinates)

	for element in shifted_coordinates:
		shift_by = shifted_coordinates.count([element[0], element[1]])
		# print(shift_by)
		updated_array[element[0]][element[1]], updated_array[element[0]][element[1] -
																		 shift_by] = updated_array[element[0]][element[1]-shift_by], updated_array[element[0]][element[1]]
		shifted_coordinates = [
			value for value in shifted_coordinates if value != element]

	# After all shifts
	# for element in updated_array:
		# print(element)

	return updated_array


def print_gameboard(gameboard):
	symbols = [' ', '$', '^', '@', '+', '=', '*', 'V', ';', '&']

	# gameboard assumed to be 9x9
	for row in range(9):
		print(row, end='')
		print(' | ', end='')

		for num in gameboard[row]:
			print(symbols[num] + ' ', end='')
		print()
	print('  --------------------')
	print(' 0 1 2 3 4 5 6 7 8 ')


def calculate_state_score(gameboard):
	totalscore = 0
	for i in range(9):
		for j in range(9):
			if(gameboard[i][j] != 0):
				totalscore += len(get_connected_nodes(gameboard, (i, j)))
	return totalscore




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
		
		if dead_end_counter > dead_end_counter_limit:
			print(" > dead_end_counter_limit exceeded, starting new path")
			dead_end_counter = 0
			best_num_zeroes = -1
			cords_used = []
			gameboard = copy.deepcopy(gameboard_original)
			continue
		
		# go backwards some # steps
		generator  = [1]*10 + [2]*10+ [3] * 55 + [5] * 80 + [7] * 35 +[11]*25 + [15]*10
		go_back_by = len(cords_used) - min(random.choice(generator), len(cords_used))
		cords_used = cords_used[:go_back_by]
		gameboard = copy.deepcopy(gameboard_original)
		for move in cords_used:
			modify_coords = get_connected_nodes(gameboard, move)
			gameboard = modify_gameboard(gameboard, modify_coords)
	
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

			if(len(possible_choices) > 0):
				random_choice = random.randint(0, len(possible_choices)-1)

				x, y = possible_choices[random_choice]
				start = (x, y)

				modify_coords = get_connected_nodes(gameboard, start)
				gameboard = modify_gameboard(gameboard, modify_coords)
				coordinates_used.append(start)

			else:
				break

	return coordinates_used, gameboard


#
# Manual Search

def manual_search(gameboard):
	while(True):
		testing_gameboard = copy.deepcopy(gameboard)

		print()
		print()
		print()
		print_gameboard(testing_gameboard)
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

dead_end_counter_limit = 750

def main():
	"""Show how to search for similar neighbors in a 2D array structure."""
	gameboard = image_grid.main_process()

	enable_manual = False

	if enable_manual:
		manual_search(gameboard)
	else:
		random_search(gameboard)







if __name__ == '__main__':
	start_time = time.time()
	main()
	print("Execution time --- %s seconds ---" % (time.time() - start_time))
