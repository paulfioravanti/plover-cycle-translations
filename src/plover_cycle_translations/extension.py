"""
Plover entry point extension module for Plover Cycle Translations

    - https://plover.readthedocs.io/en/latest/plugin-dev/extensions.html
    - https://plover.readthedocs.io/en/latest/plugin-dev/meta.html
"""

from collections import deque
from typing import Optional

from plover.engine import StenoEngine
from plover.formatting import _Action
from plover.registry import registry
from plover.steno import Stroke
from plover.translation import (
    Translation,
    Translator
)

from . import (
    FIRST,
    NEWEST,
    translation
)


_NEXT: int = -1
_PREVIOUS: int = 1

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
        if translation.is_valid_word_list(argument):
            self._init_cycle(translator, stroke, argument)
        elif argument.upper() == "NEXT":
            translation.cycle(translator, stroke, self._translations, _NEXT)
        elif argument.upper() == "PREVIOUS":
            translation.cycle(translator, stroke, self._translations, _PREVIOUS)
        else:
            raise ValueError(
                "No comma-separated word list or "
                "NEXT/PREVIOUS argument provided."
            )

    # Callback
    def _stroked(self, stroke: Stroke) -> None:
        if self._translations and stroke.is_correction:
            self._translations = None

    # Callback
    def _translated(self, _old: list[_Action], new: list[_Action]) -> None:
        # New text output outside of a cycle has no need of the previous
        # text's cycleable list. If it does not initalise its own new
        # cycleable list in `self._translations`, reset them so that it
        # cannot unexpectedly be transformed using the previous text's list.
        if translation.has_new_uncycleable_text(self._translations, new):
            self._translations = None

        # Multistroke outlines that return a CYCLE macro definition will end up
        # here, rather than `self.cycle_translations` being called.
        if (translations := translation.maybe_cycleable_list(new)):
            self._init_cycle_from_multistroke(new[NEWEST], translations)

    def _init_cycle(
        self,
        translator: Translator,
        stroke: Stroke,
        argument: str
    ) -> None:
        self._translations = translation.generate_cycleable_list(argument)
        translator.translate_translation(
            Translation([stroke], self._translations[FIRST])
        )

    def _init_cycle_from_multistroke(
        self,
        action: _Action,
        translations_list: str,
    ) -> None:
        self._translations = (
            translation.generate_cycleable_list(translations_list)
        )
        action.text = self._translations[FIRST]
        # NOTE: There seems to be no public API to access the `_engine`'s
        # `_translator`, so deliberately access protected property.
        # pylint: disable-next=protected-access
        self._engine._translator.untranslate_translation(
            self._engine.translator_state.translations[NEWEST]
        )
