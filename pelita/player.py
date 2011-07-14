from universe import stop
import random

class AbstractPlayer(object):

    def _set_index(self, index):
        self._index = index

    def _set_initial(self, universe):
        self.universe_states = []
        self.universe_states.append(universe)

    def set_initial(self, universe):
        pass

    def _get_move(self, universe):
        self.universe_states.append(universe)
        return self.get_move(universe)

    def get_move(self, universe):
        raise NotImplementedError(
                "You must override the 'get_move' method in your player")

class StoppingPlayer(AbstractPlayer):

    def get_move(self, universe):
        return stop

class RandomPlayer(AbstractPlayer):

    def get_move(self, universe):
        legal_moves = universe.get_legal_moves(universe.bots[self._index].current_pos)
        return random.choice(legal_moves.keys())
