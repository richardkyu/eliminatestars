import random
import image_grid

# plays and solves http://g.fromgame.com/game/13/


class Game:
    best = float('inf')
    iterations = 0
    def __init__(self, width, height, colours=2):
        self.width = width
        self.height = height
        self.colours = colours
        self.board = [[0 for __ in range(width)] for __ in range(height)]

    def generate(self, seed=0):
        # very naive way to generate a board,
        # heavily biased towards horizontal runs, not really important
        random.seed(random.randint(1, 10000))
        self.board = []
        while len(self.board) < self.width * self.height:
            self.board.extend([random.randint(1, self.colours)] * random.randint(1, self.width // 2))
        self.board = [self.board[i*self.width:(i+1)*self.width] for i in range(self.height)]
        self.drop()

    def import_board(self):
        self.board = image_grid.main_process()


    def drop(self):
        # simply gravity, keeps dropping blocks until they are all at the 'bottom'
        dropped = True
        while dropped:
            dropped = False
            for lower, above in zip(reversed(self.board), list(reversed(self.board))[1:]):
                for i in range(len(lower)):
                    if lower[i] == 0 and above[i] != 0:
                        lower[i] = above[i]
                        above[i] = 0
                        dropped = True
        # move columns to the left, leaving no empties
        rc = [i for i, c in enumerate(self.board[-1]) if c == 0]
        self.board = [[c for i, c in enumerate(line) if i not in rc] + [0 for __ in range(len(rc))] for line in self.board]

    def copy(self):
        # returns a completely new copy of this game
        game = self.__class__(self.width, self.height, self.colours)
        game.board = [line.copy() for line in self.board]
        return game

    def print(self):
        for line in self.board:
            print(''.join(map(str,line)))

    def get_move(self, start_x, start_y):
        # returns all the pairs x, y that would be removed if the block at x, y is removed
        if self.board[start_y][start_x] == 0:
            return []

        colour = self.board[start_y][start_x]
        queue = [(start_x, start_y)]
        result = {(start_x, start_y)}

        def add(a, b):
            if (a, b) not in result and self.board[b][a] == colour:
                result.add((a, b))
                queue.append((a, b))

        while queue:
            x, y = queue.pop(0)
            if x+1 < self.width:
                add(x+1, y)
            if y+1 < self.height:
                add(x, y+1)
            if x-1 >= 0:
                add(x-1, y)
            if y-1 >= 0:
                add(x, y-1)

        return result

    def get_all_moves(self):
        # finds a set of all possible moves (as tuples of moves that are all the same move)
        moves = set()
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] > 0 and not any((x, y) in m for m in moves):
                    m = self.get_move(x, y)
                    # only moves of more than one block are valid
                    if len(m) > 1:
                        moves.add(tuple(m))
        return moves

    def make_move(self, move):
        for x, y in move:
            self.board[y][x] = 0
        self.drop()

    def check_won(self):
        # returns whether the game has been completed assumes all positive colours
        number = sum(sum(line) for line in self.board)

        Game.iterations +=1
        if Game.iterations%1000000==0:
            self.print()
            print()

        if number < Game.best:
            Game.best=number
            print(f'Current best: {number}')
            self.print()
            print()

        return self.board[self.width-1][0] == 0

    def play(self):
        
        #input()
        #print(self.check_won())
        # trivial if there's nothing on the board, win in 0 moves, 1 path, empty moves
        if self.check_won():
            return 0, 1, {}
        # otherwise play all possible moves until conclusion
        moves = {}
        size = self.width * self.height
        min_d = size  # worst case as many moves as squares
        total = 0
        for move in self.get_all_moves():
            next_state = self.copy()
            next_state.make_move(move)
            d, n, rest = next_state.play()
            # only save the move if there's a way to win the game after this move
            if d < size:
                moves[(move[0], d)] = rest
                total += n
                min_d = min(min_d, d+1)
                return min_d, total, moves
        return min_d, total, moves


def main():
    g = Game(9, 9, 4) #doesn't matter if you are importing a board.

    #g.generate()
    g.import_board()

    print('Start of the game:')
    g.print()
    min_moves, paths, moves = g.play()

    #print(moves)

    if min_moves == g.width * g.height:
        print('Game cannot be won!')
    else:
        g_copy = g.copy()
        print(f'The first winning play in {min_moves} moves.') #, out of {paths} possible different games:')
        options = moves
        n = min_moves
        x, y = 0, 0
        next_options = {}
        while n > 0:
            for ((x, y), c), next_options in options.items():
                if c == n:
                    break
            print(f'Make move {(x, y)}:')
            g_copy.make_move(g_copy.get_move(x, y))
            g_copy.print()
            n -= 1
            options = next_options


if __name__ == '__main__':
    main()