"""LI-600 gsw·ΦPSII·Fs·ETR: 측정일별 평균·SE·검정과 국면(P1/P2)별 광도 보정 분석.

- 흐린 날 포함 전체 측정일 사용 (CI는 그림 표시용)
- 측정일별(PAR·기온 보정 개체값): 일원 ANOVA, 대조 vs 침수 Welch t → 같은 작물·지표 안에서 측정일 수만큼 Holm 보정
- 국면별: 모든 처리가 측정된 날만 사용(config.common_days),
          v ~ 처리 + 측정일 + 선형 PAR(Qamb) + 기온(Tair) 보정 평균·Tukey 문자, 4처리면 침수×관수 상호작용 P
출력: intermediate/daily_stats.csv (시계열 그래프용), phase_stats.csv (국면별 표)
"""
import warnings
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from config import INTER, ORDER, PHASE_END, load_li600, common_days
from stats2x2 import ancova

warnings.filterwarnings('ignore')
x = load_li600()
COLS = {'gsw': 'gsw_해석용(0 이하 제외)', 'phi': 'PhiPS2', 'fs': 'Fs', 'etr': 'ETR'}

import statsmodels.formula.api as smf
daily = []
x = x[(x.Qamb > 0)].dropna(subset=['Tair']).copy()
x['cell'] = x['날짜'].astype(str) + '_' + x['처리']
ADJ = {}
for crop in ['bean', 'lettuce']:
    xc = x[x.작물 == crop]
    for ind, c in COLS.items():
        d = xc.dropna(subset=[c])
        m = smf.ols(f'Q("{c}") ~ C(cell) + Qamb + Tair', d).fit()
        b1, b2 = m.params['Qamb'], m.params['Tair']
        ADJ[(crop, ind)] = (b1, b2, d.Qamb.mean(), d.Tair.mean())
for ind, c in COLS.items():
    x[c + '_raw'] = x[c]
    for crop in ['bean', 'lettuce']:
        b1, b2, qb, tb = ADJ[(crop, ind)]
        k = x.작물 == crop
        x.loc[k, c] = x.loc[k, c] + b1 * (qb - x.loc[k, 'Qamb']) + b2 * (tb - x.loc[k, 'Tair'])
pd.DataFrame([dict(작물=k[0], 지표=k[1], b_Qamb=v[0], b_Tair=v[1], Qamb평균=v[2], Tair평균=v[3]) for k, v in ADJ.items()]).to_csv(INTER / 'daily_adj_coef.csv', index=False)
for (crop, dat, date), g in x.groupby(['작물', 'DAT', '날짜']):
    for ind, c in COLS.items():
        trts = [t for t in ORDER if (g.처리 == t).any()]
        grs = [g.loc[g.처리 == t, c].dropna() for t in trts]
        raws = [g.loc[g.처리 == t, c + '_raw'].dropna() for t in trts]
        p = stats.f_oneway(*grs).pvalue if len(grs) > 1 else np.nan
        pw = stats.ttest_ind(grs[0], grs[trts.index('침수ETc')], equal_var=False).pvalue if '침수ETc' in trts else np.nan
        for t, a, r_ in zip(trts, grs, raws):
            daily.append(dict(지표=ind, 작물=crop, DAT=dat, 날짜=date, CI=g.CI.iloc[0], 흐림=g.흐림.iloc[0], 처리=t,
                              평균=a.mean(), SE=a.sem(), 원평균=r_.mean(), 원SE=r_.sem(), n=len(a), Qamb=g.loc[g.처리 == t, 'Qamb'].mean(),
                              Tair=g.loc[g.처리 == t, 'Tair'].mean(), 당일_ANOVA_P=p, 침수vs대조_P=pw))
daily = pd.DataFrame(daily)
for col_ in ['당일_ANOVA_P', '침수vs대조_P']:
    daily[col_ + '_Holm'] = np.nan
    for (ind, crop), g in daily.groupby(['지표', '작물']):
        u = g.drop_duplicates('DAT').dropna(subset=[col_])
        adj = dict(zip(u.DAT, multipletests(u[col_], method='holm')[1]))
        daily.loc[g.index, col_ + '_Holm'] = g.DAT.map(adj)
daily.to_csv(INTER / 'daily_stats.csv', index=False)

out = []
for crop in ['bean', 'lettuce']:
    base = x[(x.작물 == crop) & (x.DAT >= 1)]
    for per, s in [('P1', base[base.DAT <= PHASE_END[crop]]), ('P2', base[base.DAT > PHASE_END[crop]])]:
        s = common_days(s)
        days = ','.join(str(int(v)) for v in sorted(s.DAT.unique()))
        for ind, c in COLS.items():
            r, P = ancova(s, c)
            for _, row in r.iterrows():
                out.append(dict(지표=ind, 작물=crop, 국면=per, **row.to_dict(), **P, 포함DAT=days))
pd.DataFrame(out).to_csv(INTER / 'phase_stats.csv', index=False)
print('00 done')
