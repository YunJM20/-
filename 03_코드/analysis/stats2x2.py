"""통계 공통 함수: 2×2 요인(침수 유무 × 관수 100/50%) 분산분석과 Tukey HSD.

- tukey_letters(groups): 일원 ANOVA P < 0.05일 때만 Tukey-Kramer 문자(a = 평균이 가장 큼), 아니면 모두 'a'
- twoway(df, v): v ~ 침수 * 관수 (Type II) → 침수·관수·상호작용 P
- ancova(df, v): v ~ 처리 + 측정일 + 선형 PAR(Qamb) + 기온(Tair) 모형의 보정 평균(LS mean), 처리 P, Tukey 문자,
                 4처리일 때 v ~ 침수 * 관수 + 측정일 + 선형 PAR(Qamb) + 기온(Tair)의 침수·관수·상호작용 P
"""
import itertools
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import studentized_range
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from patsy import build_design_matrices

ORDER = ['ETc', 'ETc50', '침수ETc', '침수ETc50']
WL = {'ETc': 0, 'ETc50': 0, '침수ETc': 1, '침수ETc50': 1}      # 침수 유무
IR = {'ETc': 100, 'ETc50': 50, '침수ETc': 100, '침수ETc50': 50}  # 관수 수준(%)


def _letters(names, means, sig):
    """sig[(a, b)] = True면 a·b 유의차. 평균 내림차순 연속 구간으로 문자 부여."""
    order = sorted(names, key=lambda k: -means[k]); k = len(order)
    ns = lambda i, j: not sig.get((order[i], order[j]), sig.get((order[j], order[i]), False))
    ranges = []
    for i in range(k):
        j = i
        while j + 1 < k and all(ns(a, b) for a in range(i, j + 2) for b in range(a + 1, j + 2)): j += 1
        if not any(set(range(i, j + 1)) <= set(r) for r in ranges): ranges.append(list(range(i, j + 1)))
    out = {n: '' for n in names}
    for li, r in enumerate(ranges):
        for x in r: out[order[x]] += chr(97 + li)
    return out


def tukey_letters(groups, alpha=0.05):
    names = [k for k in groups if len(groups[k]) > 0]
    vals = {k: np.asarray(groups[k], float) for k in names}
    means = {k: v.mean() for k, v in vals.items()}
    P = stats.f_oneway(*vals.values()).pvalue if len(names) > 1 else np.nan
    if not (P < alpha):
        return {k: 'a' for k in names}, P
    N = sum(len(v) for v in vals.values()); df = N - len(names)
    mse = sum(((v - v.mean()) ** 2).sum() for v in vals.values()) / df
    sig = {}
    for a, b in itertools.combinations(names, 2):
        q = abs(means[a] - means[b]) / np.sqrt(mse / 2 * (1 / len(vals[a]) + 1 / len(vals[b])))
        sig[(a, b)] = studentized_range.sf(q, len(names), df) < alpha
    return _letters(names, means, sig), P


def twoway(df, v, extra=''):
    d = df.assign(W=df['처리'].map(WL), I=df['처리'].map(IR)).dropna(subset=[v])
    m = smf.ols(f'Q("{v}") ~ C(W) * C(I){extra}', d).fit()
    a = anova_lm(m, typ=2)
    return {'침수P': a.loc['C(W)', 'PR(>F)'], '관수P': a.loc['C(I)', 'PR(>F)'], '상호작용P': a.loc['C(W):C(I)', 'PR(>F)']}


def ancova(df, v, alpha=0.05):
    """df: 처리, 날짜, Qamb, v 열. 반환: DataFrame(처리, 보정평균, SE, n, 원평균, 문자) 와 P 사전."""
    d = df[['처리', '날짜', 'Qamb', 'Tair', v]].dropna()
    d = d[d.Qamb > 0].assign(lq=lambda z: z.Qamb, tq=lambda z: z.Tair, y=lambda z: z[v])
    trts = [t for t in ORDER if (d.처리 == t).any()]
    multi = d.날짜.nunique() > 1
    f = 'y ~ C(처리, levels=trts) + lq + tq' + (' + C(날짜)' if multi else '')
    m = smf.ols(f, d).fit()
    # 보정 평균: 모든 측정일 균등 가중, Qamb(선형 PAR)는 전체 평균
    dates = sorted(d.날짜.unique()); lq = d.lq.mean(); tq = d.tq.mean()
    grid = lambda t: pd.DataFrame({'처리': t, '날짜': dates, 'lq': lq, 'tq': tq})
    X = {t: np.asarray(build_design_matrices([m.model.data.orig_exog.design_info], grid(t))[0]).mean(0) for t in trts}
    b, V = m.params.values, m.cov_params().values
    em = {t: X[t] @ b for t in trts}; se = {t: np.sqrt(X[t] @ V @ X[t]) for t in trts}
    # 처리 전체 검정 (Wald F)
    names = [n for n in m.params.index if n.startswith('C(처리')]
    R = np.zeros((len(names), len(b)))
    for i, n in enumerate(names): R[i, list(m.params.index).index(n)] = 1
    Ptrt = float(m.f_test(R).pvalue)
    sig = {}
    for a_, b_ in itertools.combinations(trts, 2):
        c = X[a_] - X[b_]; t = abs(c @ b) / np.sqrt(c @ V @ c)
        sig[(a_, b_)] = studentized_range.sf(t * np.sqrt(2), len(trts), m.df_resid) < alpha if len(trts) > 2 else \
            2 * stats.t.sf(t, m.df_resid) < alpha
    L = _letters(trts, em, sig) if Ptrt < alpha else {t: 'a' for t in trts}
    P = {'처리P': Ptrt, '날짜수': len(dates)}
    if len(trts) == 4:
        P.update(twoway(d, 'y', ' + lq + tq' + (' + C(날짜)' if multi else '')))
    rows = pd.DataFrame([dict(처리=t, 보정평균=em[t], 보정SE=se[t], n=int((d.처리 == t).sum()),
                              원평균=d.loc[d.처리 == t, 'y'].mean(), 문자=L[t]) for t in trts])
    return rows, P
