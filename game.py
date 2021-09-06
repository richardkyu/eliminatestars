#! /usr/bin/env python3
from collections import deque
from operator import eq
import random, copy, time, inspect, image_grid

all_actions = [i for i in range(81)]
neighbour_offsets = ((-1, 0), (0, +1), (+1, 0), (0, -1))

class EliminateStarsGame:

	def __init__(self, gameboard):
		self.gameboard = gameboard
		self.actions_list = []
		self.num_isolated_islands = len(get_isolated_islands(self.gameboard, neighbour_offsets))
		self.action_reward_value =0
		#print("Start state:")
		#print_gameboard(self.gameboard)
	
	def get_state(self):
		return self.gameboard

	def act(self, gameboard, action, neighbors):
		x_coord = action//9
		y_coord = action%9
		start = x_coord, y_coord
		self.actions_list.append(start)
		modify_coords = find_similar(gameboard, neighbors, start, BFS=True)
		self.action_reward_value = len(modify_coords)
		gameboard = modify_gameboard(gameboard, modify_coords)
		return gameboard

	def get_reward(self):
		reward=0
		if self.gameboard[8][0]==0:
			print(self.actions_list)
			reward=1000
		elif all_isolated(self.gameboard, neighbour_offsets) == True and self.gameboard[8][0]!=0:
			eliminated = len(get_zeroes(self.gameboard, neighbour_offsets))
			if eliminated>50:
				reward =(15 +(eliminated-50))/100
			else:
				reward+= self.action_reward_value#-(len(get_isolated_islands(self.gameboard, neighbour_offsets)))/100
				
		else:
			#print("action reward " ,self.action_reward_value)
			reward = ((self.num_isolated_islands - (len(get_isolated_islands(self.gameboard, neighbour_offsets)))) + self.action_reward_value*self.action_reward_value)/5
			#print("default reward: ", reward)
			self.num_isolated_islands=(len(get_isolated_islands(self.gameboard, neighbour_offsets)))

		return reward

	def get_random_move(self, gameboard):
		possible_choices = get_nonzero(gameboard, neighbour_offsets)
		if(len(possible_choices)>0):
			random_choice = random.randint(0, len(possible_choices)-1)
		else:
			return 0
		return 9*possible_choices[random_choice][0]+possible_choices[random_choice][1]
	
	def reset(self):
		self.gameboard = image_grid.main_process()
		self.actions_list =[]
		self.num_isolated_islands=len(get_isolated_islands(self.gameboard, neighbour_offsets))
		self.action_reward_value =0




'''def start_game(gameboard, neighbour_offsets):
	while(True):
		testing_gameboard = copy.deepcopy(gameboard)
		info, largest = find_most_similar(testing_gameboard, neighbour_offsets, do_bfs=True)

		info = find_most_similar(testing_gameboard, neighbour_offsets, 'BFS')
		
		
		#print ("Suggested: ", info[0], " with ", info[1], " nodes.")
		input()
		
		print("Zeroes: ", len(get_zeroes(gameboard,neighbour_offsets)))
		print_gameboard(gameboard)'''

def check_membership(action, choices):
	if action in choices:
		return True
	else:
		return False


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

def find_similar(array, neighbors, start, BFS=True):
	"""Run either a BFS or DFS algorithm to get the next node"""
	match = get_item(array, start)
	block = {start}
	visit = deque(block)

	child = None
	if BFS:
		child = deque.popleft
	else:
		child = deque.pop

	nodes_found = []	

	while visit:
		node = child(visit)
		for offset in neighbors:
			index = get_next(node, offset)
			if index not in block:
				block.add(index)
				if is_valid(array, index):
					value = get_item(array, index)
					if eq(value, match):
						visit.append(index)
		nodes_found += [node]

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


def is_valid(array, index):
	"""Verify that the index is in range of the data structure's contents."""
	row, column = index
	return 0 <= row < len(array) and 0 <= column < len(array[row])

def get_nonzero(array, neighbors):
	nonzero = []
	for x in range(len(array)):
		for y in range(len(array[0])):
			start = x, y
			node_length = len(find_similar(array, neighbors, start, BFS=True))
			if array[x][y]!=0 and node_length>=2:
				nonzero.append([x,y])
	return nonzero

def get_zeroes(array, neighbors):
	zeroes = []
	for x in range(len(array)):
		for y in range(len(array[0])):
			if array[x][y]==0:
				zeroes.append([x,y])
	return zeroes

def get_isolated_islands(array, neighbors):
	isolated_islands=[]
	for x in range(len(array)):
		for y in range(len(array[0])):
			if len(find_similar(array, neighbors,(x,y)))==1:
				isolated_islands.append([x,y])

	#print(isolated_islands)
	return isolated_islands

def all_isolated(gameboard, neighbors):
	if len(get_isolated_islands(gameboard, neighbors))>0 and len(get_nonzero(gameboard,neighbors))==0:
		return True
	else:
		return False


def find_most_similar(gameboard, neighbors, do_bfs):
	most_similar = [0,0]
	largest = 0
	for x in range(len(gameboard)):
		for y in range(len(gameboard[0])):
			start = x, y

			#exclude 0 and exclude nodes with length <2
			node_length = len(find_similar(gameboard, neighbors, start, do_bfs))
			if gameboard[x][y] == 0 or node_length<2:
				continue
			
			number_similar = len(find_similar(gameboard, neighbors, start, do_bfs))
			if number_similar>largest:
				largest = number_similar
				most_similar = [x,y]
	
	return most_similar, largest



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
