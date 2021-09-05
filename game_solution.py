#! /usr/bin/env python3
from collections import deque
from operator import eq
import random, copy, time, inspect, image_grid


#Note: Solution (x,y) starts at top left corner, which is (0,0) and x corresponds to vertical direction, y corresponds to horizontal. 

dead_end_counter_limit = 500
def main():
	"""Show how to search for similar neighbors in a 2D array structure."""
	gameboard = image_grid.main_process()
	neighbors = ((-1, 0), (0, +1), (+1, 0), (0, -1))
	similar = eq

	print("Start state:")
	print_gameboard(gameboard)
	#to_modify = list(find_similar(some_array, neighbors, start, similar, 'BFS'))
	#gameboard = modify_gameboard(some_array, to_modify)
	enable_manual = "N" #input("Enable manual mode? (Y / N) ")

	if enable_manual == "N" or enable_manual == "No":
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
			counter+=1
			#print("Before mod:", coordinates_used)
			#for element in gameboard:
				#print(element)
			final_info = random_search(gameboard, neighbors, similar, "random")	
			#print(final_info)

			for element in final_info[0]:
				coordinates_used.append(element)
			
			#print("coord used + final info", coordinates_used

			best_so_far = final_info[1]
			if 81-best_so_far != 0:
				if (81-best_so_far)< best_result:
					best_result = 81-best_so_far
					dead_end_counter=0
					state_score = calculate_state_score(gameboard, neighbors, similar)
					#print_gameboard(gameboard)

					print("Best: ", best_result,"\n", "Coordinates: ",coordinates_used,"\n", "State score: ", state_score)
				dead_end_counter +=1
					

			#print("Coordinates: ",coordinates_used,"\n")
			#for element in gameboard:
				#print(element)

			if gameboard[8][0] != 0 and dead_end_counter<=dead_end_counter_limit:

				if len(coordinates_used)<20:
					go_back_by = len(coordinates_used) - min(random.randint(7,15), len(coordinates_used))
				else:
					go_back_by = len(coordinates_used) - min(random.randint(2,5), len(coordinates_used))
				coordinates_used = coordinates_used[:go_back_by]
				#print("After mod: ",coordinates_used)
				gameboard = copy.deepcopy(gameboard_original)
				for element in coordinates_used:
					start = element[0], element[1]
					modify_coords = list(find_similar(gameboard, neighbors, start, similar, 'BFS'))
					gameboard = modify_gameboard(gameboard, modify_coords)
				
			if dead_end_counter >dead_end_counter_limit:
				#print(coordinates_used, 81-best_so_far)
				dead_end_counter = 0
				best_result = 82
				coordinates_used = []
			
		print(coordinates_used, len(coordinates_used))
		print("Searched: ", counter, "possibilities.")
		
	else:
		#Manual entering.
		while(True):
			testing_gameboard = copy.deepcopy(gameboard)
			info = find_most_similar(testing_gameboard, neighbors, similar, 'BFS')
			print ("Suggested: ", info[0], " with ", info[1], " nodes.")
			

			x_coord = int(input("Enter x "))
			y_coord = int(input("Enter y "))
			start = x_coord, y_coord
			modify_coords = list(find_similar(gameboard, neighbors, start, similar, 'BFS'))
			print(modify_coords)

			gameboard = modify_gameboard(gameboard, modify_coords)
			print("Zeroes: ", len(get_zeroes(gameboard,neighbors,similar)))
			print_gameboard(gameboard)




def modify_gameboard(array, to_modify):
	if len(to_modify)<2:
		'''print("invalid")
		curframe = inspect.currentframe()
		calframe = inspect.getouterframes(curframe, 2)
		print('caller name:', calframe[1][3])'''
		return array
	updated_array = array.copy()

	#Change all elements in connected nodes to 0.
	for element in to_modify:
		updated_array[element[0]][element[1]] = 0
	
	#Before all shifts
	'''for element in updated_array:
		print(element)
	print("\n")'''

	#move coordinates down if there is a zero.
	for x in range(1, len(updated_array)):
		for y in range(len(updated_array[0])):
			if updated_array[x][y] == 0 and updated_array[x-1][y]!=0:
				for check in range(x,0,-1):
					updated_array[check][y], updated_array[check-1][y] = updated_array[check-1][y], updated_array[check][y]
	
	#detect when there are holes at the bottom
	empty_bottom = []
	for y in range(len(updated_array[0])):
		if updated_array[len(updated_array)-1][y] == 0:
			empty_bottom.append(y)
				
	#print(empty_bottom)
	#Iterate through grid again and collect coordinates to be shifted.
	shifted_coordinates = []
	for x in range(len(updated_array)):
		for y in range(len(updated_array[0])):
			for element in empty_bottom:
				if y>element and updated_array[x][y]!=0:
					shifted_coordinates.append([x, y])
					
	#print(shifted_coordinates)

	for element in shifted_coordinates:
		shift_by = shifted_coordinates.count([element[0], element[1]])
		#print(shift_by)
		updated_array[element[0]][element[1]], updated_array[element[0]][element[1]-shift_by] = updated_array[element[0]][element[1]-shift_by], updated_array[element[0]][element[1]]
		shifted_coordinates = [value for value in shifted_coordinates if value != element]

	#After all shifts
	#for element in updated_array:
		#print(element)
	

	return updated_array

def find_similar(array, neighbors, start, similar, mode='BFS'):
	"""Run either a BFS or BFS algorithm based on criteria from arguments."""
	match = get_item(array, start)
	block = {start}
	visit = deque(block)
	child = dict(BFS=deque.popleft, DFS=deque.pop)[mode]
	while visit:
		node = child(visit)
		for offset in neighbors:
			index = get_next(node, offset)
			if index not in block:
				block.add(index)
				if is_valid(array, index):
					value = get_item(array, index)
					if similar(value, match):
						visit.append(index)
		yield node

def print_gameboard(gameboard):
	symbols = [' ', '$','^','@','+','=','*','V',';','&']

	# gameboard assumed to be 9x9
	for row in range(9):
		print(row, end='')
		print(' | ', end='')

		for num in gameboard[row]:
			print(symbols[num] + ' ', end='')
		print()
	print('  --------------------')
	print('    0 1 2 3 4 5 6 7 8 ')
	

def get_item(array, index):
	"""Access the data structure based on the given position information."""
	row, column = index
	return array[row][column]


def get_next(node, offset):
	"""Find the next location based on an offset from the current location."""
	row, column = node
	row_offset, column_offset = offset
	return row + row_offset, column + column_offset


def is_valid(array, index):
	"""Verify that the index is in range of the data structure's contents."""
	row, column = index
	return 0 <= row < len(array) and 0 <= column < len(array[row])

def get_nonzero(array, neighbors, similar):
	nonzero = []
	for x in range(len(array)):
		for y in range(len(array[0])):
			start = x, y
			node_length = len(list(find_similar(array, neighbors, start, similar, 'BFS')))
			if array[x][y]!=0 and node_length>=2:
				nonzero.append([x,y])
	return nonzero

def get_zeroes(array, neighbors, similar):
	zeroes = []
	for x in range(len(array)):
		for y in range(len(array[0])):
			if array[x][y]==0:
				zeroes.append([x,y])
	return zeroes

def find_most_similar(array, neighbors, similar, mode):
	most_similar = [0,0]
	largest = 0
	for x in range(len(array)):
		for y in range(len(array[0])):
			start = x, y

			#exclude 0 and exclude nodes with length <2
			node_length = len(list(find_similar(array, neighbors, start, similar , 'BFS')))
			if array[x][y] == 0 or node_length<2:
				continue
			
			number_similar = len(list(find_similar(array, neighbors, start, similar, 'BFS')))
			if number_similar>largest:
				largest = number_similar
				most_similar = [x,y]
	
	return most_similar, largest


def calculate_state_score(gameboard, neighbors, similar):
	totalscore=0
	for i in range(9):
		for j in range(9):
			if(gameboard[i][j]!=0):
				totalscore+=len(list(find_similar(gameboard, neighbors, (i,j), similar)))
	return totalscore


def random_search(gameboard, neighbors, similar, method="default"):
	coordinates_used = []
	#testing_gameboard = copy.deepcopy(gameboard)
	info = find_most_similar(gameboard, neighbors, similar, 'BFS')
	
	while (info[1]>1):
		possible_choices = get_nonzero(gameboard, neighbors, similar)
		if(len(possible_choices)>0):
			random_choice = random.randint(0, len(possible_choices)-1)

			start = possible_choices[random_choice][0], possible_choices[random_choice][1]

			modify_coords = list(find_similar(gameboard, neighbors, start, similar, 'BFS'))

			gameboard = modify_gameboard(gameboard, modify_coords)
			
			'''for element in gameboard:
				print(element)'''
			
			coordinates_used.append(start)
			#print("\n")

		else:
			break
	zero_count = len(get_zeroes(gameboard, neighbors, similar))
	#print("Finishing sequence with", 81-zero_count, " blocks remaining.\n")
	#print("End State: \n")
	#for element in gameboard:
		#print(element)
	
	'''print(coordinates_used)'''
	return coordinates_used, zero_count


if __name__ == '__main__':
	start_time = time.time()
	main()
	print("Execution time --- %s seconds ---" % (time.time() - start_time))