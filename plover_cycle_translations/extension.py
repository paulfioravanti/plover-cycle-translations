"""
Plover entry point extension module for Plover Cycle Translations

    - https://plover.readthedocs.io/en/latest/plugin-dev/extensions.html
    - https://plover.readthedocs.io/en/latest/plugin-dev/meta.html
"""
from itertools import cycle
import re
from typing import (
    Iterator,
    Optional
)

from plover.engine import StenoEngine
from plover.formatting import _Action
from plover.registry import registry
from plover.steno import Stroke
from plover.translation import (
    Translation,
    Translator
)


_WORD_LIST_DIVIDER: str = ","

class CycleTranslations:
    """
    Extension class that also registers a macro plugin.
    The macro deals with caching and cycling through a list of user-defined
    translations in a single outline.
    """
    _engine: StenoEngine
    _translations_list: Optional[list[str]]
    _translations: Optional[Iterator[str]]

    def __init__(self, engine: StenoEngine) -> None:
        self._engine = engine

    def start(self) -> None:
        """
        Sets up the meta plugin, steno engine hooks, and
        variable intialisations.
        """
        self._reset_translations()
        registry.register_plugin("macro", "CYCLE", self._cycle_translations)
        self._engine.hook_connect("stroked", self._stroked)
        self._engine.hook_connect("translated", self._translated)

    def stop(self) -> None:
        """
        Tears down the steno engine hooks.
        """
        self._engine.hook_disconnect("stroked", self._stroked)
        self._engine.hook_disconnect("translated", self._translated)

    def _cycle_translations(
        self,
        translator: Translator,
        stroke: Stroke,
        argument: str
    ) -> None:
        """
        Initialises a `_translations_list` list of words based on the word list
        contained in the `argument`, and a cycleable `_translations` iterator
        over `_translations_list`, that outputs the first entry.

        If `argument` is `NEXT`, then replace the previously outputted text with
        the next word in `_translations`, and cycle the list.
        """
        if re.search(_WORD_LIST_DIVIDER, argument):
            self._init_translations(argument)
        elif argument.upper() == "NEXT":
            if self._translations:
                CycleTranslations._untranslate_last_translation(translator)
            else:
                raise ValueError(
                    "Text is not in a cycleable list, "
                    "or cycleable text needs to be re-stroked."
                )
        else:
            raise ValueError(
                "No comma-separated word list or NEXT argument provided."
            )

        if translations := self._translations:
            translator.translate_translation(
                Translation([stroke], next(translations))
            )

    def _stroked(self, stroke: Stroke) -> None:
        if self._translations and stroke == "*": # undo
            self._reset_translations()

    def _translated(self, _old: list[_Action], new: list[_Action]) -> None:
        translations_list: Optional[list[str]] = self._translations_list

        # NOTE: `translations_list` specifically needs to be used here instead
        # of `translations` because it is not possible to gain access to the
        # underlying collection inside a cycleable list to check for value
        # inclusion/exclusion.
        if (
            translations_list
            and new
            and not new[0].text in translations_list
        ):
            # New text output outside of a cycle has no need of the previous
            # text's cycleable list. If it does not initalise its own new
            # cycleable list in `self._translations`, reset them so that it
            # cannot unexpectedly be transformed using the previous text's list.
            self._reset_translations()

    @staticmethod
    def _untranslate_last_translation(translator: Translator) -> None:
        translations: list[Translation] = translator.get_state().translations

        if translations:
            translator.untranslate_translation(translations[-1])
        else:
            raise ValueError(
                "No translations output exist to attempt to cycle through."
            )

    def _reset_translations(self) -> None:
        self._translations = self._translations_list = None

    def _init_translations(self, argument: str) -> None:
        self._translations_list = argument.split(_WORD_LIST_DIVIDER)
        self._translations = cycle(self._translations_list)
