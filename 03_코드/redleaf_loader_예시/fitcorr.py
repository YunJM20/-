# -*- coding: utf-8 -*-
import glob, os
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from lio import *
G = os.path.join(ROOT, "gsw, 형광", "gsw보정")
rows = []
for f in sorted(glob.glob(os.path.join(G, "*.xlsx"))):
    d = rd(f)
    d["src"] = base(f)
    rows.append(d)
d = pd.concat(rows)
d = d[np.isfinite(d["gsw"]) & np.isfinite(d["gsw_corrected"])]
print(len(d), d["gsw"].describe().to_dict())
x, y = d["gsw"].values, d["gsw_corrected"].values
mm = lambda g, A, B: A * g / (B + g)
p, _ = curve_fit(mm, x, y, p0=[1.8, 1.7])
res = y - mm(x, *p)
print("MM", p, "rmse", np.sqrt((res ** 2).mean()), "R2", 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum())
# 선형/2차
for deg in (1, 2, 3):
    c = np.polyfit(x, y, deg)
    r = y - np.polyval(c, x)
    print(deg, c, np.sqrt((r ** 2).mean()))
d["ratio"] = d["gsw_corrected"] / d["gsw"]
print(d.groupby("src")["ratio"].describe())
print(d.sort_values("gsw").iloc[::25][["gsw", "gsw_corrected", "VPDleaf", "Tleaf", "src"]].to_string())
# 이상치
d["res"] = res
print(d.loc[d["res"].abs().sort_values(ascending=False).index[:10], ["gsw", "gsw_corrected", "res", "src", "Treatment"]])
