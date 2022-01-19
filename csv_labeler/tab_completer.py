"""
Based on https://gist.github.com/iamatypeofwalrus/5637895
--> The only changes made are to fix warnings by flake8, pylint, and so on.

Added fast_autocomplete for better detection of similar words

TODO: Add hint to readme to explain how to fine tune suggestions (max_cost,
size should be longer than list of words)
"""

import glob
import os
import readline
import configparser
from fast_autocomplete import AutoComplete


class TabCompleter:
    """
    A tab completer that can either complete from
    the filesystem or from a list.

    Partially taken from:
    http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input
    """

    def __init__(self) -> None:
        self.list_completer = None

    @staticmethod
    def path_completer(text, state):

        """
        This is the tab completer for systems paths.
        Only tested on *nix systems
        """
        # replace ~ with the user's home dir. See https://docs.python.org/2/library/os.path.html
        if "~" in text:
            text = os.path.expanduser("~")

        # autocomplete directories with having a trailing slash
        if os.path.isdir(text):
            text += "/"

        return list(glob.glob(text + "*"))[state]

    def create_list_completer(self, word_list):
        """
        This is a closure that creates a method that autocompletes from
        the given list.

        Since the autocomplete function can't be given a list to complete from
        a closure is used to create the listCompleter function with a list to complete
        from.
        """
        config = configparser.ConfigParser()
        config.read("config.ini")

        def list_completer(text, state):
            line = readline.get_line_buffer()

            if not line:
                return [c + " " for c in word_list][state]

            words = {i: {} for i in word_list}
            autocomplete = AutoComplete(words=words)
            result = autocomplete.search(
                word=text,
                max_cost=int(config["fast_autocomplete"]["max_cost"]),
                size=int(config["fast_autocomplete"]["size"]),
            )
            return [c[0] for c in result][state]

        self.list_completer = list_completer
