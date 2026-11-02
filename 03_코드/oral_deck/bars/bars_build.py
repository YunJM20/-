import sys,re,copy; sys.path.insert(0,'.')
from lib import *
R='/home/user/-/'
prs=Presentation(R+'구두발표_콩vs로메인상추_v10.pptx')
fn_el=None
for _s in prs.slides:
    for _sh in _s.shapes:
        if _sh.name=='Footnote' and fn_el is None: fn_el=copy.deepcopy(_sh._element)
sld=prs.slides._sldIdLst; ids=list(sld)
idx=[i for i,s in enumerate(prs.slides) if s.shapes.title is not None and s.shapes.title.text_frame.text.startswith('LI-600 : 명반응')][0]
for i,x in enumerate(ids):
    if i!=idx: prs.part.drop_rel(x.rId); sld.remove(x)
s=prs.slides[0]
if not [x for x in s.shapes if x.name=='Footnote']: s.shapes._spTree.append(copy.deepcopy(fn_el))
for sh in list(s.shapes):
    if sh.shape_type==13 and sh.name not in ('Logo',) and sh.width/914400>3: sh._element.getparent().remove(sh._element)
    elif getattr(sh,'has_table',False) and sh.has_table: sh._element.getparent().remove(sh._element)
set_para(s.shapes.title.text_frame.paragraphs[0],'LI-600 : P1·P2 구간별 비교 (g_{sw}, Φ_{PSII}, Φ_{NPQ}, Φ_{NO})')
s.shapes.add_picture('an/figs4/bars_period.png',Inches(0.55),Inches(1.25),width=Inches(12.2))
def byname(n): return [x for x in s.shapes if x.name==n][0]
set_para(byname('Conclusion Box').text_frame.paragraphs[0],'콩은 P1 침수구, P2 건조·복합구에서 변화가 뚜렷, 상추는 gsw 외 처리 간 차이 없음')
set_para(byname('Footnote').text_frame.paragraphs[0],'막대: 구간(P1: DAT 1~10, P2: DAT 11~) 평균 ± SE, 문자 Tukey(구간별, ANOVA P<0.05일 때만). g_{sw}: 온도 보정 gsw 원자료 평균(Rizzo & Bailey, 2026), Φ: PAR·기온 공변량 보정 평균(혼합모형, 측정일 임의효과; Ali et al., 2025; Gao et al., 2024). 콩 P1은 대조·침수만 측정.')
s.notes_slide.notes_text_frame.text='(보충 슬라이드) LI-600 지표를 P1과 P2 구간으로 묶어 막대로 비교한 것입니다. 위는 콩, 아래는 상추입니다. 콩은 P1에서 침수구의 gsw와 ΦPSII가 대조구보다 낮고 ΦNPQ와 ΦNO가 높았으며, P2에서는 건조구와 복합구의 gsw가 낮고 건조구의 ΦPSII가 가장 낮았으며 ΦNPQ는 건조구에서, ΦNO는 건조·침수·복합구에서 대조구보다 높았습니다. 상추는 P2의 gsw에서 건조구가 침수구보다 낮은 것을 제외하면 ΦPSII, ΦNPQ, ΦNO 모두 처리 간 차이가 없었습니다.'
for sh in s.shapes:
    if getattr(sh,'has_table',False) and sh.has_table: pass
fix_timing(s)
prs.save('intro/P1P2_막대.pptx'); print('saved',len(prs.slides))
