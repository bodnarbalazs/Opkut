import matplotlib.pyplot as plt
import numpy as np
import random

class Stage:
    def __init__(self, width=4, height=3):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        self.grid[0][0]=2
        
    def get_valid_moves(self):
        return [(i, j) for i in range(self.height) for j in range(self.width) if self.grid[i][j] != 0 and self.grid[i][j]!=2]

    def visualize(self):
        colors = np.array(self.grid)
        fig, ax = plt.subplots()
        ax.set_xticks(np.arange(self.width))
        ax.set_yticks(np.arange(self.height))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(length=0)
        for i in range(self.height):
            ax.axhline(i-0.5, color='black')
        for j in range(self.width):
            ax.axvline(j-0.5, color='black')

        # Use a colormap to map numbers to colors
        cmap = plt.cm.colors.ListedColormap(['gray', 'orange', 'green'])
        ax.imshow(colors, cmap=cmap, vmin=0, vmax=2)

        plt.show()
    def visualize_with_asc(self):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                print("[{}] ".format(self.grid[i][j]), end="")
            print("\n", end="")

class Box:
    def __init__(self, stage):
        self.stage = stage
        self.moves = stage.get_valid_moves()  # Use get_valid_moves method
        self.probabilities = [1 for _ in range(len(self.moves))]  # Initialize all probabilities to 1
    def heatmap(self):
        # Create a new grid with the same size as the stage
        prob_grid = [[np.nan for _ in range(self.stage.width)] for _ in range(self.stage.height)]  # Initialize with np.nan

        # Fill the grid with the probabilities
        for move, probability in zip(self.moves, self.probabilities):
            prob_grid[move[0]][move[1]] = probability

        # Convert to a numpy array for visualization
        prob_grid = np.array(prob_grid)

        fig, ax = plt.subplots()
        ax.set_xticks(np.arange(self.stage.width))
        ax.set_yticks(np.arange(self.stage.height))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(length=0)
        for i in range(self.stage.height):
            ax.axhline(i-0.5, color='black')
        for j in range(self.stage.width):
            ax.axvline(j-0.5, color='black')

        # Use a colormap that goes from red to green and maps np.nan to gray
        cmap = plt.cm.colors.LinearSegmentedColormap.from_list("mycmap", ["red", "yellow", "green"])
        cmap.set_bad('gray')  # Set color for np.nan

        # Plot the probabilities
        vmax = max(self.probabilities) if self.probabilities else 1
        im = ax.imshow(prob_grid, cmap=cmap, vmin=0, vmax=vmax)

        # Add a colorbar to show the scale
        fig.colorbar(im, ax=ax)

        plt.show()





class Player:
    def __init__(self):
        self.playbook = []
        self.currentMoves=[]
        self.wins=0
        self.losses=0
        self.winRatio=[]

    def add_to_playbook(self, box):
        self.playbook.append(box)

    def stage_in_playbook(self, stage):
        for box in self.playbook:
            if box.stage.grid == stage.grid:
                return True
        return False

    def make_move(self, stage):
    # Find the box corresponding to the current stage in the playbook
        for box in self.playbook:
            if box.stage.grid == stage.grid:
                # Choose a move randomly, weighted by the probabilities
                move = random.choices(box.moves, weights=box.probabilities, k=1)[0]
                self.currentMoves.append((stage, move))
                # Apply the move
                new_stage = self.apply_move(stage, move)

                return new_stage

        # If the stage is not in the playbook, just choose a valid move randomly
        move = random.choice(stage.get_valid_moves())  # Use get_valid_moves method
        self.currentMoves.append((stage, move))
        
        new_stage = self.apply_move(stage, move)

        if not self.stage_in_playbook(new_stage):
            self.playbook.append(Box(new_stage))

        return new_stage


    def apply_move(self, stage, move):
        # Create a new stage and apply the move
        new_stage = Stage(stage.width, stage.height)
        new_stage.grid = [row.copy() for row in stage.grid]
        for i in range(move[0], stage.height):
            for j in range(move[1], stage.width):
                new_stage.grid[i][j] = 0  # Eat the piece

        return new_stage
    
    def win(self):
        for stage, move in self.currentMoves:
            for box in self.playbook:
                if box.stage.grid == stage.grid:
                    index = box.moves.index(move)
                    box.probabilities[index] *= 1.1 # Increase the probability
        self.currentMoves = []  # Reset the moves for the next game
        self.wins+=1
        w=self.wins if self.wins != 0 else 1
        l=self.losses if self.losses != 0 else 1
        self.winRatio.append(w/(w+l))

    def lose(self):
        for stage, move in self.currentMoves:
            for box in self.playbook:
                if box.stage.grid == stage.grid:
                    index = box.moves.index(move)
                    if box.probabilities[index] > 1:
                        box.probabilities[index] *= 0.9 # Decrease the probability, but not below 1
        self.currentMoves = []  # Reset the moves for the next game
        self.losses+=1
        w=self.wins if self.wins != 0 else 1
        l=self.losses if self.losses != 0 else 1
        self.winRatio.append(w/(w+l))
        
def play(player1, player2):
    # Initialize the game with a new stage
    stage = Stage()
    stages = [stage]  # List to hold each stage

    while True:
        if len(stage.get_valid_moves()) == 0:
            # Player 1 loses if they can't make a move
            player1.lose()
            player2.win()
            # print("player 2 won")
            break
        else:
            stage = player1.make_move(stage)
            stages.append(stage)  # Append the new stage to the list

        if len(stage.get_valid_moves()) == 0:
            # Player 2 loses if they can't make a move
            player2.lose()
            player1.win()
            # print("player 1 won")
            break
        else:
            stage = player2.make_move(stage)
            stages.append(stage)  # Append the new stage to the list

    return stages  # Return the list of stages


def plotWinRatio(player):
    plt.plot(player.winRatio)
    plt.xlabel('Game')
    plt.ylabel('Win Ratio')
    plt.title('Player Win Ratio Over Time')
    plt.grid(True)
    plt.show()

# player1=Player()
# player2=Player()
# player3=Player()


# for i in range(1000):
#     play(player1,player2)
#     play(player1,player3)

   

# for box in player1.playbook:
#     box.heatmap()

# print(len(player1.playbook))
# plotWinRatio(player1)
# plotWinRatio(player2)
# plotWinRatio(player3)
