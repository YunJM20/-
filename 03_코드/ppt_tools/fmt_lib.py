# -*- coding: utf-8 -*-
import re, copy
from pptx import Presentation
from pptx.oxml.ns import qn
SUPMAP = {"⁻": "−", "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}
SUPCH = "".join(SUPMAP)
NA = r"(?<![A-Za-z0-9])"
NB = r"(?![A-Za-z0-9])"
# (정규식, 아래첨자/위첨자로 만들 그룹 번호 목록과 종류)
TOKENS = [
    ("sup", re.compile("[" + SUPCH + "]+")),
    ("sub", re.compile(r"(?<=CO)₂")),
    ("sub", re.compile(NA + r"g(sw)" + NB)),
    ("sub", re.compile(r"Φ(PSII|NPQ|NO)(?![A-Za-z])")),
    ("sub", re.compile(NA + r"V(cmax)" + NB)),
    ("sub", re.compile(NA + r"[JAP](max)" + NB)),
    ("sub", re.compile(NA + r"R(d)" + NB)),
    ("sub", re.compile(NA + r"F([vmos])" + NB)),
]
UNITDOT = re.compile(r"([A-Za-zµ]+(?:[" + SUPCH + r"]+)?) (?=[A-Za-zµ]+[" + SUPCH + "])")


def prep(t):
    return UNITDOT.sub(lambda m: m.group(1) + "·", t)


def spans(t):
    """[(start,end,kind,text_out)] 겹치지 않는 변환 구간"""
    out = []
    for kind, rx in TOKENS:
        for m in rx.finditer(t):
            if kind == "sup":
                out.append((m.start(), m.end(), "sup", "".join(SUPMAP[c] for c in m.group(0))))
            elif rx.pattern.startswith("(?<=CO)"):
                out.append((m.start(), m.end(), "sub", "2"))
            else:
                out.append((m.start(1), m.end(1), "sub", m.group(1)))
    out.sort()
    res, last = [], -1
    for s, e, k, x in out:
        if s >= last:
            res.append((s, e, k, x)); last = e
    return res


def convert_run(r_el):
    """a:r 하나를 변환. 변환이 없으면 None"""
    t_el = r_el.find(qn("a:t"))
    if t_el is None or not t_el.text:
        return 0
    t0 = t_el.text
    t = prep(t0)
    sp = spans(t)
    if t == t0 and not sp:
        return 0
    pieces, pos = [], 0
    for s, e, k, x in sp:
        if s > pos:
            pieces.append((t[pos:s], None))
        pieces.append((x, k)); pos = e
    if pos < len(t):
        pieces.append((t[pos:], None))
    parent = r_el.getparent(); idx = parent.index(r_el)
    for j, (txt, kind) in enumerate(pieces):
        nr = copy.deepcopy(r_el)
        nr.find(qn("a:t")).text = txt
        if kind:
            rpr = nr.find(qn("a:rPr"))
            if rpr is None:
                from lxml import etree
                rpr = etree.SubElement(nr, qn("a:rPr")); nr.remove(rpr); nr.insert(0, rpr)
            rpr.set("baseline", "30000" if kind == "sup" else "-25000")
        parent.insert(idx + 1 + j, nr)
    parent.remove(r_el)
    return len(pieces)


def all_paragraphs(prs):
    for sl in prs.slides:
        roots = [sl._element]
        if sl.has_notes_slide:
            roots.append(sl.notes_slide._element)
        for root in roots:
            for p in root.iter(qn("a:p")):
                yield sl, p
