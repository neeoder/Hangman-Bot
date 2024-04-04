# Import libraries
import os
import math
import time
from rich import print
from rich.traceback import install
from multiprocessing import Pool, cpu_count


install()

# Define constants
ALPHABET: list[str] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                       'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'ä', 'ö', 'ü']
NUMBERS: list[str] = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
SPECIAL_CHARS: list[str] = ['!', '.', ',', '^', '°', '#', '&', '*', '/', '\\', '|', ':', ';',
                            '\'', '$', '%', '"', '<', '>', '~', '`', '(', ')', '-', '+', '?']


# Functions
def get_new_progress_word(d_progress_word: str,
                          d_letter: str,
                          d_word: str) -> str:
    """
    Returns the new progress word with the guessed letter inserted if the word contains it.

    :param d_progress_word: Current progress word.
    :param d_letter: Guessed letter.
    :param d_word: Word to guess
    :return:
    """

    new_progress_word: str = ''
    # Cycle through all letters in the solution word
    for idx in range(len(d_word)):
        # Update progress word
        if d_word[idx] == d_letter:
            new_progress_word += d_letter
            d_progress_word = d_progress_word[:idx] + d_letter + d_progress_word[idx + 1:]
        elif d_progress_word[idx] == '_':
            new_progress_word += '_'
        else:
            new_progress_word += d_progress_word[idx]

    return new_progress_word


def remove_non_valid(filepath: str,
                     filename: str) -> None:
    """
    Removes all non-valid words from the file containing all words.

    :param filepath: Path to the wordlist
    :param filename: name of the file
    :return: None
    """

    global SPECIAL_CHARS

    # Open wordlist file and creating a temp file
    with open(filepath + filename, 'r', encoding='utf-8') as source_file, \
            open(filepath + 'temp.txt', 'w', encoding='utf-8') as temp_file:

        # Cycle through all lines (words)
        for line in source_file:
            word: str = line.strip()

            # Check if word is valid
            if not any(char.isdigit() or char.isspace() or char in SPECIAL_CHARS or ord(char) > 127 for char in word):
                # Add the word to the temp file
                temp_file.write(line)

    # Replace the old wordlist by deleting the wordlist and renaming the temp file to the name of the wordlist file
    os.remove(filepath + filename)
    os.rename(filepath + 'temp.txt', filename)


def get_average(d_nums: list[int | float | list[int | float, ...]],
                idx: int | None = None) -> float:
    """
    Calculates the average of a numbers' list or a list of number lists.

    :param d_nums: The list of numbers or a list of number lists.
    :param idx: If d_nums is a list of lists, idx defines which item in each
                inner list should be used for the average.
    :return: The average of the specified numbers.
    """

    numbers = list(d_nums)  # Create a list from the generator
    total = 0
    for num in numbers:
        # Add number to the total
        if idx is None:
            total += num
        else:
            total += num[idx]

    # Calculate the average
    average = total / len(numbers)  # Use len() on the created list
    return average


def txt2list(filename: str) -> list[str]:
    """
    Turns a text file into a list by separating each line.

    :param filename: Name of the file.
    :return: A list with the individual lines as elements.
    """

    db: list[str] = []
    with open(filename, 'r', encoding='utf-8') as file:
        # Cycle through the lines
        for line in file:
            line = line.strip()
            db.append(line)

    return db


# Currently unused
def get_letter_averages(d_words: list[str]) -> list[list[str | float]]:
    """
    Returns a list of letters with their occurrences sorted by the occurrence.

    :param d_words: A list of words to fo through.
    :return:
    """

    global ALPHABET

    averages = []
    # Cycle through the alphabet
    for letter in ALPHABET:
        letter_counts: list[int] = []
        # Counts in how many words the current letter is found
        for word in d_words:
            word = word.lower()
            letter_counts.append(word.count(letter))

        # Calculate the average count and add it with the letter to averages
        letter_average = get_average(letter_counts)
        averages.append([letter, letter_average])

    # Sort the "averages" list by the second item, from the largest count downwards
    averages.sort(key=lambda x: x[1], reverse=True)
    return averages


def get_most_common_letters(d_words: list[str],
                            non_included_letters: list[str]) -> list[list[str, int]]:
    """
    Returns a list of letters with their frequency sorted by the frequency.

    :param d_words: A list of words to fo through.
    :param non_included_letters: A list of letters that shouldn't be included.
    :return:
    """

    global ALPHABET

    if non_included_letters is None:
        non_included_letters: list[str] = []

    appearances = []
    # Cycle through the alphabet
    for letter in ALPHABET:
        if letter in non_included_letters:
            continue

        letter_appearance: int = 0
        # Cycle through all words
        for word in d_words:
            if letter in word:
                letter_appearance += 1

        appearances.append([letter, letter_appearance])

    # Sort the "averages" list by the second item, from the largest count downwards
    appearances.sort(key=lambda x: x[1], reverse=True)
    return appearances


def get_possible_words(d_progress_word: str,
                       d_wrong_guessed: list[str],
                       wordlist_path: str) -> list[str]:
    """
    Returns a list of possible words left.

    :param d_progress_word: The word with the already guessed letters and underscores as not-guessed letters.
    :type d_progress_word: Str
    :param d_wrong_guessed: A list of all wrong guessed letters.
    :type d_wrong_guessed: List[str]
    :param wordlist_path: The path to the wordlist.
    :type wordlist_path: Str
    :return: A list of possible words left.
    :rtype: List[str]
    """

    words: list[str] = txt2list(wordlist_path)
    if d_wrong_guessed == ['']:
        d_wrong_guessed = []

    # Get already guessed letters
    progress_word_letters = list(set([char for char in d_progress_word if char != '_']))

    possible_words: list[str] = []
    # Cycle through the words:
    for word in words:
        word = word.lower()
        # Exclude all words that can't be the solution word
        if len(word) == len(d_progress_word):
            if not any(letter in word for letter in d_wrong_guessed):
                for idx in range(len(word)):
                    if d_progress_word[idx] == '_':
                        if word[idx] in progress_word_letters:
                            break
                    else:
                        if word[idx] != d_progress_word[idx]:
                            break
                else:
                    possible_words.append(word)

    return possible_words


def get_word_analysis_meth1(d_progress_word: str,
                            d_wrong_guessed: list[str],
                            wordlist_path: str) -> tuple[list[str], list[list[str, int]]]:
    """
    Returns a list of possible words left and a list of letters with their frequency sorted by the frequency.

    :rtype: Object
    :param d_progress_word: The word with the already guessed letters and underscores as not-guessed letters.
    :param d_wrong_guessed: A list of all wrong guessed letters.
    :param wordlist_path: The path to the wordlist.
    :return:
    """

    if d_wrong_guessed == ['']:
        d_wrong_guessed = []

    progress_word_letters = list(set([char for char in d_progress_word if char != '_']))
    possible_words = get_possible_words(d_progress_word, d_wrong_guessed, wordlist_path)

    # Get the most common letters
    most_common_letters = get_most_common_letters(possible_words, progress_word_letters + d_wrong_guessed)
    return possible_words, most_common_letters


def worker(args: tuple[str, list[str], list[str], str, list[str], str]) -> list[tuple[str, float | int]]:
    """
    Worker function for multiprocessing.

    :param args: Args for the worker function.
    :type args: Tuple[str, list[str], list[str], str, list[str], str]
    :return: A list of tuples with the letter and the bits of information.
    :rtype: List[tuple[str, float | int]]
    """

    word, progress_word_letters, d_wrong_guessed, d_progress_word, possible_words, wordlist_path = args
    information = []
    for letter in ALPHABET:
        if letter not in progress_word_letters + d_wrong_guessed:
            if letter in word:
                new_progress_word = get_new_progress_word(d_progress_word, letter, word)
                num_new_possible_words = len(
                    get_word_analysis_meth1(new_progress_word, d_wrong_guessed, wordlist_path)[0])
                bits_of_information = math.log2(1 / (num_new_possible_words / len(possible_words)))
            else:
                bits_of_information = 0

            information.append((letter, bits_of_information))

    return information


def get_word_analysis_meth2(d_progress_word: str,
                            d_wrong_guessed: list[str],
                            wordlist_path: str) -> tuple[list[str], list[list]]:
    """
    Returns a list of possible words left and a list of letters with their average information sorted by the
    information.

    :param d_progress_word:
    :type d_progress_word:
    :param d_wrong_guessed:
    :type d_wrong_guessed:
    :param wordlist_path:
    :type wordlist_path:
    :return:
    :rtype:
    """

    if d_wrong_guessed == ['']:
        d_wrong_guessed = []

    # Get already guessed letters
    progress_word_letters = list(set([char for char in d_progress_word if char != '_']))

    possible_words = get_possible_words(d_progress_word, d_wrong_guessed, wordlist_path)

    # Use multiprocessing to speed up the computations
    start_time = time.time()
    information = []
    with Pool(cpu_count()) as p:
        results = p.map(worker,
                        [(word, progress_word_letters, d_wrong_guessed, d_progress_word, possible_words, wordlist_path)
                         for word in possible_words])

    for worker_info in results:
        information.extend(worker_info)

    # Get the letter with the highest average information
    average_information = [[letter, get_average(list(info[1] for info in information if info[0] == letter))][0]
                           for letter in set(letter for letter, _ in information)]

    print(average_information)

    # Sort the "average_information" list by the second item, from the largest count downwards
    average_information = [x for x in average_information if isinstance(x, list)]
    average_information.sort(key=lambda x: x[1], reverse=True)

    print(f"Time: {time.time() - start_time} seconds.")

    return possible_words, average_information


if __name__ == '__main__':
    print('This script is not meant to be run directly.')
