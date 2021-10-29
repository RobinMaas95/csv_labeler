# Copyright 2021 Robin Maasjosthusmann. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
"""
CSV Labeler

A simple tool for labeling your csv files
"""

import ast
import configparser
import os
import textwrap
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from colorama import Back, Fore, Style


def confirm_prompt(question: str) -> bool:
    """
    Asks the user for passed questions, accepts "Yes" (default, also valid as direct)
    Enter or "No" as answer. Returns a boolean value Yes=True/No=False

    Parameters
    ----------
    question : str
        The questions the user has to answere

    Returns
    -------
    bool
        True if the user choose Yes, False if No
    """
    reply = None
    valid_inputs = ("", "y", "n")
    while reply not in valid_inputs:
        if reply is not None:
            print('Please enter a valid value ("Y/y" or Enter for Yes, "N/n" for No)')
        reply = input(f"{question} (Y/n): ").lower()
    return reply in ("", "y")


def get_csv_filepath() -> Path:
    """
    Asks the user for the path to the csv file

    Returns
    -------
    pathlib.Path
        Path to csv file
    """
    while True:
        csv_filepath = Path(
            r"/Users/robin/Developer/dkb2homebank/Homebank.csv"
        )  # TODO: reenter input
        # Path(input("Please enter the path of the csv file: "))
        if csv_filepath.is_file():
            break
        print("No valid file found")

    return csv_filepath


def get_csv_seperator() -> str:
    """
    Asks the user for the csv file seperator

    Returns
    -------
    str
        CSV file seperator
    """
    seperator = ";"
    # input("What is the seperator of the csv file?: ")
    return seperator


def get_csv_overwrite() -> bool:
    """
    Asks the user if the label current file should be edited or a new one should be created

    Returns
    -------
    bool
        True if the current one, False if a new one
    """
    # overwrite = confirm_prompt("Append labels in the current file")
    overwrite = True
    return overwrite


def get_setup_input() -> Tuple[Path, str, bool]:
    """
    Asks the user for the csv file path, the seperator and if the current file should be edited
    or a new on should be created.

    Returns
    -------
    Tuple[Path, str, bool]
        Answers from the user
    """
    file_path = get_csv_filepath()
    seperator = get_csv_seperator()
    overwrite = get_csv_overwrite()

    return file_path, seperator, overwrite


def detect_labels(df: pd.DataFrame, label_column: str) -> bool:
    """
    Validates if the label column already contains any labels.
    Returns true if so.

    Parameters
    ----------
    df : pd.DataFrame
        Read in csv file
    label_column : str
        Column to check for labels

    Returns
    -------
    bool
        True if any column contains a label, False if not
    """
    return not df[label_column].isnull().all()


def handle_existing_labels(df: pd.DataFrame, label_column: str) -> bool:
    """
    Asks the user if he/she wants to keep existing labels if any are detected.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the label column
    label_column : str
        Name of the column which contains the labels

    Returns
    -------
    bool
        True if user wants to skip (ignore) already labeled rows, False if
        the user wants to relable them
    """
    skip_labels = False
    if detect_labels(df, label_column):
        skip_labels = not confirm_prompt(
            "Existing labels detected! Do you want to overwrite existing labels (if you"
            " choose No, all entries that already contain a label will be skipped)"
        )

    return skip_labels


def label_row(
    row: pd.Series,
    skip_labels: bool,
    config: configparser.ConfigParser,
    wrapper: textwrap.TextWrapper,
) -> str:
    """
    Prints the relevant columns of the passed row to the terminal and asks the user for
    the label.

    Parameters
    ----------
    row : pd.Series
        Row of the pandas Dataframe that contains the csv file
    skip_labels : bool
        Should rows which already have a label be skipped?
    config : configparser.ConfigParser
        ConfigParser with all information from the config.ini
    wrapper : textwrap.TextWrapper
        Wrapper object to ensure that the output of the column content is wrapped correctly

    Returns
    -------
    str
        Selected Label
    """
    if skip_labels and not pd.isna(row[config["csv"]["label_column"]]):
        return row[config["csv"]["label_column"]]

    clear_console()
    info = "None" if np.isnan(row["info"]) else row["info"]
    print("Info:\t", info)
    print("Payee:\t", row["payee"])
    memo = " ".join(row["memo"].replace("\\", "").split())
    memo = highlight_keywords(
        memo,
        ast.literal_eval(config["classification"]["keywords"]),
        config["highlighting"]["foreground"],
        config["highlighting"]["background"],
    )
    line_list = wrapper.wrap(text=memo)
    print("Memo:\t", line_list[0])
    for element in line_list[1:]:
        print("\t", element)
    print("Amount:\t", row["amount"])

    return get_classification(ast.literal_eval(config["classification"]["labels"]))


def main():
    """
    CSV Labeler

    A simple tool for labeling your csv files
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    (
        csv_filepath,
        seperator,
        _,
    ) = get_setup_input()  # TODO: Handling overwrite
    print(csv_filepath)
    df = pd.read_csv(csv_filepath, sep=seperator)

    skip_labels = handle_existing_labels(df, config["csv"]["label_column"])
    save_changes = True
    wrapper = textwrap.TextWrapper(width=100)

    for index, row in df.iterrows():
        try:
            df.loc[  # pylint: disable = no-member
                index, config["csv"]["label_column"]
            ] = label_row(row, skip_labels, config, wrapper)
        except KeyboardInterrupt:
            save_changes = confirm_prompt(
                "\nInput was canceled, should the labels created so far be saved?"
            )
            break

    if save_changes:
        print("Will save changes")
        df.to_csv(  # pylint: disable = no-member
            csv_filepath, sep=seperator, index=False
        )
    else:
        print("drop changes")


def get_classification(categories: list) -> str:
    """
    Displays the possible label classes and validates the userinput (must be a valid labelclass or a
    corresponding id). Converts a class id to the class name if necessary

    Parameters
    ----------
    categories : list
        List with the class labels

    Returns
    -------
    str
        Selected label

    Raises
    ------
    KeyboardInterrupt
        Raised when the user choose to cancel the classification
    """
    lower_category_list = [x.lower() for x in categories]
    category_integer_list = list(range(1, len(lower_category_list) + 1))
    print("\nThe following categories exist: ")
    for idx, category in enumerate(categories):
        print(f"\t{idx+1})  {category}")

    print("\n\tq) Cancel Input")

    while True:
        selected_category = input(
            "\nPlease select one of the categories, you can use type the complete name"
            " or use the corresponding number: "
        )
        if selected_category.lower() in lower_category_list:
            clear_console()
            return selected_category
        if selected_category.lower() == "cancel input" or selected_category == "q":
            raise KeyboardInterrupt("User canceled the input")
        if int(selected_category) in category_integer_list:
            selected_category = categories[int(selected_category) - 1]
            clear_console()
            return selected_category

        print("Invalid Input, please choose a valid category!")


def clear_console():
    """
    Clears consol output
    """
    os.system("cls||clear")


def highlight_keywords(
    text: str,
    keywords: list,
    foreground_color: str = "BLACK",
    background_color: str = "YELLOW",
) -> str:
    """
    Loops over the text and adds the necessary characters for word based highlighting.
    This is maybe not the most effective way to do this, but its good enough for this
    usecase.

    Parameters
    ----------
    text : str
        The original text to highlight in
    keywords : list
        List with all words that should be highlighted
    foreground_color : str
        Forgroundcolor for highlighted words
    background_color : str
        Backgroundcolor for highlighted words


    Returns
    -------
    str
        Text with added characters for highlighting
    """
    # Skip loop if there are no keywords
    if len(keywords) > 0:
        for word in text.split(" "):
            if word.lower() in [x.lower() for x in keywords]:
                text = text.replace(
                    word,
                    getattr(Fore, foreground_color.upper())
                    + getattr(Back, background_color.upper())
                    + word,
                )
            else:
                text = text.replace(f" {word}", Style.RESET_ALL + f" {word}")

    return text


if __name__ == "__main__":
    main()
