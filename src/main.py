# Copyright 2021 Robin Maasjosthusmann. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
"""
CSV Labeler

A simple tool for labeling your csv files
"""

import ast
import configparser
from distutils import util

import os
import re
import textwrap
from pathlib import Path

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
        reply = input(f"{question} (Y/n): ").casefold()
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
        csv_filepath = Path(input("Please enter the path of the csv file: "))
        if csv_filepath.is_file():
            break
        print("No valid file found")

    return csv_filepath


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


def print_relevant_columns(row: pd.Series, config: configparser.ConfigParser) -> None:
    """
    Prints all relevant columns for the classification with the corresponding value. Does
    some preprecessing for string values (removes linebreaks, splits into multiple lines if
    the text is to long...).

    Parameters
    ----------
    row : pd.Series
        Row of the csv file/dataframe. Must contain all relevant columns
    config : configparser.ConfigParser
        ConfigParser with all information from the config.ini
    """
    clear_console()
    wrapper = textwrap.TextWrapper(
        width=int(config["general"]["line_length"])
    )  # Needed for formatting outputs

    # If not at least one relevant column is defined, use all columns except of label_column
    relevant_columns = ast.literal_eval(config["csv"]["relevant_columns"])
    if len(relevant_columns) == 0:
        relevant_columns = list(
            i for i in list(row.index) if i.casefold() != config["csv"]["label_column"]
        )

    # Use the length of the longest column name to determine the width of the "name" column.
    # The width of the "value" column is the remaining space of the {line_width} defined in the
    # config.ini minus the width of the "name" column and the vale of {name_value_seperator_width}
    # (also defined in config.ini.)
    name_column_width = len(max(relevant_columns, key=len))
    value_column_width = int(config["general"]["line_length"]) - name_column_width
    line_length = int(config["general"]["name_value_seperator_width"])

    for name, value in row.items():
        if name.casefold() in [x.casefold() for x in relevant_columns]:
            # Check for empty row -> no further processing needed if empty
            if pd.isna(value):
                print_value = "None"
            else:
                # Cleanup text & highlight keywords (only in strings)
                if isinstance(value, str):
                    print_value = " ".join(value.replace("\\", "").split())
                    print_value = highlight_keywords(
                        print_value,
                        ast.literal_eval(config["classification"]["keywords"]),
                        config["highlighting"]["foreground"],
                        config["highlighting"]["background"],
                    )
                else:
                    print_value = value

            # Print column
            # If column contains text, split it into smaller parts to fit inside default terminals
            if isinstance(value, str):
                line_list = wrapper.wrap(text=print_value)
                print(
                    f"{name:{name_column_width}}:"
                    f'{"":{line_length}}{line_list[0]:{value_column_width}}'
                )
                for element in line_list[1:]:
                    print(
                        f'{"":{name_column_width}} {"":{line_length}}{element:{value_column_width}}'
                    )
            else:
                print(
                    f"{name:{name_column_width}}:"
                    f'{"":{line_length}}{str(print_value):{value_column_width}}'
                )


def label_row(
    row: pd.Series,
    skip_labels: bool,
    config: configparser.ConfigParser,
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

    Returns
    -------
    str
        Selected Label
    """
    if skip_labels and not pd.isna(row[config["csv"]["label_column"]]):
        return row[config["csv"]["label_column"]]
    print_relevant_columns(row, config)
    return get_classification(ast.literal_eval(config["classification"]["labels"]))


def main():
    """
    CSV Labeler

    A simple tool for labeling your csv files
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    if bool(util.strtobool(config["development"]["testmode"])):
        # Development behavior, set values inside of config.ini
        csv_filepath = config["development"]["csv_file"]
    else:
        # Normal behavior
        csv_filepath = get_csv_filepath()

    df = pd.read_csv(csv_filepath, sep=config["csv"]["sep"])
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Error while reading the csv file")

    if bool(util.strtobool(config["development"]["testmode"])):
        # Development behavior, set values inside of config.ini
        skip_labels = bool(util.strtobool(config["development"]["skip_labels"]))
    else:
        # Normal behavior
        skip_labels = handle_existing_labels(df, config["csv"]["label_column"])
    save_changes = True

    for index, row in df.iterrows():
        try:
            df.loc[index, config["csv"]["label_column"]] = label_row(
                row, skip_labels, config
            )
        except KeyboardInterrupt:
            save_changes = confirm_prompt(
                "\nInput was canceled, should the labels created so far be saved?"
            )
            break

    clear_console()
    print("Labeling of the CSV file completed")
    if save_changes:
        df.to_csv(csv_filepath, sep=config["csv"]["sep"], index=False)


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
    lower_category_list = [x.casefold() for x in categories]
    category_integer_list = list(range(1, len(lower_category_list) + 1))
    category_hex_list = list(hex(n) for n in category_integer_list)
    print("\nThe following categories exist: ")
    for idx, category in enumerate(categories):
        print(f"\t{idx+1:x})\t{category}")

    print("\tq)\tCancel Input")

    while True:
        skip_invalid_print = False
        selected_category = input(
            "\nPlease select one of the categories, you can use the name, a unique part"
            " of the name or the corresponding number: "
        )
        # Check if there is an exact match
        if selected_category.casefold() in lower_category_list:
            clear_console()
            return resolve_correct_label_name(selected_category, categories)
        # Check if there is a partial match
        match_list = get_partial_match(selected_category, categories)
        if len(match_list) == 1:
            if confirm_prompt(f'Did you mean "{match_list[0]}"?'):
                return match_list[0]
        if len(match_list) > 1:
            joined_list = ", ".join(f'"{w}"' for w in match_list)
            print(
                f"To many possible results ({joined_list}), please enter a unique value"
            )
            skip_invalid_print = True
        # Check if the user entered the hardcoded value 'Umbuchung'
        if selected_category.casefold() == "umbuchung" or selected_category == "u":
            clear_console()
            return "Umbuchung"
        # Check if the user entered the exit command
        if selected_category.casefold() == "cancel input" or selected_category == "q":
            raise KeyboardInterrupt("User canceled the input")
        # Check if the user entered a hex value (-> Id of a category)
        try:
            if hex(int(selected_category, 16)) in category_hex_list:
                selected_category = categories[int(selected_category, 16) - 1]
                clear_console()
                return selected_category
        except ValueError:
            pass
        if not skip_invalid_print:
            print("Invalid Input, please choose a valid category!")


def resolve_correct_label_name(label: str, label_list: list) -> str:
    """
        Resolves the correct (case sensitive) spelling to the casefolded label


    Parameters
    ----------
    label : str
        Label case insensitiv spelling
    label_list : list
        List with all labels in the correct spelling

    Returns
    -------
    str
        Correct spelled label
    """
    match = next(
        i for i, v in enumerate(label_list) if v.casefold() == label.casefold()
    )
    return label_list[match]


def get_partial_match(substring: str, label_list: list) -> list:
    """
    Validates if there is a partial match of the substring in the label_list

    Parameters
    ----------
    substring : str
        Substring to be matched
    label_list : list
        List with all labels

    Returns
    -------
    list
        Lists with all labels that were matched
    """
    regex_pattern = re.compile(f".*{substring}*", re.IGNORECASE)
    match_list = list(filter(regex_pattern.match, label_list))

    exact_match = list(
        x for x in (x.casefold() for x in match_list) if x == substring.casefold()
    )
    if len(exact_match) == 1:
        match = resolve_correct_label_name(substring.casefold(), label_list)
        return [match]

    # apply a method to each entry in the list
    match_list = [resolve_correct_label_name(item, label_list) for item in match_list]
    return match_list


def clear_console():
    """
    Clears console output
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
            if word.casefold() in [x.casefold() for x in keywords]:
                text = text.replace(
                    word,
                    getattr(Fore, foreground_color.upper())
                    + getattr(Back, background_color.upper())
                    + word,
                )
            else:
                text = text.replace(f" {word}", Style.RESET_ALL + f" {word}")

        # Add highlight end tag if the text only consists out of one and it is a keyword
        if len(text.split(" ")) == 1:
            only_word = text.split(" ")[0].casefold()
            if only_word.endswith(tuple(x.casefold() for x in keywords)):
                text += Style.RESET_ALL

    return text


if __name__ == "__main__":
    main()
