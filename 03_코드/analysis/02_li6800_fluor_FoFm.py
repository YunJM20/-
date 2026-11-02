"""LI-6800 광도별 형광 지표를 두 가지 Fo·Fm 대입 방식으로 계산.

  trt  : 처리별 평균 Fo·Fm (09 CSV에 들어 있는 값; 콩 9/28, 상추 10/27 암적응)
  pool : 작물별 4처리 평균 Fo·Fm (처리 전 곡선에도 같은 값 적용)

입력: data/09_LI6800_광곡선_개별점.csv
출력: intermediate/fluor_summary_{trt,pool}.csv (PPFD별 평균·SE), fluor_minP_{trt,pool}.csv (PPFD별 ANOVA 최소 P)
수식: NPQ=Fm/Fm'−1, Fo'=Fo/(Fv/Fm+Fo/Fm'), qP=(Fm'−Fs)/(Fm'−Fo'), qL=qP·Fo'/Fs,
      ΦNO=1/(NPQ+1+qL(Fm/Fo−1)), ΦNPQ=1−ΦPSII−ΦNO, ETR=ΦPSII·PPFD·0.84·0.5
"""
import warnings
import pandas as pd
from scipy import stats
from config import DATA, INTER, ORDER

warnings.filterwarnings('ignore')
d = pd.read_csv(DATA / '09_LI6800_광곡선_개별점.csv')
d = d[d['원본파일'].notna() & d["Fm'"].notna() & d['Fo'].notna()].copy()
d['Q'] = d['Qin'].fillna(d['PPFD']).round(-1)
d = d[d['Q'] >= 40]
# 통합값 = 작물별 처리 후 4처리 평균 Fo·Fm의 평균
POOL = {c: tuple(d[(d.작물 == c) & (d.단계2 == '처리 후')].groupby('처리')[['Fo', 'Fm']].first().mean()) for c in ['bean', 'lettuce']}
print('pooled Fo, Fm:', {k: tuple(round(v, 2) for v in vv) for k, vv in POOL.items()})


def calc(df, Fo, Fm):
    Fs = df['Fs']; Fmp = df["Fm'"]; Fop = Fo / ((Fm - Fo) / Fm + Fo / Fmp)
    o = pd.DataFrame(index=df.index)
    o['NPQ'] = Fm / Fmp - 1
    o['PhiPS2'] = (Fmp - Fs) / Fmp
    o['qP'] = (Fmp - Fs) / (Fmp - Fop)
    o['qL'] = o['qP'] * Fop / Fs
    o['PhiNO'] = 1 / (o['NPQ'] + 1 + o['qL'] * (Fm / Fo - 1))
    o['PhiNPQ'] = 1 - o['PhiPS2'] - o['PhiNO']
    o['ETR'] = o['PhiPS2'] * df['Q'] * 0.84 * 0.5
    return o


METS = ['qP', 'NPQ', 'ETR', 'PhiPS2', 'PhiNPQ', 'PhiNO', 'qL']
for mode in ['trt', 'pool']:
    parts = []
    for crop in ['bean', 'lettuce']:
        x = d[d['작물'] == crop]
        Fo, Fm = (x['Fo'], x['Fm']) if mode == 'trt' else POOL[crop]
        parts.append(calc(x, Fo, Fm).join(x[['작물', '단계2', '처리', 'Q', '원본파일']]))
    c = pd.concat(parts)
    post = c[c['단계2'] == '처리 후']
    rows = []
    for crop in ['bean', 'lettuce']:
        for m in METS:
            ps = [(stats.f_oneway(*[g.loc[g['처리'] == t, m].dropna() for t in ORDER]).pvalue, q)
                  for q, g in post[post['작물'] == crop].groupby('Q')]
            pmin, q = min(ps)
            rows.append(dict(작물=crop, 지표=m, minP=pmin, PPFD=q, 유의수=sum(pp < 0.05 for pp, _ in ps)))
    c.groupby(['작물', '단계2', '처리', 'Q'])[METS].agg(['mean', 'sem', 'count']).to_csv(INTER / f'fluor_summary_{mode}.csv')
    pd.DataFrame(rows).to_csv(INTER / f'fluor_minP_{mode}.csv', index=False)
print('02 done')
