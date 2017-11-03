#!/usr/bin/python3
"""Implements the classic Battleship board game.

Project 2 - Treehouse Techdegree - Python Web Development
"""
from constants import SHIP_INFO
from models import *
from utils import (clear_screen, is_legal_coord, print_legend, show_banner)
# import matplotlib.pyplot as plt

__author__ = "Chris Freeman"
__copyright__ = "Copyright 2016, Chris Freeman"
__license__ = "MIT"

# ignore pylint warning about using 'input'
# pylint: disable=bad-builtin


def print_board(player_name, player_view):
    """Print a player board

    Args:
        player_name (str): name of current player
        player_view (List[str]): list of strings representing board view
    """

    # board titles
    print("   {:_^22}\n".format(player_name + "'s board:"))
    # stitch together board views for display
    for player_line in player_view:
        print("   {:22}".format(player_line))
    print_legend()


def print_all_boards(opp_name, player_name, opp_view, player_view):
    """Print both player boards

    Args:
        opp_name (str): name of opponent
        player_name (str): name of current player
        opp_view (List[str]): list of strings representing board view
        player_view (List[str]): list of strings representing board view
    """
    # boards titles
    print("   {:_^22}        {:_^22}\n".format(
        opp_name + "'s board:", player_name + "'s board:"))
    # stitch together board views for display
    for opp_line, player_line in zip(opp_view, player_view):
        print("   {:22}        {:22}".format(opp_line, player_line))
    print_legend()


def gen_ship_coords(anchor, size, direction):
    """Generate ship board coordinate based on anchor location and size

    The ship coordinates start at the anchor position and run Down for
    vertical direction and run Right for horizontal direction.

    Verify ship fits on board.

    Args:
        anchor (str): two character board coordinate "A1"
        size (int): size of ship in board spaces
        orientation (str): is ship Horizontal or Vertical

    Returns:
        List[str]: list of board coordinates, if valid. Empty list otherwise.
    """
    ship_col = ord(anchor[0].upper())
    ship_row = int(anchor[1:])
    if direction[0].lower() == 'v':
        # ship runs vertically DOWN from anchor
        coords = [chr(ship_col) + str(row)
                  for row in range(ship_row, ship_row + size)]
    else:
        # ship runs horizontally RIGHT from anchor
        coords = [chr(col) + str(ship_row)
                  for col in range(ship_col, ship_col + size)]
    # check if ship bow and stern are on board
    if is_legal_coord(coords[0]) and is_legal_coord(coords[-1]):
        # coords confirmed
        return coords
    else:
        # bad ship coords
        print("Error: not all coords on board: ", coords)
        return []

def define_fleet(player):
    """Define player's ships and place on board"""
    # place each ship
    for ship_spec in SHIP_INFO:
        ship_name = ship_spec[0]
        ship_size = ship_spec[1]
        # display top banner
        clear_screen()
        show_banner()
        print("Placing Ships for {}:\n".format(player.name))
        # display board
        if type(player)==HumanPlayer:
            print_board(player.name, player.board.get_player_view())
        # display ship info
        print("Placing {} (size:{})\n".format(ship_name, ship_size))

        # get ship placement details
        while True:
            # 1. ask if vertical or horizontal
            # direction = get_vert_or_horiz()
            direction, anchor = player.direction_anchor(ship_spec)
            # 2. ask for top or left starting coordinate
            # anchor = get_anchor_coord()
            # 3. validate input (explain why input rejected)
            coords = gen_ship_coords(anchor, ship_size, direction)
            # 4. validate ship placement
            if not coords:
                print("Error: ship coordinates not all on the board\n")
                continue
            if not player.board.verify_empty(coords):
                print("Error: ship coordinates collide with other ships. "
                      "Try again\n")
                continue
            # input valid; last while loop
            break
        # create ship from input
        ship = Ship(ship_name, ship_size, coords, direction)
        # add ship to players list
        player.add_ship(ship)
        # place ship on game board
        player.board.place_ship(ship)
        # 5. redraw screen for next ship (at top of loop)
    # display top banner
    # clear_screen()
    # show_banner()
    # display board
    print("Placing Ships for {}:\n".format(player.name))
    if type(player)==HumanPlayer:
        print_board(player.name, player.board.get_player_view())

    print("All ships placed for {}. Hit ENTER to continue...."
          "".format(player.name))
    # clear_screen()


def take_turn(player, opponent, play_mode = 1):
    """Take a turn"""

    # input("It's {}'s turn. Hit ENTER to continue....".format(player.name))
    print("It's {}'s turn:\n".format(player.name))
    # print boards for guessing
    player_view = player.board.get_player_view()
    if play_mode == 1 or (play_mode == 2 and type(player) == HumanPlayer):
        opp_view = opponent.board.get_opponent_view()

        # stitch together board views for display
        print_all_boards(opponent.name, player.name, opp_view, player_view)

    # coord = get_guess(player)
    coord = player.guess()

    # remember guessed coordinates
    player.guesses.append(coord)
    
    # process guess
    response = opponent.board.guess(coord)
    player.deal_shoot_response(coord, response, opponent.board.get_opponent_view(as_list=True))

    # update board and display response
    # print("It's {}'s turn:\n".format(player.name))
    # print both boards
    if play_mode == 1 or (play_mode == 2 and type(player) == HumanPlayer) or (play_mode in [3] and player.name=='AI-1'):
        opp_view = opponent.board.get_opponent_view()
        print_all_boards(opponent.name, player.name, opp_view, player_view)
    
    print(response)
    # input("Hit ENTER to clear screen and end your turn....")

def play_a_game(player1, player2, play_mode):
#    seed = 11
#    random.seed(seed)

    name1 = player1.name
    name2 = player2.name
    print("\nNext you'll each add your ships. {} first. (No peeking {})\n\n"
          "Hit ENTER to continue....".format(name1, name2))

    # placing ships
    clear_screen()
    # defind player1's fleet and add to board
    define_fleet(player1)
    show_banner()
    print("Time to add {}'s ships. Hit ENTER to continue....".format(name2))
    # define player2's fleet and add to board
    define_fleet(player2)

    # commense game play
    show_banner()
    print("Game Time! {} goes first. Hit ENTER to continue....".format(name1))
    game_continue = True
    turn_count = 0
    while game_continue:
        turn_count += 1
        take_turn(player1, player2, play_mode)
        if not player2.ships_left():
            show_banner()
            winner = player1
            game_continue = False
            continue
        take_turn(player2, player1, play_mode)
        if not player1.ships_left():
            show_banner()
            winner = player2
            game_continue = False

    # Display final boards
    print_all_boards(player1.name, player2.name,
                     player1.board.get_player_view(),
                     player2.board.get_player_view())
    fall_behind = sum([row.count(VERTICAL_SHIP)+row.count(HORIZONTAL_SHIP) for row in player1.board.get_player_view(as_list=True)])
    print("{} WINS!!!\n"
        "{} turns in total\n"
        "Losser falls behind {} grids. \n".format(winner.name, turn_count, fall_behind))
    if type(player1) != HumanPlayer:
        print("self.call_count={}".format(player1.call_count))
    # print("Random seed: {}".format(seed))
    # input("Hit ENTER to see final boards....\n")
    return turn_count, winner

def main():
    """Run the console-based python game"""
    # start with a clear screen
    clear_screen()
    show_banner()


    play_mode = int(input("Choose play mode:\n 1. Human vs Human\n 2. Human vs AI\n 3. AI vs AI\n 4. Test AI\n"))
    # initiate player instances
    if play_mode==1:
        player1 = HumanPlayer()
        player2 = HumanPlayer()
    elif play_mode==2:
        player1 = HumanPlayer()
        player2 = AIPlayer_2_1(1)
    elif play_mode==3:
        player1 = AIPlayer_2_1(1)
        player2 = AIPlayer_2_1(2)
    
    if play_mode<=3:
        play_a_game(player1, player2, play_mode)
        
    elif play_mode==4:
        turns = []
        winner_list = []
        N = int(input("Test number?\n"))
        for i in range(N):
            player1 = AIPlayer_2_1(1)
            player2 = AIPlayer_2_0(2)
            turn, winner = play_a_game(player1, player2, play_mode)
            turns.append(turn)
            winner_list.append(winner.name)
        print("Average turns: {}".format(sum(turns)/len(turns)))
        player1_win_num = winner_list.count(player1.name)
        print("{} vs {} result {}:{}".format(player1.name, player2.name, 
              player1_win_num, N-player1_win_num))

if __name__ == '__main__':
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n quitting....")
