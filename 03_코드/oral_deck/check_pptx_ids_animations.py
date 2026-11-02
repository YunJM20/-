import sys, zipfile, re, collections
from lxml import etree
f=sys.argv[1]; z=zipfile.ZipFile(f)
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
pres=etree.fromstring(z.read('ppt/presentation.xml'))
rels=etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
rid2t={r.get('Id'):r.get('Target') for r in rels}
order=[rid2t[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')] for s in pres.find('p:sldIdLst',ns)]
print(f, len(order),'slides')
bad=0
for i,t in enumerate(order,1):
    x=etree.fromstring(z.read('ppt/'+t))
    ids=[e.get('id') for e in x.iterfind('.//p:cNvPr',ns)]
    dup=[k for k,v in collections.Counter(ids).items() if v>1]
    tm=x.find('.//p:timing',ns)
    tg=[e.get('spid') for e in x.iterfind('.//p:spTgt',ns)] if tm is not None else []
    missing=[g for g in tg if g not in ids]
    trans=x.find('.//p:transition',ns)
    flag=bool(dup or missing)
    if flag or tm is not None:
        print(i,t,'timing' if tm is not None else '','dupIDs',dup,'anim targets',tg,'MISSING',missing)
    bad+=flag
print('slides with problems:',bad)
