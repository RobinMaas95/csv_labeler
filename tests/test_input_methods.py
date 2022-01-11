"""
 Copyright 2021 Robin Maasjosthusmann. All rights reserved.
 Use of this source code is governed by a BSD-style
 license that can be found in the LICENSE file.
"""

from pathlib import Path
from typing import Union

import pandas as pd
import pytest
from csv_labeler import main
from parametrization import Parametrization
from pytest import CaptureFixture, MonkeyPatch
from pytest_mock import MockerFixture


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
def test_confirm_prompt(
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
    capsys: CaptureFixture,
    user_input: Union[str, list],
    expected_result: str,
):
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


@Parametrization.parameters(
    "categories", "category_output", "user_input", "expected_output", "expected_result"
)
@Parametrization.default_parameters(
    categories=["Shopping", "Food", "Freetime", "Car"],
    category_output=(
        "The following categories exist:"
        " \n\t1)\tShopping\n\t2)\tFood\n\t3)\tFreetime\n\t4)\tCar\n\n\tu)\tUmbuchung\n\tq)\tCancel"
        " Input\n"
    ),
)
@Parametrization.case(
    "umbuchung",
    user_input="u",
    expected_output=[],
    expected_result="Umbuchung",
)
@Parametrization.case(
    "cancel_input", user_input="q", expected_output=[], expected_result=""
)
@Parametrization.case(
    "empty_input",
    user_input=["", "u"],
    expected_output=["\nPlease select a category"],
    expected_result="Umbuchung",
)
def test_get_classification(
    monkeypatch: MonkeyPatch,
    mocker: MockerFixture,
    capsys: CaptureFixture,
    categories: list,
    category_output: str,
    user_input: Union[str, list],
    expected_output: list,
    expected_result: str,
):
    """
    Tests if the get_classification method returns the expected results.
    """
    if isinstance(user_input, str):
        monkeypatch.setattr("builtins.input", lambda _: user_input)

        if user_input == "q":
            # Test if the exception to end the input loop is raised
            with pytest.raises(KeyboardInterrupt, match="User canceled the input"):
                main.get_classification(categories)
        else:
            result = main.get_classification(categories)
            captured = capsys.readouterr()
            assert captured.out.strip() == category_output.strip()
            assert result == expected_result
    else:
        mocker.patch("builtins.input", side_effect=user_input)
        main.get_classification(categories)
        captured = capsys.readouterr()
        assert captured.out.strip() == category_output + "".join(expected_output)


@Parametrization.parameters("user_input")
@Parametrization.case("existing_path", True)
@Parametrization.case("invalid_path", False)
def test_get_csv_input(
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture,
    tmp_path: Path,
    mocker: MockerFixture,
    user_input: bool,
):
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
    monkeypatch: MonkeyPatch,
    dataframe: pd.DataFrame,
    column: str,
    user_input: str,
    expected_result: bool,
):
    """Test if the method handle_existing_labels returns the expected result."""
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
