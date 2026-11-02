import sys,re,copy; sys.path.insert(0,'.')
from lib import *
R='/home/user/-/'
prs=Presentation(R+'구두발표_콩vs로메인상추_v10.pptx')
fn_el=None
for _s in prs.slides:
    for _sh in _s.shapes:
        if _sh.name=='Footnote' and fn_el is None: fn_el=copy.deepcopy(_sh._element)
sld=prs.slides._sldIdLst; ids=list(sld)
idx=[i for i,s in enumerate(prs.slides) if s.shapes.title is not None and s.shapes.title.text_frame.text.startswith('생육 조사')][0]
for i,x in enumerate(ids):
    if i!=idx: prs.part.drop_rel(x.rId); sld.remove(x)
base=prs.slides[0]
for sh in list(base.shapes):
    if (sh.shape_type==13 and sh.width/914400>3) or (getattr(sh,'has_table',False) and sh.has_table) or sh.name in ('Text 요점','Card 요점','Header 요점'): sh._element.getparent().remove(sh._element)
if not [x for x in base.shapes if x.name=='Footnote']: base.shapes._spTree.append(copy.deepcopy(fn_el))
def dup(srcs):
    new=prs.slides.add_slide(srcs.slide_layout)
    from pptx.opc.packuri import PackURI
    new.part.partname=PackURI('/ppt/slides/slide%d.xml'%(100+len(prs.slides)))
    for sh in list(new.shapes): sh._element.getparent().remove(sh._element)
    for el in srcs.shapes._spTree:
        if el.tag.endswith('}nvGrpSpPr') or el.tag.endswith('}grpSpPr'): continue
        e2=copy.deepcopy(el)
        for b in e2.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
            rid=b.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            if rid: b.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed',new.part.relate_to(srcs.part.rels[rid].target_part,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'))
        new.shapes._spTree.append(e2)
    return new
slides=[base,dup(base),dup(base)]
SPEC=[('생육 조사 : 콩 생장·수량 지표 (1/2)','growth_bean1.png',
  '콩은 SPAD는 건조·침수구, 엽면적은 건조구에서 낮았고, 수량 구성요소는 차이 없음',
  '콩 10/6(DAT 55, R6~R7) 파괴조사. 막대: 평균 ± SE, 문자 Tukey(일원 ANOVA P<0.05일 때만). 이상값 제거 자료로 지표별 n이 다름(4~9). 종실·꼬투리는 개체당 값.',
  '(보충) 콩 최종 생육조사의 생장과 수량 구성 지표입니다. 초장, 경장, 잎 수, 분지 수는 처리 간 차이가 없었고, SPAD는 건조구와 침수구에서, 엽면적은 건조구에서 대조구보다 낮았습니다. 꼬투리 수, 종자 수, 종실과 꼬투리의 생체중·건조중은 모두 처리 간 유의한 차이가 없었지만 복합구에서 종실 값이 가장 낮은 경향이었습니다.'),
 ('생육 조사 : 콩 건물중 지표 (2/2)','growth_bean2.png',
  '콩은 줄기·지상부 건물중이 건조·침수구에서 낮고, 뿌리 건물중은 처리구에서 증가',
  '콩 10/6(DAT 55, R6~R7) 파괴조사. 막대: 평균 ± SE, 문자 Tukey(일원 ANOVA P<0.05일 때만). 지상부 = 잎 + 줄기. 이상값 제거 자료로 지표별 n이 다름(4~8).',
  '(보충) 콩 최종 생육조사의 부위별 건물중입니다. 잎 생체중·건조중은 처리 간 유의하지 않았고, 줄기와 지상부의 생체중은 건조구에서, 건조중은 침수구에서 가장 낮았습니다. 뿌리 건조중은 대조구보다 건조, 침수, 복합 처리에서 높았습니다.'),
 ('생육 조사 : 상추 최종 생육 지표','growth_lettuce.png',
  '상추는 잎 수·엽면적·지상부·뿌리 건물중이 복합구에서 가장 크게 감소, SLA는 침수·복합구에서 증가',
  '상추 10/23(DAT 16) 파괴조사, 처리당 8주. 막대: 평균 ± SE, 문자 Tukey(일원 ANOVA P<0.05일 때만). LSI: 엽형 지수, SLA: 비엽면적, 지상부/뿌리 비율(Shoot/root).',
  '(보충) 상추 최종 생육조사의 전체 지표입니다. 엽장과 지상부/뿌리 비율은 처리 간 유의한 차이가 없었고, 엽폭, 잎 수, 엽면적, 지상부 생체중·건조중, 뿌리 건조중은 대조구에서 가장 높고 복합구에서 가장 낮았습니다. SPAD는 복합구가 건조구보다 낮았고 비엽면적(SLA)은 침수와 복합 처리에서 높았습니다.')]
for s,(ttl,fig,cc,ft,nt) in zip(slides,SPEC):
    set_para(s.shapes.title.text_frame.paragraphs[0],ttl)
    for sh in list(s.shapes):
        if sh.shape_type==13 and sh.width/914400>3: sh._element.getparent().remove(sh._element)
    s.shapes.add_picture('an/figs4/'+fig,Inches(0.55),Inches(1.25),width=Inches(12.2))
    by=lambda n:[x for x in s.shapes if x.name==n][0]
    set_para(by('Conclusion Box').text_frame.paragraphs[0],cc); set_para(by('Footnote').text_frame.paragraphs[0],ft); s.notes_slide.notes_text_frame.text=nt
for s in prs.slides: fix_timing(s)
prs.save('intro/생육_전체지표.pptx'); print('saved',len(prs.slides))
