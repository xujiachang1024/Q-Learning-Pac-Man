# mlLearningAgents.py
# parsons/27-mar-2017
#
# A stub for a reinforcement learning agent to work with the Pacman
# piece of the Berkeley AI project:
#
# http://ai.berkeley.edu/reinforcement.html
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here was written by Simon Parsons, based on the code in
# pacmanAgents.py
# learningAgents.py

from pacman import Directions
from game import Agent
import random
import game
import util

# QLearnAgent
#
class QLearnAgent(Agent):

    # Constructor, called when we start running the
    def __init__(self, alpha=0.2, epsilon=0.1, gamma=0.8, numTraining = 10):
        # alpha       - learning rate
        # epsilon     - exploration rate
        # gamma       - discount factor
        # numTraining - number of training episodes
        #
        # These values are either passed from the command line or are
        # set to the default values above. We need to create and set
        # variables for them
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.gamma = float(gamma)
        self.numTraining = int(numTraining)
        # Count the number of games we have played
        self.episodesSoFar = 0
        # dictionary of Q-values
        self.Q_values = dict()
        # placeholder of the previous state
        self.prev_state = None
        # placeholder of the previous action
        self.prev_action = None
        # placeholder of the previous score
        self.prev_score = None


    # Accessor functions for the variable episodesSoFars controlling learning
    def incrementEpisodesSoFar(self):
        self.episodesSoFar += 1

    def getEpisodesSoFar(self):
        return self.episodesSoFar

    def getNumTraining(self):
        return self.numTraining

    # Accessor functions for parameters
    def setEpsilon(self, value):
        self.epsilon = value

    def getAlpha(self):
        return self.alpha

    def setAlpha(self, value):
        self.alpha = value

    def getGamma(self):
        return self.gamma

    def getMaxAttempts(self):
        return self.maxAttempts


    # getAction
    #
    # The main method required by the game. Called every time that
    # Pacman is expected to move
    def getAction(self, state, debug_mode=True):

        """
        Data about current state
        """
        legal = state.getLegalPacmanActions()
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        pacman_position = state.getPacmanPosition()
        ghost_positions = state.getGhostPositions()
        food_locations = state.getFood()
        # construct s'
        curr_state = (str(legal), str(pacman_position), str(ghost_positions), str(food_locations))
        if debug_mode:
            print("Legal moves: " + curr_state[0])
            print("Pacman position: " + curr_state[1])
            print("Ghost positions: " + curr_state[2])
            print("Food locations: ")
            print(curr_state[3])
            print("Score: " + str(state.getScore()) + "\n")

        # initialize Q-value
        if state not in self.Q_values:
            self.initialize_Q_values(state, legal)

        # update Q-value
        if self.prev_state != None:
            self.update_Q_value(state)

        # update placeholders
        self.update_placeholders(state, legal)

        return self.prev_action


    """
    training episodes: initialize Q-values
    """
    def initialize_Q_values(self, state, legal):
        self.Q_values[state] = dict()
        for action in legal:
            if action not in self.Q_values[state]:
                self.Q_values[state][action] = 0.0


    """
    training episodes: update Q-value
    """
    def update_Q_value(self, state, final_step=False):
        # calculate R(s)
        reward = state.getScore() - self.prev_score
        # calculate max(Q(s', a'))
        max_Q_value = 0.0
        if not final_step:
            max_Q_value = max(list(self.Q_values[state].values()))
        # update Q(s, a)
        self.Q_values[self.prev_state][self.prev_action] += (self.alpha * (reward + self.gamma * max_Q_value - self.Q_values[self.prev_state][self.prev_action]))


    """
    update placeholders
    """
    def update_placeholders(self, state, legal):
        # register s' as s
        self.prev_state = state
        # register a' as a
        self.prev_action = self.epsilon_greedy(state, legal)
        # register as previous score
        self.prev_score = state.getScore()


    """
    action selection: epsilon-greedy
    """
    def epsilon_greedy(self, state, legal):
        # generate a random probability
        probability = random.random()
        # if probability is less than exploration rate: random action
        if probability < self.epsilon:
            random_action = random.choice(legal)
            return random_action
        # if probability is greater than exploration rate: max Q-value action
        max_Q_action = None
        for action in legal:
            if max_Q_action == None:
                max_Q_action = action
            if self.Q_values[state][action] > self.Q_values[state][max_Q_action]:
                max_Q_action = action
        return max_Q_action


    """
    Reset placeholder variables
    """
    def reset_placeholders(self):
        self.prev_state = None
        self.prev_action = None
        self.prev_score = None


    # Handle the end of episodes
    #
    # This is called by the game after a win or a loss.
    def final(self, state, debug_mode=True):

        # update Q-value
        if self.prev_state != None:
            self.update_Q_value(state, final_step=True)

        # reset placeholder variables
        self.reset_placeholders()

        # Keep track of the number of games played, and set learning
        # parameters to zero when we are done with the pre-set number
        # of training episodes
        self.incrementEpisodesSoFar()
        if self.getEpisodesSoFar() == self.getNumTraining():
            msg = "Training Done (turning off epsilon and alpha)"
            print("%s\n%s" % (msg,"-" * len(msg)))
            self.setAlpha(0)
            self.setEpsilon(0)
