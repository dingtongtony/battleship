#!/usr/bin/python3
"""Utility functions used across Battleship projeect.

Project 2 - Treehouse Techdegree - Python Web Development
"""
from constants import (BANNER, BOARD_SIZE, VERTICAL_SHIP,
                       HORIZONTAL_SHIP, EMPTY, MISS, HIT, SUNK)
import pickle

__author__ = "Chris Freeman"
__copyright__ = "Copyright 2016, Chris Freeman"
__license__ = "MIT"


def clear_screen():
    """Clear screen using VT Esc sequence"""
    print("\033c", end="")


def show_banner():
    """print game banner"""
    print(BANNER)


def print_legend():
    """Print legend of board symbols"""
    print("Legend: Ships {} or {}   Empty {}   Miss {}   Hit {}   Sunk {}\n"
          "".format(VERTICAL_SHIP, HORIZONTAL_SHIP, EMPTY, MISS, HIT, SUNK))


def offset_to_coord(row, col):
    """Generate board coordinates from a row and column number

    Args:
        row (int): row offset
        col (int): column offset

    Returns:
        str: String coordinate in the form "A10"
    """
    return chr(ord('A') + col) + str(row + 1)


def coord_to_offset(coord):
    """Generate a row and column number from a board coordinate

    Args:
        str: String coordinate in the form "A10"

    Returns: tuple (row, column)
        row (int): 0-based row offset
        col (int): 0-based column offset
    """
    col = ord(coord[0]) - ord('A')
    row = int(coord[1:]) - 1
    return (row, col)


def is_legal_coord(coord, board_size=BOARD_SIZE):
    """Verify coordinate is on the game board

    Args:
        coord (str): board coordinate "<letter><number>"
        board_size (int): size of board. Defualt

    Returns:
        bool: True if coordinate is legal and on the board, False otherwise.
    """
    if len(coord) < 2:
        # coord  is too short to be legal
        return False
    # covert or return False
    try:
        ship_col = ord(coord[0].upper())
        ship_row = int(coord[1:])
    except (TypeError, ValueError):
        return False
    # check if coord is on board
    return (ship_col >= ord('A') and ship_col <= ord('A') + board_size - 1 and
            ship_row >= 1 and ship_row <= board_size)

def find_symbol_in_board(board, symbol):
    find = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c]==symbol:
                find.append((r,c))
    return find

def compare_two_boards(new, old, symbol=SUNK):
    if not old:
        return []
    diff = []
    for r,row in enumerate(new):
        for c, x in enumerate(row):
            if x==SUNK and old[r][c]!=SUNK:
                diff.append((r,c))
    return diff

def get_vert_or_horiz():
    """Ask user for vertical or horizontal direction"""
    while True:
        response = input(
            "Does this ship run [V]ertical, or [H]orizontal: ").strip()
        if not response:
            print("Error: Blank not allowed. Please Enter 'v' or 'h'!")
            continue
        direction = response[0].lower()
        if direction == 'v' or direction == 'h':
            return direction
        else:
            print("Error: Response {} not valid. Please Enter 'v' or 'h'!"
                  "".format(response))

def get_anchor_coord():
    """Ask user for ship anchor coordinates"""
    while True:
        response = input("What is the upper-most or left-most ship postion "
                         "(for example D4): ").strip()
        anchor = response.upper()
        if is_legal_coord(anchor):
            return anchor
        else:
            print("Coordnate {} is not on the board. Please enter Letter "
                  "and Number as one word.".format(response))

def ask_player_name(moniker="player"):
    """Ask for player's name"""
    name = None
    # get player name
    while not name:
        name = input("Enter the name of {}: ".format(moniker)).strip()
        if not name:
            print("Empty name not allowed")
    print("Thanks {}!".format(name))
    return name

def get_guess(player):
    """Ask user for guess"""
    while True:
        response = input("Enter {}'s guess (for example D4): ".format(player.name)).strip()
        guess = response.upper()
        if validate_guess(guess, player):
            break
    return guess
        # guess = response.upper()
        # if guess in player.guesses:
        #     print("Coordnate {} already guessed. Try Again."
        #           "".format(response))
        #     continue
        # if is_legal_coord(guess):
        #     return guess
        # else:
        #     print("Coordnate {} is not on the board. Please enter Letter "
        #           "and Number as one word.".format(response))

def validate_guess(guess, player):
    if guess in player.guesses:
        print("Coordnate {} already guessed. Try Again."
              "".format(guess))
        return False
    if not is_legal_coord(guess):
        print("Coordnate {} is not on the board. Please enter Letter "
              "and Number as one word.".format(guess))
        return False
    return True

def get_cache(filename):
    try:
        with open(filename, 'rb') as cache_file:
            return pickle.load(cache_file)
    except:
        return dict()