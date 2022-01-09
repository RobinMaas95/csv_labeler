"""
 Copyright 2021 Robin Maasjosthusmann. All rights reserved.
 Use of this source code is governed by a BSD-style
 license that can be found in the LICENSE file.
"""

import pandas as pd
from parametrization import Parametrization

from src import main


@Parametrization.parameters("user_input", "expected_result")
@Parametrization.case("positiv_lower", "y", True)
@Parametrization.case("postiv_upper", "Y", True)
@Parametrization.case("negativ_lower", "n", False)
@Parametrization.case("negativ_upper", "N", False)
@Parametrization.case("enter", "", True)
@Parametrization.case(
    "invalid_first_input",
    ["z", "Y"],
    'Please enter a valid value ("Y/y" or Enter for Yes, "N/n" for No)',
)
def test_confirm_prompt(monkeypatch, mocker, capsys, user_input, expected_result):
    """
    Tests if the confirm_prompt returns the expected results.
    Tests for all valid positive and negative inputs. Also tests if the loop
    inside the method is running when the user enters an invalid input.
    """
    if isinstance(user_input, str):
        monkeypatch.setattr("builtins.input", lambda _: user_input)
        assert main.confirm_prompt("test") is expected_result
    else:
        mocker.patch("builtins.input", side_effect=user_input)
        main.confirm_prompt("test")
        captured = capsys.readouterr()
        assert captured.out.strip() == expected_result


@Parametrization.parameters("user_input")
@Parametrization.case("existing_path", True)
@Parametrization.case("invalid_path", False)
def test_get_csv_input(monkeypatch, capsys, tmp_path, mocker, user_input):
    """
    Tests a valid filepath is recognized.
    For this a temporary folder ist created (pytest build-in) and
    inside this path a file is generated.
    """
    filepath = tmp_path / ("temp." + "test.csv")
    filepath.write_text("Test123", encoding="utf-8")
    if user_input:
        monkeypatch.setattr("builtins.input", lambda _: str(filepath))
        assert main.get_csv_filepath() == filepath
    else:
        mocker.patch(
            "builtins.input", side_effect=["/dummy/path/file.csv", str(filepath)]
        )
        main.get_csv_filepath()
        captured = capsys.readouterr()
        assert captured.out.strip() == "No valid file found"


@Parametrization.parameters("dataframe", "column", "user_input", "expected_result")
@Parametrization.case(
    "with_labels_y",
    pd.DataFrame(data={"labels": [None, "test", None]}),
    "labels",
    "Y",
    True,
)
@Parametrization.case(
    "with_labels_n",
    pd.DataFrame(data={"labels": [None, "test", None]}),
    "labels",
    "N",
    False,
)
@Parametrization.case(
    "no_labels",
    pd.DataFrame(data={"labels": [None, None, None]}),
    "labels",
    "",
    False,
)
def test_handle_existing_labels(
    monkeypatch,
    dataframe,
    column,
    user_input,
    expected_result,
):
    monkeypatch.setattr("builtins.input", lambda _: user_input)
    result = main.handle_existing_labels(dataframe, column)
    assert result == expected_result


if __name__ == "__main__":
    test_handle_existing_labels(
        pd.DataFrame(data={"labels": [None, "test", None]}),
        "labels",
        "Y",
        "Existing labels detected! Do you want to keep the existing labels (if you"
        " choose No, all existing labels will be deleted!)",
        True,
    )
