from pelita.layout import Layout
from pelita.containers import Mesh, new_pos

__docformat__ = "restructuredtext"

north = (0, -1)
south = (0, 1)
west  = (-1, 0)
east  = (1, 0)
stop  = (0, 0)


class Team(object):
    """ A team of bots.

    Parameters
    ----------
    index : int
        the index of the team within the Universe
    name : str
        the name of the team
    zone : tuple of int (x_min, x_max)
        the homezone of this team
    score : int, optional, default = 0
        the score of this team
    bots : list of int, optional, default = None (creates an empty list)
        the bot indices that belong to this team

    """
    def __init__(self, index, name, zone, score=0, bots=None):
        self.index = index
        self.name = name
        self.zone = zone
        self.score = score
        # we can't use a keyword argument here, because that would create a
        # single list object for all our Teams.
        if not bots:
            self.bots = []
        else:
            self.bots = bots

    def _add_bot(self, bot):
        """ Add a bot to this team.

        Parameters
        ----------
        bot : int
            the index of the bot to add

        """
        self.bots.append(bot)

    def in_zone(self, position):
        """ Check if a position is within the zone

        Parameters
        ----------
        position : tuple of int (x, y)
            the position to check

        Returns
        -------
        is_in_zone : boolean
            True if the position is in the homezone and False otherwise

        """
        return self.zone[0] <= position[0] <= self.zone[1]

    def _score_point(self):
        """ Score a single point. """
        self.score += 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return ('Team(%i, %r, %s, score=%i, bots=%r)' %
                (self.index, self.name, self.zone, self.score, self.bots))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class Bot(object):
    """ A bot on a team.

    Parameters
    ----------
    index : int
        the index of this bot within the Universe
    initial_pos : tuple of int (x, y)
        the initial position for this bot
    team_index : int
        the index of the team that this bot is on
    homezone : tuple of int (x_min, x_max)
        the homezone of this team
    current_pos : tuple of int (x, y), optional
        the current position of this bot
        default = None (will be set to initial_pos)

    Attributes
    ----------
    in_own_zone : boolean, property
        True if in its own homezone and False otherwise
    is_destroyer : boolean
        True if a destroyer, False otherwise
    is_harvester : boolean, property
        not is_destroyer

    """
    def __init__(self, index, initial_pos, team_index, homezone,
            current_pos=None):
        self.index = index
        self.initial_pos = initial_pos
        self.team_index = team_index
        self.homezone = homezone
        if not current_pos:
            self.current_pos = self.initial_pos
        else:
            self.current_pos = current_pos
        if self.in_own_zone:
            self.is_destroyer = True
        else:
            self.is_destroyer = False

    @property
    def in_own_zone(self):
        return self.homezone[0] <= self.current_pos[0] <= self.homezone[1]

    @property
    def is_harvester(self):
        return not self.is_destroyer

    def _move(self, new_pos):
        """ Move this bot to a new location.

        Its state (harvester or destroyer) will be automatically updated.
        Whoever moves the bot is responsible for checking the legality of the
        new position.

        Parameters
        ----------
        new_pos : tuple of int (x, y)
            the new position for this bot

        """
        self.current_pos = new_pos
        if self.is_destroyer:
            if not self.in_own_zone:
                self.is_destroyer = False
        elif self.is_harvester:
            if self.in_own_zone:
                self.is_destroyer = True

    def _reset(self):
        """ Reset this bot to its initial position. """
        self._move(self.initial_pos)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __cmp__(self, other):
        if self == other:
            return 0
        else:
            return self.index.__cmp__(other.index)

    def __repr__(self):
        return ('Bot(%i, %s, %i, %s , current_pos=%s)' %
                (self.index, self.initial_pos, self.team_index,
                    self.homezone, self.current_pos))


class UniverseEvent(object):
    """ Base class for all events in a Universe. """

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class BotMoves(UniverseEvent):
    """ Signifies that a bot has moved.

    Parameters
    ----------
    bot_index : int
        index of the bot

    """
    def __init__(self, bot_index):
        self.bot_index = bot_index

    def __repr__(self):
        return 'BotMoves(%i)' % self.bot_index

class BotEats(UniverseEvent):
    """ Signifies that a bot has eaten food.

    Parameters
    ----------
    bot_index : int
        index of the bot

    """
    def __init__(self, bot_index):
        self.bot_index = bot_index

    def __repr__(self):
        return 'BotEats(%i)' % self.bot_index

class BotDestroyed(UniverseEvent):
    """ Signifies that a bot has been destroyed.

    Parameters
    ----------
    harvester_index : int
        index of the destroyed bot
    destroyer_index : int
        index of the destroying bot

    """
    def __init__(self, harvester_index, destroyer_index):
        self.harvester_index = harvester_index
        self.destroyer_index = destroyer_index

    def __repr__(self):
        return ('BotDestroyed(%i, %i)'
            % (self.harvester_index, self.destroyer_index))

class TeamWins(UniverseEvent):
    """ Signify that a team has eaten all enemy food.

    Parameters
    ----------
    winning_team_index : int
        index of the winning team

    """
    def __init__(self, winning_team_index):
        self.winning_team_index = winning_team_index

    def __repr__(self):
        return ("TeamWins(%i)"
            % self.winning_team_index)

class MazeComponent(object):
    """ Base class for all items inside a maze. """

    def __str__(self):
        return self.__class__.char

    def __eq__(self, other):
        return isinstance(other, self.__class__)

class Free(MazeComponent):
    """ Object to represent a free space. """

    char = ' '

    def __repr__(self):
        return 'Free()'

class Wall(MazeComponent):
    """ Object to represent a wall. """

    char = '#'

    def __repr__(self):
        return 'Wall()'

class Food(MazeComponent):
    """ Object to represent a food item. """

    char = '.'

    def __repr__(self):
        return 'Food()'

def create_maze(layout_mesh):
    """ Transforms a layout_mesh into a maze_mesh.

    Parameters
    ----------
    layout_mesh : Mesh of single char strings
        Mesh of single character strings describing the layout

    Returns
    -------
    maze_mesh : Mesh of lists
        Mesh of lists of MazeComponents

    """
    maze_mesh = Mesh(layout_mesh.width, layout_mesh.height,
            data=[[] for i in range(len(layout_mesh))])
    for index in maze_mesh.iterkeys():
        if layout_mesh[index] == Wall.char:
            maze_mesh[index].append(Wall())
        else:
            maze_mesh[index].append(Free())
        if layout_mesh[index] == Food.char:
            maze_mesh[index].append(Food())
    return maze_mesh

def extract_initial_positions(mesh, number_bots):
    """ Extract initial positions from mesh.

    Also replaces the initial positions in the mesh with free spaces.

    Parameters
    ----------
    mesh : Mesh of characters
        the layout in mesh format
    number_bots : int
        the number of bots for which to find initial positions

    Returns
    -------
    initial pos : list of tuples
        the initial positions for all the bots
    """
    bot_ids = [str(i) for i in range(number_bots)]
    start = [(0, 0)] * number_bots
    for k, v in mesh.iteritems():
        if v in bot_ids:
            start[int(v)] = k
            mesh[k] = Free.char
    return start

def create_CTFUniverse(layout_str, number_bots,
        team_names=['black', 'white']):
    """ Factory to create a 2-Player Capture The Flag Universe.

    Parameters
    ----------
    layout_str : str
        the string encoding the maze layout
    number_bots : int
        the number of bots in the game
    team_names : length 2 list of strings, optional default = ['black', 'white']
        the names of the playing teams

    Raises
    ------
    UniverseException
        if the number of bots or layout width are odd
    LayoutEncodingException
        if there is something wrong with the layout_str, see `Layout()`

    """
    layout_chars = [cls.char for cls in [Wall, Free, Food]]

    if number_bots % 2 != 0:
        raise UniverseException(
            "Number of bots in CTF must be even, is: %i"
            % number_bots)
    layout = Layout(layout_str, layout_chars, number_bots)
    layout_mesh = layout.as_mesh()
    initial_pos = extract_initial_positions(layout_mesh, number_bots)
    maze_mesh = create_maze(layout_mesh)
    if maze_mesh.width % 2 != 0:
        raise UniverseException(
            "Width of a layout for CTF must be even, is: %i"
            % maze_mesh.width)
    homezones = [(0, maze_mesh.width//2-1), (maze_mesh.width//2,
        maze_mesh.width-1)]

    teams = []
    teams.append(Team(0, team_names[0], homezones[0], bots=range(0,
        number_bots, 2)))
    teams.append(Team(1, team_names[1], homezones[1], bots=range(1,
        number_bots, 2)))

    bots = []
    for bot_index in range(number_bots):
        team_index = bot_index % 2
        bot =  Bot(bot_index, initial_pos[bot_index],
                team_index, homezones[team_index])
        bots.append(bot)

    return CTFUniverse(maze_mesh, teams, bots)

class UniverseException(Exception):
    """ Standard error in the Universe. """
    pass

class IllegalMoveException(Exception):
    """ Raised when a bot attempts to make an illegal move. """
    pass

class CTFUniverse(object):
    """ The Universe: representation of the game state.

    Parameters
    ----------
    maze_mesh : mesh of lists of MazeComponent objects
        the maze
    teams : list of Team objects
        the teams
    bots : lits of Bot objects
        the bots

    Attributes
    ----------
    bot_positions : list of tuple of ints (x, y), property
        the current position of all bots
    food_list : list of typle of ints (x, y), property
        the positions of all edible food

    """

    move_ids = [north, south, east, west, stop]

    def __init__(self, maze_mesh, teams, bots):
        self.maze_mesh = maze_mesh
        # TODO make a deepcopy here, so that we can big_bang
        self.teams = teams
        self.bots = bots

    @property
    def bot_positions(self):
        return [bot.current_pos for bot in self.bots]

    @property
    def food_list(self):
        return [key for (key, value) in self.maze_mesh.iteritems()
                if Food() in value]

    def team_food(self, team_index):
        return [key for (key, value) in self.maze_mesh.iteritems() if Food() in
                value and self.teams[team_index].in_zone(key)]

    def enemy_food(self, team_index):
        return [key for (key, value) in self.maze_mesh.iteritems() if Food() in
                value and not self.teams[team_index].in_zone(key)]

    def enemy_bots(self, team_index):
        """ Obtain enemy bot objects.

        Parameters
        ----------
        team_index : int
            the index of the 'friendly' team

        Returns
        -------
        enemy_bots : list of Bot objects

        """
        other_teams = self.teams[:]
        other_teams.remove(self.teams[team_index])
        other_team_bots = []
        for t in other_teams:
            other_team_bots.extend(t.bots)
        return [self.bots[i] for i in other_team_bots]

    def move_bot(self, bot_id, move):
        """ Move a bot in certain direction.

        Parameters
        ----------
        bot_id : int
            index of the bot
        move : string
            direction to move in

        Returns
        -------
        events : list of UniverseEvent objects
            the events that happend during the move

        Raises
        ------
        IllegalMoveException
            if the string is an invalid or the move not possible

        """
        events = []
        # check legality of the move
        if move not in self.move_ids:
            raise IllegalMoveException(
                'Illegal move_id from bot %i: %s' % (bot_id, move))
        bot = self.bots[bot_id]
        legal_moves_dict = self.get_legal_moves(bot.current_pos)
        if move not in legal_moves_dict.keys():
            raise IllegalMoveException(
                'Illegal move from bot %r: %s'
                % (bot, move))
        bot._move(legal_moves_dict[move])
        events.append(BotMoves(bot_id))
        # check for destruction
        for enemy in self.enemy_bots(bot.team_index):
            if enemy.current_pos == bot.current_pos:
                if enemy.is_destroyer and bot.is_harvester:
                    bot._reset()
                    events.append(BotDestroyed(bot.index, enemy.index))
                elif enemy.is_harvester and bot.is_destroyer:
                    enemy._reset()
                    events.append(BotDestroyed(enemy.index, bot.index))
        # check for food being eaten
        if Food() in self.maze_mesh[bot.current_pos] and not bot.in_own_zone:
            self.maze_mesh[bot.current_pos].remove(Food())
            self.teams[bot.team_index]._score_point()
            events.append(BotEats(bot_id))
            if not self.enemy_food(bot.team_index):
                events.append(TeamWins(bot.team_index))

        return events

        # TODO:
        # check for state change
        # generate a list of events
        # propagate those events to observers
        # callbacks for the bots

    def get_legal_moves(self, position):
        """ Obtain legal moves and where they lead.

        Parameters
        ----------
        position : tuple of int (x, y)
            the position to start at

        Returns
        -------
        legal_moves_dict : dict mapping strings (moves) to positions (x, y)
            the legal moves and where they would lead.

        """
        legal_moves_dict = {}
        for move, new_pos in self.neighbourhood(position).items():
            if Free() in self.maze_mesh[new_pos]:
                legal_moves_dict[move] = new_pos
        return legal_moves_dict

    def __repr__(self):
        return ("CTFUniverse(%r, %r, %r)" %
            (self.maze_mesh, self.teams, self.bots))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def _char_mesh(self):
        out = self.maze_mesh.copy()
        for (key, value) in self.maze_mesh.iteritems():
            if Wall() in value:
                out[key] = Wall.char
            elif Food() in value:
                out[key] = Food.char
            elif Free() in value:
                out[key] = Free.char
        for bot in self.bots:
            out[bot.current_pos] = str(bot.index)
        return out

    def __str__(self):
        # TODO what about bots on the same space?
        return str(self._char_mesh)

    def as_str(self):
        return self._char_mesh.as_str()

    def pretty_print(self):
        out = str()
        out += str(self)
        out += repr(self.teams)
        out += repr(self.bots)
        print out


    def neighbourhood(self, position):
        """ Determine where a move will lead.

        Parameters
        ----------
        position : tuple of int (x, y)
            current position

        Returns
        -------
        new_pos : dict
            mapping of moves to new positions (x, y)

        """
        return dict([(move, new_pos(position, move)) for
            move in self.move_ids])

    @staticmethod
    def is_adjacent(pos1, pos2):
        return (pos1[0] == pos2[0] and abs(pos1[1] - pos2[1]) == 1 or
            pos1[1] == pos2[1] and abs(pos1[0] - pos2[0]) == 1)