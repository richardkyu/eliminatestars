#! /usr/bin/env python3
from collections import deque
from operator import eq
import random
import copy
import time
import inspect
import image_grid


# Note: Solution (x,y) starts at top left corner, which is (0,0) and x corresponds to vertical direction, y corresponds to horizontal.

dead_end_counter_limit = 500

def main():
	"""Show how to search for similar neighbors in a 2D array structure."""
	gameboard = image_grid.main_process()

	# print("Start state:")
	# print_gameboard(gameboard)
	enable_manual = "N"  # input("Enable manual mode? (Y / N) ")

	if enable_manual == "N" or enable_manual == "No":
		automatic_search(gameboard)
	else:
		manual_search(gameboard)


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





#
# BFS search (for connected pieces)
#

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

def get_nonzeroes(array) -> list:
	nonzero = []
	for x in range(len(array)):
		for y in range(len(array[0])):
			start = x, y
			node_length = len(get_connected_nodes(array, start))
			if array[x][y] != 0 and node_length >= 2:
				nonzero.append([x, y])
	return nonzero


def get_zeroes(array) -> list:
	zeroes = []
	for x in range(len(array)):
		for y in range(len(array[0])):
			if array[x][y] == 0:
				zeroes.append([x, y])
	return zeroes


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


def get_largest_nodegroup(gameboard):
	all_nodegroups = get_all_nodegroups(gameboard, valid_moves_only=False)

	if len(all_nodegroups) == 0:
		return []

	largest_group = all_nodegroups[0]
	largest_len = len(largest_group)

	for group in all_nodegroups[1:]:
		group_len = len(group)

		if group_len > largest_len:
			largest_group = group
			largest_len = group_len

	return largest_group


def calculate_state_score(gameboard):
	totalscore = 0
	for i in range(9):
		for j in range(9):
			if(gameboard[i][j] != 0):
				totalscore += len(get_connected_nodes(gameboard, (i, j)))
	return totalscore


def modify_gameboard(array, to_modify):
	if len(to_modify) < 2:
		'''print("invalid")
		curframe = inspect.currentframe()
		calframe = inspect.getouterframes(curframe, 2)
		print('caller name:', calframe[1][3])'''
		return array
	updated_array = array.copy()

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





#
# Different Searches
#

def automatic_search(gameboard):
	gameboard_original = copy.deepcopy(gameboard)
	counter = 0
	instance_counter = 0
	sum = 0
	best_result = 82
	best_so_far = 0
	dead_end_counter = 0

	average = 40
	gameboard = copy.deepcopy(gameboard_original)
	coordinates_used = []
	while(gameboard[8][0] != 0):
		counter += 1
		final_info = random_search(gameboard)

		for element in final_info[0]:
			coordinates_used.append(element)

		best_so_far = final_info[1]
		if 81-best_so_far != 0:
			if (81-best_so_far) < best_result:
				best_result = 81-best_so_far
				dead_end_counter = 0
				state_score = calculate_state_score(gameboard)

				print("Best: ", best_result, "\n", "Coordinates: ",
					  coordinates_used, "\n", "State score: ", state_score)
			dead_end_counter += 1

		if gameboard[8][0] != 0 and dead_end_counter <= dead_end_counter_limit:

			if len(coordinates_used) < 20:
				go_back_by = len(coordinates_used) - \
					min(random.randint(7, 15), len(coordinates_used))
			else:
				go_back_by = len(coordinates_used) - \
					min(random.randint(2, 5), len(coordinates_used))
			coordinates_used = coordinates_used[:go_back_by]
			gameboard = copy.deepcopy(gameboard_original)
			for element in coordinates_used:
				start = element[0], element[1]
				modify_coords = get_connected_nodes(gameboard, start)
				gameboard = modify_gameboard(gameboard, modify_coords)

		if dead_end_counter > dead_end_counter_limit:
			dead_end_counter = 0
			best_result = 82
			coordinates_used = []

	print(coordinates_used, len(coordinates_used))
	print("Searched: ", counter, "possibilities.")


def random_search(gameboard):
	coordinates_used = []
	largest_group = get_largest_nodegroup(gameboard)
	info = largest_group[0]

	while (info[1] > 1):
		# Instead of sampling from all non-zeroes, we sample
		# from possible moves, which avoids groups of size 1
		# and evenly weights all possible moves.

		# This leads to a ~10x speed improvement
		all_possible_moves = get_all_nodegroups(gameboard)
		possible_choices = [group[0] for group in all_possible_moves]

		if(len(possible_choices) > 0):
			random_choice = random.randint(0, len(possible_choices)-1)

			start = possible_choices[random_choice][0], possible_choices[random_choice][1]

			modify_coords = get_connected_nodes(gameboard, start)

			gameboard = modify_gameboard(gameboard, modify_coords)

			coordinates_used.append(start)

		else:
			break
	zero_count = len(get_zeroes(gameboard))

	return coordinates_used, zero_count



def manual_search(gameboard):
	while(True):
		testing_gameboard = copy.deepcopy(gameboard)

		largest_group = get_largest_nodegroup(testing_gameboard)
		greedy_move = largest_group[0]
		x, y = greedy_move
		print("Largest group at " + str(greedy_move))
		print("Group size: " + str(len(largest_group)))

		x_coord = int(input("Enter x "))
		y_coord = int(input("Enter y "))
		start = x_coord, y_coord
		modify_coords = get_connected_nodes(gameboard, start)
		print(modify_coords)

		gameboard = modify_gameboard(gameboard, modify_coords)
		print("Zeroes: ", len(get_zeroes(gameboard)))
		print_gameboard(gameboard)









if __name__ == '__main__':
	start_time = time.time()
	for x in range(40):
		main()
	print("Execution time --- %s seconds ---" % (time.time() - start_time))
