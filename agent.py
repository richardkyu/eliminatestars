import torch, random, image_grid, copy
import numpy as np
from game import *
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot


MAX_MEMORY = 250000
BATCH_SIZE = 1000
LR = 0.001



class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 #randomness
        self.gamma = 0.9 #discount rate, must be smaller than 1
        self.memory=deque(maxlen = MAX_MEMORY) #popleft()
        self.model = Linear_QNet(81, 256, 128, 81)
        self.trainer = QTrainer(self.model, lr = LR, gamma = self.gamma)

    def get_state(self, game):
        return game.get_state()

    def remember(self, state, action, reward, next_state, done):
        state=convert_state(state)
        next_state = convert_state(next_state)
        self.memory.append((state, action, reward, next_state, done)) #popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) #list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        state=convert_state(state)
        #print(next_state)
        next_state = convert_state(next_state)
        self.trainer.train_step(state, action, reward, next_state, done)


    
    def get_action(self, state, game):
        #random moves: tradeoff exploration / exploitation
        self.epsilon = 100 - self.n_games
        final_move = game.get_random_move(state)
        if random.randint(0,220) < self.epsilon:
            final_move = game.get_random_move(state)
            #print("Entered random: ", final_move)

        else:
            #print("Entered prediction by nn")
            state0 = torch.tensor(convert_state(state), dtype=torch.float)
            prediction = self.model(state0)
            
            print("Prediction: ", prediction)

            valid = get_nonzero(game.get_state(), neighbour_offsets)
            
            for i in range(len(valid)):
                if prediction[valid[i][0]*9 + valid[i][1]] > prediction[final_move]:
                    final_move = valid[i][0]*9 + valid[i][1]

            #print("After filter: ", final_move)

            #input()
            
            
            #double check this one later

        #print(final_move)
        #input()
        return final_move

def convert_state(state):
    state_np = np.array(state, dtype=int)
    state_flat = state_np.flatten()
    return state_flat


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = EliminateStarsGame(image_grid.main_process())

    while True:
        #get old state
        state_old = copy.deepcopy(agent.get_state(game))
        '''print("State old first")
        print_gameboard(state_old)'''
        #get move
        final_move = agent.get_action(state_old, game)
        #print("Final move: ", final_move)

        state_new = game.act(game.get_state(), final_move, neighbour_offsets)

        #perform move and get new state
        reward, done, score = game.get_reward(), (all_isolated(game.get_state(), neighbour_offsets) or game.get_state()[8][0] == 0), len(get_zeroes(game.get_state(), neighbour_offsets))
        #if reward !=0:
            #print(reward)
        
        '''if(agent.n_games>70):
            print_gameboard(state_new)
            print("Final move: ", final_move)'''
        

        #print_gameboard(state_old)
        #print_gameboard(state_new)


        #print_gameboard(state_new)
        #print("reward, isDone, score", reward, done, score, "\n")
        #input()
        
        #train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        #remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done: 
            #train long memory (experience replay and plot result)
            game.reset()
            agent.n_games +=1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()
            
            print('Game: ', agent.n_games, 'Score: ', score, 'Record: ', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()
    '''game = EliminateStarsGame(image_grid.main_process())
    while(True):
        print_gameboard(game.get_state())
        print('Suggested: ', game.get_random_move())
        action = int(input('Enter action: '))
        

        game.act(game.get_state(), action, neighbour_offsets)'''

    
    
    

