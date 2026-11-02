"""LI-6800 A-Q 곡선 NRH 피팅 → LSP(Q80), LCP, Amax(순) 산출 및 처리별 이원 ANOVA(침수 × 관수) + Tukey.

입력: data/09_LI6800_광곡선_개별점.csv, data/07_AQ_파라미터.csv
출력: intermediate/A_points.csv, fits_flag.csv, lsp_stats.csv

NRH: θ·Ag² − (α·I + Pmax)·Ag + α·I·Pmax = 0, 순광합성 A = Ag − Rd
LSP(Q80): 순광합성이 Amax(순) = Pmax − Rd 의 80%에 도달하는 PPFD (해석해)
LSP 분석 제외: 07_AQ_파라미터의 비고에 '측정 문제'가 있는 곡선(콩 5개)
"""
import warnings
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import curve_fit
from config import DATA, INTER, ORDER
from stats2x2 import tukey_letters, twoway

warnings.filterwarnings('ignore')
d = pd.read_csv(DATA / '09_LI6800_광곡선_개별점.csv')
d['Q'] = d['Qin'].fillna(d['PPFD'])

# 콩 처리 후 A 측정 행에는 원본파일이 비어 있어, 같은 Fs 값을 가진 형광 행과 매칭해 곡선을 식별
fl = d[d['원본파일'].notna() & d['Fs'].notna()][['날짜', '처리', 'Fs', '원본파일']].copy()
fl['k'] = fl['Fs'].round(4)
A = d[d['A'].notna()].copy()
A['curve'] = A['원본파일']
m = A['curve'].isna()
sub = A[m].copy()
sub['cid'] = (sub['Q'] > 1400).cumsum()            # 곡선은 PPFD 1500에서 시작
sub['k'] = sub['Fs'].round(4)
mp = (sub.drop(columns=['원본파일', 'Fs']).merge(fl.drop(columns=['Fs']), on=['날짜', '처리', 'k'], how='left')
      .groupby('cid')['원본파일'].agg(lambda s: s.dropna().unique().tolist()))
sub['curve'] = sub['cid'].map(lambda c: mp[c][0] if len(mp[c]) == 1 else f'?{c}')
A.loc[m, 'curve'] = sub['curve'].values


def nrh(I, a, th, P, Rd):
    x = a * I + P
    return (x - np.sqrt(np.maximum(x * x - 4 * th * a * I * P, 0))) / (2 * th) - Rd


rows = []
for (crop, st, trt, cv), g in A.groupby(['작물', '단계2', '처리', 'curve']):
    I = g['Q'].values; y = g['A'].values
    p0 = [0.05, 0.7, y.max() + 1, max(-y[I < 5].mean(), 0.5) if (I < 5).any() else 1]
    (a, th, P, Rd), _ = curve_fit(nrh, I, y, p0=p0, bounds=([0.001, 0.01, 1, -1], [0.2, 0.999, 80, 6]), maxfev=20000)
    pred = nrh(I, a, th, P, Rd)
    Pg = 0.8 * P + 0.2 * Rd                          # 순광합성 = 0.8·(P − Rd) 가 되는 총광합성
    rows.append(dict(작물=crop, 단계=st, 처리=trt, 곡선=cv, 날짜=g['날짜'].iloc[0], n점=len(I),
                     alpha=a, theta=th, Pgmax=P, Rd=Rd, Amax_net=P - Rd,
                     LSP_Q80=Pg * (P - th * Pg) / (a * (P - Pg)),
                     LCP=Rd * (P - th * Rd) / (a * (P - Rd)),
                     R2=1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum(),
                     RMSE=np.sqrt(((y - pred) ** 2).mean()), A_1500=y[I > 1400].mean()))
r = pd.DataFrame(rows)

p = pd.read_csv(DATA / '07_AQ_파라미터.csv')
p['곡선'] = p['raw파일'].fillna(p['file'])
flag = p[p['비고'].fillna('').str.contains('측정 문제')].set_index('곡선')['비고']
r['제외'] = r['곡선'].map(flag).notna()
r['제외사유'] = r['곡선'].map(flag).fillna('')
r.to_csv(INTER / 'fits_flag.csv', index=False)
A.to_csv(INTER / 'A_points.csv', index=False)

out = []
for crop in ['bean', 'lettuce']:
    s = r[(r.작물 == crop) & (r.단계 == '처리 후') & (~r.제외)]
    pre = r[(r.작물 == crop) & (r.단계 == '처리 전')]
    for v in ['LSP_Q80', 'Amax_net', 'theta', 'alpha', 'Rd', 'LCP']:
        grp = {t: s.loc[s.처리 == t, v].values for t in ORDER}
        L, P_ = tukey_letters(grp)
        tw = twoway(s, v)
        for t in ORDER:
            a = grp[t]
            out.append(dict(작물=crop, 지표=v, 처리=t, 평균=a.mean(), SE=a.std(ddof=1) / np.sqrt(len(a)), n=len(a),
                            Tukey=L[t], ANOVA_P=P_, **tw, 처리전_평균=pre[v].mean(),
                            처리전_SE=pre[v].std(ddof=1) / np.sqrt(len(pre)), 처리전_n=len(pre)))
pd.DataFrame(out).to_csv(INTER / 'lsp_stats.csv', index=False)
print('01 done: LSP fits', len(r))
