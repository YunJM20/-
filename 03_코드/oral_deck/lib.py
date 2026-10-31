import copy, re
from pptx import Presentation
from pptx.util import Emu, Inches
from lxml import etree
A='{http://schemas.openxmlformats.org/drawingml/2006/main}'

def _runs(p): return p._p.findall(A+'r')

def set_para(p, text, bold=None):
    """Rewrite paragraph text keeping first run's format. Markup: _{sub} ^{sup}."""
    runs=_runs(p)
    assert runs, 'no run in paragraph'
    base=runs[0]
    for r in runs[1:]: p._p.remove(r)
    # remove endParaRPr stays
    toks=re.split(r'(_\{[^}]*\}|\^\{[^}]*\})', text)
    prev=base; first=True
    for t in toks:
        if not t: continue
        kind=None
        if t.startswith('_{'): kind='sub'; t=t[2:-1]
        elif t.startswith('^{'): kind='sup'; t=t[2:-1]
        if first: r=base; first=False
        else:
            r=copy.deepcopy(base); prev.addnext(r)
        r.find(A+'t').text=t
        rpr=r.find(A+'rPr')
        if rpr is None:
            rpr=etree.SubElement(r,A+'rPr'); r.insert(0,rpr)
        if kind=='sub': rpr.set('baseline','-25000')
        elif kind=='sup': rpr.set('baseline','30000')
        else:
            if 'baseline' in rpr.attrib: del rpr.attrib['baseline']
        if bold is not None: rpr.set('b','1' if bold else '0')
        prev=r
    if first:  # empty text
        base.find(A+'t').text=''

def set_paras(shape, texts):
    """Set shape paragraphs to texts; clone last para if more texts than paras, drop extras."""
    tf=shape.text_frame
    ps=list(tf.paragraphs)
    while len(ps)<len(texts):
        new=copy.deepcopy(ps[-1]._p); ps[-1]._p.addnext(new)
        ps=list(tf.paragraphs)
    for p in ps[len(texts):]:
        p._p.getparent().remove(p._p)
    ps=list(tf.paragraphs)
    for p,t in zip(ps,texts): set_para(p,t)

def set_cell(cell, text):
    tf=cell.text_frame
    p=tf.paragraphs[0]
    runs=_runs(p)
    if not runs:
        r=etree.SubElement(p._p,A+'r'); etree.SubElement(r,A+'t')
        epr=p._p.find(A+'endParaRPr')
        if epr is not None:
            rpr=copy.deepcopy(epr); rpr.tag=A+'rPr'; r.insert(0,rpr); p._p.remove(epr); p._p.append(epr)
        runs=_runs(p)
    if len(runs)>=2 and ' (' in text and '_{' not in text:
        main,tail=text.split(' (',1)
        # find a small-format run: the last run that starts with '(' or ' ('
        small=None
        for r in runs[1:]:
            if r.find(A+'t').text.strip().startswith('('): small=r; break
        if small is None: small=runs[-1]
        for r in runs:
            if r is not runs[0] and r is not small: p._p.remove(r)
        runs[0].find(A+'t').text=main
        small.find(A+'t').text=' ('+tail
    else:
        set_para(p,text)
    for q in tf.paragraphs[1:]: q._p.getparent().remove(q._p)

def set_table(table, rows, start_row=0, start_col=0):
    for i,row in enumerate(rows):
        for j,v in enumerate(row):
            if v is None: continue
            set_cell(table.cell(start_row+i,start_col+j), v)

def table_of(slide, idx=0):
    ts=[s for s in slide.shapes if getattr(s,'has_table',False) and s.has_table]
    return ts[idx].table

def sh(slide,name_or_idx):
    return list(slide.shapes)[name_or_idx]

def replace_all_runs(shape, old, new):
    n=0
    if shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                if old in r.text: r.text=r.text.replace(old,new); n+=1
    return n

import io
def replace_picture(slide, shape, pil, valign='top', maxh=None, maxw=None):
    """Replace picture with PIL image fitted inside the old slot (uniform scale)."""
    L,T,W,H=shape.left,shape.top,shape.width,shape.height
    if maxh: H=int(maxh*914400)
    if maxw: W=int(maxw*914400)
    ar=pil.width/pil.height
    w=W; h=int(w/ar)
    if h>H: h=H; w=int(h*ar)
    left=L+(W-w)//2 if True else L
    top=T if valign=='top' else T+(H-h)//2
    b=io.BytesIO(); pil.save(b,format='PNG'); b.seek(0)
    new=slide.shapes.add_picture(b,left,top,w,h)
    new.name=shape.name
    # keep z-order
    el=shape._element; el.addprevious(new._element); el.getparent().remove(el)
    return new

def set_lead(p, lead, body):
    """Paragraph with bold lead run + normal body runs (markup in body)."""
    runs=_runs(p)
    if len(runs)<2:
        return set_para(p, lead+' '+body)
    lead_r, body_r = runs[0], runs[1]
    for r in runs[2:]: p._p.remove(r)
    # make body_r hold body text with markup using set_para-like logic
    lead_r.find(A+'t').text=lead
    # temporarily isolate body run
    p._p.remove(lead_r)
    set_para(p, body)           # operates on body_r
    p._p.insert(list(p._p).index(_runs(p)[0]), lead_r)
    if p._p.find(A+'pPr') is not None:
        pass

def set_paras2(shape, items):
    """items: str or (lead, body). Clone last paragraph if needed."""
    tf=shape.text_frame; ps=list(tf.paragraphs)
    while len(ps)<len(items):
        new=copy.deepcopy(ps[-1]._p); ps[-1]._p.addnext(new); ps=list(tf.paragraphs)
    for p in ps[len(items):]: p._p.getparent().remove(p._p)
    for p,it in zip(list(tf.paragraphs),items):
        if isinstance(it,tuple): set_lead(p,*it)
        else: set_para(p,it,bold=False)

def adopt_paras(dst, src):
    """Replace dst paragraphs by deep copies of src paragraphs (same template styles)."""
    d=dst.text_frame._txBody; s=src.text_frame._txBody
    for p in d.findall(A+'p'): d.remove(p)
    for p in s.findall(A+'p'): d.append(copy.deepcopy(p))

def delete_row(table, idx):
    tr=table._tbl.tr_lst[idx]; table._tbl.remove(tr)

def add_table_copy(dst_slide, src_shape, remove_existing=True):
    if remove_existing:
        for x in list(dst_slide.shapes):
            if getattr(x,'has_table',False) and x.has_table: x._element.getparent().remove(x._element)
    el=copy.deepcopy(src_shape._element); dst_slide.shapes._spTree.append(el)
    return el

def by_name(slide,name,nth=0):
    return [x for x in slide.shapes if x.name==name][nth]

def move(shape,left=None,top=None,width=None,height=None):
    if left is not None: shape.left=Inches(left)
    if top is not None: shape.top=Inches(top)
    if width is not None: shape.width=Inches(width)
    if height is not None: shape.height=Inches(height)

def tails_like(table, rows, cols, like_col):
    """Re-style 'main (tail)' cells so tail run is small like like_col cell in same row."""
    for r in rows:
        like=table.cell(r,like_col)
        lruns=_runs(like.text_frame.paragraphs[0])
        if len(lruns)<2: continue
        for c in cols:
            cell=table.cell(r,c); txt=cell.text_frame.text
            if ' (' not in txt: continue
            main,tail=txt.split(' (',1)
            p=cell.text_frame.paragraphs[0]
            for rr in _runs(p): p._p.remove(rr)
            m=copy.deepcopy(lruns[0]); t=copy.deepcopy(lruns[-1])
            m.find(A+'t').text=main; t.find(A+'t').text=' ('+tail
            end=p._p.find(A+'endParaRPr')
            if end is not None: end.addprevious(m); end.addprevious(t)
            else: p._p.append(m); p._p.append(t)

def tighten(table, rows, cols):
    for r in rows:
        for c in cols:
            for run in _runs(table.cell(r,c).text_frame.paragraphs[0]):
                t=run.find(A+'t')
                if t is not None and t.text and '; ' in t.text: t.text=t.text.replace('; ',';')
