from pptx import Presentation
from pptx.util import Inches
A='/tmp/claude-0/-home-user--/f2046ef5-a5f5-5769-8dca-a4878d4046a0/scratchpad/an/figs7/'
p=Presentation('/home/user/-/채소10_윤정민.pptx')
MAP={8:{'Picture 26':'irr_cum.png','ET daily':'design_timeline.png'},
 9:{'Picture 19':'gsw_ts.png','Picture 20':'gsw_rec.png','그림 6':'bars_gsw.png','그림 9':'bars_fvfm.png'},
 10:{'Picture 22':'phi3.png','그림 9':'bars_phi3.png'},
 11:{'Picture 20':'params_aligned.png'},
}
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
# 8p 결론 박스: 건조·복합은 침수 종료(DAT 3)부터 50% 관수
import sys; sys.path.insert(0,'/tmp/claude-0/-home-user--/f2046ef5-a5f5-5769-8dca-a4878d4046a0/scratchpad')
from lib import set_para as _sp
cb8=[x for x in p.slides[7].shapes if x.name=='Conclusion Box'][0]
_sp(cb8.text_frame.paragraphs[0],'침수 72시간 후 정상 관수, 건조·복합은 침수 종료(DAT 3) 후부터 대조구의 50% 관수')
# 13,14: 그래프 4개로 분리, 블록·화살표·그래프 정렬 (블록 전체 폭 0.92~12.48 = 결론 박스와 동일)
import sys; sys.path.insert(0,'/tmp/claude-0/-home-user--/f2046ef5-a5f5-5769-8dca-a4878d4046a0/scratchpad')
from lib import fix_timing
for n,crop in ((13,'bean'),(14,'lettuce')):
    s=p.slides[n-1]
    for x in list(s.shapes):
        if x.name!='Conclusion Box' and abs(x.top/914400-2.35)<0.05 and x.height/914400>3.5: x._element.getparent().remove(x._element)
    sh=list(s.shapes)
    blocks=sorted([x for x in sh if x.name.startswith('Rounded Rectangle')],key=lambda x:x.left)
    arrows=sorted([x for x in sh if x.name.startswith('Right Arrow')],key=lambda x:x.left)
    labels=sorted([x for x in sh if x.name.startswith('직사각형') and abs(x.top/914400-2.0)<0.05],key=lambda x:x.left)
    W,X0=2.5,0.92; G=(11.56-4*W)/3
    for i,b in enumerate(blocks): b.left=Inches(X0+i*(W+G)); b.width=Inches(W)
    for i,a in enumerate(arrows): a.width=Inches(0.34); a.left=Inches(X0+i*(W+G)+W+(G-0.34)/2)
    for i,l in enumerate(labels): l.left=Inches(X0+i*(W+G)+(W-2.3)/2)
    for i,nm in enumerate(('1_gsw','2_light','3_photo','4_growth')):
        pw=2.9; cx=X0+i*(W+G)+W/2
        pic=s.shapes.add_picture(A+f'{crop}_{nm}.png',Inches(cx-pw/2),Inches(2.35),Inches(pw),Inches(3.9)); pic.name=f'Graph {nm}'
    fix_timing(s)
p.save('/home/user/-/채소10_윤정민_수정.pptx')
