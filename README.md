# Hangman Project
This project is a Python-based implementation of the classic game Hangman. It includes a variety of features to enhance the gameplay experience.  

## Features

### Game Modes
The game supports two modes:
- **Normal Mode**: In this mode, the game behaves like a traditional game of Hangman. The player guesses one letter at a time, and if the letter is in the word, it is revealed in all its positions. If the letter is not in the word, it is added to a list of wrong guesses.
- **Impossible Mode**: This mode is still in development. It is designed to be a more challenging version of the game where the word to guess can change dynamically based on the player's guesses.


### Word Lists
The game supports custom word lists. Word lists can be specified using the -w command line argument followed by the path to the word list file. If no word list is specified, the game defaults to a built-in word list.

###Language Support
The game supports both English and German languages. The language can be specified using the -l command line argument followed by the language code (en for English, de for German).

###Visualizations
The project includes a visualization tool that displays a bar chart of letter frequencies in the remaining possible words. This tool is implemented using the Pygame library.

###Bot
The project includes a bot that can play the game of Hangman. The bot uses a statistical approach to guess the most likely next letter based on the current state of the game.

##Usage
To start the game, run the _game.py_ script with Python 3. Command line arguments can be used to customize the game:

- _-w <wordlist-path>_: Specify custom word list.
- _-l <language>_: Specify the language (_en_ for English, _de_ for German).
- _-m <mode>_: Specify the game mode (_normal_ or _impossible_).
For example, to start a game in normal mode with a custom word list, you would run:
'''
python3 game.py -m normal -w mywordlist.txt
'''
To use the bot, run the_ bot.py_ script with Python 3. The bot will prompt you for the current state of the game and then make a guess. The bot can be run in a loop to play an entire game.

For example, to start the bot, you would run:
'''
python3 bot.py
'''

##Development
This project is actively being developed. New features and improvements are being added regularly. Contributions are welcome!
