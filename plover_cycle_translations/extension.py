"""
Plover entry point extension module for Plover Cycle Translations

    - https://plover.readthedocs.io/en/latest/plugin-dev/extensions.html
    - https://plover.readthedocs.io/en/latest/plugin-dev/meta.html
"""
import re

from plover.engine import StenoEngine
from plover.formatting import (
    _Action,
    _Context
)
from plover.registry import registry


_WORD_LIST_DIVIDER: str = ","

class CycleTranslations:
    """
    Extension class that also registers a meta plugin.
    The meta deals with caching and cycling through a list of user-defined
    translations in a single outline.
    """
    _engine: StenoEngine
    _translations: list[str]
    _translations_length: int
    _index: int

    def __init__(self, engine: StenoEngine) -> None:
        self._engine = engine

    def start(self) -> None:
        """
        Sets up the meta plugin, steno engine hooks, and
        variable intialisations.
        """
        self._translations = []
        self._translations_length = 0
        self._index = 0
        registry.register_plugin("meta", "CYCLE", self._cycle_translations)

    def stop(self) -> None:
        """
        Tears down the steno engine hooks -- no custom action needed.
        """

    def _cycle_translations(self, ctx: _Context, argument: str) -> _Action:
        """
        Initialises a `_translations` list of words based on the word list
        contained in the `argument`, and outputs the first entry.
        If `argument` is `NEXT`, then replace the previously outputted text with
        the next word in `_translations`, and cycle the list.
        """
        action: _Action = ctx.new_action()

        if argument.upper() == "NEXT":
            self._prepare_next_translation(ctx, action)
        elif re.search(_WORD_LIST_DIVIDER, argument):
            self._init_translations(argument)
        else:
            raise ValueError("No comma-separated word list provided.")

        action.text = self._translations[self._index]
        return action

    def _prepare_next_translation(self, ctx: _Context, action: _Action) -> None:
        current_translation: str = self._translations[self._index]
        previous_output: str = ctx.last_text(len(current_translation))

        if previous_output == current_translation:
            self._index += 1
            # Reset index to zero if out of bounds
            self._index = self._index % self._translations_length

            action.prev_replace = current_translation
            # Do not put a space once a translation has been cycled
            action.prev_attach = True
        else:
            raise ValueError(
                f"{previous_output} is not part of a cyclable list."
            )

    def _init_translations(self, argument: str) -> None:
        self._translations = argument.split(_WORD_LIST_DIVIDER)
        self._translations_length = len(self._translations)
        self._index = 0
