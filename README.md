# Veil word lists

The word lists Veil's word games (Word Grid, Anagrams, Word Blocks) use in Spanish, French and Filipino, with the dictionaries they were made from and the scripts that made them. Veil bundles the lists in its phone app, in Veil Desktop and on its games-by-link web page; this repository is where anyone who has Veil can get their source.

## What's here

| Folder | What |
|---|---|
| `lists/` | The lists as Veil ships them (`words_es.txt.gz`, `words_fr.txt.gz`, `words_fil.txt.gz`: gzip, one lowercase word a line) and their notices (`LICENSE-words-*.txt`), exactly as Veil includes them. |
| `sources/es/` | The Spanish spell-check dictionaries of the RLA-ES project, version 2.9, as LibreOffice ships them: https://github.com/LibreOffice/dictionaries, folder `es/`, commit `c0865a85eb67dc377f2cf8e8fe2c4fa9e53f0dcb` (variants es_ES, es_MX, es_AR, es_CO, es_US, es_CL, es_PE, es_VE). |
| `sources/fr/` | The French spell-check dictionary by Olivier R. and contributors (Grammalecte, https://grammalecte.net/), "Classique" 7.7, as LibreOffice ships it: same repository and commit, folder `fr_FR/dictionaries/`. |
| `sources/tl/` | The Tagalog word list by Ramil Sagum and Kevin P. Scannell: https://github.com/jmalonzo/tl-wordlist, commit `1af045cf945a4e0e1d237e6dda8fe43e1a6230dc`. |
| `scripts/` | The scripts that made the lists. |

Every `.dic`, `.aff` and `tl.wl` file under `sources/` is byte for byte the file in the upstream commit named above (their git object hashes match).

## How the lists were made

```
python -I scripts/build_words.py sources out
python -I scripts/make_notices.py sources out <Veil checkout>
```

`build_words.py` spells out every word form the Hunspell affix rules give (`hunspell_expand.py`; the Tagalog list is already spelled out), keeps lowercase words of 3 to 16 letters (no names, abbreviations, numbers, or words with hyphens or apostrophes) and takes accents off: Spanish keeps ñ as its own letter, French writes é as e, ç as c, and œ and æ as oe and ae. Spanish verb forms with pronouns joined on by the affix rules (dámelo, cómetelo) are left out, as Spanish word games do. Nothing else is changed, added or removed. `make_notices.py` gzips the lists (no name or time, so the same input always gives the same file) and writes their notices.

## Licences

- **Spanish:** the dictionaries come under a choice of the GNU GPL version 3 or later, the GNU LGPL version 3 or later, or the MPL version 1.1 or later (`sources/es/LICENSE.md`). Veil uses the list under the **Mozilla Public License 2.0**, as "MPL version 1.1 or later" allows.
- **French:** **Mozilla Public License 2.0** (`sources/fr/MPL-2.0.txt`).
- **Filipino (Tagalog):** **GNU General Public License, version 2 or later** (`sources/tl/Copyright`, `sources/tl/COPYING`); Veil uses it under version 3 or later.
- **The scripts in `scripts/`:** Mozilla Public License 2.0 (`scripts/LICENSE-MPL-2.0.txt`).

Each list's full notice, with its licence text, is in `lists/LICENSE-words-<language>.txt`.
