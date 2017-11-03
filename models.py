#!/usr/bin/python3
"""Class definitions used across Battleship projeect.

Project 2 - Treehouse Techdegree - Python Web Development
"""
from constants import *
from utils import *
import random
from collections import Counter
import pickle

__author__ = "Chris Freeman"
__copyright__ = "Copyright 2016, Chris Freeman"
__license__ = "MIT"


class Board():
    """Battleship Board

    Board is a square array of Locations
    """

    def __init__(self, size=BOARD_SIZE):
        """initialize board to correct size"""
        self.size = size
        self.grid = []
        # Add 'size' number of rows
        for row in range(self.size):
            # Add 'size' number of Locations per row
            new_row = []
            for col in range(self.size):
                new_row.append(Location(offset_to_coord(row, col)))
            self.grid.append(new_row)

    def get_player_view(self, as_list = False):
        """Return player view of game board (with ships revealed)"""
        if as_list:
            view = [[location.player_view() for location in row] for row in self.grid]
        else:
            view = [BOARD_HEADING]
            row_num = 1
            for row in self.grid:
                view.append(str(row_num).rjust(2) + " " + " ".join(
                    [location.player_view() for location in row]))
                row_num += 1
            view.append("")
        return view

    def get_opponent_view(self, as_list = False):
        """Return opponent view of game board (without revealing ships)"""
        if as_list:
            view = [[location.opponent_view() for location in row] for row in self.grid]
        else:
            view = [BOARD_HEADING]
            row_num = 1
            for row in self.grid:
                view.append(str(row_num).rjust(2) + " " + " ".join(
                    [location.opponent_view() for location in row]))
                row_num += 1
            view.append("")
        return view

    def verify_empty(self, coords):
        """Verify all coordinates are clear of ships"""
        result = True
        for coord in coords:
            row, col = coord_to_offset(coord)
            # assign location ship to this ship
            if self.grid[row][col].ship:
                result = False
        return result

    def place_ship(self, ship):
        """Place Ship on board"""
        for coord in ship.coords:
            row, col = coord_to_offset(coord)
            # assign location ship to this ship
            self.grid[row][col].ship = ship

    def guess(self, coord):
        """Apply guess to board"""
        row, col = coord_to_offset(coord)
        result = self.grid[row][col].guess()
        if result == MISS:
            response = "Guess [{}]: You Missed!\n".format(coord)
        elif result == HIT:
            response = "Guess [{}]: You Hit!!\n".format(coord)
        elif result == SUNK:
            response = "Guess [{}]: You SUNK my {}\n".format(
                coord, self.grid[row][col].ship.name)
        return response


class Location():
    """A single board location tracking state and ships

    Args:
        coord (str): coordiante name "A10"

    Attributes:
        ship (Ship): the Ship occupying this location
    """

    def __init__(self, coord):
        "docstring"
        self.coord = coord
        self.ship = None
        self.state = EMPTY

    def player_view(self):
        """Return board location state as seen by player"""
        if self.ship:
            return self.ship.get_state_player(self.coord)
        else:
            return self.state

    def opponent_view(self):
        """Return board location state as seen by oppoment"""
        if self.ship:
            return self.ship.get_state_opponent(self.coord)
        else:
            return self.state

    def guess(self):
        """process a guess at this location"""
        if not self.ship:
            # a miss
            self.state = MISS
        else:
            self.state = self.ship.hit(self.coord)
        return self.state


class Player():
    """Player representing name and placed ships

    Args:
        name (str): players name

    Attributes:
        board (Board): players game board
        ships (List[Ship]): list of player ships
        guesses (List[str]): list of coordinates guessed
    """

    def __init__(self, name):
        """Define player's name, board, ships, guesses"""
        self.name = name
        # create dict of player's ships
        self.board = Board()
        self.ships = []
        self.guesses = []

    def add_ship(self, ship):
        """add ship to current list of ships"""
        self.ships.append(ship)

    def ships_left(self):
        """Search for unsunken ships"""
        found = False
        for ship in self.ships:
            if not ship.sunk:
                found = True
        return found

    def deal_shoot_response(self, coord, response, opponent_board_view):
        raise Exception("Need to implement this function in base class!")

    def direction_anchor(self, ship_spec):
        hv = random.choice('HV')
        r = random.choice(list(range(1,11)))
        c = random.choice([chr(x+64) for x in range(1,11)])
        return hv, "{}{}".format(c,r)
    
    
class HumanPlayer(Player):
    """Human Player"""
    def __init__(self):
        # ask for players names
        name = ask_player_name("Human Player")
        Player.__init__(self, name)
        self.defense_mode = None

    def direction_anchor(self, ship_spec):
        ship_name = ship_spec[0]
        if not self.defense_mode:
            self.defense_mode = int(input("1. Automatic AI randomly place\n2. Manually place\n3. Use last coordinates\n"))

        if self.defense_mode == 1:
            return Player.direction_anchor(self, ship_spec)
        elif self.defense_mode == 2:
            cache_dict = get_cache('last_coord.p')
            direction = get_vert_or_horiz()
            anchor = get_anchor_coord()
            cache_dict[ship_name] = [direction, anchor]
            pickle.dump(cache_dict, open('last_coord.p', 'wb'))
            return direction, anchor
        elif self.defense_mode == 3:
            cache_dict = get_cache('last_coord.p')
            return cache_dict[ship_name]

    def guess(self):
        return get_guess(self)

    def deal_shoot_response(self, coord, response, opponent_board_view):
        return

class AIPlayer(Player):
    """AIPlayer 1.0"""
    def __init__(self, name="1"):
        Player.__init__(self, "AI-{}".format(name))
        self.potential = []
        self.opponent_board = [[EMPTY]*BOARD_SIZE]*BOARD_SIZE
        self.last_hit = None
        self.call_count = Counter()

    def guess(self):
        while True:
            if self.potential:
                guess = self.potential.pop(0)
            else:
                guess = offset_to_coord(*self.shoot_random())
            if validate_guess(guess, self):
                break
        self.opponent_empty.remove(coord_to_offset(guess))
        return guess

    def shoot_random_basic(self):
        empty_list = find_symbol_in_board(self.opponent_board, EMPTY)
#        while True:
#            r = random.choice(list(range(BOARD_SIZE)))
#            c = random.choice(list(range(BOARD_SIZE)))
#            if not self.opponent_board or self.opponent_board[r][c]==EMPTY:
#                return offset_to_coord(r,c)
        return random.choice(empty_list)

    def shoot_random(self):
        for i in range(50):
            ind = random.choice(list(range(BOARD_SIZE**2//2)))
            c = 2*(ind%5)
            r = ind//5
            if r%2:
                c += 1
            if not self.opponent_board or self.opponent_board[r][c]==EMPTY:
                self.call_count["diagonal"] += 1
                return (r,c)
        return self.shoot_random_basic()

    def deal_shoot_response(self, coord, response, opponent_board_view):
        x,y = coord_to_offset(coord)
        hit_order = [(0,-1), (-1,0), (0,1), (1,0)]

        if "Hit" in response:
            direction = None
            if self.last_hit:
                direction = (x-self.last_hit[0], y-self.last_hit[1])
                if direction in hit_order:
                    hit_order.remove(direction)
                    hit_order.append(direction)
                    print(direction, 'move ahead')

            for dx,dy in hit_order:
                new_coord = offset_to_coord(x+dx,y+dy)
                if new_coord not in self.guesses and new_coord not in self.potential and is_legal_coord(new_coord):
                    self.potential.insert(0, new_coord)

            if direction:
                axis = None
                if not direction[0]:
                    axis = str(x + 1)
                elif not direction[1]:
                    axis = chr(ord('A') + y)
                if axis:
                    for coord in self.potential:
                        if axis in coord:
                            self.potential.remove(coord)
                            self.potential.insert(0, coord)
                            print(coord, 'move ahead')

            self.last_hit = (x,y)

        elif "SUNK" in response:
            diff = compare_two_boards(opponent_board_view, self.opponent_board)
            for x,y in diff:
                for dx,dy in hit_order:
                    around = offset_to_coord(x+dx,y+dy)
                    if around in self.potential:
                        self.potential.remove(around)
                
            if not self.potential:
                self.last_hit = None

#            ship_name = response.split()[-1]
#            ship_size = list(filter(lambda x:x[0]==ship_name, SHIP_INFO))[0][1]

        self.opponent_board = opponent_board_view
        print(self.potential)

class AIPlayer_2_0(AIPlayer):
    """AIPlayer 2.0"""
    def __init__(self, name):
        AIPlayer.__init__(self, name)
        self.hit_record = []
        self.opponent_ships = [l for _,l in SHIP_INFO]
        self.opponent_empty = [(x,y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)]

    def deal_shoot_response(self, coord, response, opponent_board_view):
        hit_order = FOUR_DIRECTION

        if "Hit" in response:
            x,y = coord_to_offset(coord)
            self.hit_record.append((x,y))

        if "SUNK" in response:
            self.potential = []
            diff = compare_two_boards(opponent_board_view, self.opponent_board, SUNK)
            for offset in diff:
                if offset in self.hit_record:
                    self.hit_record.remove(offset)
            
            ship_size = len(diff)
            self.opponent_ships.pop(self.opponent_ships.index(ship_size))
            
            if self.hit_record:
                x,y = self.hit_record[-1]
            else:
                return
            
        if "Hit" in response or "SUNK" in response:
            direction = None
            if len(self.hit_record)>=2:
                last2 = self.hit_record[-2]
                direction = (x-last2[0], y-last2[1])
                if direction in hit_order:
                    hit_order.remove(direction)
                    hit_order.append(direction)
                    print(direction, 'moved')

            for dx,dy in hit_order:
                new_coord = offset_to_coord(x+dx,y+dy)
                if new_coord not in self.guesses and new_coord not in self.potential and is_legal_coord(new_coord):
                    self.potential.insert(0, new_coord)

            if direction:
                axis = None
                if not direction[0]:
                    axis = str(x + 1)
                elif not direction[1]:
                    axis = chr(ord('A') + y)
                if axis:
                    for coord in self.potential:
                        if axis in coord:
                            self.potential.remove(coord)
                            self.potential.insert(0, coord)
                            print(coord, 'moved')


        self.opponent_board = opponent_board_view
        print(self.potential)

    def shoot_random(self):
        min_ship_len = min(self.opponent_ships)
        if min_ship_len>2:
            print("Begin search min ship len")
            for _ in range(50):
                tag = True
                x,y = AIPlayer.shoot_random_basic(self)
                for dx,dy in FOUR_DIRECTION:
                    for i in range(1,min_ship_len+1):
                        r,c = x+i*dx, y+i*dy
                        if is_legal_coord(offset_to_coord(r,c)) and self.opponent_board[r][c]!=EMPTY:
                            tag = False
                            break
                            break
                if tag:
                    print(x,y)
                    return (x,y)
        
        return AIPlayer.shoot_random(self)

class AIPlayer_2_1(AIPlayer_2_0):
    def shoot_random(self):
        min_ship_len = max(self.opponent_ships)
        if min_ship_len>2:
            min_ship_len = 3
            print("Begin search min ship len")
            legal = []
            for x,y in self.opponent_empty:
                tag = True
                # x,y = AIPlayer.shoot_random_basic(self)
                for dx,dy in FOUR_DIRECTION:
                    for i in range(1,min_ship_len+1):
                        r,c = x+i*dx, y+i*dy
                        if is_legal_coord(offset_to_coord(r,c)) and self.opponent_board[r][c]!=EMPTY:
                            tag = False
                            break
                            # break
                if tag:
                    legal.append((x,y))
            
            if legal:
                x,y = random.choice(legal)            
                # print(legal)
                self.call_count['triagonal'] += 1
                return (x,y)
        
        return AIPlayer.shoot_random(self)

class Ship():
    """Ship with name, size, coordinates, and hits

    Args:
        name (str): Name of the ship
        size (int): ship size (in board squares)
        coords (list[str]): list of ship board coords
        direction (str): ship direction vertical or horizontal

    Attributes:
        hits (int): coords "hit" by guess
        sunk (bool): all coords "hit"
        char (str): display character "|" vertical "-" horizontal
    """

    def __init__(self, name, size, coords, direction):
        """Initialize Ship with name, size and coordinates
        """
        self.name = name
        self.size = size
        self.coords = coords
        self.direction = direction
        # List[str]: coordinates of ship that has been "hit"
        self.hits = []
        # Boolean: Has this ship sunk (all coords "hit")
        self.sunk = False
        # str: display character
        if direction.lower() == 'v':
            self.char = VERTICAL_SHIP
        else:
            self.char = HORIZONTAL_SHIP

    def get_state_player(self, coord):
        """Display SUNK, HIT, or ship charactera"""
        if self.sunk:
            return SUNK
        elif coord in self.hits:
            return HIT
        else:
            return self.char

    def get_state_opponent(self, coord):
        """Display SUNK, HIT, or EMPTY (do not give away position)"""
        if self.sunk:
            return SUNK
        elif coord in self.hits:
            return HIT
        else:
            return EMPTY

    def hit(self, coord):
        """Apply a hit at this coord"""
        if coord.upper() in self.coords:
            # capture Hit!
            self.hits.append(coord)
            # check if sunk
            if len(self.hits) == self.size:
                self.sunk = True
                self.char = SUNK
                return SUNK
            else:
                return HIT
