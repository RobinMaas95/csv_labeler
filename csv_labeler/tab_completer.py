""" 
Based on https://gist.github.com/iamatypeofwalrus/5637895
Added fast_autocomplete for better detection of similar words

TODO: Clean up code
TODO: Callable from main (Path input and category selection)
TODO: Add hint to readme to explain how to fine tune suggestions (max_cost,
size should be longer than list of words)
"""

import os
import sys
import readline
import glob
from fast_autocomplete import AutoComplete


class tabCompleter(object):
    """
    A tab completer that can either complete from
    the filesystem or from a list.

    Partially taken from:
    http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input
    """

    def pathCompleter(self, text, state):
        """
        This is the tab completer for systems paths.
        Only tested on *nix systems
        """
        line = readline.get_line_buffer().split()

        # replace ~ with the user's home dir. See https://docs.python.org/2/library/os.path.html
        if "~" in text:
            text = os.path.expanduser("~")

        # autocomplete directories with having a trailing slash
        if os.path.isdir(text):
            text += "/"

        return [x for x in glob.glob(text + "*")][state]

    def createListCompleter(self, ll):
        """
        This is a closure that creates a method that autocompletes from
        the given list.

        Since the autocomplete function can't be given a list to complete from
        a closure is used to create the listCompleter function with a list to complete
        from.
        """

        def listCompleter(text, state):
            line = readline.get_line_buffer()

            if not line:
                return [c + " " for c in ll][state]

            else:
                words = {i: {} for i in ll}
                autocomplete = AutoComplete(words=words)
                res = autocomplete.search(word=text, max_cost=3, size=20)
                return [c[0] + " " for c in res][state]

        self.listCompleter = listCompleter


if __name__ == "__main__":
    t = tabCompleter()
    t.createListCompleter(
        [
            "Abos",
            "Essen bestellen",
            "Fortbildung",
            "Freizeit",
            "Geld abheben",
            "Geschenke",
            "Gesundheit",
            "Investieren",
            "Kleidung",
            "Kredite",
            "Mobilität",
            "Projekte",
            "Sport",
            "Sonstiges",
            "Technik",
            "Urlaub",
            "Verpflegung",
            "Versicherung",
            "Wohnung",
            "Handy",
            "Gehalt",
            "Netflix Krissi",
            "Rückzahlung",
            "Spesen",
            "Weitere Einkommen",
        ]
    )

    readline.set_completer_delims("\t")
    readline.parse_and_bind("tab: complete")

    readline.set_completer(t.listCompleter)

    ans = input("Complete from list ")
    print(ans)

    readline.set_completer(t.pathCompleter)
    ans = input("What file do you want? ")
    print(ans)
