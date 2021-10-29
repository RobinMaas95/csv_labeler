"""
 Copyright 2021 Robin Maasjosthusmann. All rights reserved.
 Use of this source code is governed by a BSD-style
 license that can be found in the LICENSE file.

 This test maybe only pass on mac/unix as the expected sentences are based on a mac system.
"""

from src.main import highlight_keywords


def test_no_matching_keywords():
    sentence = "This is my test sentence without keywords"
    highlighted_sentence = highlight_keywords(sentence, [])

    assert sentence == highlighted_sentence


def test_one_matching_keywords():
    sentence = "This is my test sentence with a keyword"
    expected_sentence = (
        "This\x1b[0m is\x1b[0m my\x1b[0m test\x1b[0m sentence"
        " \x1b[30m\x1b[43mwith\x1b[0m a\x1b[0m keyword"
    )
    highlighted_sentence = highlight_keywords(sentence, ["with"])
    assert expected_sentence == highlighted_sentence


def test_multiple_matching_keywords():
    sentence = "This is my test sentence with multiple keywords"
    expected_sentence = (
        "This\x1b[0m is \x1b[30m\x1b[43mmy\x1b[0m test"
        " \x1b[30m\x1b[43msentence\x1b[0m with \x1b[30m\x1b[43mmultiple\x1b[0m"
        " keywords"
    )
    highlighted_sentence = highlight_keywords(sentence, ["my", "sentence", "multiple"])
    assert expected_sentence == highlighted_sentence


def test_matching_keyword_start_sentence():
    sentence = "This is my test sentence with multiple keywords"
    expected_sentence = (
        "\x1b[30m\x1b[43mThis\x1b[0m is\x1b[0m my\x1b[0m test\x1b[0m sentence\x1b[0m"
        " with\x1b[0m multiple\x1b[0m keywords"
    )
    highlighted_sentence = highlight_keywords(sentence, ["This"])
    assert expected_sentence == highlighted_sentence


def test_matching_keyword_end_sentence():
    sentence = "This is my test sentence with multiple keywords"
    expected_sentence = (
        "This\x1b[0m is\x1b[0m my\x1b[0m test\x1b[0m sentence\x1b[0m with\x1b[0m"
        " multiple \x1b[30m\x1b[43mkeywords"
    )
    highlighted_sentence = highlight_keywords(sentence, ["keywords"])
    assert expected_sentence == highlighted_sentence
