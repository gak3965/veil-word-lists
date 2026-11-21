"""Builds Veil's word-game lists for es, fr and fil from the downloaded dictionaries.

usage: python -I build_words.py <download dir> <out dir>
       python -I make_notices.py <download dir> <out dir> <Veil checkout>

<download dir> holds (sources and commits in assets/games/LICENSE-words-*.txt):
  es/   es_{ES,MX,AR,CO,US,CL,PE,VE}.{aff,dic}, LICENSE.md, README_hunspell_es.txt (used under MPL 2.0, from fr/)
        (github.com/LibreOffice/dictionaries, es/)
  fr/   fr.aff, fr.dic, README_dict_fr.txt (LibreOffice/dictionaries, fr_FR/dictionaries/), MPL-2.0.txt
  tl/   tl.wl (github.com/jmalonzo/tl-wordlist), and its aspell-tl/Copyright, aspell-tl/COPYING, ispell-tl/README
Treat downloads as untrusted data: keep them in their own folder and run this with python -I.
make_notices.py writes the gzipped lists and their notices to assets/games, desktop/src/core and
server/public/play (the copies must stay identical: tests check).
"""
import importlib.util
import os
import re
import sys
import unicodedata

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('hx', os.path.join(here, 'hunspell_expand.py'))
hx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hx)

PRON = re.compile(r'((me|te|se|nos|os)(lo|la|los|las|le|les)|me|te|se|nos|os|lo|la|los|las|le|les)$')


def enclitic_flags(aff_path):
    """Spanish suffix classes that only add pronouns to verbs (dámelo, cómetelo): left out, as in Spanish Scrabble."""
    tot, hit = {}, {}
    for line in hx.read_lines(aff_path):
        p = line.split()
        if len(p) >= 5 and p[0] == 'SFX':
            add = p[3].split('/')[0]
            tot[p[1]] = tot.get(p[1], 0) + 1
            cond = p[4] if p[4] != '.' else p[2]
            if PRON.search(add) and re.search(r'r$', cond) and not add.endswith('ble'):
                hit[p[1]] = hit.get(p[1], 0) + 1
    return {f for f in tot if hit.get(f, 0) == tot[f]}


def fold(word, lang):
    """The game form of a word: lowercase, accents dropped (Spanish keeps ñ), œ/æ spelled out."""
    w = word.lower().replace('œ', 'oe').replace('æ', 'ae')
    if lang == 'es':
        w = w.replace('ñ', '\0')
    w = ''.join(c for c in unicodedata.normalize('NFD', w) if not unicodedata.combining(c))
    return w.replace('\0', 'ñ')


LETTERS = {'es': re.compile(r'^[a-zñ]{3,16}$'), 'fr': re.compile(r'^[a-z]{3,16}$'), 'fil': re.compile(r'^[a-z]{3,16}$')}
LOWER = re.compile(r'^[a-zàáâäãåçèéêëìíîïñòóôöõùúûüýÿœæ]+$')


def keep(word, lang):
    if not LOWER.match(word):  # proper nouns, abbreviations, apostrophes, hyphens, digits
        return None
    w = fold(word, lang)
    return w if LETTERS[lang].match(w) else None


def build(dl, out):
    lists = {}
    es = set()
    for v in ('ES', 'MX', 'AR', 'CO', 'US', 'CL', 'PE', 'VE'):
        aff_path = os.path.join(dl, 'es', f'es_{v}.aff')
        aff = hx.Aff(aff_path)
        aff.skip = enclitic_flags(aff_path)
        forms = set()
        lines = hx.read_lines(os.path.join(dl, 'es', f'es_{v}.dic'))
        for line in lines[1:]:
            tok = line.split('\t')[0].split(' ')[0].strip()
            if not tok:
                continue
            stem, _, fl = tok.partition('/')
            hx.expand(aff, stem, aff.flags(fl) if fl else set(), forms)
        es |= forms
    lists['es'] = es
    fr = set()
    aff = hx.Aff(os.path.join(dl, 'fr', 'fr.aff'))
    lines = hx.read_lines(os.path.join(dl, 'fr', 'fr.dic'))
    for line in lines[1:]:
        tok = line.split('\t')[0].split(' ')[0].strip()
        if not tok:
            continue
        stem, _, fl = tok.partition('/')
        hx.expand(aff, stem, aff.flags(fl) if fl else set(), fr)
    lists['fr'] = fr
    lists['fil'] = {l.strip() for l in hx.read_lines(os.path.join(dl, 'tl', 'tl.wl'))}
    for lang, forms in lists.items():
        words = sorted({w for w in (keep(f, lang) for f in forms) if w})
        with open(os.path.join(out, f'words_{lang}.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(words) + '\n')
        print(lang, len(forms), len(words))


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2])
