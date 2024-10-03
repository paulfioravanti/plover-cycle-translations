"""
Plover entry point extension module for Plover Cycle Translations

    - https://plover.readthedocs.io/en/latest/plugin-dev/extensions.html
    - https://plover.readthedocs.io/en/latest/plugin-dev/meta.html
"""

from itertools import cycle
import re
from typing import (
    Iterator,
    Optional,
    Pattern,
    cast
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
_CYCLEABLE_LIST: Pattern[str] = re.compile("=CYCLE:(.+)", re.IGNORECASE)

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

    # Macro entry function
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
        if CycleTranslations._has_word_list(argument):
            self._init_cycle(translator, stroke, argument)
        elif argument.upper() == "NEXT":
            self._cycle_next_translation(translator, stroke)
        else:
            raise ValueError(
                "No comma-separated word list or NEXT argument provided."
            )

    # Callback
    def _stroked(self, stroke: Stroke) -> None:
        if self._translations and stroke == "*": # undo
            self._reset_translations()

    # Callback
    def _translated(self, _old: list[_Action], new: list[_Action]) -> None:
        # New text output outside of a cycle has no need of the previous
        # text's cycleable list. If it does not initalise its own new
        # cycleable list in `self._translations`, reset them so that it
        # cannot unexpectedly be transformed using the previous text's list.
        if self._has_new_uncycleable_text(new):
            self._reset_translations()

        # Multistroke outlines that return a CYCLE macro definition will end up
        # here, rather than `self.cycle_translations` being called.
        if (translations_list := CycleTranslations._check_cycleable_list(new)):
            self._init_cycle_from_multistroke(new[-1], translations_list)

    @staticmethod
    def _check_cycleable_list(new: list[_Action]) -> Optional[str]:
        if (
            new
            and (newest_action_text := new[-1].text)
            and CycleTranslations._has_word_list(newest_action_text)
            and (match := re.match(_CYCLEABLE_LIST, newest_action_text))
        ):
            return match.group(1)

        return None

    @staticmethod
    def _has_word_list(argument: str) -> bool:
        return cast(bool, re.search(_WORD_LIST_DIVIDER, argument))

    def _reset_translations(self) -> None:
        self._translations_list = self._translations = None

    def _init_cycle(
        self,
        translator: Translator,
        stroke: Stroke,
        argument: str
    ) -> None:
        translations: Iterator[str] = self._init_translations(argument)
        translator.translate_translation(
            Translation([stroke], next(translations))
        )

    def _init_cycle_from_multistroke(
        self,
        action: _Action,
        translations_list: str,
    ) -> None:
        translations: Iterator[str] = self._init_translations(translations_list)
        action.text = next(translations)
        # NOTE: There seems to be no public API to access the engine
        # `translator`, so deliberately access protected property.
        # pylint: disable-next=protected-access
        self._engine._translator.untranslate_translation(
            self._engine.translator_state.translations[-1]
        )

    def _init_translations(self, argument: str) -> Iterator[str]:
        translations_list: list[str] = argument.split(_WORD_LIST_DIVIDER)
        translations: Iterator[str] = cycle(translations_list)

        self._translations_list = translations_list
        self._translations = translations

        return translations

    def _has_new_uncycleable_text(self, new: list[_Action]) -> bool:
        # NOTE: `translations_list` specifically needs to be used here instead
        # of `translations` because it is not possible to gain access to the
        # underlying collection inside a cycleable list to check for value
        # inclusion/exclusion.
        translations_list: Optional[list[str]] = self._translations_list

        return cast(
            bool,
            translations_list
            and new
            and new[-1].text not in translations_list
        )

    def _cycle_next_translation(
        self,
        translator: Translator,
        stroke: Stroke
    ) -> None:
        if (
            (translations := translator.get_state().translations)
            and (cycled_translations := self._translations)
        ):
            translator.untranslate_translation(translations[-1])
            translator.translate_translation(
                Translation([stroke], next(cycled_translations))
            )
        else:
            raise ValueError(
                "Text not cycleable, or cycleable text needs to be re-stroked."
            )
