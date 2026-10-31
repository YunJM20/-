import sys; sys.path.insert(0,'.')
from lib import *
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

# ===== 3 objective: 4 steps, no hypothesis
s=S(3)
for nm in ('Step 3','Depth arrow'): rm(byname(s,nm))
steps=[byname(s,'Step %d'%i) for i in (1,2,4,5)]
labels=[('① 기공','g_{sw}'),('② 명반응','Φ_{PSII} · F_{s} · ETR'),('③ 생화학적 능력','V_{cmax} · J_{max} · A_{max}'),('④ 생육·수량','건물중 · 엽면적 · 수확량')]
for k,(st,(a,b)) in enumerate(zip(steps,labels)):
    ps=st.text_frame.paragraphs; set_para(ps[0],a); set_para(ps[1],b)
    st.left=Inches(0.92+k*2.88); st.top=Inches(1.55+k*0.78)
obj=byname(s,'Objective'); ps=obj.text_frame.paragraphs; print('obj paras',[[r.text for r in p.runs] for p in ps])
# objective text (runs: lead + body; second paragraph has emphasis runs)
set_para(ps[0],'연구 목적',bold=True) if False else None
ps[0].runs[1].text='  콩과 로메인 상추에 침수·건조·복합 처리를 적용하여'
ps[1].runs[0].text='잎 생리 반응이 '
ps[1].runs[5].text='생육·수량 감소가 잎 생리로 설명되는지'
conc(s,'핵심 질문: 같은 침수·건조 재해에 콩과 로메인 상추의 생리·생육 반응은 어떻게 다른가?')
foot(s,'본 발표의 결과는 ①→④ 순서로 제시함.')
notes(s,'(약 20초) 이 연구는 수분 재해의 영향을 네 단계로 나누어 보았습니다. 가장 먼저 반응하는 기공, 광계의 명반응, 광합성의 생화학적 능력, 그리고 최종적으로 생육과 수량입니다. 콩과 로메인 상추에 침수, 건조, 복합 처리를 적용하여 잎 생리 반응이 어느 단계까지 이어지는지, 기공이 얼마나 빨리 회복되는지, 생육과 수량의 감소가 잎 생리로 설명되는지를 비교했습니다.')

# ===== 4 crops & treatments
s=S(4)
set_para(byname(s,'Header 상추').text_frame.paragraphs[0],'로메인 상추')
set_paras(byname(s,'Text 상추'),['Lactuca sativa_{ } L. (로메인) cv. 크라디우스'.replace('_{ }',''),'처리 개시: 정식 3주 후 (영양생장기)','관찰: 처리 후 16일 (DAT 0~16)'])
foot(s,'복합구는 침수 종료 후 침수구 관수량의 50%를 관수. 침수는 포트를 물통에 옮겨 3일간 잠기게 함. 콩은 처리 전부터 일부 뿌리가 포트 하단 배수구로 빠져나가 지면에 닿음.')
notes(s,'(약 20초) 공시 작물은 콩 대원콩과 로메인 상추 크라디우스이며 전북대학교 부속농장에서 재배했습니다. 상추는 정식 3주 후 영양생장기에, 콩은 개화기에 처리를 시작했습니다. 처리구는 전날 손실된 수분량, 즉 증발산량만큼 관수한 대조구, 50%만 관수한 건조구, 3일간 침지한 뒤 정상 관수한 침수구, 침수 후 50% 관수한 복합구의 네 가지입니다.')

# ===== 5 schedule
s=S(5)
for sh in s.shapes:
    if sh.has_text_frame:
        replace_all_runs(sh,'상추','로메인')
[set_para(x.text_frame.paragraphs[0],'콩 종료 DAT 55 (10/6), 로메인 DAT 16 (10/23). 점은 LI-600 측정일.') for x in s.shapes if x.name=='TextBox 56']
foot(s,'콩 침수 8/12~14, 50% 관수는 8/15부터. 로메인 상추 침수 10/7~10/10 오전, 50% 관수 10/12부터.')
notes(s,'(약 15초) 두 실험은 시기와 기간이 달라 침수 시작일을 DAT 0으로 맞추어 정렬했습니다. 로메인 상추는 처리 후 16일, 콩은 55일까지 관찰했고 점은 LI-600 측정일입니다.')

# ===== 6 measurement items: remove stage ③ (PSII damage)
s=S(6)
rows=[]
for sh in list(s.shapes):
    pass
names=['Row bg','Row chip','Row ind','Row method']
bg=allnames(s,'Row bg'); chip=allnames(s,'Row chip'); ind=allnames(s,'Row ind'); met=allnames(s,'Row method')
for k in (2,):   # remove 3rd row (③ 광계 II 손상)
    for g in (bg,chip,ind,met): rm(g[k])
bg=[x for x in bg if x._element.getparent() is not None and x not in ()]
bg=allnames(s,'Row bg'); chip=allnames(s,'Row chip'); ind=allnames(s,'Row ind'); met=allnames(s,'Row method')
chips=['① 기공','② 명반응','③ 생화학적 능력','④ 생육·수량']
inds=['g_{sw}','Φ_{PSII}, F_{s}, ETR','V_{cmax}, J_{max} / A_{max}, α','생체중, 건조중, 엽면적, 엽수, SPAD, 수확량']
mets=['LI-600 포로미터, 처리 개시 후 반복 측정','LI-600 명적응 형광 (F_{s}, F_{m}′), PAR·기온 보정','LI-6800 A-Ci (FvCB), A-Q 곡선','파괴 조사(로메인 DAT 16, 콩 DAT 20·55), 로메인 캐노피 투영 엽면적(사진)']
for k in range(4):
    y=1.50+k*1.08
    for g in (bg,chip,ind,met): g[k].top=Inches(y)
    set_para(chip[k].text_frame.paragraphs[0],chips[k]); set_para(ind[k].text_frame.paragraphs[0],inds[k]); set_para(met[k].text_frame.paragraphs[0],mets[k])
foot(s,'P1 = 침수 시작~종료 후 7일(콩 DAT 1~9: 대조구·침수만, 로메인 DAT 5~10 공통 측정일), P2 = 이후. 표 값 = PAR·기온 보정 평균(괄호 = PAR만 보정; 원 평균). Φ_{PSII}는 처리 × PAR 모형의 PPFD 300·1,200 예측으로 비교. 생육은 전 개체 사용.')
notes(s,'(약 20초) 앞서 제시한 네 단계에 맞추어 지표를 측정했습니다. 기공전도도와 명반응은 LI-600으로 반복 측정했고, 광합성의 생화학적 능력은 LI-6800의 A-Ci와 A-Q 곡선으로 평가했습니다. 생육은 파괴 조사로 측정했고 로메인 상추는 상면 사진으로 투영 엽면적도 추적했습니다. 통계는 측정일과 측정 당시 광도·기온을 보정한 평균에 침수 × 관수 이원 분산분석을 적용했습니다.')

# ===== 33 (new) environment: methods
s=S(33); title(s,'환경 조건: 처리 기간의 기온과 일사')
replace_picture(s,byname(s,'Picture 26'),img(FG+'env_cmp.png'),valign='top')
sv=allnames(s,'Stat value'); sl=allnames(s,'Stat label')
set_para(sv[0].text_frame.paragraphs[0],'18.2 vs 28.4 °C'); set_para(sl[0].text_frame.paragraphs[0],'처리 기간 평균 기온 (로메인 vs 콩 DAT 0~16)')
set_para(sv[1].text_frame.paragraphs[0],'17.5 vs 22.0'); set_para(sl[1].text_frame.paragraphs[0],'DLI (mol·m^{−2}·d^{−1}, 로메인 vs 콩 DAT 0~16)')
set_paras2(byname(s,'Text 요점'),['로메인 처리 기간(10/7~10/23): 평균 기온 18.2 °C, 최저 5.0 °C, 상대습도 71%','콩 처리 초기(DAT 0~16): 평균 기온 28.4 °C — 로메인보다 약 10 °C 높음','DLI도 로메인이 낮음 (17.5 vs 22.0)','10월에는 기온 하강이 뚜렷해 증산 요구량 자체가 낮음','두 실험은 계절·온실·생육단계가 달라 병렬 사례로 해석'])
conc(s,'로메인은 저온·중간 일사 조건에서 처리되어 증발산 부하와 건조 스트레스 강도가 다름')
foot(s,'밭콩: CR1000X 기상 센서, 로메인: 26번 온실 환경 데이터(CR300; 10/13·10/18 결측일 제외). 로메인 DLI = 일사량(MJ) × 2.02 mol/MJ 추정.')
notes(s,'(약 20초) 두 실험은 계절이 달라 환경 조건이 크게 다릅니다. 콩의 처리 초기 평균 기온은 28.4도, 로메인 상추는 18.2도로 약 10도 낮았고 일적산광량도 로메인이 낮았습니다. 따라서 같은 50% 관수라도 증발산 부하가 달라 건조 스트레스 강도가 다르며, 두 작물의 차이는 병렬 사례로 해석하겠습니다.')

# ===== 7 treatment check: irrigation + daily transpiration
s=S(7); title(s,'처리 검증: 관수량 비교와 일일 증산량')
replace_picture(s,byname(s,'Picture 26'),img(F2+'et_daily.png'),valign='top')
sv=allnames(s,'Stat value'); sl=allnames(s,'Stat label')
set_para(sv[0].text_frame.paragraphs[0],'43% · 40%'); set_para(sl[0].text_frame.paragraphs[0],'건조구 누적 관수량 (로메인 · 콩, 대조구 대비)')
set_para(sv[1].text_frame.paragraphs[0],'56% · 87%'); set_para(sl[1].text_frame.paragraphs[0],'침수구 누적 관수량 (로메인 · 콩, 대조구 대비)')
set_paras2(byname(s,'Text 요점'),[('관수량:',' 건조 로메인 43%·콩 40%, 침수 56%·87%, 복합 37%·44% (대조구 대비)'),
 ('로메인 침수:',' 3일 침지 후 화분이 과습해 관수가 대조구의 56% — 복합구는 침수구의 66%'),
 ('일일 증산량:',' 로메인은 건조 72%·침수 84%·복합 74% (대조구 대비, DAT 6~16), 콩은 건조 54%·침수 95% (로드셀)'),
 '콩 복합구는 증산량(로드셀) 자료 없음, 콩은 뿌리가 배수구로 이탈해 실제 수분 이용은 다를 수 있음'])
conc(s,'감수 관수는 실현됨 — 로메인 침수구는 과습으로 관수가 적었고 콩은 뿌리 이탈 가능성')
foot(s,'관수: 포트에 들어간 누적 관수량(대조구 대비), 콩 8/16~10/6, 로메인 10/12~10/22. 일일 증산량 = 전날 관수 후 − 당일 관수 전 무게(로메인: 증산량·관수량 시트, 콩: 로드셀 mm × 38.01 g/mm). 로메인 점선 음영 = ± SE.')
notes(s,'(약 30초) 결과를 보기 전에 처리가 실제로 어떻게 들어갔는지 확인했습니다. 대조구 대비 누적 관수량은 건조구가 로메인 43%, 콩 40%로 설계인 50%에 가까웠습니다. 침수구는 콩이 87%였지만 로메인은 화분이 과습한 상태가 유지되어 56%만 관수되었습니다. 일일 증산량은 로메인이 건조 72%, 침수 84%, 복합 74%였고 콩은 건조 54%, 침수 95%였습니다. 다만 콩은 포트 밖으로 나간 뿌리가 있어 실제 수분 이용은 다를 수 있습니다.')

# ===== 8 gsw
s=S(8)
replace_picture(s,byname(s,'Picture 13'),img(FG+'ts_gsw.png'),valign='top')
t=table_of(s)
set_table(t,[['Treatment',None,None,'Romaine P1','Romaine P2'],
 [None,None,None,'0.264 a (0.264;0.264)','0.155 ab (0.153;0.155)'],[None,None,None,'0.249 a (0.249;0.248)','0.113 b (0.112;0.113)'],
 [None,None,None,'0.255 a (0.255;0.254)','0.161 a (0.160;0.162)'],[None,None,None,'0.237 a (0.237;0.237)','0.144 ab (0.143;0.145)'],
 [None,None,None,'n.s.','I n.s. (0.11)'],[None,None,None,'0.085','0.067']])
tails_like(t,range(1,5),[3,4],2)
set_paras2(byname(s,'TextBox 10'),[('콩 P1:',' 침수 0.26 vs 대조구 0.35 — 측정일을 반복으로 해도 유의 (P=0.006)'),
 ('콩 P2:',' 건조·복합 0.22~0.23 < 대조구·침수 0.35, 관수 효과만 유의 (P=0.001; W × I P=0.99)'),
 ('로메인 P1:',' 4처리 차이 없음 (P=0.20) — 침수 중(DAT 2~4) 0.10→0.028→0.10 vs 대조구 0.24~0.29, DAT 5부터 대조구 수준'),
 ('로메인 P2:',' 건조 0.113 (b) < 침수 0.161 (a), 관수 효과 P=0.015 (측정일 반복은 n.s., P=0.11); DAT 16 건조 0.055 vs 대조구 0.144'),
 '로메인 최저값: DAT 3에 대조구의 10% (0.026 vs 0.256)'])
foot(s,'표: 측정일·선형 PAR·기온 보정 평균, Tukey 문자, 괄호 = (PAR만 보정; 원 평균). P(측정일 반복) = 처리별 측정일 평균 ~ 침수 × 관수 + 측정일 (W 침수, I 관수). 그림: PAR·기온 보정 일평균, 음영 ± SE, 회색 띠 흐린 날, * 당일 P<0.05(Holm).')
notes(s,'(약 40초) 첫 번째 단계인 기공입니다. 그래프와 표는 측정 광도와 기온을 보정한 값입니다. 침수 기간 동안 두 작물 모두 기공전도도가 감소했습니다. 로메인 상추는 침수 3일째 대조구의 10%까지 떨어졌다가 배수 직후 빠르게 회복했고, 콩은 침수 효과가 DAT 9까지 이어졌습니다. 건조는 두 작물 모두 후반에 기공전도도를 낮췄습니다.')

# ===== 9 recovery (new figure with drought + combined)
s=S(9); title(s,'① 기공 회복 속도: 로메인은 빠르게, 콩은 느리게')
replace_picture(s,byname(s,'Picture 26'),img(F2+'recovery3.png'),valign='top')
set_paras2(byname(s,'Recovery text'),[('로메인:',' 침수 DAT 3 최저(10%) → DAT 5~6(87~98%) 대조구 수준 회복. 건조·복합(DAT 5~)은 DAT 5~14에 74~127%로 대조구 수준, 건조는 DAT 16 39%'),
 ('콩:',' 침수 DAT 2~9에 39~90%(DAT 9 52%) → DAT 17 86%, DAT 23 99%. 건조·복합(DAT 17~)은 DAT 23~30에 31~71%로 낮고 DAT 44에 81~83%, DAT 51에 36~45%')])
sv=allnames(s,'Stat value'); sl=allnames(s,'Stat label')
set_para(sv[0].text_frame.paragraphs[0],'2~3일'); set_para(sl[0].text_frame.paragraphs[0],'로메인: 배수 후 대조구 수준까지 회복')
set_para(sv[1].text_frame.paragraphs[0],'DAT 9: 52%'); set_para(sl[1].text_frame.paragraphs[0],'콩: 침수 종료 6일 후에도 미회복')
conc(s,'같은 3일 침수에도 로메인은 배수 2~3일 만에 회복, 콩은 DAT 9까지 회복되지 않음')
foot(s,'각 처리 g_{sw} ÷ 같은 날 대조구 g_{sw} × 100 (PAR·기온 보정 일평균). * 대조 vs 처리 P<0.05(Welch t, Holm 보정). 콩 DAT 10~16은 측정 없음, 콩 건조·복합은 DAT 17부터 측정.')
notes(s,'(약 50초) 각 처리구의 기공전도도를 같은 날 대조구에 대한 비율로 나타낸 그래프입니다. 로메인 상추는 침수 3일째 10%까지 떨어졌지만 배수 후 2~3일, 즉 DAT 5~6에 대조구 수준으로 회복했습니다. 콩은 DAT 9에도 52%로 회복되지 않았고 DAT 17 이후에야 대조구에 가까워졌습니다. 건조구와 복합구는 두 작물 모두 처리 후반에 대조구보다 낮아지는 시기가 있었고, 로메인의 복합구는 DAT 5에 75%였다가 DAT 6에 97%로 대조구 수준을 회복했습니다.')

# ===== 11 PhiPSII
s=S(11); title(s,'② Φ_{PSII}: 콩은 고광도 건조에서만 저하')
replace_picture(s,byname(s,'Picture 13'),img(FG+'phi_light.png'),valign='top')
t=table_of(s)
set_table(t,[[None,None,None,None,'Romaine P1','Romaine P2'],
 [None,None,None,None,'0.611 a (0.611;0.599)','0.645 a (0.645;0.658)'],[None,None,None,None,'0.595 a (0.595;0.612)','0.649 a (0.649;0.661)'],
 [None,None,None,None,'0.591 a (0.591;0.595)','0.642 a (0.642;0.637)'],[None,None,None,None,'0.585 a (0.585;0.576)','0.655 a (0.655;0.642)'],
 [None,None,None,None,'W 0.24 (n.s.)','–']])
tails_like(t,range(1,5),[4,5],2)
set_paras2(byname(s,'TextBox 10'),[
 'P1: 측정일 반복 검정은 두 작물 모두 차이 없음 (콩 P=0.44, 로메인 P=0.24) — 콩 보정 평균의 침수 0.68 vs 대조구 0.70은 작고 보정 방식에 민감',
 ('콩 P2:',' 저광(300) 0.72~0.75로 차이 없음, 고광(1,200)에서 건조 0.50 < 복합 0.54 < 침수 0.58 < 대조구 0.68'),
 '처리 × 광도 상호작용 P<0.001 — 건조의 명반응 저하는 과잉광에서만 (기공 제한의 2차 결과와 부합)',
 '로메인은 P1 0.585~0.611 (침수 효과 P=0.049, 처리 P=0.10), P2 0.642~0.655 (P=0.75): 구간 차이 없음'])
conc(s,'콩 건조의 Φ_{PSII} 저하는 고광도에서만 — 로메인은 잎 광화학 효율 변화 없음 (침수 후 약 3% 낮은 경향)')
foot(s,'표: 측정일·선형 PAR·기온 보정 평균(콩 P2는 처리 × PAR 모형의 PPFD 300·1,200 예측, 9/4 기준). 괄호 = (PAR만 보정; 원 평균). P(측정일 반복) = 처리별 측정일 평균 ~ 침수 × 관수 + 측정일. 문자: Tukey(로메인은 n.s.라 모두 a).')
notes(s,'(약 35초) 두 번째 단계인 명반응입니다. 처리 초기에는 측정일을 반복으로 한 검정에서 두 작물 모두 ΦPSII 차이가 없었습니다. 콩 P2에서는 건조구의 ΦPSII가 낮은 광도에서는 대조구와 같았지만 PPFD 1,200의 고광도에서만 0.68에서 0.50으로 낮아졌습니다. 로메인 상추는 모든 구간에서 처리 간 차이가 없었습니다. 따라서 로메인에서는 기공이 닫혔는데도 명반응은 영향을 받지 않았습니다.')

# ===== 13 photosynthetic capacity
s=S(13); title(s,'③ 광합성 능력 (A-Ci, A-Q 파라미터)')
replace_picture(s,byname(s,'Picture 13'),img(FG+'params.png'),valign='top')
t=table_of(s)
set_table(t,[['Parameter','Soybean pre','Soybean P','Romaine pre','Romaine P'],
 ['V_{cmax}','60.4','0.011','98.3','0.029'],['J_{max}','83.3','<0.001','172.7','0.047'],['R_{d}','1.44','0.049','1.70','0.87'],['A_{max}','15.4','0.686','26.4','0.58'],['α','0.047','0.420','0.063','0.79']])
set_paras2(byname(s,'TextBox 10'),[('콩 9월 A-Ci(선별 15곡선):',' V_{cmax} 대조구 90 (a) > 침수 85 > 복합 75 > 건조 68 (b) (P=0.011), J_{max} 대조구·침수 (a) > 복합·건조 (b) (P<0.001) — 관수 주효과만 유의'),
 ('로메인 Vcmax:',' 대조구 104 (a) > 건조 94 > 침수 88 > 복합 73 (b) (P=0.029, 침수 P=0.012), J_{max}도 같은 순서로 감소 (P=0.047, 침수 P=0.024)'),
 'R_{d}·A_{max}·α·A-Q 곡선은 두 작물 모두 차이 없음 (로메인 P≥0.58)',
 '처리별 측정일이 달라(콩 9/2~9/17, 로메인 10/16~19) 측정일과 교락 — 곡선 수가 적어(처리당 3~4개) 해석 주의'])
conc(s,'콩 건조·복합구(9월)와 로메인 복합구(10월)에서 V_{cmax}·J_{max}가 낮은 경향 — 측정일 교락으로 확정은 어려움')
foot(s,'상자: 사분위(n≥4), 가로선: 평균 ± SE(n<4), 점: 개별 곡선, 문자: Tukey. 표: pre = 처리 전 평균, P = 처리 후 4처리 ANOVA. 콩: 9월 파라미터 \'선택적 데이터\' 시트(9/2~9/17). 로메인: 10/16~19, 10/19 CR 4는 CR-2와 같은 개체라 제외.')
notes(s,'(약 35초) 세 번째 단계인 광합성의 생화학적 능력입니다. 콩은 9월 측정에서 건조구와 복합구의 최대 카르복실화 속도와 최대 전자전달 속도가 낮았고, 로메인 상추도 복합구에서 가장 낮은 경향을 보였습니다. 다만 처리별로 측정일이 달라 측정일과 처리 효과가 섞여 있고 곡선 수도 처리당 3~4개로 적어 확정적으로 말하기는 어렵습니다. 암호흡, 최대 광합성, 양자수율은 두 작물 모두 처리 간 차이가 없었습니다.')

# ===== 14 growth + yield (one slide)
s=S(14); title(s,'④ 생육·수량: 로메인 감소, 콩은 차이 없음')
for nm in ('Stat box','Stat value','Stat label'):
    for x in allnames(s,nm): rm(x)
pic=replace_picture(s,byname(s,'Picture 26'),img(F2+'yield_cmp.png'),valign='top')
src=[x for x in S(11).shapes if getattr(x,'has_table',False) and x.has_table][0]
el=add_table_copy(s,src,remove_existing=False)
tshape=[x for x in s.shapes if x._element is el][0]
tb=tshape.table
rows_data=[['Crop · variable','Control','Drought','Waterlog.','Combined','P'],
 ['Romaine DAT 16','','','','',''],
 ['Shoot FW (g)','89.9 a','63.5 b','66.3 b','55.4 b','<0.001'],['Shoot DW (g)','6.47 a','5.43 ab','4.30 bc','3.69 c','<0.001'],
 ['Leaf area (cm²)','1599 a','1289 b','1348 ab','1138 b','0.001'],['Root DW (g)','4.46 a','2.71 b','2.01 b','1.45 b','<0.001'],
 ['Soybean DAT 55','','','','',''],
 ['Seed DW (g)','69.3','66.3','63.0','57.0','0.438'],['Seed no.','354','334','326','300','0.468'],['Pod no.','170','162','163','144','0.404']]
while len(tb.rows)<len(rows_data):
    tr=copy.deepcopy(tb._tbl.tr_lst[-1]); tb._tbl.append(tr)
widths=[1.9,1.1,1.1,1.1,1.1,1.0]
for c,w in zip(tb.columns,widths): c.width=Inches(w)
for r_i,row in enumerate(rows_data):
    tb.rows[r_i].height=Inches(0.255)
    for c_i,v in enumerate(row):
        cell=tb.cell(r_i,c_i)
        txt=v if v else ' '
        set_cell(cell,txt)
tshape.left=Inches(0.50); tshape.top=Inches(3.38); tshape.width=Inches(sum(widths)); tshape.height=Inches(0.255*len(rows_data))
byname(s,'Picture 26').left=Inches(0.72)
set_paras2(byname(s,'Text 요점'),[('로메인:',' 지상부 건물중 건조 −16%, 침수 −34%, 복합 −43% (침수 P<0.001, 관수 P=0.026, 상호작용 없음: 가법적)'),
 '생체중 −29·−26·−38%, 엽면적 −16~29%, 뿌리 건물중 −39~68%',
 ('콩 DAT 20:',' 침수구 꼬투리+종실 건물중 65% (침수 주효과 P=0.009)'),
 ('콩 DAT 55:',' 종실 건물중 57~63 g, 종실 수·꼬투리 수·100립중 모두 차이 없음 (P≥0.20) — 검출 한계 약 40~50%, 뿌리 이탈')])
conc(s,'로메인은 침수·건조·복합 모두 생육이 감소(복합 −43%), 콩은 종실 수량 구성요소에서 처리 간 차이 없음')
foot(s,'로메인 10/23(DAT 16) 파괴조사 처리당 8주, 콩 10/6(DAT 55, R6~R7) 파괴조사(성숙기 최종 수확 전) n=6~9. 평균 ± SE, 문자: Tukey(ANOVA P<0.05일 때만). 100립중 P=0.196.')
notes(s,'(약 50초) 네 번째 단계인 생육과 수량입니다. 로메인 상추는 건조구 16%, 침수구 34%, 복합구 43%의 지상부 건물중 감소를 보였고 침수와 건조의 효과가 더해지는 가법적인 형태였습니다. 엽면적과 뿌리 건물중도 함께 줄었습니다. 콩은 DAT 20에 침수구의 꼬투리와 종실 발달이 대조구의 65%로 늦어졌지만 DAT 55에는 종실 건물중, 종실 수, 꼬투리 수, 100립중 모두 처리 간 차이가 없었습니다. 다만 검출 한계가 약 40~50%이고 뿌리가 포트 밖으로 나간 영향이 있어 근거는 약합니다.')

# ===== 15 canopy (romaine)
s=S(15); title(s,'④ 로메인 생육 감소는 잎 생리로 설명되지 않음')
replace_picture(s,byname(s,'Picture 26'),img(FG+'lettuce_path.png'),valign='top')
sv=allnames(s,'Stat value'); sl=allnames(s,'Stat label')
set_para(sv[0].text_frame.paragraphs[0],'2.7일'); set_para(sl[0].text_frame.paragraphs[0],'침수구 건물중 생장 손실 (대조구 RGR 0.152 d^{−1} 환산)')
set_para(sv[1].text_frame.paragraphs[0],'≈ 1.2일'); set_para(sl[1].text_frame.paragraphs[0],'기공 제한 탄소 손실 추정 (DAT 1~8 결손 2.4일분 × 0.5)')
set_paras2(byname(s,'Text 요점'),[('DAT 5:',' 투영 엽면적 침수 72%·복합 69% (대조구 대비, P=0.002) — 침수 3일 동안 잎 확장이 거의 멈춤'),
 ('DAT 16:',' 침수 85%, 복합 77%, 건조 95% — 배수 후 침수구 확장 속도는 대조구보다 빠르나(RGR 0.031 vs 0.015 d^{−1}) 초기 손실을 만회하지 못함'),
 '건물중 기준 생장 손실 침수 2.7일·복합 3.7일분 > 기공 제한 탄소 손실 추정 ≈ 1.2일분 → 탄소 부족만으로 설명 불가',
 '건조구는 DAT 12 이후 캐노피 확장 정체 (RGR 최저)'])
conc(s,'건물중 손실(2.7일분)이 기공 제한 탄소 손실(≈1.2일분)보다 큼 — 잎 생리만으로 설명 불가')
foot(s,'투영 엽면적: 상면 사진 SAM 분할, 처리당 6개체 반복 촬영, * 날짜별 P<0.05, ◇ DAT 16 건물중. 처리 전 캐노피 미측정. 탄소 손실 = Σ(1 − 침수/대조 g_{sw}) × 0.5 (A 감소율 가정). 생장 손실 일수 = ln(DW대조/DW처리)/RGR대조.')
notes(s,'(약 50초) 이 발표의 핵심 결과입니다. 로메인 상추는 잎의 광합성 지표가 거의 변하지 않았는데 생육은 크게 줄었습니다. 그 원인을 캐노피 사진으로 추적했습니다. 침수 3일 동안 잎 확장이 멈춰 DAT 5의 투영 엽면적이 대조구의 약 70%에 그쳤고 배수 후 확장 속도는 대조구보다 빨랐지만 초기 손실을 따라잡지 못했습니다. 건물중 기준 생장 손실은 침수구 2.7일분인 반면, 기공이 닫혀 잃은 탄소는 약 1.2일분으로 추정되어 탄소 공급만으로는 설명이 되지 않습니다.')

# ===== 16 summary matrix (crop x treatment x stage)
s=S(16)
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
htxt=[('① 기공','g_{sw}'),('② 명반응','Φ_{PSII}'),('③ 생화학','V_{cmax} · A_{max}'),('④ 생육·수량','건물중 · 종실')]
for h,x,(a,b) in zip(heads,X,htxt):
    h.left=Inches(x); h.width=Inches(W); ps=h.text_frame.paragraphs; set_para(ps[0],a); set_para(ps[1],b)
N,Mi,G,Sg='EFEFEF','D9EAD3','F8CBAD','E97132'
grid=[ # rows: 로메인 건조, 침수, 복합, 콩 건조, 침수, 복합 ; cols 4
 [(['↓ 후반','(DAT 16 39%)'],G),(['–'],N),(['–'],N),(['↓ 건물중 84%','(생체중 71%)'],G)],
 [(['↓ → 회복','DAT 5~6'],Mi),(['–'],N),(['↓ 경향','(측정일 교락)'],G),(['↓↓ 66%'],Sg)],
 [(['↓ → 회복','DAT 6'],Mi),(['–'],N),(['↓ 경향','(V_{cmax} 73)'],G),(['↓↓ 57%'],Sg)],
 [(['↓ 지속'],G),(['↓↓','(고광도)'],Sg),(['↓ V_{cmax}·J_{max}','(9월)'],G),(['– 종실 96%','(뿌리 이탈 가능)'],N)],
 [(['↓ DAT 9까지','미회복'],G),(['–','(보정 시 0.68 vs 0.70)'],N),(['–'],N),(['– 종실 91%','(DAT 20 꼬투리 65%)'],N)],
 [(['↓ 지속'],G),(['↓ (고광도)','건조보다 작음(가설)'],G),(['↓ J_{max}','(9월)'],G),(['– 종실 82%','(DAT 20 꼬투리 72%)'],N)]]
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
conc(s,'로메인은 잎 생리 변화 없이 생육 −43%, 콩은 건조 시 고광도 명반응 저하 (교차 내성은 가설)')
foot(s,'↓↓ 큰 감소 · ↓ 감소 · – 차이 없음 (기공은 P1·P2 포함, 콩 Φ_{PSII}는 PPFD 1,200 예측값, 생화학은 콩 9월·로메인 10월 곡선, 측정일 교락). 생육: 로메인 건물중 DAT 16, 콩 종실 건물중 DAT 55 (대조구 대비 %), 검출 한계 약 40~50%, 뿌리 이탈 가능.')
notes(s,'(약 20초) 지금까지의 결과를 작물, 처리, 단계별로 정리한 표입니다. 로메인 상추는 기공이 침수 직후 크게 닫혔다가 며칠 만에 회복했고 명반응에는 변화가 없었지만, 생육은 침수 처리에서 가장 크게 감소했습니다. 콩은 기공 회복이 느렸고 건조 처리에서 고광도 명반응 저하가 나타났지만 수량 구성요소에는 차이가 없었습니다. 즉 같은 수분 재해라도 작물에 따라 영향이 나타나는 단계가 다릅니다.')

# ===== 17 / 34 discussion
def cards(slide,items):
    heads=[x for x in slide.shapes if x.name.startswith('Header ') and '요점' not in x.name]
    texts=[x for x in slide.shapes if x.name.startswith('Text ')]
    for h,t,(ht,bl) in zip(heads,texts,items):
        set_para(h.text_frame.paragraphs[0],ht); set_paras(t,bl)
s=S(17); title(s,'고찰 ①: 침수 직후 기공이 먼저 닫히는 이유와 회복 속도 차이')
cards(s,[('① 침수 → 기공 폐쇄: 수분 공급 문제',['g_{sw}만 급감(로메인 DAT 3 10%)하고 Φ_{PSII}·V_{cmax}는 유지 → 광합성 장치 손상이 아니라 CO_{2} 공급 제한','뿌리 저산소 → ATP 고갈·세포질 산성화 → 아쿠아포린 기능 저하 → 뿌리 수리전도도·잎 수분 상태 악화 → 기공 폐쇄 (Tan 2018; Haverroth 2024)']),
 ('② 기공은 잎 수분 상태에 반응',['기공은 잎 수분 상태(팽압)의 피드백으로 조절되고 ABA가 관여할 수 있음 (Buckley 2019)','침수 유발 탈수는 건조와 닮은 점이 많음 (Haverroth 2024) — 건조구 g_{sw}는 토양 수분이 줄어든 후반에 낮아짐']),
 ('③ 회복 속도: 뿌리 기능과 재산소 신호',['배수 후 재산소화에서 ROS·ABA·에틸렌 신호의 균형이 기공 개방과 노화를 좌우 (Yeung 2018; Sasidharan 2018)','로메인 DAT 5~6 vs 콩 DAT 9 이후: 콩은 포트 밖 뿌리 절단·손상으로 수리전도도 회복이 늦었을 가능성 (가설)']),
 ('④ 복합: 선행 침수의 영향',['로메인 복합구 g_{sw}는 건조구와 비슷해 침수 이력의 추가 효과는 뚜렷하지 않음','다요인 조합은 단일 스트레스와 다른 반응을 낼 수 있고(Zandalinas & Mittler 2022), 선행 스트레스가 이후 반응을 바꿀 수 있음(Hilker 2016) — 콩 고광도 Φ_{PSII}의 복합 > 건조는 가설'])])
conc(s,'침수는 광합성 장치가 아니라 수분 공급 경로를 통해 기공을 닫고, 회복 속도는 뿌리 기능 회복에 달려 있을 것')
foot(s,'Tan et al. 2018 J Plant Physiol; Haverroth et al. 2024 Plant Physiol; Buckley 2019 New Phytol; Yeung et al. 2018 PNAS; Sasidharan et al. 2018 Plant Physiol; Zandalinas & Mittler 2022 New Phytol; Hilker et al. 2016 Biol Rev (참고문헌: 보충 자료)')
notes(s,'(약 55초) 고찰입니다. 먼저 두 작물 모두 침수 직후 기공전도도만 크게 떨어지고 명반응과 광합성 능력은 유지되었다는 점은, 광합성 장치의 손상이 아니라 이산화탄소 공급 제한임을 뜻합니다. 뿌리의 저산소는 ATP 고갈과 세포질 산성화로 아쿠아포린 기능을 떨어뜨려 뿌리의 수리전도도를 낮추고, 이것이 잎의 수분 상태를 악화시켜 기공을 닫는 것으로 보고됩니다. 건조도 잎 수분 상태를 통해 기공을 닫기 때문에 두 재해는 같은 경로를 공유합니다. 회복 속도의 차이는 배수 후 재산소화 단계의 신호 균형과 뿌리 기능의 회복에 달려 있고, 콩은 포트 밖으로 나간 뿌리가 끊기면서 회복이 늦었을 가능성이 있으나 이는 가설입니다.')

s=S(34); title(s,'고찰 ②: 생리 회복에도 생육이 감소하는 이유와 작물 간 차이')
cards(s,[('① 로메인: 공급원보다 수용부(잎 확장) 제한',['침수 중 투영 엽면적 증가가 멈춤(DAT 5 69~72%) → 건물중 생장 손실 2.7일분 vs 기공 제한 탄소 손실 ≈ 1.2일분','식물 생장은 광합성(탄소 공급)보다 조직 성장과 세포 팽압이 먼저 제한됨 (Körner 2015; Tardieu 2018)']),
 ('② 로메인: 수확물이 잎 → 생육 손실이 곧 수량',['영양생장기에 처리했고 수확물이 지상부라 잎 확장 정지가 수량 감소로 직결 (건물중 −34~43%)','배수 후 확장 속도는 회복했으나(RGR 0.031 vs 0.015 d^{−1}) 초기 손실을 만회하지 못함']),
 ('③ 콩: 느린 회복에도 수량 차이 없음',['개화기 처리 후 55일 관찰: DAT 20 꼬투리+종실 65% 지연이 DAT 55에는 차이 없음 → 생식 구조의 보상 가능성 (가설)','검출 한계 약 40~50%이고 포트 밖 뿌리로 건조 강도가 희석됐을 수 있음']),
 ('④ 수분 스트레스 반응은 작물마다 다름',['로메인: 생리 회복 빠름 + 생육 감소 / 콩: 생리 회복 느림 + 수량 차이 없음','재해 진단에는 잎 생리 지표와 함께 잎 신장·생장 지표가 필요하며, 선행 스트레스 효과는 뿌리 영향을 분리한 뒤 검증 필요 (Hilker 2016)'])])
conc(s,'로메인의 생육 감소는 침수 중 잎 확장 정지로, 콩의 수량 유지는 생식 구조 보상 가능성으로 해석 (모두 가설)')
foot(s,'Körner 2015 Curr Opin Plant Biol 25:107; Tardieu et al. 2018 Annu Rev Plant Biol; Hilker et al. 2016 Biol Rev 91:1118 (참고문헌: 보충 자료)')
notes(s,'(약 55초) 두 번째 고찰입니다. 로메인 상추는 생리 지표가 회복되었는데도 생육이 크게 줄었습니다. 식물의 생장은 광합성으로 얻은 탄소의 양보다 조직 성장과 세포 팽압이 먼저 제한되는 경우가 많고, 이번에도 침수 중 잎 확장이 멈춰 생긴 손실이 기공 제한으로 잃은 탄소 추정치보다 컸습니다. 로메인은 영양생장기에 처리했고 수확물이 잎이라 생육 손실이 곧 수량 손실입니다. 반면 콩은 개화기에 처리해 늦어진 꼬투리와 종실이 이후 따라잡힌 것으로 보이며 생식 구조의 보상 가능성이 있지만 검출 한계와 뿌리 이탈 때문에 가설로 두겠습니다.')

# ===== 18 conclusion
s=S(18)
cs=allnames(s,'Concl')
set_para(cs[0].text_frame.paragraphs[0],'기공 회복 속도'); set_para(cs[0].text_frame.paragraphs[1],'침수는 두 작물 모두에서 기공전도도를 먼저 낮췄다. 로메인은 배수 2~3일 후(DAT 5~6) 대조구 수준으로 회복했고, 콩은 배수 6일 후(DAT 9)에도 대조구의 52%였으며 DAT 23에 회복이 확인되었다.')
set_para(cs[1].text_frame.paragraphs[0],'명반응과 광합성 능력'); set_para(cs[1].text_frame.paragraphs[1],'로메인은 Φ_{PSII}에 처리 차이가 없었고 V_{cmax}·J_{max}는 복합구에서 낮은 경향(측정일 교락)이었다. 콩은 건조에 의한 Φ_{PSII} 저하가 고광도에서만 나타났다(PPFD 1,200에서 0.68 → 0.50).')
set_para(cs[2].text_frame.paragraphs[0],'생육·수량'); set_para(cs[2].text_frame.paragraphs[1],'로메인은 생리가 회복되었는데도 지상부 건물중이 감소했고(건조 −16%, 침수 −34%, 복합 −43%) 침수 중 잎 확장 정지가 주요 원인으로 해석된다. 콩은 DAT 20 꼬투리·종실 지연(65%)이 DAT 55에는 차이가 없어 수량 구성요소에 차이가 없었다.')
conc(s,'같은 침수에도 로메인은 생리 회복이 빠르나 생육이 감소, 콩은 회복이 느리나 수량 차이 없음 — 수분 스트레스 반응은 작물마다 다르다')
notes(s,'(약 40초) 결론입니다. 첫째, 침수는 두 작물에서 기공을 먼저 제한했고 로메인은 배수 2~3일 만에, 콩은 DAT 9 이후에 회복했습니다. 둘째, 명반응과 광합성 능력은 로메인에서 거의 변하지 않았고 콩은 건조 처리의 고광도에서만 명반응이 저하되었습니다. 셋째, 로메인은 생리가 회복되었는데도 침수 중 잎 확장 정지로 생육이 감소했고, 콩은 수량 구성요소에 차이가 없었습니다. 따라서 수분 스트레스에 대한 반응은 작물마다 다르며, 피해 진단에는 잎 생리 지표와 함께 잎 신장과 생장 지표가 필요합니다. 향후 재해 강도와 지속 기간을 세분화하고 잎 신장과 뿌리 기능을 직접 측정할 계획입니다. 감사합니다.')
notes(S(19),'이상으로 발표를 마치겠습니다. 감사합니다. (질의응답 2분)')

# ===== appendix list
s=S(20)
tb=byname(s,'Appendix list')
set_paras(tb,['A1. LI-600 보정: 선형 PAR + 기온','A2. LI-6800 광-광합성 곡선 (A-Q)','A3. 정상 상태 형광 (F_{s})','A4. 전자전달속도 (ETR)','A5. 측정 당시 일사 조건: 흐린 날 표시','A6. 참고문헌'])
notes(s,'질의응답용 보충 자료 목록입니다.')

# ===== A1 LI-600 calibration
s=S(21)
t=table_of(s)
set_table(t,[['지표','콩 P1 PAR만 P','콩 P1 + 기온 P','로메인 P1 PAR만 P','로메인 P1 + 기온 P'],
 ['Φ_{PSII}','<0.001','<0.001','0.10','0.099'],['ETR','0.081','0.021','0.070','0.060'],['F_{s}','<0.001','0.002','0.63','0.66'],['g_{sw}','<0.001','<0.001','0.19','0.20']])
while len(t.rows)>5: delete_row(t,len(t.rows)-1)
set_paras2(byname(s,'TextBox 10'),['이유: 같은 날에도 처리 간 PAR·기온이 달랐음 (콩 8/13 PAR 970 vs 632, 기온 33.3 vs 34.0 °C; 로메인 PAR 약 30~1,250)',
 '모형: y = μ + 처리 + 측정일 + β_{1}·Q_{amb} + β_{2}·T_{air} + ε (Ali et al. 2025; Gao et al. 2024)',
 '선형 PAR이 AIC 최소, Φ_{PSII}는 PAR 100당 콩 −0.022, 로메인 −0.029 감소, 기온 기울기는 비유의',
 '로메인: g_{sw}·Φ_{PSII}·F_{s}·ETR 모두 PAR만 보정과 PAR+기온 보정의 판정이 같음'])
conc(s,'큰 차이(g_{sw}, F_{s}, 콩 P2)는 보정에 안정적 — 작은 차이(콩 P1 Φ_{PSII}, ETR)는 보정 방식에 민감')
notes(s,'질의응답용 자료입니다. LI-600은 야외 광에서 측정하기 때문에 같은 날에도 처리마다 측정 광도와 기온이 달랐습니다. 그래서 측정일, 선형 PAR, 기온을 공변량으로 보정했고, 로메인 상추에서는 PAR만 보정한 결과와 기온까지 보정한 결과의 유의성 판정이 모든 지표에서 같았습니다.')

# ===== A2 A-Q curves (repurposed slide 22)
s=S(22); title(s,'A2. LI-6800 광-광합성 곡선 (A-Q)')
a=load('v6',19); leg=trim(a.crop((0,0,a.width,66)),pad=4); soy=trim(a.crop((0,66,1286,a.height)),pad=4)
rom=img(FG+'aq_romaine.png')
replace_picture(s,byname(s,'Picture 13'),with_legend(leg,hcat([soy,rom],gap=60,height=soy.height)),valign='top')
set_para(byname(s,'Header PPFD별 Dunc').text_frame.paragraphs[0],'PPFD 1,500에서의 A')
t=table_of(s)
set_table(t,[['A (PPFD 1500)','Soybean','Romaine'],['Pre-treatment','12.9','22.6'],['Control','16.4','19.5'],['Drought','16.7','19.5'],['Waterlogging','12.5','21.2'],['Combined','15.8','17.7']])
while len(t.rows)>6: delete_row(t,len(t.rows)-1)
set_paras(byname(s,'TextBox 10'),['PPFD 8개 수준 모두에서 처리 간 유의차 없음 (최소 P: 콩 0.057, 로메인 0.533)','처리 전 곡선은 콩에서 처리 후보다 낮고(약 13), 로메인은 처리 전 약 23으로 처리 후(18~21)보다 높음','콩 침수구 12.5는 대조구 16.4보다 낮은 경향 (P≈0.06), 로메인 복합구 17.7도 낮은 경향 (n.s.)'])
conc(s,'두 작물 모두 처리 간 A-Q 곡선 차이는 없음')
foot(s,'값: 평균 ± SE (µmol CO_{2} m^{−2}·s^{−1}). 콩 처리 전 7/22~23(3곡선), 로메인 처리 전 10/4(3곡선), 처리 후 처리당 3곡선(10/16~19). PPFD 수준별 Tukey.')
notes(s,'질의응답용 자료입니다. 광합성 광반응 곡선은 PPFD 8개 수준 모두에서 두 작물 모두 처리 간 유의한 차이가 없었습니다.')

# ===== A3 Fs, A4 ETR
s=S(25); title(s,'A3. 정상 상태 형광 (F_{s}): 실제 값 비교')
replace_picture(s,byname(s,'Picture 13'),img(FG+'ts_fs.png'),valign='top')
t=table_of(s)
set_table(t,[['Treatment',None,None,'Romaine P1','Romaine P2'],[None,None,None,'157.3 a (157.1;158.3)','142.1 a (142.8;143.2)'],[None,None,None,'161.0 a (161.0;159.3)','141.8 a (142.5;142.7)'],[None,None,None,'158.0 a (158.0;157.7)','141.6 a (142.1;141.2)'],[None,None,None,'161.6 a (161.7;162.6)','144.5 a (144.7;143.4)'],[None,None,None,'0.99','0.63'],[None,None,None,'0.66','0.92']])
tails_like(t,range(1,5),[3,4],2)
set_paras(byname(s,'TextBox 10'),['처리 전 F_{s}: 콩 118, 로메인 154','콩 P1 침수 139 (a) > 대조구 129 (b), P2 건조·침수·복합 131~134 (a) > 대조구 113 (b)','로메인 P1 155~162, P2 142~145: 처리 간 차이 없음 (P=0.66, 0.92)'])
conc(s,'F_{s} 절대값 차이는 형광 신호 크기 변화를 포함 — 생리 해석은 비율 지표(Φ_{PSII})로')
foot(s,'표: 측정일·선형 PAR(Q_{amb})·기온(T_{air}) 보정 평균, Tukey 문자, 괄호 = (PAR만 보정; 원 평균). 공통 측정일만 사용(로메인 P1 = DAT 5~10). W × I = 침수 × 관수 상호작용. 그림(보정 일평균): 음영 ± SE, 점선 P1/P2 경계, 회색 띠 흐린 날, * 당일 P<0.05(Holm), X 처리 전.')
notes(s,'질의응답용 자료입니다. 정상 상태 형광 Fs의 절대값은 로메인 상추에서 처리 간 차이가 없었고, 콩에서는 침수·건조 처리구가 대조구보다 높았습니다.')
s=S(26); title(s,'A4. 전자전달속도 (ETR): 실제 값 비교')
replace_picture(s,byname(s,'Picture 13'),img(FG+'ts_etr.png'),valign='top')
t=table_of(s)
set_table(t,[['Treatment',None,None,'Romaine P1','Romaine P2'],[None,None,None,'141.7 a (141.5;147.1)','75.6 a (76.4;72.3)'],[None,None,None,'137.8 a (137.8;129.8)','78.3 a (79.0;75.5)'],[None,None,None,'132.7 a (132.7;130.8)','72.7 a (73.2;75.6)'],[None,None,None,'130.1 a (130.2;134.5)','80.4 a (80.5;85.6)'],[None,None,None,'0.84','0.56'],[None,None,None,'0.060','0.61']])
tails_like(t,range(1,5),[3,4],2)
set_paras(byname(s,'TextBox 10'),['처리 전 ETR: 콩 187','콩 P1 대조구 119 (a) vs 침수 110 (b) (P=0.021, 보정 방식에 따라 유의성이 달라짐), P2 대조구 190 (a) > 복합 165 (bc) > 건조 146 (c) (W × I P=0.036)','로메인 P1 대조구 142 > 침수 133·복합 130 (침수 효과 P=0.011, 처리 P=0.060; 측정일 반복 n.s., P=0.46), P2 차이 없음 (P=0.61)'])
foot(s,'표: 측정일·선형 PAR(Q_{amb})·기온(T_{air}) 보정 평균, Tukey 문자, 괄호 = (PAR만 보정; 원 평균). 공통 측정일만 사용(로메인 P1 = DAT 5~10). W × I = 침수 × 관수 상호작용.')
notes(s,'질의응답용 자료입니다. 전자전달속도는 측정 광도에 비례하므로 광도를 보정한 평균으로 비교했고, 로메인 상추에서는 침수구가 약 6~8% 낮은 경향을 보였지만 측정일 반복 기준으로는 유의하지 않았습니다.')

# ===== A5 cloudy days
s=S(27)
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
refs=['Ali et al. (2025) J Exp Bot 76:4141.','Buckley TN (2019) New Phytol 224 (doi:10.1111/nph.15899).','Gao et al. (2024) J Exp Bot 75:4904.','Haverroth EJ et al. (2024) Plant Physiol 197(1):kiae336.','Hilker M et al. (2016) Biol Rev 91:1118–1133.','Körner C (2015) Curr Opin Plant Biol 25:107–114.','Sasidharan R et al. (2018) Plant Physiol 176:1106–1117.','Swain DL et al. (2018) Nat Clim Change 8:427–433.','Tan X et al. (2018) J Plant Physiol 227:20–30.','Tardieu F, Simonneau T, Muller B (2018) Annu Rev Plant Biol 69.','Yeung E et al. (2018) PNAS 115:E6085–E6094.','Zandalinas SI, Mittler R (2022) New Phytol 234:1161–1167.']
set_paras(byname(s,'Appendix list'),refs)
notes(s,'발표에 인용한 참고문헌입니다.')

# ===== delete excluded + reorder
sld=prs.slides._sldIdLst; ids=list(sld)
order=[1,2,3,4,5,6,33,7,8,9,11,13,14,15,16,17,34,18,19,20,21,22,25,26,27,35]
keep={ids[i-1] for i in order}
for x in ids:
    if x not in keep:
        prs.part.drop_rel(x.rId); sld.remove(x)
cur={ids[i-1]:i for i in order}
newlist=[ids[i-1] for i in order]
for x in list(sld): sld.remove(x)
for x in newlist: sld.append(x)
prs.save('oral/oral_v1.pptx'); print('saved',len(prs.slides))
