import sys,re,copy; sys.path.insert(0,'.')
from lib import *
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import pandas as pd, numpy as np
from PIL import Image
R='/home/user/-/'; AN='an/'
src=open('oral_b.py').read()
for fn in ('bottom_border','compact_table','drop_col','set_widths'):
    m=re.search(r'\ndef '+fn+r'\(.*?(?=\ndef |\n# =====|\nMM=)',src,flags=re.S); exec(m.group(0))
prs=Presentation(R+'구두발표_콩vs로메인상추_v6.pptx')
S=lambda n: prs.slides[n-1]
def byname(s,n,k=0): return [x for x in s.shapes if x.name==n][k]
def allnames(s,n): return [x for x in s.shapes if x.name==n]
def rm(sh): sh._element.getparent().remove(sh._element)
def img(p): return Image.open(p).convert('RGB')
def notes(s,t): s.notes_slide.notes_text_frame.text=t
def conc(s,t): set_para(byname(s,'Conclusion Box').text_frame.paragraphs[0],t)
def foot(s,t): set_para(byname(s,'Footnote').text_frame.paragraphs[0],t)
PNS='{http://schemas.openxmlformats.org/presentationml/2006/main}'
def newids(s,els):
    mx=max(int(e.get('id')) for e in s.shapes._spTree.iter(PNS+'cNvPr'))
    for el in els:
        for c in el.iter(PNS+'cNvPr'): mx+=1; c.set('id',str(mx))
def copy_el(dst,el):
    e=copy.deepcopy(el); dst.shapes._spTree.append(e); newids(dst,[e]); return e
def add_pic(s,path,x,y,w):
    return s.shapes.add_picture(path,Inches(x),Inches(y),width=Inches(w))
MM=pd.read_csv(AN+'intermediate/mm_phase.csv')
def fill_mm(t,ind,fmt,name=None):
    while len(t.rows)>5: delete_row(t,len(t.rows)-1)
    for c_i,h in enumerate([name or 'Treatment','Soybean P1','Soybean P2','Romaine P1','Romaine P2']): set_cell(t.cell(0,c_i),h)
    for r_i,(tn,tr) in enumerate([('Control','ETc'),('Drought','ETc50'),('Waterlogging','침수ETc'),('Combined','침수ETc50')],start=1):
        set_cell(t.cell(r_i,0),tn)
        for c_i,(cr,pe) in enumerate([('bean','P1'),('bean','P2'),('lettuce','P1'),('lettuce','P2')],start=1):
            q=MM[(MM.지표==ind)&(MM.작물==cr)&(MM.구간==pe)&(MM.처리==tr)]
            set_cell(t.cell(r_i,c_i),'–' if q.empty else (fmt.format(q.보정평균.iloc[0])+' '+q.문자.iloc[0]))
def tbl(s,k=0): return [x for x in s.shapes if getattr(x,'has_table',False) and x.has_table][k]
# ---------------- global text fix
def fixp(p):
    for r in p.runs:
        if '상추 상추' in r.text: r.text=r.text.replace('상추 상추','상추')
    if '상추 상추' in p.text:
        full=p.text.replace('상추 상추','상추'); rs=p.runs; rs[0].text=full
        for r in rs[1:]: r._r.getparent().remove(r._r)
for s in prs.slides:
    for sh in s.shapes:
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs: fixp(p)
        if getattr(sh,'has_table',False) and sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    for p in c.text_frame.paragraphs: fixp(p)
    if s.has_notes_slide:
        t=s.notes_slide.notes_text_frame.text
        if '상추 상추' in t: s.notes_slide.notes_text_frame.text=t.replace('상추 상추','상추')
# ---------------- slide 3 / 6 labels
s=S(3)
ps=byname(s,'Step 2').text_frame.paragraphs; set_para(ps[1],'Φ_{PSII} · Φ_{NPQ} · Φ_{NO}')
set_para(byname(s,'TextBox 47').text_frame.paragraphs[0],'틸라코이드 막 PSII 전자전달 저해: 광화학 효율(ΦPSII)과 에너지 소산(ΦNPQ·ΦNO) 변화')
s=S(6)
set_para(allnames(s,'Row ind')[1].text_frame.paragraphs[0],'Φ_{PSII}, Φ_{NPQ}, Φ_{NO}')
# ---------------- slide 7: env table
e1=pd.read_csv(R+'data/19_환경_밭콩_일별.csv'); e2=pd.read_csv(R+'로메인data/25_환경_일별.csv')
e1=e1[(e1.DAT>=0)&(e1.DAT<=16)]; e2=e2[(e2.DAT>=0)&(e2.DAT<=16)]; e2=e2[e2['결측일(자료<1400)'].astype(str)!='True']
rowsE=[('최고기온 (°C)',e2.최고기온.mean(),e1.최고기온.mean()),('최저기온 (°C)',e2.최저기온.mean(),e1.최저기온.mean()),('평균 상대습도 (%)',e2.평균습도.mean(),e1.평균습도.mean())]
print('env',rowsE)
s=S(7)
card=byname(s,'Card 요점'); card.height=Inches(1.95)
set_paras2(byname(s,'Text 요점'),[('상추:',' 처리 기간 동안 저온·중간 일사 조건'),('콩:',' 처리 초기에 상추보다 고온·고일사 조건')])
byname(s,'Text 요점').height=Inches(1.5)
tsrc=tbl(S(9)).table; tel=copy_el(s,tbl(S(9))._element)
tsh=[x for x in s.shapes if x._element is tel][0]; tt=tsh.table
drop_col(tt,4); drop_col(tt,3)
while len(tt.rows)>4: delete_row(tt,len(tt.rows)-1)
for c_i,h in enumerate(['DAT 0~16 평균','상추','콩']): set_cell(tt.cell(0,c_i),h)
for r_i,(nm,a,b) in enumerate(rowsE,start=1):
    set_cell(tt.cell(r_i,0),nm); set_cell(tt.cell(r_i,1),f'{a:.1f}'); set_cell(tt.cell(r_i,2),f'{b:.1f}')
set_widths(tsh,[1.7,1.06,1.06],0.3); tsh.left=Inches(8.6); tsh.top=Inches(3.85)
foot(s,'밭콩: CR1000X 기상 센서, 상추: 26번 온실 환경 데이터(CR300; 10/13·10/18 결측일 제외). 상추 DLI = 일사량(MJ) × 2.02 mol/MJ 추정. 점선 = 침수 시작일. 표: DAT 0~16 일별 값의 평균.')
notes(s,'(약 25초) 두 실험은 계절이 달라 환경 조건이 크게 다릅니다. 콩의 처리 초기 평균 기온은 28.4도, 상추는 18.2도로 약 10도 낮았고 일적산광량도 상추가 낮았습니다. 표에는 같은 기간의 최고·최저 기온과 평균 상대습도를 정리했는데, 기온과 일사 외의 환경도 두 실험이 다릅니다. 따라서 같은 50% 관수라도 증발산 부하가 달라 건조 스트레스 강도가 다르며, 두 작물의 비교는 병렬 사례로 해석하겠습니다.')
# ---------------- slide 8: narrative
s=S(8)
set_paras2(byname(s,'Text 요점'),[('건조·복합:',' 두 작물 모두 설계대로 관수량이 감소'),
 ('상추:',' 대조구와 침수구의 차이가 커서, 침수가 생육에 직접적인 타격을 입혔을 가능성'),
 ('콩:',' 대조구와 침수구의 차이가 크지 않아, 3일 침수가 큰 타격을 입히지 못한 것으로 추정')])
conc(s,'콩은 3일 침수의 타격이 작았던 것으로 추정, 상추는 침수가 생육에 직접 타격을 입혔을 가능성')
notes(s,'(약 30초) 결과를 보기 전에 처리가 실제로 어떻게 들어갔는지 누적 관수량으로 확인했습니다. 대조구 대비 건조구는 상추 43%, 콩 40%로 설계인 50%에 가까웠고, 복합구도 각각 37%, 44%였습니다. 주목할 점은 침수구입니다. 콩은 침수구가 대조구의 87%로 대조구와 큰 차이가 없어 3일 침수가 콩에는 큰 타격을 주지 못한 것으로 추정됩니다. 반대로 상추는 침수구가 56%로 대조구와 차이가 커서, 침수가 상추의 생육에 직접적인 타격을 입혔을 가능성이 있습니다.')
# ---------------- slide 9 merged (gsw + recovery)
s9=S(9); s10=S(10)
for nm in ('Picture 13','TextBox 10','Card 요점','Header 요점'): rm(byname(s9,nm))
set_para(s9.shapes.title.text_frame.paragraphs[0],'LI-600 : 기공전도도 (g_{sw})와 회복 (% of control)')
W9=6.4; add_pic(s9,AN+'figs2/ts_gsw_w.png',0.5,1.25,W9)
h1=W9*825/2250; add_pic(s9,AN+'figs3/recovery_w.png',0.5,1.25+h1+0.05,W9)
t9=tbl(s9); t9.left=Inches(7.3); t9.top=Inches(1.4)
gr=pd.read_csv(AN+'intermediate/gsw_phase_raw.csv')
tt=t9.table
for c_i,h in enumerate(['Treatment','Soybean P1','Soybean P2','Romaine P1','Romaine P2']): set_cell(tt.cell(0,c_i),h)
for r_i,(tn,tr) in enumerate([('Control','ETc'),('Drought','ETc50'),('Waterlogging','침수ETc'),('Combined','침수ETc50')],start=1):
    set_cell(tt.cell(r_i,0),tn)
    for c_i,(cr,pe) in enumerate([('bean','P1'),('bean','P2'),('lettuce','P1'),('lettuce','P2')],start=1):
        q=gr[(gr.작물==cr)&(gr.구간==pe)&(gr.처리==tr)]; set_cell(tt.cell(r_i,c_i),'–' if q.empty else f'{q.원평균.iloc[0]:.3f} {q.문자.iloc[0]}')
set_widths(t9,[1.35,0.97,0.97,0.97,0.97],0.3)
# stat boxes from slide 10
stat=[x for x in s10.shapes if x.name.startswith('Stat')]
els=[copy_el(s9,x._element) for x in stat]
objs=[[y for y in s9.shapes if y._element is e][0] for e in els]
pos=[(7.3,3.35,5.0,1.3),(7.35,3.4,4.9,0.75),(7.38,4.1,4.85,0.5),(7.3,4.85,5.0,1.3),(7.35,4.9,4.9,0.75),(7.38,5.6,4.85,0.5)]
for o,(x,y,w,h) in zip(objs,pos): o.left=Inches(x); o.top=Inches(y); o.width=Inches(w); o.height=Inches(h)
conc(s9,'기공은 두 작물 모두 침수에 즉시 반응 — 상추는 배수 직후 회복, 콩은 회복이 느림')
foot(s9,'표·그림: PAR·기온 보정 이전 원자료(온도 보정 gsw, Rizzo & Bailey 2026) 평균, Tukey 문자. 아래 그림: 각 처리 gsw ÷ 같은 날 대조구 gsw × 100, * 대조 vs 처리 P<0.05(Welch t, Holm). 건조·복합은 회색, 빗금 = 침수 기간, 회색 띠 = 흐린 날, 콩 DAT 10~16 측정 없음.')
notes(s9,'(약 70초) 첫 번째 단계인 기공입니다. 위 그래프는 기공전도도의 일별 변화이고, 아래 그래프는 각 처리를 같은 날 대조구에 대한 비율로 나타낸 것입니다. 두 작물 모두 침수 기간 동안 기공전도도가 크게 감소했습니다. 상추는 침수 3일째에 대조구의 10%까지 떨어졌다가 배수 직후 DAT 5~6에 대조구 수준으로 회복했습니다. 반면 콩은 침수가 끝나고 6일이 지난 DAT 9에도 대조구의 48%였고 DAT 23에 대조구 수준으로 돌아왔습니다. P2에서는 건조와 복합 처리가 두 작물 모두 후반에 기공전도도를 낮췄습니다. 건조와 복합은 회색으로 두고 침수 위주로 설명했습니다.')
# delete slide 10
sld=prs.slides._sldIdLst; ids=list(sld)
prs.part.drop_rel(ids[9].rId); sld.remove(ids[9])
# ---------------- slide 11 (now index 10): phi
s=prs.slides[9]
assert s.shapes.title.text_frame.text.startswith('LI-600 : 광계')
pic=byname(s,'Picture 13'); replace_picture(s,pic,img(AN+'figs2/ts_phi.png'),valign='top')
fill_mm(tbl(s).table,'phi','{:.3f}')
foot(s,'표·그림: PAR·기온 공변량 보정 평균(혼합모형, 측정일 임의효과; Ali et al., 2025; Gao et al., 2024), Tukey 문자. P2는 PPFD 수준을 나누지 않고 통합하여 분석. 그림: 음영 ± SE, 빗금 침수 기간, 점선 P1/P2 경계, 회색 띠 흐린 날, * 당일 P<0.05(Holm), x 처리 전.')
set_paras2(byname(s,'TextBox 10'),[('콩 P1:',' 침수구가 대조구보다 약간 낮았음'),('콩 P2:',' 건조구가 가장 낮았음'),('상추:',' P1·P2 모두 처리 간 차이 없음')])
notes(s,'(약 30초) 두 번째 단계인 명반응의 광화학 효율 ΦPSII입니다. P2 구간은 광도 수준을 나누지 않고 통합하여 분석했습니다. 콩은 P1에서 침수구가 대조구보다 약간 낮았고, P2에서는 건조구가 가장 낮았습니다. 상추는 P1과 P2 모두 처리 간 차이가 없었습니다. 이어서 이 에너지가 어디로 소산되었는지 ΦNPQ와 ΦNO로 보겠습니다.')
# ---------------- new slide: PhiNPQ / PhiNO (dup of merged slide 9 layout)
def dup(srcs):
    new=prs.slides.add_slide(srcs.slide_layout)
    from pptx.opc.packuri import PackURI
    new.part.partname=PackURI('/ppt/slides/slide100.xml')
    for sh in list(new.shapes): sh._element.getparent().remove(sh._element)
    for el in srcs.shapes._spTree:
        if el.tag.endswith('}nvGrpSpPr') or el.tag.endswith('}grpSpPr'): continue
        e2=copy.deepcopy(el)
        for b in e2.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
            rid=b.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            if rid: b.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed',new.part.relate_to(srcs.part.rels[rid].target_part,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'))
        new.shapes._spTree.append(e2)
    return new
n=dup(s9)
for sh in list(n.shapes):
    if sh.name.startswith('Stat') or sh.shape_type==13 and sh.name.startswith('Picture'): rm(sh)
set_para(n.shapes.title.text_frame.paragraphs[0],'LI-600 : 에너지 소산 양자수율 (Φ_{NPQ}, Φ_{NO})')
add_pic(n,AN+'figs2/ts_phinpq_w.png',0.5,1.25,W9); add_pic(n,AN+'figs2/ts_phino_w.png',0.5,1.25+h1+0.05,W9)
t1=tbl(n); t1.left=Inches(7.3); t1.top=Inches(1.4); fill_mm(t1.table,'phinpq','{:.3f}','Φ_{NPQ}'); set_widths(t1,[1.35,0.97,0.97,0.97,0.97],0.3)
te=copy_el(n,t1._element); t2=[x for x in n.shapes if x._element is te][0]; t2.top=Inches(3.95); fill_mm(t2.table,'phino','{:.3f}','Φ_{NO}'); set_widths(t2,[1.35,0.97,0.97,0.97,0.97],0.3)
def tb(sl,x,y,w,h,paras,size=12):
    t=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=t.text_frame; tf.word_wrap=True
    for i,(lead,body) in enumerate(paras):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        for tx,b in ((lead,True),(body,False)):
            r=p.add_run(); r.text=tx; r.font.size=Pt(size); r.font.bold=b; r.font.color.rgb=RGBColor.from_string('333333')
    return t
tb(n,7.3,2.95,5.0,0.8,[('콩:',' P1 침수구, P2 건조·복합구에서 높은 경향'),('상추:',' 처리 간 차이 없음')])
tb(n,7.3,5.5,5.0,0.8,[('콩:',' P1 침수구, P2 건조·침수·복합구가 모두 대조구보다 높음'),('상추:',' 처리 간 차이 없음')])
conc(n,'콩은 ΦNPQ·ΦNO가 높아 명반응에 타격을 입은 것으로 추정, 상추는 처리 간 유의한 차이 없음')
foot(n,'Φ_{NPQ}=1−Φ_{PSII}−Φ_{NO}, Φ_{NO}=1/(NPQ+1+qL(Fm/Fo−1)) (Kramer et al., 2004). Fo·Fm: 가장 가까운 날짜의 암적응 처리별 평균. 표·그림: PAR·기온 공변량 보정 평균(혼합모형, 측정일 임의효과), Tukey 문자.')
notes(n,'(약 40초) 흡수한 빛에너지가 광화학이 아닌 곳으로 어떻게 소산되었는지 보여주는 ΦNPQ와 ΦNO입니다. ΦNPQ는 조절된 열소산, ΦNO는 조절되지 않는 소산으로 광계 손상의 위험을 나타냅니다. 상추는 두 지표 모두 처리 간 차이가 없었습니다. 콩은 ΦNPQ가 P2에서 건조구와 복합구에서 높은 경향이었고, ΦNO는 P2에서 건조, 침수, 복합 처리가 모두 대조구보다 높았으며 P1에서도 침수구가 높았습니다. ΦPSII가 낮아진 것과 함께 보면 콩은 명반응에 타격을 입은 것으로 추정됩니다.')
# move new slide after phi slide
sld=prs.slides._sldIdLst; last=list(sld)[-1]; sld.remove(last); sld.insert(10,last)
# ---------------- photosynthesis slide (index 12 now)
s=prs.slides[11]; assert s.shapes.title.text_frame.text.startswith('LI-6800')
conc(s,'콩 건조·복합구(9월)와 상추 복합구(10월)에서 Vcmax·Jmax가 낮은 경향')
foot(s,'상자: 사분위(n≥4), 가로선: 평균 ± SE(n<4), 점: 개별 곡선, 문자: Tukey(ANOVA P<0.05일 때만), x: 처리 전. 콩 9/2~9/17, 상추 10/16~19 측정.')
nt=s.notes_slide.notes_text_frame.text
nt=nt.replace(' 다만 처리별로 측정일이 달라 측정일과 처리 효과가 섞여 있고 곡선 수도 처리당 3~4개로 적어 확정적으로 말하기는 어렵습니다.','')
notes(s,nt)

s=prs.slides[12]; assert s.shapes.title.text_frame.text.startswith('생육 조사')
_n=s.notes_slide.notes_text_frame.text
notes(s,' '.join(x for x in re.split(r'(?<=[.])\s+',_n) if '포트 밖' not in x))
# ---------------- summary slide (index 15)
s=prs.slides[13]; assert s.shapes.title.text_frame.text.startswith('종합')
heads=allnames(s,'Col head'); hh=[h for h in heads if abs(h.left/914400-5.10)<0.05][0]
set_para(hh.text_frame.paragraphs[1],'Φ_{PSII} · Φ_{NPQ} · Φ_{NO}')
cells=sorted(allnames(s,'Cell'),key=lambda c:(round(c.top/914400,2),c.left))
col2={2:None}
newtxt={(3,1):['ΦPSII ↓','ΦNPQ ↑ · ΦNO ↑'],(4,1):['ΦPSII ↓ (P1)','ΦNO ↑'],(5,1):['ΦNPQ ↑ 경향','ΦNO ↑']}
for (r,c),tx in newtxt.items(): set_paras(cells[r*4+c],[x.replace('ΦPSII','Φ_{PSII}').replace('ΦNPQ','Φ_{NPQ}').replace('ΦNO','Φ_{NO}') for x in tx])
for r in range(6):
    c=cells[r*4+2]
    if '측정일 교락' in c.text_frame.text: set_paras(c,['↓ 경향'])
    if '(9월)' in c.text_frame.text: set_paras(c,[c.text_frame.paragraphs[0].text])
foot(s,'↓↓ 큰 감소 · ↓ 감소 · ↑ 증가 · – 차이 없음. ④ 대조구 대비 %: 상추 지상부 건물중(DAT 16), 콩 생육 = 지상부 생체중(잎+줄기), 수량 = 종실 생체중(DAT 55).')
notes(s,'(약 25초) 지금까지의 결과를 작물, 처리, 단계별로 정리한 표입니다. 상추는 기공이 침수 직후 크게 닫혔다가 며칠 만에 회복했고 명반응에는 변화가 없었지만, 건물중은 침수 34%, 복합 43% 감소했습니다. 콩은 기공 회복이 느렸고 건조구에서 ΦPSII가 낮고 ΦNPQ와 ΦNO가 높아 명반응에 타격을 입은 것으로 보이지만, 수량은 종실 생체중 기준 5~14% 감소하는 데 그쳤습니다. 같은 수분 재해라도 작물에 따라 영향이 나타나는 단계가 다릅니다.')
# ---------------- recap slides 16, 17 (index 15,16)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig=plt.figure(figsize=(12.2,4.1)); gs=fig.add_gridspec(1,4,wspace=0.34,left=0.055,right=0.995,top=0.90,bottom=0.12,width_ratios=[1,1.25,1,1])
lefts,rights=[np.array(x) for x in gs.get_grid_positions(fig)[2:4]]; cen=(lefts+rights)/2; plt.close(fig)
for idx,crop,txt2 in [(14,'bean',None),(15,'lettuce',None)]:
    s=prs.slides[idx]
    pic=byname(s,'Picture 56'); rm(pic)
    p2=add_pic(s,AN+f'figs3/recap_{crop}.png',0.55,1.98,12.2)
    rects=[x for x in s.shapes if x.name.startswith('Rounded Rectangle')]
    rects=sorted(rects,key=lambda r:r.left)
    for r_,c_ in zip(rects,cen): r_.left=Inches(0.55+12.2*c_-1.35)
    ps=rects[1].text_frame.paragraphs; set_para(ps[1],'ΦPSII · ΦNPQ · ΦNO')
    arrows=sorted([x for x in s.shapes if x.name.startswith('Right Arrow')],key=lambda r:r.left)
    for k,a in enumerate(arrows): a.left=Inches((0.55+12.2*cen[k]+0.55+12.2*cen[k+1])/2-0.25)
    # keep picture behind labels
    s.shapes._spTree.remove(p2._element); s.shapes._spTree.insert(2,p2._element)
s=prs.slides[14]
notes(s,'(약 65초) 먼저 콩입니다. 앞서 본 결과를 논리 순서대로 다시 정리하겠습니다. 침수 직후 기공전도도가 먼저 감소했고 DAT 9에도 대조구의 48%로 회복이 느렸습니다. 뿌리의 저산소는 아쿠아포린 기능과 뿌리 수리전도도를 떨어뜨려 잎의 수분 상태를 악화시키고 기공을 닫는 것으로 보고됩니다. 두 번째로 명반응에서는 건조구에서 ΦPSII가 낮아졌고 ΦNPQ와 ΦNO가 높아져, 광화학에 쓰이지 못한 에너지가 열소산과 조절되지 않는 소산으로 빠져나간 것으로 보입니다. 세 번째로 광합성 능력도 건조·복합구에서 낮은 경향이었습니다. 그러나 네 번째 수량은 종실 생체중이 5~14% 감소하는 경향이었으나 큰 차이가 없었습니다. 한편 대조구와 침수구의 차이가 크지 않았다는 점에서 3일 침수는 콩에 큰 타격을 주지 못한 것으로 추정됩니다. 개화기 처리 후 55일의 회복 기간 동안 보상이 있었을 가능성도 있으나 이는 가설입니다.')
s=prs.slides[15]
notes(s,'(약 60초) 다음은 상추입니다. 침수 3일째 기공전도도가 대조구의 10%까지 떨어졌지만 배수 후 2~3일 만에 대조구 수준으로 회복했습니다. 명반응 지표인 ΦPSII, ΦNPQ, ΦNO는 모두 처리 간 차이가 없었고, 광합성 능력은 복합구에서만 낮은 경향이었습니다. 그럼에도 지상부 건물중은 건조 16%, 침수 34%, 복합 43% 감소했습니다. 대조구와 침수구의 차이가 크다는 점에서 침수가 상추의 생육에 직접적인 타격을 입혔을 가능성이 있습니다. 식물의 생장은 탄소 공급보다 조직 성장과 세포 팽압이 먼저 제한되는 경우가 많아, 침수 기간에 생긴 생장 손실이 회복 후에도 유지된 것으로 해석됩니다.')
# ---------------- conclusion slide (index 18)
s=prs.slides[16]; assert s.shapes.title.text_frame.text.startswith('결론')
cs=allnames(s,'Concl')
set_para(cs[1].text_frame.paragraphs[1],'상추는 ΦPSII·ΦNPQ·ΦNO에 처리 차이가 없었고 Vcmax·Jmax는 복합구에서 낮은 경향이었다. 콩은 건조구에서 ΦPSII가 낮고 ΦNPQ·ΦNO가 높아 명반응에 타격을 입은 것으로 추정되며, Vcmax·Jmax도 건조구에서 낮았다.')
set_para(cs[2].text_frame.paragraphs[1],'상추는 대조구와 침수구의 차이가 커 침수가 생육에 직접 타격을 입혔을 가능성이 있으며 지상부 건물중이 감소했다(건조 −16%, 침수 −34%, 복합 −43%). 콩은 대조·침수 차이가 작아 3일 침수의 타격이 작았던 것으로 추정되며, 종실 생체중은 5~14% 감소하는 경향이었으나 유의한 차이는 없었다.')
notes(s,'(약 40초) 결론입니다. 첫째, 침수는 두 작물에서 기공을 먼저 제한했고 상추는 배수 2~3일 만에, 콩은 DAT 9 이후에 회복했습니다. 둘째, 상추는 명반응에 변화가 없었고, 콩은 건조구에서 ΦPSII가 낮고 ΦNPQ와 ΦNO가 높아 명반응에 타격을 입은 것으로 추정됩니다. 셋째, 상추는 대조구와 침수구의 차이가 커 침수가 생육에 직접 타격을 입혔을 가능성이 있고 건물중이 감소했습니다. 콩은 대조구와 침수구의 차이가 작아 3일 침수의 타격이 작았던 것으로 보이며 수량은 감소하는 경향이었지만 큰 차이는 없었습니다. 따라서 수분 스트레스에 대한 반응은 작물마다 다르며, 피해를 진단할 때는 잎 생리 지표와 생장 지표를 함께 봐야 합니다. 감사합니다.')
# ---------------- appendix: A1 text, Fs, ETR
for i,s in enumerate(prs.slides):
    tt=s.shapes.title.text_frame.text if s.shapes.title is not None else ''
    if tt.startswith('LI-600 : PAR·기온 보정'):
        set_paras2(byname(s,'TextBox 10'),['이유: 같은 날에도 처리 간 측정 PAR·기온이 달랐음','모형: y = μ + 처리 + β_{1}·Q_{amb} + β_{2}·T_{air} + 측정일(임의효과) + ε (Ali et al., 2025; Gao et al., 2024)','PAR과 기온을 양적(선형) 공변량으로 넣어 처리별 보정 평균(BLUE)을 산출, Φ_{PSII}는 PAR이 높을수록 낮아짐','기공전도도(g_{sw})는 PAR·기온 보정 없이 온도 보정 gsw(Rizzo & Bailey, 2026)를 사용'])
        notes(s,'질의응답용 자료입니다. LI-600은 야외 광에서 측정하기 때문에 같은 날에도 처리마다 측정 광도와 기온이 달랐습니다. 그래서 Ali 등과 Gao 등의 방법에 따라 PAR과 기온을 양적 공변량으로, 측정일을 임의효과로 넣은 혼합모형으로 처리별 보정 평균을 구했습니다. 기공전도도는 온도 보정 gsw를 그대로 사용했습니다.')
    if tt.startswith('LI-600 : 정상 상태 형광'):
        replace_picture(s,byname(s,'Picture 13'),img(AN+'figs2/ts_fs.png'),valign='top'); fill_mm(tbl(s).table,'fs','{:.1f}')
        foot(s,'표: PAR(Q_{amb})·기온(T_{air}) 공변량 보정 평균(혼합모형, 측정일 임의효과), Tukey 문자.')
    if tt.startswith('LI-600 : 전자전달속도'):
        replace_picture(s,byname(s,'Picture 13'),img(AN+'figs2/ts_etr.png'),valign='top'); fill_mm(tbl(s).table,'etr','{:.1f}')
        foot(s,'표: PAR(Q_{amb})·기온(T_{air}) 공변량 보정 평균(혼합모형, 측정일 임의효과), Tukey 문자.')
# ---------------- borders/compact for all tables, timing
for s in prs.slides:
    for sh in s.shapes:
        if getattr(sh,'has_table',False) and sh.has_table: compact_table(sh.table); bottom_border(sh.table)
    fix_timing(s)
prs.save('oral/oral_v8.pptx'); print('saved',len(prs.slides))
