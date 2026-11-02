import sys,copy; sys.path.insert(0,'.')
from lib import *
from pptx.util import Inches,Pt
R='/home/user/-/'
prs=Presentation(R+'구두발표_콩vs로메인상추_v11.pptx')
PNS='{http://schemas.openxmlformats.org/presentationml/2006/main}'
src=prs.slides[5]; s=prs.slides[6]
cbx=[x for x in src.shapes if x.name=='Conclusion Box'][0]._element
ids=prs.slides._sldIdLst
for i,x in reversed(list(enumerate(list(ids)))):
    if i!=6: prs.part.drop_rel(x.rId); ids.remove(x)
s=prs.slides[0]
for x in list(s.shapes):
    if x.name in('Stat box','Stat value','Stat label'): x._element.getparent().remove(x._element)
pic=[x for x in s.shapes if x.name=='Picture 26'][0]
pic.left,pic.top,pic.width,pic.height=Inches(0.55),Inches(3.78),Inches(6.4),Inches(6.4*3.0/7.7)
tx=[x for x in s.shapes if x.name=='Text 요점'][0]
tx.left,tx.top,tx.width,tx.height=Inches(7.3),Inches(3.85),Inches(5.3),Inches(2.4)
for p in tx.text_frame.paragraphs:
    for r in p.runs: r.font.size=Pt(14)
ET=s.shapes.add_picture('/tmp/claude-0/-home-user--/f2046ef5-a5f5-5769-8dca-a4878d4046a0/scratchpad/an/figs6/design_timeline.png',Inches(0.7),Inches(1.2),Inches(11.4)); ET.name='ET daily'
e=copy.deepcopy(cbx); s.shapes._spTree.append(e)
mx=max(int(c.get('id')) for c in s.shapes._spTree.iter(PNS+'cNvPr'))
for c in e.iter(PNS+'cNvPr'): mx+=1; c.set('id',str(mx))
cb=[x for x in s.shapes if x._element is e][0]
cb.left,cb.top,cb.width,cb.height=Inches(0.92),Inches(6.33),Inches(11.56),Inches(0.55)
set_para(cb.text_frame.paragraphs[0],'침수 72시간 후 정상 관수, 건조·복합은 대조구의 50% 관수 — 실제 누적 관수량도 설계대로 감소')
s.notes_slide.notes_text_frame.text=s.notes_slide.notes_text_frame.text+' 위쪽 도식은 처리 설계입니다. 대조는 전날 증산량만큼 관수, 건조는 그 50%, 침수는 72시간, 즉 DAT 0~3 동안 물에 담근 뒤 정상 관수, 복합은 침수 후 50% 관수입니다.'
fix_timing(s)
prs.save(R+'구두발표_7p_누적관수량_처리설계.pptx')
