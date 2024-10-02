# Plover Cycle Translations

[![Build Status][Build Status image]][Build Status url] [![PyPI - Version][PyPI version image]][PyPI url] [![PyPI - Downloads][PyPI downloads image]][PyPI url] [![linting: pylint][linting image]][linting url]

This [Plover][] [extension][] [plugin][] contains a [macro][] that allows you
define multiple translations in a single outline, and then cycle through them
[Alt-Tab][]- or [IME][]-style using a "selector stroke". It covers similar
ground to Plover's [`retro_toggle_asterisk`][] macro, but is broader in
scope than just toggling between an outline and its asterisk-flagged equivalent
(e.g. `"HAOEU": "high"` and `"HAO*EU": "hi"`).

Cycling translations can be helpful for disambiguating between [homophones][]
(words that are pronounced the same but differ in spelling; e.g. "sent", "cent",
and "scent"), or words and their similar sounding [proper nouns][] (e.g. "mark",
"Mark", and "Marc") with a single outline, rather than needing to remember all
their respective outlines.

For some examples of cycleable list entries to add to your own steno
dictionaries, see [here][].

## Install

1. In the Plover application, open the Plugins Manager (either click the Plugins
   Manager icon, or from the `Tools` menu, select `Plugins Manager`).
2. From the list of plugins, find `plover-cycle-translations`
3. Click "Install/Update"
4. When it finishes installing, restart Plover
5. After re-opening Plover, open the Configuration screen (either click the
   Configuration icon, or from the main Plover application menu, select
   `Preferences...`)
6. Open the Plugins tab
7. Check the box next to `plover_cycle_translations` to activate the plugin

## Usage

Using the "sent", "cent", and "scent" example above, the outlines for them in
Plover theory are:

- `"SEPBT": "sent"` - indicative of a [phonetic][] (how the word sounds)
  reading of "sent"
- `"KREPBT": "cent"` - indicative of an [orthographic][] (how the word is
  spelled) reading of "cent", using the [fingerspelled "C"][] `KR` chord
- `"SKREPBT": "scent"` - orthographic, similar to "cent"

If you wanted to standardise on the phonetic `SEPBT` outline for all three
words, you could use this plugin to create a dictionary entry as follows:

```json
"SEPBT": "=CYCLE:sent,cent,scent"
```

This will output "sent" when stroked. You then use a "selector stroke" to cycle
to the next word in the comma-separated list of words, in the order they are
defined. An example of a "selector stroke" dictionary entry would be:

```json
"R*R": "=CYCLE:NEXT"
```

As you cycle through the word list, each outputted word gets replaced with the
next word entry. Once you hit the end of the list, the cycle begins again: in
the example above, if you stroke `=CYCLE:NEXT` when you have output "scent",
it will be replaced with "sent".

Cycleable dictionary entries are not limited to just single stroke outlines.
Multiple stroke outline entries are also supported:

```json
"ABG/SEL": "=CYCLE:axel,axle,axil"
```

Non-text characters like emoji are also supported:

```json
"H-PBD": "=CYCLE:👍,👎,👊"
```

## Development

Clone from GitHub with [git][] and install test-related dependencies with
[pip][]:

```console
git clone git@github.com:paulfioravanti/plover-cycle-translations.git
cd plover-cycle-translations
python -m pip install --editable ".[test]"
```

If you are a [Tmuxinator][] user, you may find my [plover-cycle-translations
project file][] of reference.

### Python Version

Plover's Python environment currently uses version 3.9 (see Plover's
[`workflow_context.yml`][] to confirm the current version).

So, in order to avoid unexpected issues, use your runtime version manager to
make sure your local development environment also uses Python 3.9.x.

### Testing

- [Pylint][] is used for code quality
- [Mypy][] is used for static type checking

Currently, there is not enough logic in the plugin that doesn't depend on
internal state of the extension class to justify extraction to other modules.
Since the only parts of the plugin able to be tested are ones that do not rely
directly on Plover, automated testing with [Pytest][] has not really been
possible.

Run linting and type checking with the following commands:

```console
pylint plover_cycle_translations
mypy plover_cycle_translations
```

If you are a [`just`][] user, you may find the [`justfile`][] useful during
development in running multiple code quality commands. You can run the following
command from the project root directory:

```console
just
```

### Deploying Changes

After making any code changes, deploy the plugin into Plover with the following
command:

```console
plover --script plover_plugins install --editable .
```

> Where `plover` in the command is a reference to your locally installed version
> of Plover. See the [Invoke Plover from the command line][] page for details on
> how to create that reference.

When necessary, the plugin can be uninstalled via the command line with the
following command:

```console
plover --script plover_plugins uninstall plover-cycle-translations
```

[Alt-Tab]: https://en.wikipedia.org/wiki/Alt-Tab
[Build Status image]: https://github.com/paulfioravanti/plover-cycle-translations/actions/workflows/ci.yml/badge.svg
[Build Status url]: https://github.com/paulfioravanti/plover-cycle-translations/actions/workflows/ci.yml
[extension]: https://plover.readthedocs.io/en/latest/plugin-dev/extensions.html
[fingerspelled "C"]: https://www.artofchording.com/sounds/fingerspelling.html#letter-c
[Git]: https://git-scm.com/
[here]: https://github.com/paulfioravanti/steno-dictionaries/blob/main/dictionaries/cycleable.md
[homophones]: https://en.wikipedia.org/wiki/Homophone
[IME]: https://en.wikipedia.org/wiki/Input_method
[Invoke Plover from the command line]: https://github.com/openstenoproject/plover/wiki/Invoke-Plover-from-the-command-line
[`just`]: https://github.com/casey/just
[`justfile`]: ./test/justfile
[linting image]: https://img.shields.io/badge/linting-pylint-yellowgreen
[linting url]: https://github.com/pylint-dev/pylint
[macro]: https://plover.readthedocs.io/en/latest/plugin-dev/macros.html
[meta]: https://plover.readthedocs.io/en/latest/plugin-dev/metas.html
[Mypy]: https://github.com/python/mypy
[orthographic]: https://en.wikipedia.org/wiki/Orthography
[phonetic]: https://en.wikipedia.org/wiki/Phonetics
[pip]: https://pip.pypa.io/en/stable/
[plover-cycle-translations project file]: https://github.com/paulfioravanti/dotfiles/blob/master/tmuxinator/plover_cycle_translations.yml
[proper nouns]: https://en.wikipedia.org/wiki/Proper_noun
[PyPI]: https://pypi.org/
[PyPI downloads image]: https://img.shields.io/pypi/dm/plover-cycle-translations
[PyPI version image]: https://img.shields.io/pypi/v/plover-cycle-translations
[PyPI url]: https://pypi.org/project/plover-cycle-translations/
[Plover]: https://www.openstenoproject.org/
[Plover Plugins Registry]: https://github.com/openstenoproject/plover_plugins_registry
[plugin]: https://plover.readthedocs.io/en/latest/plugins.html#types-of-plugins
[Pylint]: https://github.com/pylint-dev/pylint
[Pytest]: https://docs.pytest.org/en/stable/
[`retro_toggle_asterisk`]: https://plover.readthedocs.io/en/latest/translation_language.html#other-formatting-actions
[Tmuxinator]: https://github.com/tmuxinator/tmuxinator
[`workflow_context.yml`]: https://github.com/openstenoproject/plover/blob/master/.github/workflows/ci/workflow_context.yml
