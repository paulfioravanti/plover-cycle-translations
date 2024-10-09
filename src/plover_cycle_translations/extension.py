"""
Plover entry point extension module for Plover Cycle Translations

    - https://plover.readthedocs.io/en/latest/plugin-dev/extensions.html
    - https://plover.readthedocs.io/en/latest/plugin-dev/meta.html
"""

from collections import deque
import re
from typing import (
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
_NEXT: int = 1
_PREVIOUS: int = -1
_NEWEST: int = -1
_FIRST: int = 0

class CycleTranslations:
    """
    Extension class that also registers a macro plugin.
    The macro deals with caching and cycling through a list of user-defined
    translations in a single outline.
    """

    _engine: StenoEngine
    _translations: Optional[deque[str]]

    def __init__(self, engine: StenoEngine) -> None:
        self._engine = engine

    def start(self) -> None:
        """
        Sets up the meta plugin, steno engine hooks, and
        variable intialisations.
        """
        self._translations = None
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
        Initialises a `_translations` deque, initialised with a list of words
        based on the word list contained in the `argument`.

        If `argument` is `NEXT`, then replace the previously outputted text with
        the next word in `_translations`.

        If `argument` is `PREVIOUS`, then replace the previously outputted text
        with the previous word in `_translations`.
        """
        if CycleTranslations._has_word_list(argument):
            self._init_cycle(translator, stroke, argument)
        elif argument.upper() == "NEXT":
            self._cycle_translation(translator, stroke, _NEXT)
        elif argument.upper() == "PREVIOUS":
            self._cycle_translation(translator, stroke, _PREVIOUS)
        else:
            raise ValueError(
                "No comma-separated word list or "
                "NEXT/PREVIOUS argument provided."
            )

    # Callback
    def _stroked(self, stroke: Stroke) -> None:
        if self._translations and stroke == "*": # undo
            self._translations = None

    # Callback
    def _translated(self, _old: list[_Action], new: list[_Action]) -> None:
        # New text output outside of a cycle has no need of the previous
        # text's cycleable list. If it does not initalise its own new
        # cycleable list in `self._translations`, reset them so that it
        # cannot unexpectedly be transformed using the previous text's list.
        if self._has_new_uncycleable_text(new):
            self._translations = None

        # Multistroke outlines that return a CYCLE macro definition will end up
        # here, rather than `self.cycle_translations` being called.
        if (translations := CycleTranslations._check_cycleable_list(new)):
            self._init_cycle_from_multistroke(new[_NEWEST], translations)

    @staticmethod
    def _check_cycleable_list(new: list[_Action]) -> Optional[str]:
        if (
            new
            and (newest_action_text := new[_NEWEST].text)
            and CycleTranslations._has_word_list(newest_action_text)
            and (match := re.match(_CYCLEABLE_LIST, newest_action_text))
        ):
            return match.group(1)

        return None

    @staticmethod
    def _has_word_list(argument: str) -> bool:
        return cast(bool, re.search(_WORD_LIST_DIVIDER, argument))

    def _init_cycle(
        self,
        translator: Translator,
        stroke: Stroke,
        argument: str
    ) -> None:
        translations: deque[str] = self._init_translations(argument)
        translator.translate_translation(
            Translation([stroke], translations[_FIRST])
        )

    def _init_cycle_from_multistroke(
        self,
        action: _Action,
        translations_list: str,
    ) -> None:
        translations: deque[str] = self._init_translations(translations_list)
        action.text = translations[_FIRST]
        # NOTE: There seems to be no public API to access the `_engine`'s
        # `_translator`, so deliberately access protected property.
        # pylint: disable-next=protected-access
        self._engine._translator.untranslate_translation(
            self._engine.translator_state.translations[_NEWEST]
        )

    def _init_translations(self, argument: str) -> deque[str]:
        translations_list: list[str] = argument.split(_WORD_LIST_DIVIDER)
        translations: deque[str] = deque(translations_list)

        self._translations = translations

        return translations

    def _has_new_uncycleable_text(self, new: list[_Action]) -> bool:
        translations: Optional[deque[str]] = self._translations

        return cast(
            bool,
            translations
            and new
            and CycleTranslations._is_unknown_translation(
                new[_NEWEST],
                translations
            )
        )

    @staticmethod
    def _is_unknown_translation(
        action: _Action,
        translations: deque[str]
    ) -> bool:
        text: str = action.text

        # Check for prefix translations
        if action.next_attach:
            return f"{{{text}^}}" not in translations

        # Check for suffix translations. Non-suffix translations will come
        # through on _Actions with prev_attach=True if stroked after a prefix,
        # so we need to check whether both the text and its suffix version are
        # absent from the `translations`.
        if action.prev_attach:
            return (
                text not in translations
                and f"{{^{text}}}" not in translations
            )

        return text not in translations

    def _cycle_translation(
        self,
        translator: Translator,
        stroke: Stroke,
        direction: int
    ) -> None:
        if (
            (translator_translations := translator.get_state().translations)
            and (translations := self._translations)
        ):
            translator.untranslate_translation(translator_translations[_NEWEST])
            translations.rotate(direction)
            translator.translate_translation(
                Translation([stroke], translations[_FIRST])
            )
        else:
            raise ValueError(
                "Text not cycleable, or cycleable text needs to be re-stroked."
            )
