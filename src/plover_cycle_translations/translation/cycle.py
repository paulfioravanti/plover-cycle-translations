"""
Module relating to cycleable translations.
"""

from collections import deque
from typing import (
    Optional,
    Pattern,
    cast
)
import re

from plover.formatting import _Action
from plover.steno import Stroke
from plover.translation import (
    Translation,
    Translator
)

from .. import (
    FIRST,
    NEWEST
)
from .list import is_valid_word_list


_CYCLEABLE_LIST: Pattern[str] = re.compile("=CYCLE:(.+)", re.IGNORECASE)

def cycle(
    translator: Translator,
    stroke: Stroke,
    translations: Optional[deque[str]],
    direction: int
) -> None:
    """
    Removes an old outputted translation, cycles the translation list, and
    outputs the next translation in the cycleable list.
    """
    if (
        translations and
        (translator_translations := translator.get_state().translations)
    ):
        translator.untranslate_translation(translator_translations[NEWEST])
        translations.rotate(direction)
        translator.translate_translation(
            Translation([stroke], translations[FIRST])
        )
    else:
        raise ValueError(
            "Text not cycleable, or cycleable text needs to be re-stroked."
        )

def has_new_uncycleable_text(
    translations: Optional[deque[str]],
    new: list[_Action]
) -> bool:
    """
    Determine whether the `text` in the newest `_Action` contains a
    non-cycleable list (in other words, a "normal" steno translation entry).
    The return value for this function should signal whether the current
    cycleable translations list should be discarded.
    """
    return cast(
        bool,
        translations
        and new
        and _is_unknown_translation(new[NEWEST], translations)
    )

def maybe_cycleable_list(new: list[_Action]) -> Optional[str]:
    """
    Determine whether the `text` in the newest `_Action` is a valid cycleable
    list. If so, return the list, or None if not.
    """
    if (
        new
        and (newest_action_text := new[NEWEST].text)
        and is_valid_word_list(newest_action_text)
        and (match := re.match(_CYCLEABLE_LIST, newest_action_text))
    ):
        return match.group(1)

    return None

def _is_unknown_translation(action: _Action, translations: deque[str]) -> bool:
    text: str = action.text

    # Check for prefix translations
    if action.next_attach:
        return f"{{{text}^}}" not in translations

    # Check for suffix translations. Non-suffix translations will come
    # through on _Actions with prev_attach=True if stroked after a prefix,
    # so we need to check whether both the text and its suffix version are
    # absent from the `translations`.
    if action.prev_attach:
        return all(
            string not in translations
            for string in [text, f"{{^{text}}}"]
        )

    return text not in translations
