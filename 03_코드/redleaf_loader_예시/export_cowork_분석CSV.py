# -*- coding: utf-8 -*-
"""PPT에 쓰인 자료를 Cowork 분석용 CSV로 내보낸다. 결과: 1차 년도(2026)/cowork_분석자료/data/*.csv"""
import os, sys, json, shutil, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\yunjm\pptwork\cmp")
ns = {"__name__": "x"}
exec(compile(open(r"C:\Users\yunjm\pptwork\cmp\cmp_figs2.py", encoding="utf-8").read(), "cmp_figs2", "exec"), ns)
D, cloud, cloud_tab, TR = ns["D"], ns["cloud"], ns["cloud_tab"], ns["TR"]
import cmp_data2 as c2
sys.path.insert(0, r"C:\Users\yunjm\pptwork\lettuce")

OUT = r"C:\Users\yunjm\OneDrive - jbnu.ac.kr\바탕 화면\연구 과제\밭콩 과제\1차 년도(2026)\cowork_분석자료\data"
os.makedirs(OUT, exist_ok=True)
START = {"bean": pd.Timestamp("2026-08-12"), "let": pd.Timestamp("2026-10-07")}
LABEL = {"ETc": "ETc 100% (대조구)", "ETc50": "ETc 50% (건조)", "침수ETc": "Flooding-ETc 100% (침수)", "침수ETc50": "Flooding-ETc 50% (복합)"}


def save(df, name):
    df.to_csv(os.path.join(OUT, name), index=False, encoding="utf-8-sig")
    print(name, df.shape)


# 1. 흐린 날 판정
ct = cloud_tab.copy()
ct["date"] = pd.to_datetime(ct["date"]).dt.strftime("%Y-%m-%d")
save(ct.rename(columns={"species": "작물(bean/let)", "date": "날짜", "start": "측정시작", "end": "측정끝", "sw_mean": "측정구간 평균SW(W m-2)", "sw_cv": "SW 변동계수",
                        "sw_ref": "기준SW(±10일 90분위수)", "n": "SW 자료수", "CI": "맑음지수CI", "excl": "제외여부", "manual": "직접판정"}), "01_흐린날_판정_CI.csv")

# 2. LI-600 개별 측정 (흐린 날 표시 포함)
b = D["bean_li"].copy()
b["작물"] = "bean"; b["제외(흐림)"] = b["날짜"].isin(cloud["bean"])
l = D["let_li"].copy()
l["작물"] = "lettuce"; l["제외(흐림)"] = l["날짜"].isin(cloud["let"])
cols = ["작물", "날짜", "DAT", "처리", "반복", "Time", "Qamb", "gsw_보정", "gsw_해석용", "VPDleaf", "Fs", "Fm'", "PhiPS2", "ETR", "Tleaf", "제외(흐림)", "원본파일"]
b2 = b.rename(columns={"Time": "Time"}); l2 = l.copy()
allli = pd.concat([b2.reindex(columns=cols), l2.reindex(columns=cols)], ignore_index=True)
allli["날짜"] = pd.to_datetime(allli["날짜"]).dt.strftime("%Y-%m-%d")
allli = allli.rename(columns={"gsw_보정": "gsw_보정(mol m-2 s-1)", "gsw_해석용": "gsw_해석용(0 이하 제외)"})
save(allli, "02_LI600_개별측정.csv")
# 처리 전 LI-600 (밭콩 8/7)
pre = ns["bpre"].copy(); pre["작물"] = "bean"
save(pd.concat([pre.reindex(columns=cols[:-2] + ["원본파일"]), ns["lpre_li"].assign(작물="lettuce").reindex(columns=cols[:-2] + ["원본파일"])], ignore_index=True), "02b_LI600_처리전_개별측정.csv")

# 3. 암적응 Fv/Fm
bd = D["bean_dark"].assign(작물="bean"); ld = D["let_dark"].assign(작물="lettuce")
dcols = ["작물", "날짜", "DAT", "처리", "반복", "Fo", "Fm", "Fv/Fm", "비고", "원본파일"]
dd = pd.concat([bd.reindex(columns=dcols), ld.reindex(columns=dcols)], ignore_index=True)
dd["날짜"] = pd.to_datetime(dd["날짜"]).dt.strftime("%Y-%m-%d")
dpre = pd.concat([ns["bdpre"].assign(작물="bean").reindex(columns=dcols), ns["ldpre"].assign(작물="lettuce").reindex(columns=dcols)])
save(pd.concat([dd, dpre.assign(날짜=pd.to_datetime(dpre["날짜"]).dt.strftime("%Y-%m-%d"))], ignore_index=True), "03_암적응_FvFm_개별측정.csv")

# 4. 측정일별 평균·SE·n·ANOVA P (지표 × 작물 × DAT × 처리)
S = json.load(open(r"C:\Users\yunjm\pptwork\cmp\summary2.json", encoding="utf-8"))
rows = []
src = {"gsw": ("gsw_해석용", "gsw_해석용"), "phi": ("PhiPS2", "PhiPS2"), "fs": ("Fs", "Fs"), "etr": ("ETR", "ETR"), "fvfm": ("Fv/Fm", "Fv/Fm")}
dfs = {"gsw": (ns["bl"], ns["ll"]), "phi": (ns["bl"], ns["ll"]), "fs": (ns["bl"], ns["ll"]), "etr": (ns["bl"], ns["ll"]), "fvfm": (ns["bdk"], ns["ldk"])}
for key, (bc, lc) in src.items():
    for sp, df, col in (("bean", dfs[key][0], bc), ("lettuce", dfs[key][1], lc)):
        pp = S[key]["bean" if sp == "bean" else "let"]["p_by_day"]
        g = df.groupby(["DAT", "처리"])[col].agg(["mean", "sem", "count"]).reset_index()
        for _, r in g.iterrows():
            rows.append(dict(지표=key, 작물=sp, DAT=int(r.DAT), 날짜=(START["bean" if sp == "bean" else "let"] + pd.Timedelta(days=int(r.DAT))).strftime("%Y-%m-%d"),
                             처리=r["처리"], 평균=r["mean"], SE=r["sem"], n=int(r["count"]), 당일_ANOVA_P=pp.get(str(int(r.DAT)))))
save(pd.DataFrame(rows), "04_측정일별_평균_SE_P.csv")

# 5. 구간(초기/후기) Duncan 결과
rows = []
for key in src:
    for per in ("early", "full"):
        for sp, nm in (("bean", "bean"), ("let", "lettuce")):
            r = S[key][per].get(sp)
            if not r:
                continue
            for t in TR:
                if t in r["mean"]:
                    rows.append(dict(지표=key, 구간=("초기(대조구·침수만 측정)" if per == "early" else "후기(4처리 측정)"), 작물=nm, 처리=t, 평균=r["mean"][t], SE=r["se"][t], n=r["n"][t],
                                     Duncan문자=r["letter"][t], ANOVA_P=r["p"], 포함DAT=",".join(map(str, S[key]["dates"][sp][per]))))
    for sp in ("bean", "let"):
        if sp in S[key].get("pre", {}):
            p = S[key]["pre"][sp]; rows.append(dict(지표=key, 구간="처리 전", 작물="bean" if sp == "bean" else "lettuce", 처리="Pre", 평균=p["mean"], SE=p["se"], n=p["n"]))
save(pd.DataFrame(rows), "05_구간별_Duncan.csv")

# 6. A-Ci / A-Q 파라미터
bpa, bpq = c2.bean_pre_params()
aci = pd.concat([D["bean_aci"].assign(작물="bean").rename(columns={"날짜": "date"}), bpa.assign(작물="bean", 단계="처리 전"), D["let_aci"].assign(작물="lettuce", 단계=lambda x: np.where(pd.to_datetime(x["date"]) < "2026-10-07", "처리 전", "처리 후"))], ignore_index=True)
aq = pd.concat([D["bean_aq"].assign(작물="bean").rename(columns={"날짜": "date"}), bpq.assign(작물="bean", 단계="처리 전"), D["let_aq"].assign(작물="lettuce", 단계=lambda x: np.where(pd.to_datetime(x["date"]) < "2026-10-07", "처리 전", "처리 후"))], ignore_index=True)
for df in (aci, aq):
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
save(aci, "06_ACi_파라미터.csv"); save(aq, "07_AQ_파라미터.csv")
rows = []
for k, v in S["par"].items():
    for sp, nm in (("bean", "bean"), ("let", "lettuce")):
        r = v[sp]["stat"]
        for t in TR:
            rows.append(dict(파라미터=k, 작물=nm, 처리=t, 평균=r["mean"][t], SE=r["se"][t], n=r["n"][t], Duncan문자=r["letter"][t], ANOVA_P=r["p"], 처리전_평균=v[sp]["pre"]["mean"], 처리전_SE=v[sp]["pre"]["se"], 처리전_n=v[sp]["pre"]["n"]))
save(pd.DataFrame(rows), "08_ACi_AQ_파라미터_Duncan.csv")

# 7. LI-6800 광도 곡선 (A, 형광 유도 지표) — 개별 점
bq = ns["bq"].assign(작물="bean", 단계2="처리 후");
bf = ns["b_curves"]["post"].assign(작물="bean", 단계2="처리 후")
bpc = ns["bpre_cur"].assign(작물="bean", 단계2="처리 전")
lcur = D["let_cur"].assign(작물="lettuce"); lcur["단계2"] = lcur["단계"]
keep = ["작물", "단계2", "날짜", "처리", "Qin", "PPFD", "A", "Ci", "gsw", "Fo", "Fm", "Fs", "Fm'", "Fv/Fm", "NPQ", "PhiPS2", "ETR", "Fo'", "Fv'/Fm'", "qP", "qL", "PhiNO", "PhiNPQ", "원본파일"]
save(pd.concat([x.reindex(columns=keep) for x in (bq, bf, bpc, lcur)], ignore_index=True).assign(날짜=lambda z: pd.to_datetime(z["날짜"]).dt.strftime("%Y-%m-%d")), "09_LI6800_광곡선_개별점.csv")

# 8. 생육
bg = D["bean_growth"].copy(); bg = bg[bg["Treatment"].isin(TR)]
bg["날짜"] = pd.to_datetime(bg["날짜"]).dt.strftime("%Y-%m-%d")
bg["지상부FW(잎+줄기)"] = bg["잎 F.W"] + bg["줄기 F.W"]; bg["지상부DW(잎+줄기)"] = bg["잎 D.W"] + bg["줄기 D.W"]
save(bg, "10_생육_밭콩_파괴조사.csv")
lg = D["let_growth"].copy(); lg["날짜"] = pd.to_datetime(lg["날짜"]).dt.strftime("%Y-%m-%d")
save(lg, "11_생육_잎상추.csv")
rows = []
for var, d in S["growth"].items():
    for grp, r in d.items():
        for t in TR:
            rows.append(dict(지표=var, 조사=grp, 처리=t, 평균=r["mean"][t], SE=r["se"][t], n=r["n"][t], Duncan문자=r["letter"][t], ANOVA_P=r["p"]))
save(pd.DataFrame(rows), "12_생육_Duncan.csv")

# 9. 잎상추 관수·증산량
Q = pd.read_pickle(r"C:\Users\yunjm\pptwork\cmp\lc\Q.pkl"); M = pd.read_pickle(r"C:\Users\yunjm\pptwork\cmp\lc\M.pkl")
save(Q.assign(날짜=Q["date"].dt.strftime("%Y-%m-%d")).drop(columns="date").rename(columns={"trt": "처리(한글)", "target": "목표관수량(g/개체)", "sheet": "시트 평균관수량(g/개체)", "irr_keep": "CSV 안정값(g/개체)", "irr_peak": "CSV 피크(g/개체)", "delivered": "사용값(g/개체)", "src": "출처"}), "13_잎상추_일별_관수량_로드셀CSV.csv")
save(M.assign(날짜=M["date"].dt.strftime("%Y-%m-%d")).drop(columns="date").rename(columns={"trt": "처리(한글)", "lc_et": "로드셀 증산량(g/개체)", "man_et": "화분6반복 평균(g/개체)", "man_sd": "화분 SD", "man_n": "화분 n", "flag": "판정"}), "14_잎상추_일별_증산량_로드셀vs화분.csv")
et = D["let_et"].copy(); et["날짜"] = pd.to_datetime(et["날짜"]).dt.strftime("%Y-%m-%d"); save(et.drop(columns=["md"], errors="ignore"), "15_잎상추_화분증산량_원자료.csv")
shutil.copy(r"C:\Users\yunjm\pptwork\cmp\lc\lc_summary.json", os.path.join(OUT, "16_잎상추_관수·증산량_요약통계.json"))
# 로드셀 일별 요약(1분 자료는 용량이 커서 원본 CSV 경로만 안내)
shutil.copy(r"C:\Users\yunjm\pptwork\cmp\bean_et_daily.csv", os.path.join(OUT, "17_밭콩_일물소모_로드셀vsEC5.csv"))
shutil.copy(r"C:\Users\yunjm\pptwork\cmp\summary_et.json", os.path.join(OUT, "18_밭콩_일물소모_요약.json"))

# 10. 환경
import plot_environment as pe
e, hours = pe.load(); e = e[e["date"] <= ns["cd"].ps.END]
dli = pe.daily_dli(e).set_index("date")["DLI"]
bd_ = e.groupby("date").agg(평균기온=("temp", "mean"), 최고기온=("temp", "max"), 최저기온=("temp", "min"), 평균습도=("rh", "mean")); bd_["DLI_mol"] = dli
bd_.index = pd.to_datetime(bd_.index); bd_ = bd_[bd_.index >= "2026-08-07"]
bd_["DAT"] = (bd_.index - START["bean"]).days; bd_.index = bd_.index.strftime("%Y-%m-%d"); bd_.index.name = "날짜"
save(bd_.reset_index(), "19_환경_밭콩_일별.csv")
ld_ = D["let_daily"].copy(); ld_["날짜"] = pd.to_datetime(ld_["날짜"]); ld_ = ld_[ld_["날짜"] >= "2026-10-01"]; ld_["DAT"] = (ld_["날짜"] - START["let"]).dt.days; ld_["날짜"] = ld_["날짜"].dt.strftime("%Y-%m-%d")
save(ld_, "20_환경_잎상추_일별.csv")
shutil.copy(r"C:\Users\yunjm\pptwork\cmp\summary.json", os.path.join(OUT, "21_요약통계_관수·환경_summary.json"))
shutil.copy(r"C:\Users\yunjm\pptwork\cmp\summary2.json", os.path.join(OUT, "22_요약통계_지표_summary2.json"))
print("done")
