import sys,re,copy; sys.path.insert(0,'.')
from lib import *
from pptx.util import Pt
from pptx.dml.color import RGBColor
from PIL import Image
R='/home/user/-/'; AN='an/'
src=open('oral_b.py').read()
for fn in ('bottom_border','compact_table','drop_col','set_widths'):
    m=re.search(r'\ndef '+fn+r'\(.*?(?=\ndef |\n# =====|\nMM=)',src,flags=re.S); exec(m.group(0))
prs=Presentation(R+'구두발표_콩vs로메인상추_v9.pptx')
SL=list(prs.slides); S=lambda n: SL[n-1]
PNS='{http://schemas.openxmlformats.org/presentationml/2006/main}'; ANS='{http://schemas.openxmlformats.org/drawingml/2006/main}'
def byname(s,n,k=0): return [x for x in s.shapes if x.name==n][k]
def rm(sh): sh._element.getparent().remove(sh._element)
def notes(s,t): s.notes_slide.notes_text_frame.text=t
def newids(s,els):
    mx=max(int(e.get('id')) for e in s.shapes._spTree.iter(PNS+'cNvPr'))
    for el in els:
        for c in el.iter(PNS+'cNvPr'): mx+=1; c.set('id',str(mx))
def copy_el(dst,el):
    e=copy.deepcopy(el); dst.shapes._spTree.append(e); newids(dst,[e]); return e
def shp(s,el): return [x for x in s.shapes if x._element is el][0]
# ---------- merge slide 7 -> slide 4
s4,s7=S(4),S(7)
set_para(s4.shapes.title.text_frame.paragraphs[0],'공시 작물, 수분 처리 및 재배 환경')
for nm,hy,cy,ty in (('상추',1.25,1.48,1.78),('콩',3.15,3.38,3.68)):
    byname(s4,'Header '+nm).top=Inches(hy); c=byname(s4,'Card '+nm); c.top=Inches(cy); c.height=Inches(1.6); byname(s4,'Text '+nm).top=Inches(ty); byname(s4,'Text '+nm).height=Inches(1.3)
te=copy_el(s4,[x for x in s7.shapes if getattr(x,'has_table',False) and x.has_table][0]._element); tx=shp(s4,te); tt=tx.table
set_widths(tx,[2.3,1.5,1.55],0.26); tx.left=Inches(0.92); tx.top=Inches(5.15)
# only top and bottom rules
for tc in tt._tbl.iter(ANS+'tc'):
    tcPr=tc.find(ANS+'tcPr')
    if tcPr is not None:
        for tag in ('lnT','lnB'):
            for e in tcPr.findall(ANS+tag): tcPr.remove(e)
bottom_border(tt)
tbx=byname(s4,'TextBox 121'); tbx.height=Inches(1.3)
p=tbx.text_frame.add_paragraph()
for tx_,b in (('재배 장소 : ',True),('전북대학교 부속농장 온실',False)):
    r=p.add_run(); r.text=tx_; r.font.size=Pt(13); r.font.bold=b; r.font.color.rgb=RGBColor.from_string('333333')
notes(s4,'(약 40초) 공시 작물은 상추와 콩 두 종이며, 각각 대조, 건조, 침수, 복합 네 처리구를 설정했습니다. 두 실험 모두 전북대학교 부속농장 온실에서 진행했습니다. 관수는 식물체가 전날 증산한 만큼 다음날 관수했고, 건조와 복합 처리는 그 50%만 관수했으며, 침수는 포트를 물에 담가 72시간, 즉 3일간 처리했습니다. 복합 처리는 침수 직후 건조 처리를 이어서 했습니다. 처리 기간인 DAT 0~16의 환경은 표와 같이 콩이 상추보다 평균 기온이 약 10도 높았고 일적산광량과 습도도 달라, 같은 처리라도 스트레스 강도가 다를 수 있어 두 작물은 병렬 사례로 비교하겠습니다.')
# ---------- recap pictures / texts
def swap_pic(s,path):
    pic=[x for x in s.shapes if x.shape_type==13 and abs(x.width/914400-12.2)<0.05][0]
    L,T,W,H=pic.left,pic.top,pic.width,pic.height; el=pic._element
    n=s.shapes.add_picture(path,L,T,W,H); el.addprevious(n._element); el.getparent().remove(el)
swap_pic(S(13),AN+'figs4/recap3_bean.png'); swap_pic(S(14),AN+'figs4/recap3_lettuce.png')
for s in (S(13),S(14)):
    rects=sorted([x for x in s.shapes if x.name.startswith('Rounded Rectangle')],key=lambda r:r.left)
    set_para(rects[0].text_frame.paragraphs[1],'g_{sw}'); set_para(rects[1].text_frame.paragraphs[1],'Φ_{PSII} · Φ_{NPQ} · Φ_{NO} (P2)')
for s,crop in ((S(13),'bean'),(S(14),'lettuce')):
    refs={'bean':'Tan et al. 2018; Haverroth et al. 2024; Buckley 2019; Yeung et al. 2018; Sasidharan et al. 2018 (참고문헌: 보충 자료)','lettuce':'Körner 2015; Tardieu et al. 2018; Haverroth et al. 2024 (참고문헌: 보충 자료)'}[crop]
    fl=[x for x in s.shapes if x.name=='Footnote']
    if fl: f=fl[0]
    else: f=shp(s,copy_el(s,byname(S(15),'Footnote')._element))
    set_para(f.text_frame.paragraphs[0],'① g_{sw}: 대조·침수 색, 그 외 회색. ② P2 보정 평균 ± SE(측정일 변동 포함), 문자 Tukey. '+refs)
nt=S(13).notes_slide.notes_text_frame.text
nt=nt.replace('두 번째 그래프처럼 광화학에 쓰이는 ΦPSII는 줄고 ΦNPQ와 ΦNO의 비율이 늘었습니다','두 번째 그래프처럼 P2 구간에서 건조·복합구의 ΦPSII는 낮고 ΦNPQ와 ΦNO는 높았습니다')
notes(S(13),nt)
nt=S(14).notes_slide.notes_text_frame.text
nt=nt.replace('첫 번째 그래프처럼 침수 중 기공이 대조구의 10%까지 떨어졌지만','첫 번째 그래프처럼 침수 중 기공전도도가 크게 떨어졌지만').replace('두 번째 그래프처럼 흡수한 에너지의 분배는 처리 간 차이가 없어','두 번째 그래프처럼 P2 구간의 ΦPSII, ΦNPQ, ΦNO는 처리 간 차이가 없어')
notes(S(14),nt)

def swap_by(s,test,path):
    pic=[x for x in s.shapes if x.shape_type==13 and test(x)][0]
    L,T,W,H=pic.left,pic.top,pic.width,pic.height; el=pic._element
    n=s.shapes.add_picture(path,L,T,W,H); el.addprevious(n._element); el.getparent().remove(el)
from PIL import Image as _I
def _asp(p): im=_I.open(p); return im.width/im.height
w=lambda x:x.width/914400
# slide 9: top picture is the one with the smaller 'top'
pics9=sorted([x for x in S(9).shapes if x.shape_type==13 and abs(w(x)-6.4)<0.1],key=lambda x:x.top)
for pic,pth in zip(pics9,('an/figs4/gsw_ts.png','an/figs4/gsw_rec.png')):
    L,T,W,H=pic.left,pic.top,pic.width,pic.height; el=pic._element; n=S(9).shapes.add_picture(pth,L,T,W,H); el.addprevious(n._element); el.getparent().remove(el)
swap_by(S(10),lambda x:abs(w(x)-6.3)<0.1,'an/figs4/phi3.png')
swap_by(S(11),lambda x:x.name=='Picture 13','an/figs3/params.png')
for n_,pth in ((19,'an/figs3/aq.png'),(20,'an/figs2/ts_fs.png'),(21,'an/figs2/ts_etr.png')): swap_by(S(n_),lambda x:x.name=='Picture 13',pth)
# tables: drop pre-treatment rows
for s_ in (S(11),S(19)):
    for sh in s_.shapes:
        if getattr(sh,'has_table',False) and sh.has_table:
            t_=sh.table
            for i_ in range(len(t_.rows)-1,0,-1):
                if t_.cell(i_,0).text_frame.text.strip().startswith('Pre'): delete_row(t_,i_)
# appendix A2 text/footnote
set_paras2(byname(S(19),'TextBox 10'),['모든 PPFD 수준에서 처리 간 유의차 없음','콩 침수구와 상추 복합구가 낮은 경향'])
set_para(byname(S(19),'Footnote').text_frame.paragraphs[0],'값: 평균 ± SE (µmol CO_{2} m^{−2}·s^{−1}). 콩 9/2~9/17, 상추 10/16~19 측정(처리당 3~4곡선). PPFD 수준별 Tukey.')
# ---------- delete slide 7, swap 5 and 6
sld=prs.slides._sldIdLst; ids=list(sld)
prs.part.drop_rel(ids[6].rId); sld.remove(ids[6])
ids=list(sld); a,b=ids[4],ids[5]; sld.remove(b); sld.insert(4,b)
for s in prs.slides:
    for sh in s.shapes:
        if getattr(sh,'has_table',False) and sh.has_table and sh._element is not te: compact_table(sh.table); bottom_border(sh.table)
    fix_timing(s)
compact_table(tt)
prs.save('oral/oral_v10.pptx'); print('saved',len(prs.slides))
