import os; os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import sys
import json
import time
import pygame
from rich import print
from rich.table import Table
from rich.console import Console
from rich.traceback import install
from tools import get_word_analysis_meth1, txt2list, get_word_analysis_meth2


install()
cs = Console()


def check_keyboard() -> None:
    """
    Checks for keyboard events and quits the game if the escape key is pressed.

    :return:
    :rtype: None
    """

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()


def analyze_and_update(progress_word: str,
                       wrong_guessed: list[str],
                       word: str,
                       wordlist_path: str) -> tuple[str, str]:
    """
    Analyzes possible words and updates the progress word based on a guessed letter.

    :param wordlist_path: Path to the wordlist
    :param progress_word: The word with the already guessed letters and underscores as not-guessed letters.
    :param wrong_guessed: A list of all wrong guessed letters.
    :param word: The word to guess
    :return:
        - next_letter: The most frequent letter from possible remaining words.
        - updated_progress_word: The updated progress word with the guessed letter inserted if valid.
    """

    words = txt2list(wordlist_path)  # Read wordlist only once (outside the loop)

    # Get already guessed letters and lowercase words (pre-processing)
    guessed_letters = set(char for char in progress_word if char != '_')
    possible_words = [w.lower() for w in words if len(w) == len(progress_word)]

    # Filter possible words based on progress and wrong guesses
    filtered_words = [w for w in possible_words
                      if not any(letter in w for letter in wrong_guessed)
                      and all(w[i] == guessed_letters.pop() if p != '_' else True for i, p in enumerate(progress_word))]

    # Get the most common letter from the remaining words
    letter_counts = {}
    for w in filtered_words:
        for ch in w:
            letter_counts[ch] = letter_counts.get(ch, 0) + 1
    next_letter = max(letter_counts, key=letter_counts.get)

    # Update progress_word if the letter is present
    updated_progress_word = ""
    for i, char in enumerate(word):
        if char == next_letter:
            updated_progress_word += next_letter
        elif progress_word[i] == '_':
            updated_progress_word += '_'
        else:
            updated_progress_word += progress_word[i]

    return next_letter, updated_progress_word


# Classes
class Visualisation:
    """
    Visualizes data in a bar chart with pygame.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 500), pygame.RESIZABLE)
        pygame.display.set_caption('Occurrences')
        self.clock = pygame.time.Clock()
        self.colors = [
            (255, 87, 51),
            (52, 152, 219),
            (243, 156, 18),
            (46, 204, 113),
            (231, 76, 60),
            (155, 89, 182),
            (39, 174, 96),
            (230, 126, 34),
            (26, 188, 156),
            (211, 84, 0),
            (41, 128, 185),
            (224, 130, 131),
            (22, 160, 133),
            (241, 196, 15),
            (44, 62, 80),
            (192, 57, 43),
            (142, 68, 173),
            (46, 204, 113),
            (52, 152, 219),
            (231, 76, 60),
            (243, 156, 18),
            (26, 188, 156),
            (241, 196, 15),
            (52, 152, 219),
            (39, 174, 96),
            (192, 57, 43),
            (230, 126, 34),
            (44, 62, 80),
            (142, 68, 173)
        ]

    def draw_bar_chart(self,
                       labels: list[str],
                       values: list[int],
                       gap_size: int | float = 20) -> None:
        """
        Draws a bar chart with the given labels and values.

        :param labels:
        :type labels: List[str]
        :param values:
        :type values: List[int]
        :param gap_size: Gap size between the bars
        :type gap_size: int | float
        :return:
        :rtype: None
        """

        bar_width: float = (self.screen.get_width() - (gap_size * 2) - ((len(labels) - 1) * gap_size)) / (len(labels))
        font = pygame.font.SysFont('arial', int(bar_width * 0.9))
        value_limit: float = max(values) * 1.2
        x: int = gap_size
        for i in range(len(labels)):
            y = self.screen.get_height() * (values[i] / value_limit)
            pygame.draw.rect(self.screen, self.colors[i],
                             [x, self.screen.get_height() - y, bar_width, y])
            text = font.render(labels[i], True, 'white')
            self.screen.blit(text, (x + ((bar_width - text.get_width()) / 2),
                                    self.screen.get_height() - y - (text.get_height() * 0.9)))
            x += bar_width + gap_size

    def run(self, searching_intervall: int | float = 3) -> None:
        """
        Main loop for the visualization.

        :param searching_intervall: Time intervall to search for new data
        :type searching_intervall: int | float
        :return:
        :rtype: None
        """

        labels = []
        values = []
        while True:
            check_keyboard()
            self.screen.fill('black')

            if int(time.time()) % searching_intervall == 0:
                try:
                    with open('live_data.json', 'r') as file:
                        json_obj = json.load(file)

                    labels = list(json_obj.keys())
                    values = list(json_obj.values())

                except json.JSONDecodeError:
                    labels = []
                    values = []

            if 0 in values:
                first_idx = values.index(0)
                values = values[:first_idx]
                labels = labels[:first_idx]

            if not labels:
                font = pygame.font.Font('./Neoteric-32A8.ttf',
                                        int((self.screen.get_width() / 18) + 100))
                text = font.render('No data available.', True, 'white')
                self.screen.blit(text, ((self.screen.get_width() - text.get_width()) / 2,
                                        (self.screen.get_height() - text.get_height()) / 2))
            else:
                self.draw_bar_chart(labels, values)

            pygame.display.flip()
            self.clock.tick()


class Bot:
    """
    A bot that can guess words based on the progress and wrong guessed letters.
    """

    def __init__(self, wordlist_path: str) -> None:
        self.wordlist_path = wordlist_path

    def guess(self, d_progress_word: str,
              wrong_guessed: list[str]) -> tuple[list[str], list[list[str, int]]]:
        """
        Prints out the number of possible words left, and the most probable letter with its probability.

        :param d_progress_word:
        :param wrong_guessed:
        :return:
        """

        word_analysis = get_word_analysis_meth1(d_progress_word, wrong_guessed, self.wordlist_path)
        print(f'Possible words: {len(word_analysis[0])}')
        if len(word_analysis[0]) <= 10:
            print(word_analysis[0])

        return word_analysis

    def loop_ask(self, method: int = 1) -> None:
        """
        Asks in a loop for a progress word and wrong guessed letters and prints out some information.

        :return:
        """

        while True:
            progress_word: str = cs.input('Progress word: ')
            if progress_word == '':
                stop = cs.input('Do you want to quit the game? ').lower()
                if stop == 'y' or stop == 'yes':
                    open('live_data.json', 'w', encoding='utf-8').close()
                    quit()

            wrong_guessed: list[str] = cs.input('Wrong guessed letters: ').split(',')
            if method == 1:
                word_analysis = get_word_analysis_meth1(progress_word, wrong_guessed, self.wordlist_path)
            else:
                word_analysis = get_word_analysis_meth2(progress_word, wrong_guessed, self.wordlist_path)

            if len(word_analysis[0]) <= 10:
                print(word_analysis[0])

            print(f'{len(word_analysis[0])} possible words left.')
            if method == 1:
                letter_freq_table = Table(title='[magenta]Letter frequencies')
                letter_freq_table.add_column('Letter', justify='center', style='cyan')
                letter_freq_table.add_column('Occurrence', justify='center', style='green')
                letter_freq_table.add_column('Probability', justify='center', style='magenta')

                for letter, occ in word_analysis[1][:5]:
                    letter_freq_table.add_row(letter, str(occ), f'{occ / len(word_analysis[0]) * 100:.2f}%')

                print()
                cs.print(letter_freq_table)
            else:
                bit_table = Table(title='[magenta]Information in bits')
                bit_table.add_column('Letter', justify='center', style='cyan')
                bit_table.add_column('Information', justify='center', style='green')

                for letter, info in word_analysis[1][:5]:
                    bit_table.add_row(letter, str(info))

                print()
                cs.print(bit_table)

            data_dict = {data[0]: data[1] for data in word_analysis[1]}
            json_obj = json.dumps(data_dict, indent=4, ensure_ascii=False)
            with open('live_data.json', 'w', encoding='utf-8') as file:
                file.write(json_obj)

    def method_comparison(self) -> None:
        # Animation for the bar chart
        # Still in progress
        pass

    # In progress
    def test_bot(self):
        """
        Test the bot by running it on every word in the wordlist.
        Takes a lot of time at the moment.

        :return:
        :rtype: None
        """
        with open(self.wordlist_path, 'r', encoding='utf-8') as file:
            words = [word.lower().strip() for word in file.readlines()]

        start = time.time()
        total_words = len(words)

        for i, word in enumerate(words):
            progress_word = '_' * len(word)
            wrong_guessed = []
            while True:
                next_letter, progress_word = analyze_and_update(progress_word, wrong_guessed, word, self.wordlist_path)
                print(f'Word: {word} | Progress: {progress_word} | Next letter: {next_letter}')

                if progress_word == word:
                    break

            elapsed_time = time.time() - start
            remaining_time = elapsed_time / (i + 1) * (total_words - i - 1)
            print(f"Progress: {(i + 1) / total_words:.2%} | Time elapsed: {elapsed_time:.2f} | Time left:"
                  f"{remaining_time:.2f}")

            i += 1


def start_dialog(args: list[str]) -> None:
    """
    Starts a dialog to choose the program to run.

    :param args: Command line arguments
    :type args: list[str]
    :return:
    :rtype: None
    """

    if cs.color_system == 'standard' or cs.color_system is None:
        print('[bold italic red]Your terminal may not support full rich features.')
        print('[italic]Please consider using a terminal that supports "True Color".')

    bot_method = 1
    programm = None
    lang = None
    if args:
        if 'b' in args:
            programm = 'bot'
        elif 'v' in args:
            programm = 'visualization'
        elif 't' in args:
            programm = 'testing'
        elif 'b2' in args:
            programm = 'bot'
            bot_method = 2

            print('[italic red][bold]Warning:[/bold] Method 2 is still in progress.'
                  'It could take a while to calculate the next letter and even showing wrong results.')

        if 'en' in args:
            lang = 'en'
        elif 'ge' in args or 'de' in args:
            lang = 'de'
        elif 'h' in args or '-h' in args or '--help' in args:
            print('Usage: python bot.py [b, v, t, b2] [en, ge]')
            print('[cyan]b:[/cyan] Bot')
            print('[cyan]v:[/cyan] Visualization')
            print('[cyan]t:[/cyan] Testing')
            print('[cyan]b2:[/cyan] Bot with method 2 [bold italic red](in progress)')
            quit()

    if programm is None:
        programm = cs.input('[cyan]Bot[/cyan] / [cyan]Visualization[/cyan] / [cyan]Testing[/cyan]?: ').lower()
    if lang is None:
        lang = cs.input('[cyan]Language:[/cyan] (german, english) ').lower()

    if lang == 'en':
        wordlist = 'Wordlists/wordlist_english.txt'
    elif lang == 'ge' or lang == 'de':
        wordlist = 'Wordlists/german.txt'
    else:
        print('[italic red]Language not supported.')
        quit()

    if 'b' in programm:
        bot = Bot(wordlist)
        bot.loop_ask(bot_method)
    elif 'v' in programm:
        visualization = Visualisation()
        visualization.run(searching_intervall=1)
    elif 't' in programm:
        bot = Bot(wordlist)
        bot.test_bot()
    else:
        print('[italic red]Invalid program.')
        quit()


if __name__ == '__main__':
    start_dialog(sys.argv)
