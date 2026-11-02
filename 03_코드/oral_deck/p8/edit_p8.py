import sys,re,copy,pandas as pd; sys.path.insert(0,'.')
from lib import *
from pptx.util import Pt,Inches
from pptx.dml.color import RGBColor
R='/home/user/-/'; AN='an/'
src=open('oral_b.py').read()
for fn in ('bottom_border','compact_table','drop_col','set_widths'):
    m=re.search(r'\ndef '+fn+r'\(.*?(?=\ndef |\n# =====|\nMM=)',src,flags=re.S); exec(m.group(0))
prs=Presentation(R+'구두발표_콩vs로메인상추_v10.pptx')
ids=prs.slides._sldIdLst; sl=list(ids)
for i,x in reversed(list(enumerate(sl))):
    if i!=7: prs.part.drop_rel(x.rId); ids.remove(x)
s=prs.slides[0]
PNS='{http://schemas.openxmlformats.org/presentationml/2006/main}'
def rm(sh): sh._element.getparent().remove(sh._element)
for x in list(s.shapes):
    if x.shape_type==6: rm(x)
pics=[x for x in s.shapes if x.shape_type==13 and x.name.startswith('Picture')]
for x in pics: rm(x)
tbx=[x for x in s.shapes if getattr(x,'has_table',False) and x.has_table][0]
W=5.3; H=W*765/2250
XL,XR=0.8,7.1; Y1=1.2; Y2=Y1+H+0.04
for x,files in ((XL,('an/figs4/gsw_ts.png','an/figs4/gsw_rec.png')),(XR,('an/figs6/fvfm_ts.png','an/figs6/fvfm_rec.png'))):
    for y,f in zip((Y1,Y2),files): s.shapes.add_picture(f if f.startswith('/') else f,Inches(x),Inches(y),Inches(W),Inches(H))
# tables
tl=tbx; el=tbx._element
fe=copy.deepcopy(el); s.shapes._spTree.append(fe)
mx=max(int(e.get('id')) for e in s.shapes._spTree.iter(PNS+'cNvPr'))
for c in fe.iter(PNS+'cNvPr'): mx+=1; c.set('id',str(mx))
tr=[x for x in s.shapes if x._element is fe][0]
P=pd.read_csv(AN+'intermediate/fvfm_phase.csv')
cols=[('bean','P1'),('bean','P2'),('lettuce','P1'),('lettuce','P2')]
trts=['ETc','ETc50','침수ETc','침수ETc50']
for j,(cr,ph) in enumerate(cols,1):
    for i,t in enumerate(trts,1):
        q=P[(P.작물==cr)&(P.구간==ph)&(P.처리==t)]
        txt='–' if q.empty else f'{q.원평균.iloc[0]:.3f} {q.문자.iloc[0]}'
        set_cell(tr.table.cell(i,j),txt)
for tt,x in ((tl,XL),(tr,XR)):
    set_widths(tt,[1.1,1.05,1.05,1.05,1.05],0.22); tt.left=Inches(x); tt.top=Inches(Y2+H+0.08)
    # scale to W
set_para(s.shapes.title.text_frame.paragraphs[0],'LI-600 : 기공전도도 (gsw) · 암적응 Fv/Fm')
cb=[x for x in s.shapes if x.name=='Conclusion Box'][0]
set_para(cb.text_frame.paragraphs[0],'gsw: 상추 배수 후 회복, 콩 회복 느림 — Fv/Fm: 침수 중·직후 소폭 감소 후 회복')
for p in cb.text_frame.paragraphs[1:]: p._p.getparent().remove(p._p)
# footnote: copy style from conclusion box text
fb=s.shapes.add_textbox(Inches(0.5),Inches(6.02),Inches(12.3),Inches(0.3)); fb.name='Footnote'
tf=fb.text_frame; tf.word_wrap=True
r=tf.paragraphs[0].add_run()
r.text='표: 구간별 평균 + Tukey 문자 / Fv/Fm: LI-600 야간 암적응, 콩 DAT 9(LI-6800) 제외, P2는 DAT 29만 / * 당일 처리 간 유의(Holm)'
r.font.size=Pt(8); r.font.color.rgb=RGBColor(0x59,0x59,0x59)
s.notes_slide.notes_text_frame.text=('(약 70초) 8페이지는 광합성의 첫 단계인 기공전도도와 광계 II의 최대 광화학 효율인 Fv/Fm을 함께 보여줍니다. 왼쪽 gsw에서 두 작물 모두 침수 기간 중 크게 감소했고, 상추는 배수 직후 대조구 수준으로 회복한 반면 콩은 회복이 느렸습니다. 오른쪽 Fv/Fm은 값 자체가 0.82~0.84로 변화 폭이 작았습니다. 콩은 P1에서 침수구가 대조구보다 낮았지만 P2에서는 처리 간 차이가 없었고, 상추도 P1 침수구가 약간 낮았다가 P2 후반에 복합구만 낮아졌습니다. 즉 광계 II 자체의 손상은 크지 않고, 앞선 gsw 감소가 더 민감한 반응임을 시사합니다.')
prs.save(R+'구두발표_8p_gsw_FvFm.pptx')
