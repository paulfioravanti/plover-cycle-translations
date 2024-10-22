"""
Module relating to translation lists.
"""

from collections import deque
import re
from typing import cast


_WORD_LIST_DIVIDER: str = ","

def generate_cycleable_list(argument: str) -> deque[str]:
    """
    Generate a deque cycleable list from `argument`. Check for whether
    `argument` is a valid cycleable list occurs in the extension class.
    """
    return deque(argument.split(_WORD_LIST_DIVIDER))

def is_valid_word_list(argument: str) -> bool:
    """
    Determine if `argument` contains a valid word list.
    """
    return cast(bool, re.search(_WORD_LIST_DIVIDER, argument))
