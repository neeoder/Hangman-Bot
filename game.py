# Import libraries
import os
import sys
import random
from rich import print
from rich.console import Console
from rich.progress import Progress
from rich.traceback import install

from tools import txt2list, get_new_progress_word, get_word_analysis_meth1


install()
cs = Console()


# Classes
class Modes:
    """
    Enum class for the game modes
    """
    NORMAL = 'normal'
    IMPOSSIBLE = 'impossible'  # In development


class Game:
    """
    Main game class
    """
    def __init__(self, mode: str,
                 wordlist_path: str,
                 graphics: bool = True) -> None:
        self.mode = mode
        self.words = txt2list(wordlist_path)

        self.graphics = graphics
        self.hangman_ascii = [
            ['----------      '],
            ['     |          ',
             '     |          ',
             '     |          ',
             '     |          ',
             '----------      '],
            ['     _________  ',
             '     |          ',
             '     |          ',
             '     |          ',
             '     |          ',
             '----------      '],
            ['     _________  ',
             '     | /        ',
             '     |/         ',
             '     |          ',
             '     |          ',
             '----------      '],
            ['     _________  ',
             '     | /     |  ',
             '     |/         ',
             '     |          ',
             '     |          ',
             '----------      '],
            ['     _________  ',
             '     | /     |  ',
             '     |/      O  ',
             '     |          ',
             '     |          ',
             '----------      '],
            ['     _________  ',
             '     | /     |  ',
             '     |/      O  ',
             '     |       |  ',
             '     |          ',
             '----------      '],
            ['     _________  ',
             '     | /     |  ',
             '     |/      O  ',
             '     |      /|  ',
             '     |          ',
             '----------      '],
            ['     _________  ',
             '     | /     |  ',
             '     |/      O  ',
             '     |      /|\\',
             '     |          ',
             '----------      '],
            ['     _________  ',
             '     | /     |  ',
             '     |/      O  ',
             '     |      /|\\',
             '     |      /   ',
             '----------      '],
            ['     _________  ',
             '     | /     |  ',
             '     |/      O  ',
             '     |      /|\\',
             '     |      / \\',
             '----------      ']
        ]

    def print_hangman(self, wrong_guessed: list,
                      word: str) -> bool | None:
        """
        Print the hangman ASCII art

        :param word: The word to guess
        :type word: str
        :param wrong_guessed: List of wrong guessed letters
        :return: bool | None
        """

        if self.graphics:
            for line in self.hangman_ascii[len(wrong_guessed) - 1]:
                print(line)

            if len(wrong_guessed) > len(self.hangman_ascii) - 1:
                print('[bright_red]You lost!')
                print(f'The word was [bright_green]{word}[/bright_green].')
                stop = input('Another game? ')
                if stop == 'y' or stop == 'yes':
                    return True
                else:
                    quit()

    def start(self) -> None:
        """
        Main game loop

        :return: None
        """

        word_lengths = {}
        if self.mode == Modes.IMPOSSIBLE:
            word_lengths = {}
            for word in self.words:
                if len(word) not in word_lengths:
                    word_lengths[len(word)] = 1
                else:
                    word_lengths[len(word)] += 1

            # Sort the dictionary by value
            word_lengths = dict(sorted(word_lengths.items(), key=lambda item: item[1], reverse=True))

        while True:
            if self.mode == Modes.IMPOSSIBLE:
                word = '_' * list(word_lengths.keys())[0]
            else:
                word: str = random.choice(self.words).lower()
            progress_word = '_' * len(word)
            wrong_guessed = []
            while True:
                print(progress_word)

                letter = input('Letter: ')
                if letter == '':
                    stop = input('Do you want to quit the game? ').lower()
                    if stop == 'yes' or stop == 'y':
                        print(f'The word was [bright_green]{word}[/bright_green].')
                        quit()

                if self.mode == Modes.NORMAL:
                    if get_new_progress_word(progress_word, letter, word) == progress_word:
                        wrong_guessed.append(letter)

                        if self.print_hangman(wrong_guessed, word):
                            break

                    progress_word = get_new_progress_word(progress_word, letter, word)
                else:
                    words_with_letter = 0
                    for word in self.words:
                        if letter in word:
                            words_with_letter += 1

                    word_without_letter = len(self.words) - words_with_letter

                    if words_with_letter > word_without_letter:
                        possible_words = {}
                        with Progress() as progress:
                            task = progress.add_task('[bright_magenta]Calculating...', total=len(self.words))
                            for word in self.words:
                                if letter in word:
                                    words_left = len(get_word_analysis_meth1(progress_word,
                                                                             wrong_guessed,
                                                                             'Wordlists/german.txt')[0])
                                    possible_words[word] = words_left

                                progress.update(task, advance=1)

                        possible_words = dict(sorted(possible_words.items(), key=lambda item: item[1], reverse=True))
                        print(possible_words)
                    else:
                        wrong_guessed.append(letter)

                        if self.print_hangman(wrong_guessed, word):
                            break

                if progress_word == word:
                    print(progress_word)
                    print('[bright_green]You won!')
                    stop = input('Another game? ')
                    if stop == 'y' or stop == 'yes':
                        break
                    else:
                        quit()


def start_dialog(args: list[str]) -> None:
    """
    Start dialog for the game

    :return: None
    """

    if cs.color_system == 'standard' or cs.color_system is None:
        print('[bold italic red]Your terminal may not support full rich features.')
        print('[italic]Please consider using a terminal that supports "True Color".')

    game_mode = None
    wordlist = None
    lang = None
    if len(args) > 1:
        if '-w' in args:
            wordlist = args[args.index('-w') + 1]
            if not os.path.exists(wordlist):
                print('[italic red]Wordlist not found.')
                quit()
        else:
            if '-l' in args:
                lang = args[args.index('-l') + 1]

        if '-m' in args:
            game_mode = args[args.index('-m') + 1]

        if '-h' in args:
            print('Usage: python3 game.py [-w wordlist-path] [-l language] [-m mode]')
            print('[bright_green]Options:')
            print('[cyan]-w:[/cyan] Wordlist path')
            print('[cyan]-l:[/cyan] Language (german/english)')
            print('[cyan]-m:[/cyan] Game mode (normal/impossible)')
            quit()

    if game_mode is None:
        game_mode = cs.input('[cyan]Game mode:[/cyan] (normal/impossible) ')

    if lang is None and wordlist is None:
        lang = cs.input('[cyan]Language:[/cyan] (german/english) ')

    if game_mode == 'normal' or game_mode == '':
        game_mode = Modes.NORMAL
    elif game_mode == 'impossible':
        game_mode = Modes.IMPOSSIBLE

        print('[italic red][bold]Warning: [/bold]This mode is still in development. '
              'It can currently take a long time to calculate.')
    else:
        print('[italic red]Mode not supported.')
        quit()

    if lang == 'german' or lang == 'de':
        wordlist = 'Wordlists/german.txt'
    elif lang == 'english' or lang == 'en' or lang == '':
        wordlist = 'Wordlists/wordlist_english.txt'
    else:
        print('[italic red]Language not supported.')
        quit()

    game = Game(game_mode, wordlist)

    game.start()


if __name__ == '__main__':
    start_dialog(sys.argv)
