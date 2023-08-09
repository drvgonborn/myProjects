import hashlib
import hmac
import random
import secrets
import sys
from tabulate import tabulate
import argparse


class HmacGenerator:

    def __init__(self):
        self.__secret_key = None
        self.__hmac_value = None

    def __generate_random_secret_key(self):
        key = secrets.token_hex(32)
        self.__secret_key = key

    def get_secret_key(self):
        return self.__secret_key

    def get_hmac(self):
        return self.__hmac_value

    def generate(self, message):
        self.__generate_random_secret_key()
        self.__hmac_value = hmac.new(self.__secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
        return self


class GameResult:
    def __init__(self, moves):
        self.moves = moves

    def determine(self, user_move, computer_move):
        user_move_index = self.moves.index(user_move)
        computer_move_index = self.moves.index(computer_move)

        if user_move_index == computer_move_index:
            return "Draw"

        rearranged_words = self.moves[user_move_index:] + self.moves[:user_move_index]

        half_length = len(self.moves) // 2

        if half_length < rearranged_words.index(self.moves[computer_move_index]):
            return "Win"
        else:
            return "Lose"


class GameMenu:

    def __init__(self, moves):
        self.moves = moves
        self.help_table = ResultTableConstructor(moves).build_table()

    def display_menu(self, hmac_value):
        print(f"HMAC:\n{hmac_value}")

        for move_word in self.moves:
            print(f"{self.moves.index(move_word) + 1} - {move_word}")

        print("? - help")
        print("0 - exit")

    @staticmethod
    def display_result(user_move, computer_move, result, secret_key):
        print(f"Your move: {user_move}")
        print(f"Computer move: {computer_move}")
        print(f"Result: {result}!")
        print(f"HMAC key:\n{secret_key}\n")

    @staticmethod
    def make_user_choice():
        return input("Enter you move: ")

    @staticmethod
    def wait_back_to_menu():
        input("Press 'Enter' to return to the menu")

    @staticmethod
    def display_error(error_message):
        print(f"[ERROR] {error_message}")

    @staticmethod
    def exit_game():
        print("[Game Exit]")
        sys.exit()

    def display_help(self):
        print("[Table of possible outcomes]")
        print(self.help_table.get_table())


class ResultTableConstructor:

    def __init__(self, moves):
        self.moves = moves
        self.game_result = GameResult(self.moves)
        self.result_table = []

    def build_table(self):
        header = ["User \\ PC"] + self.moves
        self.result_table.append(header)

        for user_move in self.moves:
            row = [user_move]

            for computer_move in self.moves:
                result = self.game_result.determine(user_move, computer_move)
                row.append(result)
            self.result_table.append(row)

        return self

    def get_table(self):
        return tabulate(self.result_table, tablefmt="fancy_grid")


class Game:
    def __init__(self, moves):
        self.moves = moves
        self.game_result = GameResult(moves)
        self.hmac = HmacGenerator()
        self.menu = GameMenu(moves)

    def __make_computer_move(self):
        return random.choice(self.moves)

    def play_game(self):

        computer_move = self.__make_computer_move()

        hmac = self.hmac.generate(computer_move)

        hmac_value = hmac.get_hmac()

        self.menu.display_menu(hmac_value)

        user_move = None

        while not user_move:
            user_choice = self.menu.make_user_choice()

            if user_choice == "?":
                self.menu.display_help()
                continue
            try:
                user_choice_index = int(user_choice)

                if user_choice_index == 0:
                    self.menu.exit_game()

                if user_choice_index < 0:
                    self.menu.display_error("Only positive numbers!")
                    continue

                user_move_index = user_choice_index - 1

                user_move = self.moves[user_move_index]

            except ValueError:
                self.menu.display_error("Only number or '?'")
                continue

            except IndexError:
                self.menu.display_error("Select move only from the menu")
                continue

        game_result = self.game_result.determine(user_move, computer_move)

        self.menu.display_result(user_move, computer_move, game_result, hmac.get_secret_key())
        self.menu.wait_back_to_menu()

    def check_correct_input_moves(self):

        if len(self.moves) < 3:
            self.menu.display_error("The number of moves must be greater than 3!")
            self.menu.exit_game()

        if len(self.moves) % 2 == 0:
            self.menu.display_error("Enter an odd number of moves!")
            self.menu.exit_game()

        if len(self.moves) != len(set(self.moves)):
            self.menu.display_error("There should be no repetitive moves!")
            self.menu.exit_game()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game_moves", nargs="+", help="Number of moves separated by a space")
    args = parser.parse_args()

    game_moves = args.game_moves

    game = Game(game_moves)
    game.check_correct_input_moves()
    while True:
        try:
            game.play_game()
        except KeyboardInterrupt:
            break
