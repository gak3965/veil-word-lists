"""Expands a Hunspell .dic/.aff pair into every word form it accepts (one per line, UTF-8).

Handles FLAG (single char, UTF-8, long, num), AF aliases, prefixes and suffixes with conditions,
two suffix levels (continuation classes), prefix x suffix cross products, prefix continuation
suffixes, NEEDAFFIX, FORBIDDENWORD and CIRCUMFIX (forms with a lone circumfix affix are dropped).
Compounding is not expanded (word games don't need it).

usage: python -I hunspell_expand.py file.aff file.dic [more.aff more.dic ...] > out.txt
"""
import re
import sys


def read_lines(path):
    with open(path, 'rb') as f:
        data = f.read()
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        text = data.decode('iso-8859-1')
    return text.lstrip('﻿').splitlines()


class Aff:
    def __init__(self, path):
        self.flag = 'char'
        self.af = {}
        self.need = self.forbid = self.circ = None
        self.pfx, self.sfx = {}, {}
        self.skip = set()
        lines = read_lines(path)
        for line in lines:
            parts = line.split()
            if not parts or parts[0].startswith('#'):
                continue
            if parts[0] == 'FLAG' and len(parts) > 1:
                self.flag = parts[1]
        i = 0
        while i < len(lines):
            parts = lines[i].split()
            i += 1
            if not parts or parts[0].startswith('#'):
                continue
            key = parts[0]
            if key == 'AF' and len(parts) > 1 and parts[1].isdigit():
                n = int(parts[1])
                for k in range(n):
                    p = lines[i + k].split()
                    self.af[str(k + 1)] = self.flags(p[1]) if len(p) > 1 else set()
                i += n
            elif key in ('NEEDAFFIX', 'PSEUDOROOT') and len(parts) > 1:
                self.need = next(iter(self.flags(parts[1])))
            elif key == 'FORBIDDENWORD' and len(parts) > 1:
                self.forbid = next(iter(self.flags(parts[1])))
            elif key == 'CIRCUMFIX' and len(parts) > 1:
                self.circ = next(iter(self.flags(parts[1])))
            elif key in ('PFX', 'SFX') and len(parts) >= 4 and parts[3].isdigit() and parts[2] in ('Y', 'N'):
                fl = next(iter(self.flags(parts[1])))
                cross = parts[2] == 'Y'
                n = int(parts[3])
                rules = []
                for k in range(n):
                    p = lines[i + k].split()
                    if len(p) < 4 or p[0] != key:
                        continue
                    strip = '' if p[2] == '0' else p[2]
                    add, _, cont = p[3].partition('/')
                    add = '' if add == '0' else add
                    cont = (self.af.get(cont) if cont.isdigit() and self.af else self.flags(cont)) if cont else set()
                    cond = p[4] if len(p) > 4 else '.'
                    rx = self.cond(cond, key == 'PFX')
                    rules.append((strip, add, cont, rx, cross))
                i += n
                (self.pfx if key == 'PFX' else self.sfx).setdefault(fl, []).extend(rules)

    def flags(self, s):
        if self.af and s.isdigit() and s in self.af:
            return set(self.af[s])
        if self.flag == 'long':
            return {s[k:k + 2] for k in range(0, len(s) - 1, 2)}
        if self.flag == 'num':
            return {x for x in s.split(',') if x}
        return set(s)

    @staticmethod
    def cond(c, prefix):
        if c == '.':
            return None
        out, k = '', 0
        while k < len(c):
            ch = c[k]
            if ch == '[':
                j = c.index(']', k)
                body = c[k + 1:j]
                neg = body.startswith('^')
                if neg:
                    body = body[1:]
                out += '[' + ('^' if neg else '') + ''.join(re.escape(x) for x in body) + ']'
                k = j + 1
            elif ch == '.':
                out += '.'
                k += 1
            else:
                out += re.escape(ch)
                k += 1
        return re.compile(('^' + out) if prefix else (out + '$'))


def sfx_apply(rule, w):
    strip, add, cont, rx, cross = rule
    if strip and not w.endswith(strip):
        return None
    if rx is not None and not rx.search(w):
        return None
    if len(strip) >= len(w) and strip:
        # FULLSTRIP lets the whole word go.
        pass
    return w[:len(w) - len(strip)] + add


def pfx_apply(rule, w):
    strip, add, cont, rx, cross = rule
    if strip and not w.startswith(strip):
        return None
    if rx is not None and not rx.search(w):
        return None
    return add + w[len(strip):]


def expand(aff, stem, flags, out):
    def ok(cont):
        return (aff.need is None or aff.need not in cont) and (aff.circ is None or aff.circ not in cont)

    if aff.forbid is not None and aff.forbid in flags:
        return
    if aff.need is None or aff.need not in flags:
        out.add(stem)
    sfx_forms = []  # (word, cross)
    for f in flags - aff.skip:
        for r in aff.sfx.get(f, ()):
            w = sfx_apply(r, stem)
            if w is None:
                continue
            if ok(r[2]):
                out.add(w)
            sfx_forms.append((w, r[4]))
            for f2 in r[2]:
                for r2 in aff.sfx.get(f2, ()):
                    w2 = sfx_apply(r2, w)
                    if w2 is None:
                        continue
                    if ok(r2[2]):
                        out.add(w2)
                    sfx_forms.append((w2, r[4] and r2[4]))
    for f in flags:
        for p in aff.pfx.get(f, ()):
            pw = pfx_apply(p, stem)
            if pw is None:
                continue
            if ok(p[2]):
                out.add(pw)
            if p[4]:
                for w, cross in sfx_forms:
                    if cross:
                        x = pfx_apply(p, w)
                        if x is not None:
                            out.add(x)
            for f2 in p[2]:
                for r in aff.sfx.get(f2, ()):
                    x = sfx_apply(r, stem)
                    if x is not None:
                        x = pfx_apply(p, x)
                        if x is not None and ok(r[2]):
                            out.add(x)


def main(args):
    words = set()
    for k in range(0, len(args), 2):
        aff = Aff(args[k])
        lines = read_lines(args[k + 1])
        start = 1 if lines and lines[0].strip().isdigit() else 0
        for line in lines[start:]:
            tok = line.split('\t')[0].split(' ')[0].strip()
            if not tok or tok.startswith('#'):
                continue
            stem, _, fl = tok.partition('/')
            flags = aff.flags(fl) if fl else set()
            expand(aff, stem, flags, words)
    sys.stdout.reconfigure(encoding='utf-8', newline='\n')
    for w in sorted(words):
        sys.stdout.write(w + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])
