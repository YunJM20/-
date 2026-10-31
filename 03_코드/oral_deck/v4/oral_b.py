import sys; sys.path.insert(0,'.')
from lib import *
from pptx.util import Pt
from figs import *
import pandas as pd
prs=Presentation('oral/o3.pptx')
S=lambda n: prs.slides[n-1]
FG='an/figures/'; F2='an/figs2/'
def rm(shape): shape._element.getparent().remove(shape._element)
def byname(slide,name,nth=0):
    return [x for x in slide.shapes if x.name==name][nth]
def allnames(slide,name): return [x for x in slide.shapes if x.name==name]
def img(p): return Image.open(p).convert('RGB')
def notes(slide,text): slide.notes_slide.notes_text_frame.text=text
def title(slide,text):
    set_para(byname(slide,'Title 1').text_frame.paragraphs[0],text)
def conc(slide,text):
    set_para(byname(slide,'Conclusion Box').text_frame.paragraphs[0],text)
def foot(slide,text):
    set_para(byname(slide,'Footnote').text_frame.paragraphs[0],text)


import re as _re
F3='an/figs3/'
def runs_para(p,parts):
    """parts: list of (text, italic). Rebuild paragraph runs from first run's format."""
    rs=p._p.findall(A+'r'); base=rs[0]
    for r in rs[1:]: p._p.remove(r)
    prev=None
    for i,(t,it) in enumerate(parts):
        r=base if i==0 else copy.deepcopy(base)
        if i>0: prev.addnext(r)
        r.find(A+'t').text=t
        rpr=r.find(A+'rPr')
        if rpr is None: rpr=etree.SubElement(r,A+'rPr'); r.insert(0,rpr)
        if 'baseline' in rpr.attrib: del rpr.attrib['baseline']
        rpr.set('i','1' if it else '0'); prev=r
def clean_cell(txt):
    txt=_re.sub(r'\s*\([^)]*\)\s*$','',txt)   # drop trailing parentheses
    return txt
def clean_table(t,drop_prefix=('P (','처리 ×','W × I','Treatment P','P(')):
    # delete P-value rows
    for i in range(len(t.rows)-1,0,-1):
        if t.cell(i,0).text_frame.text.strip().startswith(drop_prefix): delete_row(t,i)
    for r_i in range(len(t.rows)):
        for c_i in range(len(t.columns)):
            c=t.cell(r_i,c_i); tx=c.text_frame.text
            if '(' in tx and r_i>0 and tx.strip() not in ('–',): set_cell(c,clean_cell(tx))
def drop_col(t,idx):
    tbl=t._tbl; grid=tbl.tblGrid; gc=grid.findall(A+'gridCol')[idx]; grid.remove(gc)
    for tr in tbl.tr_lst:
        tc=tr.tc_lst[idx]; tr.remove(tc)
def set_widths(shape,widths,rowh=None):
    t=shape.table
    for c,w in zip(t.columns,widths): c.width=Inches(w)
    shape.width=Inches(sum(widths))
    if rowh:
        for r in t.rows: r.height=Inches(rowh)
        shape.height=Inches(rowh*len(t.rows))

def bottom_border(table,w=28575):
    last=table._tbl.tr_lst[-1]
    for tc in last.tc_lst:
        tcPr=tc.get_or_add_tcPr()
        for e in tcPr.findall(A+'lnB'): tcPr.remove(e)
        ln=etree.Element(A+'lnB',w=str(w),cap='flat',cmpd='sng',algn='ctr')
        sf=etree.SubElement(ln,A+'solidFill'); etree.SubElement(sf,A+'srgbClr',val='000000'); etree.SubElement(ln,A+'prstDash',val='solid')
        idx=0
        for i,ch in enumerate(list(tcPr)):
            if ch.tag in (A+'lnL',A+'lnR',A+'lnT'): idx=i+1
        tcPr.insert(idx,ln)
def pct(v,d=0): 
    s=f'{abs(v):.{d}f}'
    return ('−' if v<0 else '+')+s+'%'
def sub_title(slide,text): title(slide,text)

# ===== 1 title
s=S(1); t=[x for x in s.shapes if x.name=='제목 1'][0]
r=t.text_frame.paragraphs[0].runs
print('title runs',[x.text for x in r])
r[0].text='침수 및 건조 복합재해에 대한 콩과'
r[2].text='Comparison of Growth and Physiological Responses of Soybean and Romaine Lettuce to Flooding, Drought, and Combined Stress'
r[1].text='로메인 상추의 생육 및 생리 반응 비교'
notes(s,'(약 10초) 안녕하십니까. 전북대학교 스마트농업AI융합학과 윤정민입니다. 오늘은 침수와 건조, 그리고 두 재해가 연속으로 발생한 복합재해 조건에서 콩과 로메인 상추의 생리 및 생육 반응을 비교한 결과를 발표하겠습니다. (발표 10분, 질의응답 2분)')

# ===== 2 background (content kept)
notes(S(2),'(약 30초) 최근 집중호우와 폭염·가뭄이 짧은 간격으로 반복되면서 한 생육기 안에서 침수와 건조를 연이어 겪는 일이 늘고 있습니다. 침수는 근권 산소 결핍으로, 건조는 토양 수분 부족으로 기공을 닫게 하지만, 두 재해가 연속될 때 피해가 누적되는지, 선행 스트레스가 순화 효과를 주는지는 작물마다 다를 수 있습니다. 그런데 재해 유형별로 생리 반응이 어느 단계에서 제한되는지를 작물 간에 비교한 연구는 충분하지 않습니다.')

# ===== 3 objective
s=S(3)
for nm in ('Step 3','Depth arrow'): rm(byname(s,nm))
steps=[byname(s,'Step %d'%i) for i in (1,2,4,5)]
labels=[('① 기공','g_{sw}'),('② 명반응','Φ_{PSII}'),('③ 생화학적 능력','V_{cmax} · J_{max} · LSP'),('④ 생육·수량','수량 · 지상부 건물중')]
for k,(st,(a,b)) in enumerate(zip(steps,labels)):
    ps=st.text_frame.paragraphs; set_para(ps[0],a); set_para(ps[1],b)
    st.left=Inches(0.92+k*2.88); st.top=Inches(1.55+k*0.78)
obj=byname(s,'Objective'); ps=obj.text_frame.paragraphs
ps[0].runs[1].text='  콩과 로메인 상추에 침수·건조·복합 처리를 적용하여'
ps[1].runs[0].text='잎 생리 반응이 '
ps[1].runs[5].text='생육·수량 감소로 이어지는지'
conc(s,'핵심 질문: 같은 침수·건조 재해에 콩과 로메인 상추의 생리·생육 반응은 어떻게 다른가?')
foot(s,'본 발표의 결과는 ①→④ 순서로 제시함.')
notes(s,'(약 20초) 이 연구는 수분 재해의 영향을 네 단계로 나누어 보았습니다. 가장 먼저 반응하는 기공, 광계의 명반응, 광합성의 생화학적 능력, 그리고 최종적으로 생육과 수량입니다. 콩과 로메인 상추에 침수, 건조, 복합 처리를 적용하여 잎 생리 반응이 어느 단계까지 이어지는지, 기공이 얼마나 빨리 회복되는지, 생육과 수량의 감소로 이어지는지를 비교했습니다.')

# ===== 4 crops & treatments
s=S(4)
set_para(byname(s,'Header 상추').text_frame.paragraphs[0],'로메인 상추')
tx=byname(s,'Text 상추'); set_paras(tx,['x','처리 개시: 정식 3주 후 (영양생장기)','관찰: 처리 후 16일 (DAT 0~16)'])
runs_para(tx.text_frame.paragraphs[0],[('Lactuca sativa',True),(' L. cv. Claudius',False)])
tx=byname(s,'Text 콩'); runs_para(tx.text_frame.paragraphs[0],[('Glycine max',True),(' (L.) Merr. cv. Daewonkong',False)])
foot(s,'복합구는 침수 종료 후 침수구 관수량의 50%를 관수. 침수는 포트를 물통에 옮겨 3일간 잠기게 함. 콩은 처리 전부터 일부 뿌리가 포트 하단 배수구로 빠져나가 지면에 닿음.')
notes(s,'(약 20초) 공시 작물은 콩 대원콩과 로메인 상추 클라우디우스이며 전북대학교 부속농장에서 재배했습니다. 상추는 정식 3주 후 영양생장기에, 콩은 개화기에 처리를 시작했습니다. 처리구는 전날 손실된 수분량, 즉 증발산량만큼 관수한 대조구, 50%만 관수한 건조구, 3일간 침지한 뒤 정상 관수한 침수구, 침수 후 50% 관수한 복합구의 네 가지입니다.')

# ===== 5 schedule (rebuilt)
s=S(5)
for sh_ in list(s.shapes):
    if sh_.name.startswith('Oval') or sh_.name in ('TextBox 37','TextBox 55','TextBox 56'): rm(sh_)
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
# romaine row up under soybean row
lab=byname(s,'TextBox 38'); lab.top=Inches(3.2)
for nm in ('Rounded Rectangle 39','Rounded Rectangle 41'): byname(s,nm).top=Inches(3.1)
set_para(lab.text_frame.paragraphs[0],'로메인')
def box(x,y,w,h,text,fill,fc='FFFFFF',size=12,bold=False,align=PP_ALIGN.CENTER):
    b=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    b.fill.solid(); b.fill.fore_color.rgb=RGBColor.from_string(fill); b.line.fill.background(); b.shadow.inherit=False
    tf=b.text_frame; tf.word_wrap=True; tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    tf.margin_left=tf.margin_right=Inches(0.08); tf.margin_top=tf.margin_bottom=Inches(0.03)
    p=tf.paragraphs[0]; p.alignment=align; r=p.add_run(); r.text=text; r.font.size=Pt(size); r.font.bold=bold; r.font.color.rgb=RGBColor.from_string(fc)
    return b
rowsd=[('LI-600','기공전도도 · 형광','P1 : 매일 (DAT 1~9)\nP2 : 1~2주 간격','P1 : 매일 (DAT 1~10)\nP2 : 이틀 간격'),
       ('LI-6800','광합성 곡선 (A-Ci, A-PPFD)','P2 : 9월 중순\n(9/2~9/17, DAT 21~36)','P1~P2 : 10월 중순\n(10/16~10/19, DAT 9~12)'),
       ('생육 조사','수량 · 생육','9/1 (DAT 20), 10/6 (DAT 55)','10/23 (DAT 16)')]
X0=2.10; DX=0.19
for (y0,bnd,end) in [(2.74,9.5,55),(3.64,10.5,16)]:
    box(X0,y0,DX*bnd,0.22,'P1','5B9BD5',size=10,bold=True); box(X0+DX*bnd,y0,DX*(end-bnd),0.22,'P2','2F5597',size=10,bold=True)
box(2.1,4.05,4.9,0.4,'콩','6B4226',size=12,bold=True); box(7.15,4.05,5.4,0.4,'로메인 상추','2E6B3F',size=12,bold=True)
for i,(h,hs,a,b_) in enumerate(rowsd):
    y=4.5+i*0.5
    hb=box(0.5,y,1.5,0.44,h,'0B76A0',size=13,bold=True)
    box(2.1,y,4.9,0.44,a.replace('\n','  /  '),'E8EEF2',fc='1F2D3A',size=11.5)
    box(7.15,y,5.4,0.44,b_.replace('\n','  /  '),'E8EEF2',fc='1F2D3A',size=11.5)
byname(s,'Conclusion Box').top=Inches(6.05); byname(s,'Conclusion Box').height=Inches(0.55)
conc(s,'P1 : 침수 시작 ~ 종료 후 7일 (초기 반응·회복 시작)  ·  P2 : 이후 (회복 후기·건조 영향)')
foot(s,'콩 침수 8/12~14, 50% 관수는 8/15부터. 로메인 침수 10/7~10/10 오전, 50% 관수 10/12부터. 침수 시작일을 DAT 0으로 맞추어 두 작물을 정렬. P1 = 콩 DAT 1~9, 로메인 DAT 1~10 / P2 = 이후.')
notes(s,'(약 15초) 두 실험은 시기와 기간이 달라 침수 시작일을 DAT 0으로 맞추어 정렬했습니다. 로메인 상추는 처리 후 16일, 콩은 55일까지 관찰했습니다. LI-600은 초기에는 매일, 이후에는 콩은 1~2주 간격, 로메인은 이틀 간격으로 측정했고 LI-6800 광합성 곡선은 콩은 9월 중순, 로메인은 10월 중순에 측정했습니다. 결과는 침수 시작부터 종료 후 7일까지를 P1, 그 이후를 P2로 나누어 제시합니다.')

# ===== 6 measurement items
s=S(6)
bg=allnames(s,'Row bg'); chip=allnames(s,'Row chip'); ind=allnames(s,'Row ind'); met=allnames(s,'Row method')
for g in (bg,chip,ind,met): rm(g[2])
bg=allnames(s,'Row bg'); chip=allnames(s,'Row chip'); ind=allnames(s,'Row ind'); met=allnames(s,'Row method')
chips=['① 기공','② 명반응','③ 생화학적 능력','④ 생육·수량']
inds=['g_{sw}','Φ_{PSII}, F_{s}, ETR','V_{cmax}, J_{max}, R_{d}, A–PPFD (LSP)','종실 생체중·건조중, 지상부 건물중']
mets=['LI-600 포로미터, 처리 개시 후 반복 측정, 보정 gsw (Rizzo & Bailey, 2026)','LI-600 명적응 형광, PAR·기온 보정 (Ali et al., 2025; Gao et al., 2024)','LI-6800 A-Ci (FvCB), 광-광합성 곡선 (NRH 모형, LSP)','파괴 조사 (로메인 DAT 16, 콩 DAT 20·55)']
for k in range(4):
    y=1.50+k*1.08
    for g in (bg,chip,ind,met): g[k].top=Inches(y)
    set_para(chip[k].text_frame.paragraphs[0],chips[k]); set_para(ind[k].text_frame.paragraphs[0],inds[k]); set_para(met[k].text_frame.paragraphs[0],mets[k])
conc(s,'통계: 침수 × 관수 이원 ANOVA·Tukey (형광 지표는 측정일·PAR·기온 보정 평균)')
foot(s,'P1 = 침수 시작~종료 후 7일(콩 DAT 1~9, 로메인 DAT 1~10), P2 = 이후. 형광 지표(Φ_{PSII}, F_{s}, ETR) = PAR·기온 보정 평균 (Ali et al., 2025; Gao et al., 2024), g_{sw} = 온도 보정 gsw (Rizzo & Bailey, 2026; PAR·기온 공변량 보정 없음). 생육은 전 개체 사용.')
notes(s,'(약 20초) 앞서 제시한 네 단계에 맞추어 지표를 측정했습니다. 기공전도도와 명반응은 LI-600으로 반복 측정했고, 형광 지표는 측정 당시의 광도와 기온 차이를 선행 연구를 따라 공변량으로 보정했고, 기공전도도는 보정하지 않은 값을 사용했습니다. 광합성의 생화학적 능력은 LI-6800의 A-Ci와 광-광합성 곡선으로 평가했고, 생육과 수량은 파괴 조사로 측정했습니다.')

# ===== 33 (new) environment
s=S(33); title(s,'기상 센서 : 기온, 일적산광량 (DLI)')
replace_picture(s,byname(s,'Picture 26'),img(F3+'env.png'),valign='top')
sv=allnames(s,'Stat value'); sl=allnames(s,'Stat label')
set_para(sv[0].text_frame.paragraphs[0],'18.2 vs 28.4 °C'); set_para(sl[0].text_frame.paragraphs[0],'처리 기간 평균 기온 (로메인 vs 콩 DAT 0~16)')
set_para(sv[1].text_frame.paragraphs[0],'17.5 vs 22.0'); set_para(sl[1].text_frame.paragraphs[0],'DLI (mol·m^{−2}·d^{−1}, 로메인 vs 콩 DAT 0~16)')
set_paras2(byname(s,'Text 요점'),[('로메인:',' 처리 기간(10/7~10/23) 평균 기온 18.2 °C, DLI 17.5 mol·m^{−2}·d^{−1}로 저온·중간 일사 조건'),
 ('콩:',' 처리 초기(DAT 0~16) 평균 기온 28.4 °C, DLI 22.0 mol·m^{−2}·d^{−1}로 로메인보다 약 10 °C 높은 조건')])
conc(s,'로메인은 저온·중간 일사 조건에서 처리되어 증발산 부하와 건조 스트레스 강도가 다름')
foot(s,'밭콩: CR1000X 기상 센서, 로메인: 26번 온실 환경 데이터(CR300; 10/13·10/18 결측일 제외). 로메인 DLI = 일사량(MJ) × 2.02 mol/MJ 추정. 점선 = 침수 시작일.')
notes(s,'(약 20초) 두 실험은 계절이 달라 환경 조건이 크게 다릅니다. 콩의 처리 초기 평균 기온은 28.4도, 로메인 상추는 18.2도로 약 10도 낮았고 일적산광량도 로메인이 낮았습니다. 따라서 같은 50% 관수라도 증발산 부하가 달라 건조 스트레스 강도가 다르며, 두 작물의 차이는 병렬 사례로 해석하겠습니다.')

# ===== 7 treatment check
s=S(7); title(s,'로드셀·포트 무게 : 누적 관수량')
replace_picture(s,byname(s,'Picture 26'),img(F3+'irr_cum.png'),valign='top')
sv=allnames(s,'Stat value'); sl=allnames(s,'Stat label')
set_para(sv[0].text_frame.paragraphs[0],'43% · 40%'); set_para(sl[0].text_frame.paragraphs[0],'건조구 누적 관수량 (로메인 · 콩, 대조구 대비)')
set_para(sv[1].text_frame.paragraphs[0],'56% · 87%'); set_para(sl[1].text_frame.paragraphs[0],'침수구 누적 관수량 (로메인 · 콩, 대조구 대비)')
set_paras2(byname(s,'Text 요점'),[('로메인:',' 누적 관수량은 건조 43%·침수 56%·복합 37% (대조구 대비, 10/12~10/22, 포트 무게)'),
 ('콩:',' 누적 관수량은 건조 40%·침수 87%·복합 44% (대조구 대비, 8/16~10/6, 로드셀)')])
conc(s,'감수 관수는 실현됨 — 로메인 침수구는 과습으로 관수가 적었고 콩은 뿌리 이탈 가능성')
foot(s,'누적 관수량 = 일별 관수량의 합. 콩: 로드셀 관수량(mm) × 38.01 g/mm, 8/16~10/6(DAT 4~55). 로메인: 대조구는 로드셀 평균 관수량, 그 외는 관수량 시트의 포트 평균, 10/12~10/22(DAT 5~15).')
notes(s,'(약 30초) 결과를 보기 전에 처리가 실제로 어떻게 들어갔는지 확인했습니다. 대조구 대비 누적 관수량은 건조구가 로메인 43%, 콩 40%로 설계인 50%에 가까웠습니다. 침수구는 콩이 87%였지만 로메인은 화분이 과습한 상태가 유지되어 56%만 관수되었습니다. 복합구는 로메인 37%, 콩 44%였습니다. 다만 콩은 포트 밖으로 나간 뿌리가 있어 실제 수분 이용은 다를 수 있습니다.')

# ===== 8 gsw
s=S(8); title(s,'LI-600 : 기공전도도 (g_{sw})')
replace_picture(s,byname(s,'Picture 13'),img(F2+'ts_gsw.png'),valign='top')
t=table_of(s)
gr=pd.read_csv('an/intermediate/gsw_phase_raw.csv')
def gv(crop,per,tr):
    q=gr[(gr.작물==crop)&(gr.구간==per)&(gr.처리==tr)]
    return '–' if q.empty else f'{q.원평균.iloc[0]:.3f} {q.문자.iloc[0]}'
set_table(t,[['Treatment','Soybean P1','Soybean P2','Romaine P1','Romaine P2']]+[[tn]+[gv(c,p_,tr) for c,p_ in [('bean','P1'),('bean','P2'),('lettuce','P1'),('lettuce','P2')]] for tn,tr in [('Control','ETc'),('Drought','ETc50'),('Waterlogging','침수ETc'),('Combined','침수ETc50')]])
clean_table(t)
set_paras2(byname(s,'TextBox 10'),[('콩 P1:',' 침수구 0.27이 대조구 0.36보다 낮음'),
 ('콩 P2:',' 건조·복합구 0.22~0.23이 대조구·침수구 0.35보다 낮음'),
 ('로메인 P1:',' 침수 중 DAT 3에 대조구의 10%까지 급감했으나 DAT 5에 89%로 회복'),
 ('로메인 P2:',' 건조구 0.113이 침수구 0.162보다 낮음')])
foot(s,'표·그림: PAR·기온 보정 이전 원자료(온도 보정 gsw, Rizzo & Bailey 2026) 평균, Tukey 문자(처리 + 측정일 모형). 그림: 음영 ± SE, 회색 띠 흐린 날, 빗금 침수 기간, * 당일 P<0.05(Holm).')
notes(s,'(약 40초) 첫 번째 단계인 기공입니다. 그래프와 표는 측정 광도와 기온을 보정한 값입니다. 침수 기간 동안 두 작물 모두 기공전도도가 감소했습니다. 로메인 상추는 침수 3일째 대조구의 10%까지 떨어졌다가 배수 직후 빠르게 회복했고, 콩은 침수 효과가 DAT 9까지 이어졌습니다. 건조는 두 작물 모두 후반에 기공전도도를 낮췄습니다.')

# ===== 9 recovery
s=S(9); title(s,'LI-600 : 기공전도도 회복 (g_{sw}, % of control)')
replace_picture(s,byname(s,'Picture 26'),img(F3+'recovery.png'),valign='top')
set_paras2(byname(s,'Recovery text'),[('로메인:',' 침수 DAT 3에 대조구의 10%까지 낮아졌다가 DAT 5~6(89~98%)에 대조구 수준으로 회복'),
 ('콩:',' 침수 종료 6일 후(DAT 9)에도 48%였고 DAT 17 86%, DAT 23 105%로 회복')])
sv=allnames(s,'Stat value'); sl=allnames(s,'Stat label')
set_para(sv[0].text_frame.paragraphs[0],'2~3일'); set_para(sl[0].text_frame.paragraphs[0],'로메인: 배수 후 대조구 수준까지 회복')
set_para(sv[1].text_frame.paragraphs[0],'DAT 9: 48%'); set_para(sl[1].text_frame.paragraphs[0],'콩: 침수 종료 6일 후에도 미회복')
conc(s,'같은 3일 침수에도 로메인은 배수 2~3일 만에 회복, 콩은 DAT 9까지 회복되지 않음')
foot(s,'각 처리 g_{sw} ÷ 같은 날 대조구 g_{sw} × 100 (PAR·기온 보정 이전 일평균). * 대조 vs 처리 P<0.05(Welch t, Holm 보정). 건조·복합은 회색. 콩 DAT 10~16은 측정 없음, 콩 건조·복합은 DAT 17부터 측정.')
notes(s,'(약 50초) 각 처리구의 기공전도도를 같은 날 대조구에 대한 비율로 나타낸 그래프입니다. 건조와 복합은 회색으로 두고 침수 위주로 설명하겠습니다. 로메인 상추는 침수 3일째 10%까지 떨어졌지만 배수 후 2~3일, 즉 DAT 5~6에 대조구 수준으로 회복했습니다. 콩은 DAT 9에도 48%로 회복되지 않았고 DAT 17 이후에야 대조구에 가까워졌습니다.')

# ===== 11 PhiPSII
s=S(11); title(s,'LI-600 : 광계 II 양자수율 (Φ_{PSII})')
replace_picture(s,byname(s,'Picture 13'),img(F2+'ts_phi.png'),valign='top')
shp=[x for x in s.shapes if getattr(x,'has_table',False) and x.has_table][0]; t=shp.table
drop_col(t,3)
while len(t.rows)>5: delete_row(t,len(t.rows)-1)
ph=pd.read_csv('an/intermediate/phi_phase_single.csv')
def pv(crop,ph_,tr):
    q=ph[(ph.작물==crop)&(ph.구간==ph_)&(ph.처리==tr)]
    return '–' if q.empty else f'{q.보정평균.iloc[0]:.3f} {q.문자.iloc[0]}'
hdr=['Treatment','Soybean P1','Soybean P2','Romaine P1','Romaine P2']
for c_i,h in enumerate(hdr): set_cell(t.cell(0,c_i),h)
for r_i,tr in enumerate(['ETc','ETc50','침수ETc','침수ETc50'],start=1):
    for c_i,(crop,ph_) in enumerate([('bean','P1'),('bean','P2'),('lettuce','P1'),('lettuce','P2')],start=1): set_cell(t.cell(r_i,c_i),pv(crop,ph_,tr))
set_widths(shp,[1.9,1.4,1.4,1.4,1.4])
set_paras2(byname(s,'TextBox 10'),[('콩 P1:',' 침수구 0.679가 대조구 0.704보다 낮음'),
 ('콩 P2:',' 건조구 0.609가 가장 낮고 대조구 0.696과 차이를 보임 (복합 0.631, 침수 0.660)'),
 ('로메인:',' P1 0.585~0.611, P2 0.642~0.655로 4처리 간 차이 없음')])
conc(s,'콩은 건조구에서 Φ_{PSII}가 낮았고, 로메인은 처리 간 차이 없음')
foot(s,'표·그림: 측정일·PAR·기온 보정 평균, Tukey 문자. P2는 PPFD 수준을 나누지 않고 통합하여 분석. 그림: 음영 ± SE, 점선 P1/P2 경계, 회색 띠 흐린 날, * 당일 P<0.05(Holm), X 처리 전.')
notes(s,'(약 35초) 두 번째 단계인 명반응입니다. P2 구간은 광도 수준을 나누지 않고 통합하여 분석했습니다. 콩에서는 P1에서 침수구가 대조구보다 약간 낮았고, P2에서는 건조구의 Φ_PSII가 0.61로 대조구 0.70보다 낮았습니다. 로메인 상추는 P1과 P2 모두 처리 간 차이가 없었습니다. 따라서 로메인에서는 기공이 닫혔는데도 명반응은 영향을 받지 않았습니다.')

# ===== 13 photosynthetic capacity
s=S(13); title(s,'LI-6800 : 광합성 능력 (V_{cmax}, J_{max}, R_{d}, A–PPFD)')
replace_picture(s,byname(s,'Picture 13'),img(F3+'params.png'),valign='top',maxh=3.0,maxw=7.2)
shp=[x for x in s.shapes if getattr(x,'has_table',False) and x.has_table][0]; t=shp.table
for _ in range(2):
    for tr in t._tbl.tr_lst:
        tr.append(copy.deepcopy(tr.tc_lst[-1]))
    t._tbl.tblGrid.append(copy.deepcopy(t._tbl.tblGrid.findall(A+'gridCol')[-1]))
pt=pd.read_csv('an/intermediate/params_table.csv')
def g(crop,par,tr,pre=False):
    q=pt[(pt.crop==crop)&(pt.par==par)&(pt.trt==tr)].iloc[0]
    if pre: return f'{q.pre:.0f}'
    lets=pt[(pt.crop==crop)&(pt.par==par)].letter.fillna('')
    show=len(set(lets))>1
    return f'{q["mean"]:.0f}'+(f' {q.letter}' if show else '')
hd=['Treatment','Soy V_{cmax}','Soy J_{max}','Soy LSP','Rom V_{cmax}','Rom J_{max}','Rom LSP']
for c_i,h in enumerate(hd): set_cell(t.cell(0,c_i),h)
cols=[('bean','Vcmax'),('bean','Jmax'),('bean','LSP'),('lettuce','Vcmax'),('lettuce','Jmax'),('lettuce','LSP')]
set_cell(t.cell(1,0),'Pre-treatment'); 
for c_i,(cr,pa) in enumerate(cols,start=1): set_cell(t.cell(1,c_i),g(cr,pa,'ETc',pre=True))
for r_i,(tr,nm) in enumerate(zip(['ETc','ETc50','침수ETc','침수ETc50'],['Control','Drought','Waterlogging','Combined']),start=2):
    set_cell(t.cell(r_i,0),nm)
    for c_i,(cr,pa) in enumerate(cols,start=1): set_cell(t.cell(r_i,c_i),g(cr,pa,tr))
set_widths(shp,[1.4,0.95,0.95,0.95,1.0,1.0,0.95],0.255); shp.left=Inches(0.5); shp.top=Inches(4.5)
set_paras2(byname(s,'TextBox 10'),[('콩:',' 건조구의 V_{cmax} 68·J_{max} 104가 대조구 90·150보다 낮고, LSP는 건조구가 816으로 대조구 561보다 높음'),
 ('로메인:',' 복합구의 V_{cmax} 73·J_{max} 142가 대조구 104·200보다 낮고, LSP는 처리 간 차이 없음')])
conc(s,'콩 건조·복합구(9월)와 로메인 복합구(10월)에서 V_{cmax}·J_{max}가 낮은 경향 — 측정일 교락으로 확정은 어려움')
foot(s,'상자: 사분위(n≥4), 가로선: 평균 ± SE(n<4), 점: 개별 곡선, 문자: Tukey(ANOVA P<0.05일 때만). 곡선: NRH 모형 평균, ▼ = LSP (광포화점), 로메인 1,500 초과는 외삽(점선). 콩 9/2~9/17, 로메인 10/16~19 측정으로 처리와 측정일이 교락됨.')
notes(s,'(약 35초) 세 번째 단계인 광합성의 생화학적 능력입니다. 콩은 9월 측정에서 건조구와 복합구의 최대 카르복실화 속도와 최대 전자전달 속도가 낮았고, 로메인 상추도 복합구에서 가장 낮은 경향을 보였습니다. 오른쪽 광-광합성 곡선의 역삼각형은 광포화점으로, 콩은 건조구에서 높았고 로메인은 처리 간 차이가 없었습니다. 다만 처리별로 측정일이 달라 측정일과 처리 효과가 섞여 있고 곡선 수도 처리당 3~4개로 적어 확정적으로 말하기는 어렵습니다.')

# ===== 14 yield
s=S(14); title(s,'생육 조사 : 수량 및 지상부 생육')
for nm in ('Stat box','Stat value','Stat label'):
    for x in allnames(s,nm): rm(x)
pic=replace_picture(s,byname(s,'Picture 26'),img(F3+'yield.png'),valign='top')
pic.left=Inches(0.72); pic.top=Inches(1.25)
src=[x for x in S(11).shapes if getattr(x,'has_table',False) and x.has_table][0]
el=add_table_copy(s,src,remove_existing=False)
tshape=[x for x in s.shapes if x._element is el][0]; tb=tshape.table
yt=pd.read_csv('an/intermediate/yield_table.csv')
def yrow(lab,i):
    r=yt.iloc[i]; vals=[r.ETc,r.ETc50,r.침수ETc,r.침수ETc50]; d=[None,r.d_ETc50,r.d_침수,r.d_복합]
    fm=(lambda v:f'{v:.1f}') if vals[0]<20 else (lambda v:f'{v:.0f}')
    cells=[]
    for k,(v,dd) in enumerate(zip(vals,d)):
        cells.append(fm(v) if dd is None else f'{fm(v)} ({pct(-int(abs(dd)+0.5) if dd<0 else int(abs(dd)+0.5))})')
    return [lab]+cells
rows_data=[['Crop · variable','Control','Drought','Waterlog.','Combined'],['Romaine DAT 16','','','',''],
 yrow('Shoot FW (g)',4),yrow('Shoot DW (g)',5),['Soybean DAT 55','','','',''],
 yrow('Seed DW (g)',0),yrow('Seed no.',1),yrow('Pod no.',2),yrow('Seed FW (g)',3)]
while len(tb.rows)<len(rows_data):
    tb._tbl.append(copy.deepcopy(tb._tbl.tr_lst[-1]))
while len(tb.rows)>len(rows_data): delete_row(tb,len(tb.rows)-1)
for r_i,row in enumerate(rows_data):
    for c_i,v in enumerate(row): set_cell(tb.cell(r_i,c_i),v if v else ' ')
set_widths(tshape,[1.9,1.45,1.45,1.45,1.45],0.255); tshape.left=Inches(0.5); tshape.top=Inches(3.72)
set_paras2(byname(s,'Text 요점'),[('로메인:',' 지상부 건물중이 건조 −16%, 침수 −34%, 복합 −43% 감소하고 생체중도 −29·−26·−38% 감소 (DAT 16)'),
 ('콩:',' 종실 생체중은 −5·−5·−14%, 종실 건조중은 −4·−9·−18%로 감소하는 경향이나 처리 간 유의한 차이 없음 (DAT 55)')])
conc(s,'로메인은 건물중 −16~43% 감소, 콩은 수량 감소 경향이나 유의차 없음')
foot(s,'표: 평균 (대조구 대비 %), 건조·침수·복합 순. 로메인 10/23(DAT 16) 처리당 8~9주, 콩 10/6(DAT 55, R6~R7) 파괴조사 n=6~9. 그림: 평균 ± SE, 문자 Tukey(ANOVA P<0.05일 때만). 종실 생체중 = 개체당 종실 전체 생체중, 처리 간 유의차 없음.')
notes(s,'(약 50초) 네 번째 단계인 생육과 수량입니다. 로메인 상추는 건조구 16%, 침수구 34%, 복합구 43%의 지상부 건물중 감소를 보였습니다. 콩은 종실 생체중, 종실 건조중, 종실 수, 꼬투리 수 모두 처리 간 유의한 차이가 없었습니다. 표에 대조구 대비 감소율을 같이 적었는데, 종실 생체중은 건조 5%, 침수 5%, 복합 14% 감소했고 종실 건조중은 복합구에서 18%까지 감소하는 경향이 있었습니다. 다만 검출 한계가 약 40~50%이고 뿌리가 포트 밖으로 나간 영향이 있어 근거는 약합니다.')

# ===== 16 summary matrix
s=S(16); title(s,'종합 : 지표별 반응 (대조구 대비)')
A_NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
def fill(shape,hexv):
    f=shape._element.spPr.find('a:solidFill',A_NS); f[0].set('val',hexv)
heads=allnames(s,'Col head')
for h in heads:
    if abs(h.left/914400-5.90)<0.05 or abs(h.left/914400-7.50)<0.05: rm(h)
heads=allnames(s,'Col head')
cells=allnames(s,'Cell')
for c in cells:
    if abs(c.left/914400-5.90)<0.05 or abs(c.left/914400-7.50)<0.05: rm(c)
cells=allnames(s,'Cell')
X=[2.70,5.10,7.50,9.90]; W=2.30
htxt=[('① 기공','g_{sw}'),('② 명반응','Φ_{PSII}'),('③ 생화학','V_{cmax} · J_{max}'),('④ 생육·수량','대조구 대비 %')]
for h,x,(a,b) in zip(heads,X,htxt):
    h.left=Inches(x); h.width=Inches(W); ps=h.text_frame.paragraphs; set_para(ps[0],a); set_para(ps[1],b)
N,Mi,G,Sg='EFEFEF','D9EAD3','F8CBAD','E97132'
grid=[ # rows: 로메인 건조, 침수, 복합, 콩 건조, 침수, 복합
 [(['↓ 후반','(DAT 16 33%)'],G),(['–'],N),(['–'],N),(['건물중 −16%'],G)],
 [(['↓ → 회복','DAT 5~6'],Mi),(['–'],N),(['↓ 경향','(측정일 교락)'],G),(['건물중 −34%'],Sg)],
 [(['↓ → 회복','DAT 6'],Mi),(['–'],N),(['↓ 경향','(V_{cmax} 73)'],G),(['건물중 −43%'],Sg)],
 [(['↓ 지속'],G),(['↓↓ (P2)'],Sg),(['↓ V_{cmax}·J_{max}','(9월)'],G),(['생육 −35%','수량 −5%'],G)],
 [(['↓ DAT 9까지','미회복'],G),(['↓ (P1)'],G),(['–'],N),(['생육 −28%','수량 −5%'],G)],
 [(['↓ 지속'],G),(['↓ (P2)'],G),(['↓ J_{max}','(9월)'],G),(['생육 −19%','수량 −14%'],N)]]
rowtop=[2.18,2.82,3.46,4.22,4.86,5.50]
k=0
cells=sorted(cells,key=lambda c:(round(c.top/914400,2),c.left))
for r_i in range(6):
    for c_i in range(4):
        c=cells[r_i*4+c_i]; txt,colr=grid[r_i][c_i]
        c.left=Inches(X[c_i]); c.width=Inches(W); c.top=Inches(rowtop[r_i])
        set_paras(c,txt); fill(c,colr)
for lab in allnames(s,'Row label'):
    replace_all_runs(lab,'상추','로메인')
conc(s,'로메인은 건물중 −16~43% 감소, 콩은 종실 생체중 −5~14% 감소 경향')
foot(s,'↓↓ 큰 감소 · ↓ 감소 · – 차이 없음. ④ 대조구 대비 %: 로메인 지상부 건물중(DAT 16), 콩 생육 = 지상부 생체중(잎+줄기), 수량 = 종실 생체중(DAT 55). 생화학은 콩 9월·로메인 10월 곡선(측정일 교락).')
notes(s,'(약 20초) 지금까지의 결과를 작물, 처리, 단계별로 정리한 표입니다. 로메인 상추는 기공이 침수 직후 크게 닫혔다가 며칠 만에 회복했고 명반응에는 변화가 없었지만, 건물중은 침수 34%, 복합 43% 감소했습니다. 콩은 기공 회복이 느렸고 건조구에서 명반응이 낮았지만 수량은 종실 생체중 기준 5~14% 감소하는 데 그쳤습니다. 같은 수분 재해라도 작물에 따라 영향이 나타나는 단계가 다릅니다.')

# ===== 17 / 34 discussion (recap graphs)
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
def recap_slide(s,crop,ttl,steps,concl,ft,nt):
    title(s,ttl)
    for x in list(s.shapes):
        if x.name.startswith(('Card ','Header ','Text ')): rm(x)
    pic=s.shapes.add_picture(F3+f'recap_{crop}.png',Inches(0.55),Inches(2.05),width=Inches(12.2))
    n=len(steps); W=12.2; cx=[0.55+W*f for f in (0.13,0.375,0.62,0.865)]
    for k,(a,b) in enumerate(steps):
        bx=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(cx[k]-1.35),Inches(1.35),Inches(2.7),Inches(0.62))
        bx.fill.solid(); bx.fill.fore_color.rgb=RGBColor.from_string('0B76A0'); bx.line.fill.background(); bx.shadow.inherit=False
        tf=bx.text_frame; tf.word_wrap=True; tf.vertical_anchor=MSO_ANCHOR.MIDDLE
        tf.margin_top=tf.margin_bottom=Inches(0.02)
        p=tf.paragraphs[0]; p.alignment=PP_ALIGN.CENTER; r=p.add_run(); r.text=a; r.font.size=Pt(13); r.font.bold=True; r.font.color.rgb=RGBColor(255,255,255)
        p2=tf.add_paragraph(); p2.alignment=PP_ALIGN.CENTER; r2=p2.add_run(); r2.text=b; r2.font.size=Pt(10.5); r2.font.color.rgb=RGBColor(255,255,255)
        if k<n-1:
            ar=s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,Inches(cx[k]+1.42),Inches(1.52),Inches(0.5),Inches(0.28))
            ar.fill.solid(); ar.fill.fore_color.rgb=RGBColor.from_string('9AA5AE'); ar.line.fill.background(); ar.shadow.inherit=False
    conc(s,concl); foot(s,ft); notes(s,nt)
recap_slide(S(17),'bean','고찰 : 콩 (기공 → 명반응 → 광합성 능력 → 수량)',
 [('① 기공','gsw 회복'),('② 명반응','ΦPSII'),('③ 광합성 능력','Vcmax · Jmax'),('④ 수량','종실 생체중')],
 '콩은 생리 지표에서 차이가 있었고, 수량에는 감소하는 경향이 보였지만 큰 차이가 없었다',
 '기공·수량 그래프의 건조·복합은 회색. Tan et al. 2018 J Plant Physiol; Haverroth et al. 2024 Plant Physiol; Buckley 2019 New Phytol; Yeung et al. 2018 PNAS; Sasidharan et al. 2018 Plant Physiol (참고문헌: 보충 자료 A6)',
 '(약 60초) 먼저 콩입니다. 앞서 본 결과를 논리 순서대로 다시 정리하겠습니다. 침수 직후 기공전도도가 먼저 감소했고 DAT 9에도 대조구의 48%로 회복이 느렸습니다. 뿌리의 저산소는 아쿠아포린 기능과 뿌리 수리전도도를 떨어뜨려 잎의 수분 상태를 악화시키고 기공을 닫는 것으로 보고됩니다. 두 번째로 명반응은 건조구에서 P2에 낮아졌고, 세 번째로 광합성의 생화학적 능력도 건조·복합구에서 낮은 경향이었습니다. 그러나 네 번째 수량은 종실 생체중이 5~14% 감소하는 경향이었으나 큰 차이가 없었습니다. 즉 콩은 생리 지표에서는 차이가 있었지만 수량으로는 이어지지 않았습니다. 개화기 처리 후 55일의 회복 기간 동안 보상이 있었을 가능성이 있으나 이는 가설입니다.')
recap_slide(S(34),'lettuce','고찰 : 로메인 상추 (기공 → 명반응 → 광합성 능력 → 건물중)',
 [('① 기공','gsw 회복'),('② 명반응','ΦPSII'),('③ 광합성 능력','Vcmax · Jmax'),('④ 생육','지상부 건물중')],
 '로메인 상추는 회복이 빨랐지만 침수 기간 동안의 손실이 유지됨',
 '기공·수량 그래프의 건조·복합은 회색. Körner 2015 Curr Opin Plant Biol 25:107; Tardieu et al. 2018 Annu Rev Plant Biol; Haverroth et al. 2024 Plant Physiol (참고문헌: 보충 자료 A6)',
 '(약 60초) 다음은 로메인 상추입니다. 침수 3일째 기공전도도가 대조구의 10%까지 떨어졌지만 배수 후 2~3일 만에 대조구 수준으로 회복했습니다. 명반응은 처리 간 차이가 없었고, 광합성의 생화학적 능력은 복합구에서만 낮은 경향이었습니다. 그럼에도 지상부 건물중은 건조 16%, 침수 34%, 복합 43% 감소했습니다. 식물의 생장은 탄소 공급보다 조직 성장과 세포 팽압이 먼저 제한되는 경우가 많아, 침수 기간 동안 생긴 생장 손실이 회복 후에도 유지된 것으로 해석됩니다. 로메인은 영양생장기에 처리했고 수확물이 지상부라 이 손실이 곧 수량 손실입니다.')

# ===== 18 conclusion
s=S(18); title(s,'결론')
for _n in ('Card 향후 계획','Header 향후 계획','Future step','Down'):
    for _x in allnames(s,_n): rm(_x)
cs=allnames(s,'Concl')
for _x in cs: _x.width=Inches(10.8)
set_para(cs[0].text_frame.paragraphs[0],'기공 회복 속도'); set_para(cs[0].text_frame.paragraphs[1],'침수는 두 작물 모두에서 기공전도도를 먼저 낮췄다. 로메인은 배수 2~3일 후(DAT 5~6) 대조구 수준으로 회복했고, 콩은 배수 6일 후(DAT 9)에도 대조구의 48%였으며 DAT 23에 회복이 확인되었다.')
set_para(cs[1].text_frame.paragraphs[0],'명반응과 광합성 능력'); set_para(cs[1].text_frame.paragraphs[1],'로메인은 Φ_{PSII}에 처리 차이가 없었고 V_{cmax}·J_{max}는 복합구에서 낮은 경향(측정일 교락)이었다. 콩은 건조구에서 Φ_{PSII}(P2)와 V_{cmax}·J_{max}가 낮았다.')
set_para(cs[2].text_frame.paragraphs[0],'생육·수량'); set_para(cs[2].text_frame.paragraphs[1],'로메인은 기공이 회복되었는데도 침수 기간의 손실이 유지되어 지상부 건물중이 감소했다(건조 −16%, 침수 −34%, 복합 −43%). 콩은 종실 생체중이 5~14% 감소하는 경향이었으나 처리 간 유의한 차이는 없었다.')
conc(s,'로메인은 회복이 빠르나 생육 감소, 콩은 회복이 느리나 수량 차이 작음 — 반응은 작물마다 다름')
notes(s,'(약 40초) 결론입니다. 첫째, 침수는 두 작물에서 기공을 먼저 제한했고 로메인은 배수 2~3일 만에, 콩은 DAT 9 이후에 회복했습니다. 둘째, 명반응과 광합성 능력은 로메인에서 거의 변하지 않았고 콩은 건조구에서 낮았습니다. 셋째, 로메인은 기공이 회복되었는데도 침수 기간의 손실이 유지되어 건물중이 감소했고, 콩은 수량이 감소하는 경향이었지만 큰 차이는 없었습니다. 따라서 수분 스트레스에 대한 반응은 작물마다 다릅니다. 감사합니다.')
notes(S(19),'이상으로 발표를 마치겠습니다. 감사합니다. (질의응답 2분)')

# ===== appendix list
s=S(20)
tb=byname(s,'Appendix list')
set_paras(tb,['A1. LI-600 보정: 선형 PAR + 기온','A2. LI-6800 광-광합성 곡선 (A-Q)','A3. 정상 상태 형광 (F_{s})','A4. 전자전달속도 (ETR)','A5. 측정 당시 일사 조건: 흐린 날 표시','A6. 참고문헌'])
notes(s,'질의응답용 보충 자료 목록입니다.')

# ===== A1 LI-600 calibration
s=S(21); title(s,'LI-600 : PAR·기온 보정')
for _x in [x for x in s.shapes if getattr(x,'has_table',False) and x.has_table]: rm(_x)
set_paras2(byname(s,'TextBox 10'),['이유: 같은 날에도 처리 간 PAR·기온이 달랐음 (콩 8/13 PAR 970 vs 632, 기온 33.3 vs 34.0 °C; 로메인 PAR 약 30~1,250)',
 '모형: y = μ + 처리 + 측정일 + β_{1}·Q_{amb} + β_{2}·T_{air} + ε (Ali et al., 2025; Gao et al., 2024)',
 '선형 PAR이 AIC 최소, Φ_{PSII}는 PAR 100당 콩 −0.022, 로메인 −0.029 감소, 기온 기울기는 비유의',
 '로메인: g_{sw}·Φ_{PSII}·F_{s}·ETR 모두 PAR만 보정과 PAR+기온 보정의 판정이 같음'])
conc(s,'큰 차이(g_{sw}, F_{s}, 콩 P2)는 보정에 안정적 — 작은 차이(콩 P1 Φ_{PSII}, ETR)는 보정 방식에 민감')
notes(s,'질의응답용 자료입니다. LI-600은 야외 광에서 측정하기 때문에 같은 날에도 처리마다 측정 광도와 기온이 달랐습니다. 그래서 측정일, 선형 PAR, 기온을 공변량으로 보정했고, 로메인 상추에서는 PAR만 보정한 결과와 기온까지 보정한 결과의 유의성 판정이 모든 지표에서 같았습니다.')

# ===== A2 A-Q curves (repurposed slide 22)
s=S(22); title(s,'LI-6800 : 광-광합성 곡선 (A-Q)')
replace_picture(s,byname(s,'Picture 13'),img(F3+'aq.png'),valign='top')
set_para(byname(s,'Header PPFD별 Dunc').text_frame.paragraphs[0],'PPFD 1,500에서의 A')
t=table_of(s)
set_table(t,[['A (PPFD 1500)','Soybean','Romaine'],['Pre-treatment','12.9','22.6'],['Control','16.4','19.5'],['Drought','16.7','19.5'],['Waterlogging','12.5','21.2'],['Combined','15.8','17.7']])
while len(t.rows)>6: delete_row(t,len(t.rows)-1)
set_paras(byname(s,'TextBox 10'),['PPFD 8개 수준 모두에서 처리 간 유의차 없음','처리 전 곡선은 콩에서 처리 후보다 낮고(약 13), 로메인은 처리 전 약 23으로 처리 후(18~21)보다 높음','콩 침수구 12.5는 대조구 16.4보다 낮은 경향, 로메인 복합구 17.7도 낮은 경향'])
conc(s,'두 작물 모두 처리 간 A-Q 곡선 차이는 없음')
foot(s,'값: 평균 ± SE (µmol CO_{2} m^{−2}·s^{−1}). 콩 처리 전 7/22~23(3곡선), 로메인 처리 전 10/4(3곡선), 처리 후 처리당 3곡선(10/16~19). PPFD 수준별 Tukey.')
notes(s,'질의응답용 자료입니다. 광합성 광반응 곡선은 PPFD 8개 수준 모두에서 두 작물 모두 처리 간 유의한 차이가 없었습니다.')

# ===== A3 Fs, A4 ETR
s=S(25); title(s,'LI-600 : 정상 상태 형광 (F_{s})')
replace_picture(s,byname(s,'Picture 13'),img(F2+'ts_fs.png'),valign='top')
t=table_of(s)
set_table(t,[['Treatment',None,None,'Romaine P1','Romaine P2'],[None,None,None,'157.3 a (157.1;158.3)','142.1 a (142.8;143.2)'],[None,None,None,'161.0 a (161.0;159.3)','141.8 a (142.5;142.7)'],[None,None,None,'158.0 a (158.0;157.7)','141.6 a (142.1;141.2)'],[None,None,None,'161.6 a (161.7;162.6)','144.5 a (144.7;143.4)'],[None,None,None,'0.99','0.63'],[None,None,None,'0.66','0.92']])
clean_table(t)
set_paras(byname(s,'TextBox 10'),['처리 전 F_{s}: 콩 118, 로메인 154','콩 P1 침수 139 > 대조구 129, P2 건조·침수·복합 131~134 > 대조구 113','로메인 P1 155~162, P2 142~145로 처리 간 차이 없음'])
conc(s,'F_{s} 절대값 차이는 형광 신호 크기 변화를 포함 — 생리 해석은 비율 지표(Φ_{PSII})로')
foot(s,'표: 측정일·선형 PAR(Q_{amb})·기온(T_{air}) 보정 평균, Tukey 문자. 그림(보정 일평균): 음영 ± SE, 점선 P1/P2 경계, 회색 띠 흐린 날, * 당일 P<0.05(Holm), X 처리 전.')
notes(s,'질의응답용 자료입니다. 정상 상태 형광 Fs의 절대값은 로메인 상추에서 처리 간 차이가 없었고, 콩에서는 침수·건조 처리구가 대조구보다 높았습니다.')
s=S(26); title(s,'LI-600 : 전자전달속도 (ETR)')
replace_picture(s,byname(s,'Picture 13'),img(F2+'ts_etr.png'),valign='top')
t=table_of(s)
set_table(t,[['Treatment',None,None,'Romaine P1','Romaine P2'],[None,None,None,'141.7 a (141.5;147.1)','75.6 a (76.4;72.3)'],[None,None,None,'137.8 a (137.8;129.8)','78.3 a (79.0;75.5)'],[None,None,None,'132.7 a (132.7;130.8)','72.7 a (73.2;75.6)'],[None,None,None,'130.1 a (130.2;134.5)','80.4 a (80.5;85.6)'],[None,None,None,'0.84','0.56'],[None,None,None,'0.060','0.61']])
clean_table(t)
set_paras(byname(s,'TextBox 10'),['처리 전 ETR: 콩 187','콩 P1 대조구 119 > 침수 110, P2 대조구 190 > 복합 165 > 건조 146','로메인 P1 대조구 142 > 침수 133·복합 130 경향, P2 처리 간 차이 없음'])
foot(s,'표: 측정일·선형 PAR(Q_{amb})·기온(T_{air}) 보정 평균, Tukey 문자.')
notes(s,'질의응답용 자료입니다. 전자전달속도는 측정 광도에 비례하므로 광도를 보정한 평균으로 비교했고, 로메인 상추에서는 침수구가 약 6~8% 낮은 경향을 보였지만 측정일 반복 기준으로는 유의하지 않았습니다.')

# ===== A5 cloudy days
s=S(27); title(s,'A5. 측정 당시 일사 조건: 흐린 날 표시')
for lab in allnames(s,'Rounded Rectangle 8'): set_para(lab.text_frame.paragraphs[0],'로메인 상추')
rows=[('10/06','10:20–10:22','214','0.50','사용 (흐림)'),('10/08','09:29–09:36','133','0.42','사용 (흐림)'),('10/09','10:53–10:59','228','0.45','사용 (흐림)'),
('10/10','09:44–09:53','354','0.96','사용'),('10/11','11:17–11:28','366','0.74','사용'),('10/12','10:36–10:57','484','0.97','사용'),
('10/13','09:33–10:06','14','0.04','사용 (흐림)'),('10/14','09:28–09:53','378','1.10','사용'),('10/15','09:31–09:51','342','0.98','사용'),
('10/16','09:40–09:56','334','0.90','사용'),('10/17','08:59–09:33','260','0.97','사용'),('10/19','08:28–09:27','134','0.60','사용'),
('10/21','09:47–10:04','21','0.05','사용 (흐림)'),('10/23','09:33–09:55','340','0.95','사용')]
set_table(table_of(s,1),[list(r) for r in rows],start_row=1)
foot(s,'CI = 측정 구간 평균 SW / 같은 시각대 ±10일 90분위수 SW(맑은 날 기준). 날짜별 예외 없이 한 규칙으로 통일. 로메인 10/13은 SW 자료가 4분뿐(결측).')
notes(s,'질의응답용 자료입니다. 흐린 날은 제외하지 않고 측정 광도와 기온으로 보정했으며, 맑음지수 0.5 미만인 날을 그림에 회색 띠로 표시했습니다.')

# ===== A6 references
s=S(35); title(s,'A6. 참고문헌')
refs=['Ali et al. (2025) J Exp Bot 76:4141.','Buckley TN (2019) New Phytol 224 (doi:10.1111/nph.15899).','Gao et al. (2024) J Exp Bot 75:4904.','Haverroth EJ et al. (2024) Plant Physiol 197(1):kiae336.','Hilker M et al. (2016) Biol Rev 91:1118–1133.','Körner C (2015) Curr Opin Plant Biol 25:107–114.','Rizzo KT, Bailey BN (2026) Plant Cell Environ 49:1412–1423.','Sasidharan R et al. (2018) Plant Physiol 176:1106–1117.','Swain DL et al. (2018) Nat Clim Change 8:427–433.','Tan X et al. (2018) J Plant Physiol 227:20–30.','Tardieu F, Simonneau T, Muller B (2018) Annu Rev Plant Biol 69.','Yeung E et al. (2018) PNAS 115:E6085–E6094.','Zandalinas SI, Mittler R (2022) New Phytol 234:1161–1167.']
set_paras(byname(s,'Appendix list'),refs)
notes(s,'발표에 인용한 참고문헌입니다.')

# ===== delete excluded + reorder
sld=prs.slides._sldIdLst; ids=list(sld)
order=[1,2,3,4,5,6,33,7,8,9,11,13,14,16,17,34,18,19,20,21,22,25,26,27,35]
keep={ids[i-1] for i in order}
for x in ids:
    if x not in keep:
        prs.part.drop_rel(x.rId); sld.remove(x)
cur={ids[i-1]:i for i in order}
newlist=[ids[i-1] for i in order]
for x in list(sld): sld.remove(x)
for x in newlist: sld.append(x)
for _s in prs.slides:
    for _sh in _s.shapes:
        if getattr(_sh,'has_table',False) and _sh.has_table: bottom_border(_sh.table)
    fix_timing(_s)
prs.save('oral/oral_v4.pptx'); print('saved',len(prs.slides))
