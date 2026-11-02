# -*- coding: utf-8 -*-
"""LI-600 측정 시각의 일사(온실 외부 SW) 기반 흐린 날 판정.
맑음 지수 CI = 측정 구간 평균 SW / 같은 시각대(±30분)의 ±10일 90분위수 SW(맑은 날 포락선). 둘 다 SW는 온실 외부 일사계."""
import sys, os
import numpy as np
import pandas as pd
sys.path.insert(0, r"C:\Users\yunjm\pptwork\cmp")
sys.path.insert(0, r"C:\Users\yunjm\pptwork\lettuce")
import cmp_data as cd
import lettuce_data as LD

OUT = os.path.join(cd.OUTDIR, "cloud.csv")


def env_bean():
    e = cd.gc.read_sheet("8_환경데이터")
    e["시간"] = pd.to_datetime(e["시간"])
    return e.set_index("시간")["SWUpper_Avg"].astype(float).sort_index()


def env_let():
    e = LD.load_env()
    return e.set_index("시간")["SW"].astype(float).sort_index()


def clear_env(sw, t0, t1, day):
    """day의 같은 시각대 맑은 날 포락선"""
    vals = []
    for k in range(-10, 11):
        d = day + pd.Timedelta(days=k)
        seg = sw[(sw.index >= d + (t0 - day) - pd.Timedelta(minutes=30)) & (sw.index <= d + (t1 - day) + pd.Timedelta(minutes=30))]
        if len(seg):
            vals.append(seg.mean())
    return np.nanpercentile(vals, 90) if vals else np.nan


def windows(df, tcol, datecol):
    out = []
    for day, sub in df.groupby(datecol):
        ts = pd.to_datetime(sub[tcol].astype(str).str.strip(), format="%H:%M:%S", errors="coerce").dropna()
        if ts.empty:
            continue
        s = ts.dt.hour * 3600 + ts.dt.minute * 60 + ts.dt.second
        out.append((pd.Timestamp(day).normalize(), pd.Timedelta(seconds=float(s.min())), pd.Timedelta(seconds=float(s.max()))))
    return out


def run():
    D = cd.load_all()
    rows = []
    for sp, sw, df in (("bean", env_bean(), D["bean_li"]), ("let", env_let(), D["let_li"])):
        dcol = "날짜"
        tcol = "Time"
        for day, a, b in windows(df, tcol, dcol):
            t0, t1 = day + a - pd.Timedelta(minutes=15), day + b + pd.Timedelta(minutes=15)
            seg = sw[(sw.index >= t0) & (sw.index <= t1)]
            ref = clear_env(sw, day + a, day + b, day)
            rows.append(dict(species=sp, date=day, start=str((day + a).time())[:5], end=str((day + b).time())[:5], sw_mean=float(seg.mean()) if len(seg) else np.nan,
                             sw_cv=float(seg.std() / seg.mean()) if len(seg) and seg.mean() > 0 else np.nan, sw_ref=ref, n=len(seg)))
    r = pd.DataFrame(rows)
    r["CI"] = r["sw_mean"] / r["sw_ref"]
    r.to_csv(OUT, index=False, encoding="utf-8-sig")
    return r


if __name__ == "__main__":
    r = run()
    pd.set_option("display.width", 200)
    print(r.round(2).to_string())
