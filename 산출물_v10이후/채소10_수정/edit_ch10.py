from pptx import Presentation
from pptx.util import Inches
A='/tmp/claude-0/-home-user--/f2046ef5-a5f5-5769-8dca-a4878d4046a0/scratchpad/an/figs7/'
p=Presentation('/home/user/-/채소10_윤정민.pptx')
MAP={8:{'Picture 26':'irr_cum.png','ET daily':'design_timeline.png'},
 9:{'Picture 19':'gsw_ts.png','Picture 20':'gsw_rec.png','그림 6':'bars_gsw.png','그림 9':'bars_fvfm.png'},
 10:{'Picture 22':'phi3.png','그림 9':'bars_phi3.png'},
 13:{'Picture 65':'recap3_bean.png','그림 7':'gsw_P2_bean.png'},
 14:{'Picture 65':'recap3_lettuce.png','그림 8':'gsw_P2_lettuce.png'}}
def walk(shs):
    for x in shs:
        if x.shape_type==6: yield from walk(x.shapes)
        else: yield x
for n,m in MAP.items():
    for x in walk(p.slides[n-1].shapes):
        if x.shape_type==13 and x.name in m and x.width>914400*2.5:
            part=x.part.related_part(x._element.blipFill.blip.rEmbed); part._blob=open(A+m[x.name],'rb').read()
            if m[x.name].startswith('gsw_P2'):
                from PIL import Image; w=Image.open(A+m[x.name]).size[0]/300; x.width=Inches(w)
            print(n,x.name,m[x.name])
# 13,14: 블록·화살표 겹침 해소 (블록 2.5in, 간격 0.5in, 화살표는 간격 중앙)
for n in (13,14):
    s=p.slides[n-1]; sh=list(s.shapes)
    blocks=sorted([x for x in sh if x.name.startswith('Rounded Rectangle')],key=lambda x:x.left)
    arrows=sorted([x for x in sh if x.name.startswith('Right Arrow')],key=lambda x:x.left)
    labels=sorted([x for x in sh if x.name.startswith('직사각형') and abs(x.top/914400-2.0)<0.05],key=lambda x:x.left)
    W,G,X0=2.5,0.5,1.06
    for i,b in enumerate(blocks): b.left=Inches(X0+i*(W+G)); b.width=Inches(W)
    for i,a in enumerate(arrows): a.width=Inches(0.34); a.left=Inches(X0+i*(W+G)+W+(G-0.34)/2)
    for i,l in enumerate(labels): l.left=Inches(X0+i*(W+G)+(W-2.3)/2)
p.save('/home/user/-/채소10_윤정민_수정.pptx')
