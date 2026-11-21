"""Writes the word lists (gzip -9 -n style, no name or time) and their notice files into Veil.

usage: python -I make_notices.py <download dir> <out dir> <Veil checkout> (see build_words.py)
"""
import gzip
import os
import sys

dl, out, root = sys.argv[1:4]


def read(*p):
    with open(os.path.join(dl, *p), 'rb') as f:
        data = f.read()
    try:
        t = data.decode('utf-8')
    except UnicodeDecodeError:
        t = data.decode('iso-8859-1')
    return t.lstrip('﻿').replace('\r\n', '\n').rstrip('\n') + '\n'


MADE = """How Veil made it: every word form the dictionaries' affix rules give was spelled out (the
script is tool/game_words/ in Veil's source), then only lowercase words of 3 to 16 letters were
kept (no names, abbreviations, numbers, or words with hyphens or apostrophes) and accents were
taken off{extra}. Nothing else was changed, added or removed.
"""

RULE = '=' * 78 + '\n'

# Where anyone who has Veil can get the dictionaries a list was made from and the scripts that made it.
SOURCES = (
    'The dictionaries this list was made from, exactly as their projects publish them, and the\n'
    'scripts that made the list from them are at https://github.com/gak3965/veil-word-lists.\n\n'
)

notices = {
    'es': (
        'Spanish word list for Veil\'s word games (words_es.txt.gz)\n' + RULE + '\n'
        'Made from the Spanish spell-check dictionaries of the RLA-ES project, version 2.9, as\n'
        'shipped by LibreOffice: https://github.com/LibreOffice/dictionaries, folder es/, commit\n'
        'c0865a85eb67dc377f2cf8e8fe2c4fa9e53f0dcb (variants es_ES, es_MX, es_AR, es_CO, es_US,\n'
        'es_CL, es_PE and es_VE, together).\n\n'
        + MADE.format(extra=' (ñ kept as its own letter). Verb forms with pronouns joined on by the\naffix rules (dámelo, cómetelo) were left out, as Spanish word games do')
        + '\nThe dictionaries come under a choice of three licences: the GNU GPL version 3 or later,\n'
        'the GNU LGPL version 3 or later, or the MPL version 1.1 or later. Veil uses this list under\n'
        'the Mozilla Public License, version 2.0 (as "MPL version 1.1 or later" allows), whose text\n'
        'is at the end of this file. The list itself is its source form: words_es.txt.gz unpacks to\n'
        'plain text, one word a line.\n\n' + SOURCES
        + RULE + 'The dictionary\'s README (README_hunspell_es.txt)\n' + RULE + read('es', 'README_hunspell_es.txt')
        + '\n' + RULE + 'LICENSE.md\n' + RULE + read('es', 'LICENSE.md')
        + '\n' + RULE + 'Mozilla Public License, version 2.0\n' + RULE + read('fr', 'MPL-2.0.txt')
    ),
    'fr': (
        'French word list for Veil\'s word games (words_fr.txt.gz)\n' + RULE + '\n'
        'Made from the French spell-check dictionary by Olivier R. and contributors (Grammalecte,\n'
        'https://grammalecte.net/), "Classique" version 7.7, as shipped by LibreOffice:\n'
        'https://github.com/LibreOffice/dictionaries, folder fr_FR/dictionaries/, commit\n'
        'c0865a85eb67dc377f2cf8e8fe2c4fa9e53f0dcb.\n\n'
        + MADE.format(extra=' (é = e, ç = c; œ and æ written oe and ae)')
        + '\nThis Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a\n'
        'copy of the MPL was not distributed with this file, You can obtain one at\n'
        'http://mozilla.org/MPL/2.0/. The list itself is its source form: words_fr.txt.gz unpacks\n'
        'to plain text, one word a line. Its text is at the end of this file.\n\n' + SOURCES
        + RULE + 'The dictionary\'s README (README_dict_fr.txt)\n' + RULE + read('fr', 'README_dict_fr.txt')
        + '\n' + RULE + 'Mozilla Public License, version 2.0\n' + RULE + read('fr', 'MPL-2.0.txt')
    ),
    'fil': (
        'Filipino (Tagalog) word list for Veil\'s word games (words_fil.txt.gz)\n' + RULE + '\n'
        'Made from the Tagalog spell-check word list by Ramil Sagum and Kevin P. Scannell, as kept\n'
        'at https://github.com/jmalonzo/tl-wordlist (tl.wl, commit\n'
        '1af045cf945a4e0e1d237e6dda8fe43e1a6230dc), the list the Hunspell and Aspell Tagalog\n'
        'dictionaries (tl_PH) are built from.\n\n'
        + MADE.format(extra=' (the list has none)').replace("every word form the dictionaries' affix rules give was spelled out (the\nscript is tool/game_words/ in Veil's source), then only", "the list already spells out every word form (the script is tool/game_words/\nin Veil's source); only")
        + '\nIt is free software under the GNU General Public License, version 2 or (at your option)\n'
        'any later version; Veil uses it under version 3 or later. The notice and version 2\'s text follow.\n\n' + SOURCES
        + RULE + 'Copyright\n' + RULE + read('tl', 'Copyright')
        + '\n' + RULE + 'README\n' + RULE + read('tl', 'README')
        + '\n' + RULE + 'GNU General Public License, version 2\n' + RULE + read('tl', 'COPYING')
    ),
}

places = [os.path.join(root, 'assets', 'games'), os.path.join(root, 'desktop', 'src', 'core'), os.path.join(root, 'server', 'public', 'play')]
for p in places:
    os.makedirs(p, exist_ok=True)
for lang, text in notices.items():
    with open(os.path.join(out, f'words_{lang}.txt'), 'rb') as f:
        raw = f.read()
    gz = gzip.compress(raw, compresslevel=9, mtime=0)
    for p in places:
        name = ('game_words_' if 'desktop' in p else 'words_') + lang + '.txt.gz'
        with open(os.path.join(p, name), 'wb') as f:
            f.write(gz)
        with open(os.path.join(p, f'LICENSE-words-{lang}.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
    print(lang, len(raw), len(gz))
