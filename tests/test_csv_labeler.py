"""
Tests for csv labeler
"""

import pandas as pd
from parametrization import Parametrization

import src.main as main


@Parametrization.parameters("dataframe", "column", "expected_result")
@Parametrization.case(
    "labels_exist", pd.DataFrame(data={"labels": [None, "test", None]}), "labels", True
)
@Parametrization.case(
    "no_labels", pd.DataFrame(data={"labels": [None, None, None]}), "labels", False
)
def test_detect_labels(dataframe, column, expected_result):
    """
    Tests if the detection of existing labels works correctly.
    """
    result = main.detect_labels(dataframe, column)
    assert result == expected_result
