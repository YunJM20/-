# -*- coding: utf-8 -*-
"""9월 잎상추 폴더의 원자료를 표준 DataFrame으로 읽는다 (LI-600, 암적응, 파라미터, LI-6800 곡선, 증산량, 관수량, 환경, 캐노피)"""
import glob, os, re
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from lio import ROOT, rd, sheets, base

TRT_CODE = {"C": "대조구", "D": "건조", "W": "침수", "WD": "복합"}
TRT_ORDER = ["C", "D", "W", "WD"]
SPECIES = {"L": "Red Leaf", "R": "Romaine"}
PAT = re.compile(r"^(WD|W|D|C)([LR])?(?:[-\s]?(\d+))?$")


def norm_time(t):
    t = str(t).strip()
    m = re.match(r"^(\d{1,2}):(\d{2}):(\d{2})", t)
    return f"{int(m.group(1)):02d}:{m.group(2)}:{m.group(3)}" if m else t


NAME_PAT = re.compile(r"^(침수ETc50|침수ETc|ETc50|ETc)(?:[-_]?(\d+))?$")
NAME_CODE = {"ETc": "C", "ETc50": "D", "침수ETc": "W", "침수ETc50": "WD"}


def parse_label(lbl):
    """'CL-1','WDR-3','CR-2','ETc50','침수 ETc 50-3' -> (code, species_letter or None, rep) ; 실패하면 (None, None, None)"""
    if lbl is None or (isinstance(lbl, float) and np.isnan(lbl)):
        return None, None, None
    t = str(lbl).strip().replace(" ", "")
    m = NAME_PAT.match(t)
    if m:
        return NAME_CODE[m.group(1)], None, (int(m.group(2)) if m.group(2) else None)
    m = PAT.match(t)
    if not m:
        return None, None, None
    return m.group(1), m.group(2), (int(m.group(3)) if m.group(3) else None)


# ------------------------------------------------------------------ LI-600
GSW_COLS = ["Obs#", "Time", "Date", "Species", "Treatment", "Number", "gsw", "gbw", "gtw", "VPDleaf", "Fs", "Fm'", "PhiPS2", "ETR", "Tleaf", "Qamb"]


def load_corrections():
    """gsw보정/ 폴더의 보정 파일(Corrected 시트 또는 단일 시트)에서 {(날짜, 시각): gsw_corrected}"""
    corr = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "gsw, 형광", "gsw보정", "*.xlsx"))):
        names = sheets(f)
        c = rd(f, sheet_name="Corrected") if "Corrected" in names else rd(f)
        for _, r in c.iterrows():
            corr[(str(r["Date"])[:10], norm_time(r["Time"]))] = r["gsw_corrected"]
    return corr


def load_li600():
    """gsw/ 폴더 xlsx(처리 라벨·모든 열) + 사용자 보정값. 보정값이 없는 행은 제외. Romaine은 사용하지 않는다(사용자 지시)."""
    corr = load_corrections()
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "gsw, 형광", "gsw", "*.xlsx"))):
        if "잎상추" in sheets(f):
            d = rd(f, sheet_name="잎상추", header=0)
        else:
            d = rd(f, header=1).iloc[1:]
        d = d[[c for c in GSW_COLS if c in d.columns]].copy()
        for c in ["Obs#", "Number", "gsw", "gbw", "gtw", "VPDleaf", "Fs", "Fm'", "PhiPS2", "ETR", "Tleaf", "Qamb"]:
            if c in d.columns:
                d[c] = pd.to_numeric(d[c], errors="coerce")
        d["Date"] = d["Date"].astype(str).str[:10]
        d["Time"] = d["Time"].map(norm_time)
        d["원본파일"] = base(f)
        out.append(d)
    d = pd.concat(out, ignore_index=True)
    d = d[d["Date"].str.len() == 10]
    d["gsw_보정"] = [corr.get((a, b), np.nan) for a, b in zip(d["Date"], d["Time"])]
    n_nocorr = int(d["gsw_보정"].isna().sum())
    d = d[d["gsw_보정"].notna()].copy()
    codes = d["Treatment"].map(parse_label)
    d["처리코드"] = [c[0] for c in codes]
    d["반복"] = [c[2] for c in codes]
    sp = []
    for (c, letter, rep), s_ in zip(codes, d["Species"]):
        if isinstance(s_, str) and s_.strip():
            sp.append("Romaine" if s_.strip().startswith("Romaine") else "잎상추")
        elif letter == "R":
            sp.append("Romaine")
        else:
            sp.append("잎상추")                   # 품종 표시가 없는 단일 측정은 잎상추
    d["품종"] = sp
    d = d[d["품종"] != "Romaine"].copy()
    d["원본라벨"] = d["Treatment"]
    d["처리"] = d["처리코드"].map(TRT_CODE)
    d["날짜"] = pd.to_datetime(d["Date"])
    d["보정방법"] = "사용자 보정 파일"
    d = d.rename(columns={"Obs#": "Obs"})
    return d, (n_nocorr,)


def read_licor(f, **kw):
    """LI-600 export: 헤더행(Obs#)을 찾아 읽고 단위 행을 버린다"""
    raw = rd(f, header=None, **kw)
    hi = None
    for i in range(min(6, len(raw))):
        if "Obs#" in [str(x) for x in raw.iloc[i].tolist()]:
            hi = i
            break
    if hi is None:
        # 헤더 행이 없는 파일(261018): 다른 파일과 같은 열 순서를 사용
        ref = rd(os.path.join(ROOT, "gsw, 형광", "형광", "261007_형광.xlsx"), header=1)
        cols = list(ref.columns)[: raw.shape[1]]
        d = raw.copy()
        d.columns = cols
        return d
    d = raw.iloc[hi + 1:].copy()
    d.columns = [str(x) for x in raw.iloc[hi].tolist()]
    return d.iloc[1:] if str(d.iloc[0, 1]).upper().startswith("HH") else d


def load_dark():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "gsw, 형광", "형광", "26*.xlsx"))):   # 26MMDD_형광.xlsx만 (LI-6800 형광.xlsx는 Fo/Fm 전용)
        d = rd(f, sheet_name="잎상추", header=0) if "잎상추" in sheets(f) else read_licor(f)
        keep = [c for c in ["Obs#", "Time", "Date", "Observation", "Treatment", "gsw", "Fo", "Fm", "Fv/Fm"] if c in d.columns]
        d = d[keep].copy()
        if "Treatment" not in d.columns:
            d["Treatment"] = np.nan
        for c in ["Obs#", "gsw", "Fo", "Fm", "Fv/Fm"]:
            if c in d.columns:
                d[c] = pd.to_numeric(d[c], errors="coerce")
        d["Date"] = d["Date"].astype(str).str[:10]
        d["원본파일"] = base(f)
        out.append(d)
    d = pd.concat(out, ignore_index=True)
    d = d[d["Date"].str.len() == 10]
    codes = d["Treatment"].map(parse_label)
    d["처리코드"] = [c[0] for c in codes]
    d["반복"] = [c[2] for c in codes]
    d["처리"] = d["처리코드"].map(TRT_CODE)
    d["원본라벨"] = d["Treatment"]
    d["날짜"] = pd.to_datetime(d["Date"])
    d["비고"] = np.where(d["처리코드"].isna(), "처리 라벨 없음(분석 제외)", "")
    return d


# ------------------------------------------------------------------ A-Ci / A-Q 파라미터
def load_params():
    f = os.path.join(ROOT, "광합성", "광합성 파라미터 종합.xlsx")
    res = {}
    for sh, key in (("A-Ci_results", "aci"), ("A-Q_results", "aq")):
        d = rd(f, sheet_name=sh, header=0)
        d = d.rename(columns={d.columns[3]: "라벨"})
        last = str(d.columns[-1])
        if last.startswith("Unnamed") or last == "nan":
            d = d.rename(columns={d.columns[-1]: "비고"})
        else:
            d["비고"] = np.nan
        d = d[d["file"].notna()].copy()
        d["묶음날짜"] = pd.to_datetime(d["date"].astype(str).str[:10])          # 파라미터 파일에 적힌 묶음 날짜(10/16~10/19는 10/16으로 묶음)
        d["date"] = pd.to_datetime(d["file"].astype(str).str.extract(r"^(\d{4}-\d{2}-\d{2})")[0])   # 실제 측정일(파일명)
        codes = d["라벨"].map(parse_label)
        d["처리코드"] = [c[0] for c in codes]
        d["반복"] = [c[2] for c in codes]
        d["처리"] = d["처리코드"].map(TRT_CODE)
        d["제외"] = d["비고"].astype(str).str.contains("제외")
        res[key] = d
    return res


# ------------------------------------------------------------------ 잎상추 암적응 Fo, Fm (2026-10-27 LI-6800 측정)
def load_ojip():
    """형광/LI-6800 형광.xlsx '정리' 시트(2026-10-27 저녁 암적응, CL/DL/WL/WDL x 3개체): Fo, Fm. 측정별 값과 처리별 평균을 돌려준다.
    (8월 OJIP 36개 파일은 다른 작기 자료라 2026-10-27 사용자 지시로 사용하지 않음. 함수 이름만 호환을 위해 유지)"""
    f = os.path.join(ROOT, "gsw, 형광", "형광", "LI-6800 형광.xlsx")
    t = rd(f, sheet_name="정리")
    t["처리라벨"] = t["Treatment"].astype(str).str.strip()
    t["처리코드"] = t["처리라벨"].str.replace(r"-\d+$", "", regex=True).map({"CL": "C", "DL": "D", "WL": "W", "WDL": "WD"})
    t["개체"] = t["처리라벨"].str.extract(r"-(\d+)$")[0].astype(int)
    d = pd.DataFrame({"처리코드": t["처리코드"], "개체": t["개체"], "반복": 1, "측정일시": t["date"].astype(str), "Fo": t["Fo"].astype(float), "Fm": t["Fm"].astype(float),
                      "원본라벨": t["처리라벨"], "원본파일": base(f)})
    d["Fv/Fm"] = (d["Fm"] - d["Fo"]) / d["Fm"]
    return d, d.groupby("처리코드")[["Fo", "Fm"]].mean()


# ------------------------------------------------------------------ LI-6800 광반응곡선(형광 포함)
def load_6800_curves():
    rows = []
    for folder in sorted(os.listdir(os.path.join(ROOT, "광합성"))):
        if not os.path.isdir(os.path.join(ROOT, "광합성", folder)) or not folder.startswith("2026-"):
            continue
        for f in sorted(glob.glob(os.path.join(ROOT, "광합성", folder, "*light.xlsx"))):
            try:
                c = rd(f, sheet_name="Clean_Data")
                r = rd(f, sheet_name="Raw_Data")
            except Exception:
                continue
            n = min(len(c), len(r))
            c = c.iloc[:n].reset_index(drop=True)
            r = r.iloc[:n].reset_index(drop=True)
            m = re.search(r"(\d{4}-\d{2}-\d{2})-(\d{4})_logdata (.+?) light", base(f))
            date, tm, lbl = m.group(1), m.group(2), m.group(3)
            lbl = lbl.replace(" ", "-")
            lbl = {"L-1": "CL-1", "L-2": "CL-2", "L-3": "CL-3"}.get(lbl, lbl)
            code, letter, rep = parse_label(lbl)
            if letter == "R":
                continue                       # Romaine 제외
            df = pd.DataFrame({"날짜": pd.Timestamp(date), "시각": tm, "원본라벨": lbl, "처리코드": code, "반복": rep, "Qin": r["Qin"].values,
                               "A": c["A"].values, "Ci": c["Ci"].values, "gsw": c["gsw"].values, "Fo": c["Fo"].values, "Fm": c["Fm"].values,
                               "Fs": c["Fs"].values, "Fm'": c["Fm'"].values, "원본파일": base(f)})
            rows.append(df)
    d = pd.concat(rows, ignore_index=True)
    d["처리"] = d["처리코드"].map(TRT_CODE)
    d["단계"] = np.where(d["날짜"] < "2026-10-07", "처리 전", np.where(d["날짜"] <= "2026-10-10", "침수 직후", "처리 후"))
    # Fo, Fm: 곡선 파일의 값(광도 0 지점이 암적응이 안 되어 Fv/Fm이 낮음)은 쓰지 않고 10/27 LI-6800 암적응 측정의 처리별 평균으로 대체 (처리 전 곡선은 대조구 평균)
    d["Fo_파일"], d["Fm_파일"] = d["Fo"], d["Fm"]
    _, mean_ = load_ojip()
    key = d["처리코드"].fillna("C")
    d["Fo"] = key.map(mean_["Fo"])
    d["Fm"] = key.map(mean_["Fm"])
    # 유도 형광 지표 (밭콩 15_형광계산 시트와 같은 식)
    Fo, Fm, Fs, Fmp, Q = d["Fo"], d["Fm"], d["Fs"], d["Fm'"], d["Qin"]
    ok = (Fs > 0) & (Fmp > 0) & (Fo > 0) & (Fm > 0) & (Q > 0)
    d["유효"] = ok
    d["Fv/Fm"] = (Fm - Fo) / Fm
    d["NPQ"] = (Fm - Fmp) / Fmp
    d["PhiPS2"] = (Fmp - Fs) / Fmp
    d["ETR"] = d["PhiPS2"] * Q * 0.84 * 0.5
    d["Fo'"] = Fo / (d["Fv/Fm"] + Fo / Fmp)
    d["Fv'/Fm'"] = 1 - d["Fo'"] / Fmp
    d["qP"] = (Fmp - Fs) / (Fmp - d["Fo'"])
    d["qN"] = (Fm - Fmp) / (Fm - d["Fo'"])
    d["qL"] = d["qP"] * d["Fo'"] / Fs
    d["PhiNO"] = 1 / (d["NPQ"] + 1 + d["qL"] * (Fm / Fo - 1))
    d["PhiNPQ"] = 1 - d["PhiPS2"] - d["PhiNO"]
    for c in ["NPQ", "PhiPS2", "ETR", "Fo'", "Fv'/Fm'", "qP", "qN", "qL", "PhiNO", "PhiNPQ"]:
        d.loc[~ok, c] = np.nan
    return d


# ------------------------------------------------------------------ 증산량 / 관수량
def load_et():
    out = []
    f1 = os.path.join(ROOT, "증산량 계산", "증산량_잎상추_1007-1010.xlsx")
    d = rd(f1, sheet_name="증산량(ETc,침ETc)")
    d = d.rename(columns={"무게(g)": "관수후(g)"})
    d["관수전(g)"] = np.nan
    d["비고"] = ""
    d["원본파일"] = base(f1)
    out.append(d[["날짜", "Treatment", "Repeat", "관수전(g)", "관수후(g)", "증산량(g)", "비고", "원본파일"]])
    f2 = os.path.join(ROOT, "증산량 계산", "증산량_잎상추_1011-1023.xlsx")
    d = rd(f2, sheet_name="증산량(ETc,침ETc)")
    d = d.rename(columns={"관수 전(g)": "관수전(g)", "관수 후(g)": "관수후(g)"})
    d["원본파일"] = base(f2)
    out.append(d[["날짜", "Treatment", "Repeat", "관수전(g)", "관수후(g)", "증산량(g)", "비고", "원본파일"]])
    e = pd.concat(out, ignore_index=True)
    e["날짜"] = pd.to_datetime(e["날짜"].astype(str).str[:10])
    e["Repeat"] = pd.to_numeric(e["Repeat"], errors="coerce")
    e["처리"] = e["Treatment"].map({"ETc": "대조구", "침수 ETc": "침수"})
    e["비고"] = e["비고"].fillna("")
    return e


def load_irrigation():
    out = []
    for fn in ("증산량_잎상추_1007-1010.xlsx", "증산량_잎상추_1011-1023.xlsx"):
        f = os.path.join(ROOT, "증산량 계산", fn)
        a = rd(f, sheet_name="로드셀관수량")
        b = rd(f, sheet_name="관수량 비교")
        a = a[a["날짜"].notna()]
        b = b[b["날짜"].notna()]
        m = a.merge(b[[c for c in ["날짜", "Treatment", "목표관수량(g)", "관수 시간(s)", "관수량 차이", "비고"] if c in b.columns]], on=["날짜", "Treatment"], how="left")
        m["원본파일"] = fn
        out.append(m)
    d = pd.concat(out, ignore_index=True)
    d["날짜"] = pd.to_datetime(d["날짜"].astype(str).str[:10])
    d["처리"] = d["Treatment"].astype(str).str.replace(r"\s+", "", regex=True).map({"ETc": "대조구", "ETc50": "건조", "침수ETc": "침수", "침수50": "복합"})
    d["비고"] = d["비고"].fillna("") if "비고" in d.columns else ""
    return d


# ------------------------------------------------------------------ 환경 (26번 온실, CR300 1분)
def load_env():
    f = os.path.join(ROOT, "26번 온실 환경 데이터.xlsx")
    d = rd(f, header=1)
    d = d.iloc[2:].copy()
    d["TIMESTAMP"] = pd.to_datetime(d["TIMESTAMP"], errors="coerce")
    d = d[d["TIMESTAMP"].notna()]
    for c in d.columns:
        if c != "TIMESTAMP":
            d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.rename(columns={"TIMESTAMP": "시간", "Air_Temp_Avg": "T", "RH_Avg": "RH", "Air_Press_Avg": "P", "WindSpeed_Avg": "WS", "Solar_Avg": "SW",
                          "NET_SOLAR_Avg": "RN", "Loadcell_Avg": "LC"})
    # 로거 재가동 직후 온도·습도·일사 모두 0인 행은 결측
    bad = (d["T"] == 0) & (d["RH"] == 0) & (d["SW"] == 0)
    d.loc[bad, ["T", "RH", "SW", "P", "WS", "RN"]] = np.nan
    return d[["시간", "T", "RH", "P", "WS", "SW", "RN", "LC"]].sort_values("시간").reset_index(drop=True)


def load_env_summary():
    f = os.path.join(ROOT, "환경데이터_정리_0922이후", "26번 온실 환경 요약_0922이후.xlsx")
    return rd(f, sheet_name="일별 요약")


# ------------------------------------------------------------------ 캐노피 사진
def canopy_cover(path):
    """위에서 찍은 사진에서 식물(채도가 높은 붉은 보라/녹색 픽셀) 면적(px)과 이미지 대비 비율(%)을 구한다.
    콘크리트 바닥(저채도 회색), 줄자·화분(오른쪽 띠), 삼각대(저명도)는 제외한다."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(float)
    h, w, _ = a.shape
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = (mx - mn) / (mx + 1e-6)
    exg = 2 * g - r - b
    # 붉은 잎: r > g, 채도 높음, 어두움 / 녹색 잎: exg > 0
    red = (r > g + 10) & (r > b + 5) & (sat > 0.28)
    dark_red = (mx < 150) & (r >= g) & (sat > 0.18)
    green = (exg > 15) & (sat > 0.2)
    mask = (red | dark_red | green)
    mask[:, int(w * 0.66):] = False          # 줄자/화분 띠 제외
    mask[int(h * 0.80):, :] = False          # 삼각대 영역 제외
    mask[: int(h * 0.12), :] = False
    # 소잡음 제거: 3x3 열림
    from scipy import ndimage as ndi
    mask = ndi.binary_opening(mask, structure=np.ones((5, 5)))
    mask = ndi.binary_closing(mask, structure=np.ones((9, 9)))
    lab, n = ndi.label(mask)
    if n == 0:
        return 0, 0.0, mask
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 0.15 * sizes.max()])
    area = int(keep.sum())
    return area, 100.0 * area / (h * w), keep


def load_canopy(save_masks=None):
    """사진 기반 캐노피. 줄자(50 cm를 뺀 길이)의 화소 길이로 날짜별 스케일(px/cm)을 보정해 면적(cm2)을 구한다"""
    from tape2 import tape_len
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "캐노피_잎상추", "*", "*.jpg"))):
        m = re.search(r"(\d{6})_(WDL|WL|DL|CL)_(\d+)\.jpg", base(f))
        date = pd.Timestamp("20" + m.group(1)[:2] + "-" + m.group(1)[2:4] + "-" + m.group(1)[4:])
        code = {"CL": "C", "DL": "D", "WL": "W", "WDL": "WD"}[m.group(2)]
        area, pct, mask = canopy_cover(f)
        tp = tape_len(f)
        rows.append(dict(날짜=date, 처리코드=code, 처리=TRT_CODE[code], 반복=int(m.group(3)), 캐노피면적_px=area, 캐노피비율_pct=pct,
                         줄자길이_px=(tp or {}).get("len_px", np.nan), 원본파일=base(f)))
        if save_masks:
            from PIL import Image
            im = Image.open(f).convert("RGB")
            arr = np.asarray(im).copy()
            arr[mask] = (0.5 * arr[mask] + 0.5 * np.array([0, 255, 255])).astype(np.uint8)
            Image.fromarray(arr).resize((350, 467)).save(os.path.join(save_masks, base(f).replace(".jpg", ".png")))
    d = pd.DataFrame(rows)
    med = d.groupby("날짜")["줄자길이_px"].transform("median")
    ok = (d["줄자길이_px"] - med).abs() / med < 0.05
    d["줄자길이_사용_px"] = np.where(ok, d["줄자길이_px"], med)          # 이상값은 같은 날 중앙값으로 대체
    d["스케일_px_per_cm"] = d["줄자길이_사용_px"] / 50.0
    d["캐노피면적_cm2"] = d["캐노피면적_px"] / d["스케일_px_per_cm"] ** 2
    return d


# ------------------------------------------------------------------ 생육조사
def load_growth():
    """생육조사_잎상추.xlsx (10/7 처리 전 대조구 9개체, 10/23 4처리 × 9개체). 지상부 생체중·건조중은 전체 값, 지하부 건조중은 배지 제외 값 사용(2026-10-27 자료 완성)"""
    f = os.path.join(ROOT, "생육조사_잎상추.xlsx")
    raw = rd(f, header=None)
    d = raw.iloc[2:].copy()
    names = {0: "날짜", 1: "Treatment", 2: "Repeat", 3: "SPAD", 4: "엽장", 5: "엽폭", 6: "엽수", 7: "엽면적", 8: "지상부생체중_TW측정용", 9: "지상부생체중_나머지", 10: "지상부생체중",
             11: "지상부건조중_TW측정용", 12: "지상부건조중_나머지", 13: "지상부건조중_전체", 14: "지하부건조중_배지포함", 15: "지하부건조중", 16: "포화중_TW", 17: "RWC",
             19: "TW_1h", 20: "TW_2h", 21: "TW_22.5h", 22: "TW_25h"}
    d = d[[c for c in names if c in d.columns]].rename(columns=names)
    d["날짜"] = pd.to_datetime(d["날짜"].astype(str).str[:10], errors="coerce")
    d = d[d["날짜"].notna()].copy()
    for c in d.columns:
        if c not in ("날짜", "Treatment"):
            d[c] = pd.to_numeric(d[c], errors="coerce")
    codes = d["Treatment"].map(parse_label)
    d["처리코드"] = [c[0] for c in codes]
    d["처리"] = d["처리코드"].map(TRT_CODE)
    return d.reset_index(drop=True)
