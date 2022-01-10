"""
 Copyright 2021 Robin Maasjosthusmann. All rights reserved.
 Use of this source code is governed by a BSD-style
 license that can be found in the LICENSE file.
"""

from csv_labeler.main import get_partial_match


def test_no_matching_label():
    """
    Test for no matching label for substring
    """
    label_list = ["Treehouseladder", "House", "Housetopcolor", "Lighthouses"]
    substring = "food"
    result = get_partial_match(substring, label_list)
    assert result == []


def test_exact_match_case_sensitiv():
    """
    Test with a exact match (complete word) with the correct spelling (upper-/lowercase)
    """
    label_list = ["Treehouseladder", "House", "Housetopcolor", "Lighthouses"]
    substring = "House"
    result = get_partial_match(substring, label_list)
    assert result == ["House"]


def test_exact_match_case_insensitiv():
    """
    Test with a exact match (complete word) with the incorrect spelling (upper-/lowercase)
    """
    label_list = ["Treehouseladder", "House", "Housetopcolor", "Lighthouses"]
    substring = "hOUse"
    result = get_partial_match(substring, label_list)
    assert result == ["House"]


def test_match_start_of_the_word():
    """
    Matching substring is at the beginning of the label
    """
    label_list = ["Treehouseladder", "House", "Housetopcolor", "Lighthouses"]
    substring = "Light"
    result = get_partial_match(substring, label_list)
    assert result == ["Lighthouses"]


def test_match_end_of_the_word():
    """
    Matching substring is at the end of the label
    """
    label_list = ["Treehouseladder", "House", "Housetopcolor", "Lighthouses"]
    substring = "ladder"
    result = get_partial_match(substring, label_list)
    assert result == ["Treehouseladder"]


def test_match_middle_of_the_word():
    """
    Matching substing is in the middle of the label
    """
    label_list = ["Treehouse", "House", "Housetopcolor", "Lighthouses"]
    substring = "top"
    result = get_partial_match(substring, label_list)
    assert result == ["Housetopcolor"]


def test_multiple_matches():
    """
    Test for multiple matching labels.
    Result should equal the label list.
    """
    label_list = ["Treehouse", "House", "Housetop", "Lighthouses"]
    substring = "hous"

    result = get_partial_match(substring, label_list)
    assert label_list == result
