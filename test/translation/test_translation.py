from collections import deque
import pytest
from typing import cast

from plover_cycle_translations import translation


def test_generating_a_cycleable_list():
    assert (
        translation.generate_cycleable_list("a,b,c")
        == deque(["a", "b", "c"])
    )

def test_determining_an_invalid_word_list_blank():
    assert bool(translation.is_valid_word_list("")) == False

def test_determining_an_invalid_word_list_single_word():
    assert bool(translation.is_valid_word_list("hello")) == False

def test_determining_a_valid_word_list_single_comma():
    # This might seem silly, but if that's what the user wants...
    assert bool(translation.is_valid_word_list(",")) == True

def test_determining_a_valid_word_list():
    assert bool(translation.is_valid_word_list("a,b")) == True
