"""생육(파괴조사)과 A-Ci·A-Q 파라미터: 2×2 이원 ANOVA(침수 × 관수) + Tukey HSD.

- 콩 지상부 총 건물중 = 잎 + 줄기 + 꼬투리 + 종실 D.W, 생식기관 건물중 = 꼬투리 + 종실 D.W
- Tukey 문자는 일원 ANOVA P < 0.05일 때만 부여(아니면 모두 a)
- A-Ci·A-Q 처리 후 곡선: 콩은 9월 '선택적 데이터'(9/2~9/17), 상추 10/16~10/19, 제외 표시 곡선 제외
출력: intermediate/growth_stats.csv, param_stats.csv
"""
import warnings
import numpy as np
import pandas as pd
from config import DATA, INTER, ORDER
from stats2x2 import tukey_letters, twoway

warnings.filterwarnings('ignore')


def summarize(df, v, keys):
    grp = {t: df.loc[df.처리 == t, v].dropna().values for t in ORDER}
    L, P = tukey_letters(grp)
    tw = twoway(df[df[v].notna()], v)
    return [dict(**keys, 처리=t, 평균=a.mean(), SE=a.std(ddof=1) / np.sqrt(len(a)), n=len(a), 대조구대비=a.mean() / grp['ETc'].mean() * 100,
                 Tukey=L[t], ANOVA_P=P, **tw) for t, a in grp.items()]


# ---------------- 생육
b = pd.read_csv(DATA / '10_생육_밭콩_파괴조사.csv').rename(columns={'Treatment': '처리'})
b['잎줄기FW'] = b['지상부FW(잎+줄기)']; b['잎줄기DW'] = b['지상부DW(잎+줄기)']
b['생식기관DW'] = b['꼬투리 D.W'] + b['알 D.W']
b['종실DW'] = b['알 D.W']
b['지상부총DW'] = b['잎줄기DW'] + b['생식기관DW']
b['뿌리DW'] = b['뿌리 D.W']
l = pd.read_csv(DATA / '11_생육_잎상추.csv')
l['처리'] = l['처리'].map({'대조구': 'ETc', '건조': 'ETc50', '침수': '침수ETc', '복합': '침수ETc50'})
l = l[l.날짜 == '2026-10-23']

rows = []
for date, dat in [('2026-09-01', 20), ('2026-10-06', 55)]:
    s = b[b.날짜 == date]
    for v in ['지상부총DW', '생식기관DW', '종실DW', '잎줄기FW', '잎줄기DW', '뿌리DW', 'SPAD', '꼬투리 수', '알 수']:
        rows += summarize(s, v, dict(작물='bean', DAT=dat, 지표=v))
for v in ['지상부생체중', '지상부건조중_전체', '엽면적', '엽수', '지하부건조중', 'SPAD', 'RWC']:
    rows += summarize(l, v, dict(작물='lettuce', DAT=16, 지표=v))
pd.DataFrame(rows).to_csv(INTER / 'growth_stats.csv', index=False)

# ---------------- A-Ci·A-Q 파라미터
def postf(df):
    df = df.copy(); df['date'] = df['date'].astype(str)
    p_ = df[df.단계.str.replace(' ', '') == '처리후']
    # 콩: 9월 파라미터 엑셀 '선택적 데이터' 시트(9/2~9/17)만 사용, 8월 A-Ci(8/19~8/21)는 측정 시기가 달라 제외
    p_ = p_[((p_.작물 == 'bean') & (p_.date >= '2026-09-01')) | ((p_.date >= '2026-10-16') & (p_.date <= '2026-10-19'))]
    return p_[p_['제외'] != True]


aci = postf(pd.read_csv(DATA / '06_ACi_파라미터.csv')); aq = postf(pd.read_csv(DATA / '07_AQ_파라미터.csv'))
rows = []
for crop in ['bean', 'lettuce']:
    for v, df in [('Vcmax', aci), ('Jmax', aci), ('Rd', aci), ('Amax', aq), ('alpha', aq)]:
        rows += summarize(df[df.작물 == crop], v, dict(작물=crop, 파라미터=v))
pd.DataFrame(rows).to_csv(INTER / 'param_stats.csv', index=False)
print('05 done')
