 Copyright 2021 Robin Maasjosthusmann. All rights reserved.
 Use of this source code is governed by a BSD-style
 license that can be found in the LICENSE file.
"""

from parametrization import Parametrization

import src.main as main


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
