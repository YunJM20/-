# -*- coding: utf-8 -*-
"""9월 잎상추 폴더 -> (1) 잎상추_9월_종합데이터.xlsx  (2) 잎상추_9월_Duncan검정_결과.xlsx"""
import os, pickle
import numpy as np
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import lettuce_data as L
from lio import ROOT
from duncan_xl import *

OUT1 = os.path.join(ROOT, "잎상추_9월_종합데이터.xlsx")
OUT2 = os.path.join(ROOT, "잎상추_9월_Duncan검정_결과.xlsx")
TRT = ["C", "D", "W", "WD"]
NM = L.TRT_CODE
LBL = {"C": "대조구(CL)", "D": "건조(DL)", "W": "침수(WL)", "WD": "복합(WDL)"}
PHASES = [("P0 처리 전 (~10/06)", "2026-01-01", "2026-10-06"), ("P1 침수 처리 (10/07~10/10)", "2026-10-07", "2026-10-10"),
          ("P2 처리 후 초기 (10/11~10/16)", "2026-10-11", "2026-10-16"), ("P3 처리 후 후기 (10/17~10/23)", "2026-10-17", "2026-10-23")]

# ------------------------------------------------------------------ 자료
li, (n_nocorr,) = L.load_li600()
dark = L.load_dark()
par = L.load_params()
cur = L.load_6800_curves()
et = L.load_et()
irr = L.load_irrigation()
env = L.load_env()
env["RN"] = env["RN"].replace([np.inf, -np.inf], np.nan)
can = pd.read_csv(os.path.join(os.path.dirname(__file__), "canopy.csv"), parse_dates=["날짜"])


def phase_of(d):
    for n, a, b in PHASES:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b):
            return n
    return None


# ---- 환경: 일별/시간대별
es = lambda T: 0.6108 * np.exp(17.27 * T / (T + 237.3))
env["vpd"] = es(env["T"]) * (1 - env["RH"].clip(upper=100) / 100)
env["date"] = env["시간"].dt.normalize()
cnt = env.groupby("date")["T"].count()
okd = cnt[cnt >= 1380].index
e = env[env["date"].isin(okd)].copy()
e["day"] = e["SW"] >= 10
hh = e.set_index("시간")[["SW"]].resample("1h").mean()
hh["dli"] = hh["SW"] * 3600 * 0.45 * 4.57 * 1e-6
dli = hh.assign(date=hh.index.normalize()).groupby("date")["dli"].sum()
daily = e.groupby("date").agg(평균기온=("T", "mean"), 최고기온=("T", "max"), 최저기온=("T", "min"), 평균습도=("RH", "mean"), 평균VPD=("vpd", "mean"), 최대VPD=("vpd", "max"),
                              평균풍속=("WS", "mean"), 평균기압=("P", "mean"), 평균일사=("SW", "mean"), 순복사=("RN", "mean"))
daily["주간기온"] = e[e["day"]].groupby("date")["T"].mean()
daily["야간기온"] = e[~e["day"]].groupby("date")["T"].mean()
daily["주간습도"] = e[e["day"]].groupby("date")["RH"].mean()
daily["야간습도"] = e[~e["day"]].groupby("date")["RH"].mean()
daily["일사_MJ"] = daily["평균일사"] * 0.0864
daily["순복사_MJ"] = daily["순복사"] * 0.0864
daily["DLI_mol"] = dli
daily["30℃초과(h)"] = e.assign(f=e["T"] > 30).groupby("date")["f"].mean() * 24
daily["10℃미만(h)"] = e.assign(f=e["T"] < 10).groupby("date")["f"].mean() * 24
Tm, u2 = daily["평균기온"], np.maximum(daily["평균풍속"], 0.05)
delta = 4098 * es(Tm) / (Tm + 237.3) ** 2
gam = 0.000665 * (daily["평균기압"] / 10)
esm = (es(daily["최고기온"]) + es(daily["최저기온"])) / 2
ea = daily["평균습도"].clip(upper=100) / 100 * es(Tm)
daily["ET0_mm"] = (0.408 * delta * daily["순복사_MJ"].fillna(daily["일사_MJ"] * 0.77) + gam * 900 / (Tm + 273) * u2 * (esm - ea)) / (delta + gam * (1 + 0.34 * u2))
daily["구간"] = [phase_of(d) for d in daily.index]
daily = daily.reset_index().rename(columns={"date": "날짜"})
hour = e.assign(시각=e["시간"].dt.hour).groupby("시각").agg(평균기온=("T", "mean"), 평균습도=("RH", "mean"), 평균VPD=("vpd", "mean"), 평균일사=("SW", "mean"))

# ---- LI-600 정리
li["구간"] = [phase_of(d) for d in li["날짜"]]
li["gsw_해석용"] = li["gsw_보정"].where(li["gsw_보정"] > 0)       # 0 이하(측정 잡음)는 분석에서 제외
li["Qamb구간"] = np.where(li["Qamb"] < 300, "저광", np.where(li["Qamb"] <= 800, "중광", "고광"))
lt = li[li["처리코드"].notna()].copy()
lt["md"] = lt["날짜"].dt.strftime("%m-%d")
dark["md"] = dark["날짜"].dt.strftime("%m-%d")
dk = dark[dark["처리코드"].notna()].copy()
et["md"] = et["날짜"].dt.strftime("%m-%d")
et["제외"] = et["비고"].isin(["배액", "솎아냄"]) | et["증산량(g)"].isna() | et["원본파일"].str.contains("1007-1010")
et.loc[et["원본파일"].str.contains("1007-1010") & et["증산량(g)"].notna(), "비고"] = "10/7~10/10 파일: 관수 전·후 구분 없는 1일 1회 무게 → 증산량 신뢰 낮음(제외)"
irr.loc[(irr["날짜"] == "2026-10-23") & (irr["평균관수량(g)"] == 0), ["로드셀관수량(g)", "평균관수량(g)"]] = np.nan
irr["md"] = irr["날짜"].dt.strftime("%m-%d")
can["md"] = can["날짜"].dt.strftime("%m-%d")

# ------------------------------------------------------------------ (1) 종합 데이터 엑셀
def fmt_ws(ws, widths=None):
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFFFF")
        c.fill = PatternFill("solid", fgColor="2F5597")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"
    for i, col in enumerate(ws.iter_cols(min_row=1, max_row=1), 1):
        ws.column_dimensions[col[0].column_letter].width = (widths or {}).get(col[0].value, 13)


notes = [
    ["항목", "내용"],
    ["자료 출처", "…\\추계 원예학회\\9월 잎상추 폴더 (gsw·형광, 광합성, 증산량 계산, 캐노피_잎상추, 26번 온실 환경 데이터, 환경데이터_정리_0922이후)"],
    ["작성일", "2026-10-26"],
    ["처리 표기", "CL=대조구(ETc 100%), DL=건조(ETc 50%), WL=침수(침수 후 ETc 100%), WDL=복합(침수 후 ETc 50%). 관수량 시트의 'ETc 50', '침수 50'은 각각 DL, WDL"],
    ["처리 일정(사용자 확인)", "침수 처리 10/7 오전 ~ 10/10 오전(3일), 건조 처리는 10/10부터 시작했고 건조·복합의 50% 관수(로드셀 기록)는 10/12부터 들어감. 구간: P0 처리 전(~10/6), P1 침수 처리(10/7~10/10), P2 처리 후 초기(10/11~10/16), P3 처리 후 후기(10/17~10/23)"],
    ["품종", "잎상추(Red Leaf)만 사용. 품종 표시와 처리 라벨이 없는 단일 측정은 잎상추로 봄. Romaine(라벨 R, Species=Romaine)은 사용자 지시로 분석과 이 파일에서 제외"],
    ["측정 구성", "10/6: 대조구만, 10/8~10/11: 대조구·침수, 10/10 저녁 암적응부터 4처리 측정, 광합성·gsw의 건조·복합 측정은 10/12부터"],
    ["1_LI600_gsw_형광", "gsw/ 폴더 xlsx(원자료·처리 라벨)에 gsw보정/ 폴더의 사용자 보정값(gsw_corrected)을 (날짜, 시각)으로 연결. 보정값이 없는 행은 제외. 10/17 측정은 사용자가 정리한 '잎상추' 시트(라벨 ETc, ETc50, 침수ETc, 침수ETc50 → CL, DL, WL, WDL로 환산)를 사용"],
    ["gsw 분석값", "분석에는 사용자 보정 gsw(gsw_보정)를 사용. 원값 gsw는 참고용으로만 수록"],
    ["gsw ≤ 0", "gsw_보정이 0 이하인 행(측정 잡음)은 gsw_해석용 열에서 공란으로 두고 통계에서 제외"],
    ["2_암적응형광", "형광/ 폴더 xlsx의 Fo, Fm, Fv/Fm. 10/7, 10/10, 10/16(잎상추 시트, 라벨 ETc·ETc50·침수ETc·침수ETc50 → CL·DL·WL·WDL로 환산)은 사용자가 라벨을 추가한 자료. 10/15는 라벨에 반복 번호가 없음. 10/10 저녁에는 건조·복합도 측정됨"],
    ["3·4 A-Ci / A-Q 파라미터", "광합성/광합성 파라미터 종합.xlsx의 A-Ci_results, A-Q_results. 사용자가 '제외'로 표시한 행은 제외 열 True로 표시하고 분석에서 뺌. 날짜는 raw 파일명 기준 실제 측정일(10/4 처리 전, 10/10 침수 직후, 10/16~10/19 처리 후)이며 묶음날짜 열에 파라미터 파일의 묶음 날짜(10/16)를 함께 적음"],
    ["5_LI6800_광반응_형광", "광합성/ 폴더의 light curve raw(10/4 처리 전 3개, 10/16~10/19 처리 후 4처리 × 4개)에서 Fs, Fm', Qin을 읽고, Fo·Fm은 곡선 파일의 값이 아니라 형광/LI-6800 형광.xlsx(2026-10-27 암적응 측정 12개)의 처리별 평균(12_Fo_Fm_1027 시트)을 적용해 qP, NPQ, ETR, PhiPS2, PhiNO, PhiNPQ 등을 계산(밭콩 15_형광계산 시트와 같은 식). 사유: 곡선 파일의 Fo·Fm은 광도 0 지점이 암적응이 안 돼 Fv/Fm이 낮음(파일 값은 Fo_파일·Fm_파일 열에 보존). 처리 전(10/4) 곡선은 대조구(CL) 평균 적용. Romaine(R) 파일 제외. 실제 측정일은 파일명 기준(10/16~10/19)"],
    ["12_Fo_Fm_1027", "형광/LI-6800 형광.xlsx '정리' 시트(2026-10-27 20:16~20:35 LI-6800 암적응 측정, CL·DL·WL·WDL × 3개체 = 12개)의 Fo, Fm과 Fv/Fm=(Fm-Fo)/Fm. 아래쪽에 처리별 평균(5_LI6800_광반응_형광에 적용). 8월 형광/잎상추_OJIP 36개 파일은 다른 작기 자료라 2026-10-27 사용자 지시로 사용하지 않음"],
    ["13_흐린날_판정", "LI-600 측정 시각 일사(SW)가 같은 시각대 ±10일 90분위수의 50% 미만(CI<0.5)이면 흐린 날로 제외. 사용자 직접 판정(2026-10-27): 10/6·10/7·10/8은 맑음, 10/19는 흐림으로 확정. 암적응 Fv/Fm은 야간 측정이라 적용하지 않음. 1_LI600_gsw_형광 시트에 CI와 흐린날제외 열을 추가"],
    ["6_증산량", "증산량 계산/ 폴더. 대조구(ETc)와 침수 ETc 포트 무게(각 3~6포트). 증산량 = 전날 관수 후 − 당일 관수 전. 비고가 '배액'·'솎아냄'인 행은 제외 열 True"],
    ["7_관수량", "로드셀관수량·관수량 비교 시트. 평균관수량 = 로드셀 관수량 ÷ 4(포트 평균). 10/18 목표관수량 오계산, 10/18~10/19 로드셀 이상은 비고에 표시"],
    ["8·9 환경", "26번 온실 환경 데이터(CR300, 1분). 2026-08-22~10-23. 로거 재가동 직후 온도·습도·일사 모두 0인 행은 결측, 하루 1380분 미만 기록 날은 제외. 주간=일사 10 W m-2 이상. DLI = 일 누적 일사 × 0.45 × 4.57, ET0는 FAO-56 Penman-Monteith 일 단위 근사(풍속 하한 0.05 m/s)"],
    ["10_캐노피", "캐노피_잎상추/ 사진(10/12, 15, 19, 23; 처리당 6장)에서 식물 영역(붉은 보라·녹색 픽셀)을 분리해 면적(px)과 이미지 대비 비율을 구하고, 상추 옆에 빼 둔 줄자 50 cm의 화소 길이(날짜별 중앙값, 이미지 간 편차 ≤3.5%)로 스케일을 보정해 면적(cm2)을 계산. 줄자는 바닥 높이, 식물 상단은 더 높아 원근 오차가 있을 수 있음(상대 비교용)"],
    ["11_생육조사", "생육조사_잎상추.xlsx (10/7 처리 전 대조구 9개체, 10/23 4처리 × 9개체: SPAD, 엽장, 엽폭, 엽수, 엽면적, 지상부 생체중, 지하부 건조중, RWC 등). 2026-10-27 지상부 생체중·건조중 자료 완성: 지상부 생체중·건조중은 'TW측정용'과 '나머지'를 합친 '전체' 값(열 지상부생체중, 지상부건조중_전체)을 사용하고 TW측정용·나머지 열은 참고로만 보존. 지하부 건조중은 배지를 제외한 값(열 지하부건조중)을 사용(배지 포함 값은 지하부건조중_배지포함). RWC는 개체 3개씩(TW 측정분)"],
]
with pd.ExcelWriter(OUT1, engine="openpyxl") as xw:
    pd.DataFrame(notes[1:], columns=notes[0]).to_excel(xw, "0_안내", index=False)
    cols = ["날짜", "품종", "처리", "처리코드", "원본라벨", "반복", "Obs", "Time", "Qamb", "gsw", "gsw_보정", "보정방법", "gsw_해석용", "VPDleaf", "Fs", "Fm'", "PhiPS2", "ETR",
            "Tleaf", "구간", "원본파일"]
    x = li[cols].copy()
    import sys as _sys
    _sys.path.insert(0, r"C:\Users\yunjm\pptwork\cmp")
    import cmp_data2 as _c2
    _cx = _c2.cloudy_dates()[1]
    _cx = _cx[_cx["species"] == "let"].set_index("date")
    x["CI(맑음지수)"] = li["날짜"].map(_cx["CI"])
    x["흐린날제외"] = li["날짜"].map(_cx["excl"]).fillna(False)
    x["날짜"] = x["날짜"].dt.strftime("%Y-%m-%d")
    x.to_excel(xw, "1_LI600_gsw_형광", index=False)
    d2 = dark[["날짜", "처리", "처리코드", "원본라벨", "반복", "Obs#", "Time", "Fo", "Fm", "Fv/Fm", "gsw", "비고", "원본파일"]].copy()
    d2["날짜"] = d2["날짜"].dt.strftime("%Y-%m-%d")
    d2.to_excel(xw, "2_암적응형광", index=False)
    a = par["aci"][["date", "묶음날짜", "처리", "처리코드", "라벨", "반복", "time", "Vcmax", "Jmax", "Rd", "제외", "비고", "file"]].copy()
    a["date"] = a["date"].dt.strftime("%Y-%m-%d")
    a["묶음날짜"] = a["묶음날짜"].dt.strftime("%Y-%m-%d")
    a.rename(columns={"date": "날짜", "라벨": "원본라벨", "file": "원본파일"}).to_excel(xw, "3_ACi_파라미터", index=False)
    q = par["aq"][["date", "묶음날짜", "처리", "처리코드", "라벨", "반복", "time", "alpha", "theta", "Amax", "Rd", "제외", "file"]].copy()
    q["date"] = q["date"].dt.strftime("%Y-%m-%d")
    q["묶음날짜"] = q["묶음날짜"].dt.strftime("%Y-%m-%d")
    q.rename(columns={"date": "날짜", "라벨": "원본라벨", "file": "원본파일"}).to_excel(xw, "4_AQ_파라미터", index=False)
    oj, oj_mean = L.load_ojip()
    oj.to_excel(xw, sheet_name="12_Fo_Fm_1027", index=False)
    mm = oj_mean.reset_index().rename(columns={"Fo": "평균 Fo", "Fm": "평균 Fm"})
    mm.to_excel(xw, sheet_name="12_Fo_Fm_1027", index=False, startrow=len(oj) + 3)
    _cx2 = _c2.cloudy_dates()[1]
    _cx2 = _cx2[_cx2["species"] == "let"].copy()
    _cx2["date"] = _cx2["date"].dt.strftime("%Y-%m-%d")
    _cx2["판정"] = np.where(_cx2["excl"], "흐림(제외)", "맑음(사용)")
    _cx2.rename(columns={"species": "작물", "date": "날짜", "start": "시작", "end": "끝", "sw_mean": "SW 평균(W m-2)", "sw_cv": "SW CV", "sw_ref": "맑은날 기준 SW", "manual": "직접판정"}).drop(columns=["n", "excl"]).to_excel(xw, sheet_name="13_흐린날_판정", index=False)
    c2 = cur.copy()
    c2["날짜"] = c2["날짜"].dt.strftime("%Y-%m-%d")
    c2.to_excel(xw, "5_LI6800_광반응_형광", index=False)
    e2 = et[["날짜", "처리", "Treatment", "Repeat", "관수전(g)", "관수후(g)", "증산량(g)", "제외", "비고", "원본파일"]].copy()
    e2["날짜"] = e2["날짜"].dt.strftime("%Y-%m-%d")
    e2.to_excel(xw, "6_증산량", index=False)
    i2 = irr[[c for c in ["날짜", "처리", "Treatment", "관수 전(kg)", "관수 후(kg)", "로드셀관수량(g)", "평균관수량(g)", "배수 후(kg)", "평균 배액(g)", "목표관수량(g)", "관수 시간(s)", "관수량 차이", "비고", "원본파일"] if c in irr.columns]].copy()
    i2["날짜"] = i2["날짜"].dt.strftime("%Y-%m-%d")
    i2.to_excel(xw, "7_관수량", index=False)
    d3 = daily.copy()
    d3["날짜"] = d3["날짜"].dt.strftime("%Y-%m-%d")
    d3.round(3).to_excel(xw, "8_환경_일별", index=False)
    hour.round(3).reset_index().to_excel(xw, "9_환경_시간대별", index=False)
    c3 = can.copy()
    c3["날짜"] = c3["날짜"].dt.strftime("%Y-%m-%d")
    c3.round(3).to_excel(xw, "10_캐노피", index=False)
    gr_ = L.load_growth()
    gr_["날짜"] = gr_["날짜"].dt.strftime("%Y-%m-%d")
    gr_.to_excel(xw, "11_생육조사", index=False)
wb = openpyxl.load_workbook(OUT1)
for ws in wb.worksheets:
    fmt_ws(ws, {"원본파일": 40, "비고": 22, "구간": 26})
ws = wb["0_안내"]
ws.column_dimensions["A"].width = 24
ws.column_dimensions["B"].width = 160
for r in ws.iter_rows(min_row=2):
    for c in r:
        c.alignment = Alignment(wrap_text=True, vertical="top")
wb.save(OUT1)
print("saved", OUT1)

pickle.dump(dict(li=li, lt=lt, dk=dk, par=par, cur=cur, et=et, irr=irr, daily=daily, can=can, ab=(n_nocorr,)), open(os.path.join(os.path.dirname(__file__), "lettuce.pkl"), "wb"))
