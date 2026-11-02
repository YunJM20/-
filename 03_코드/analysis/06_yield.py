"""수확량 비교 (콩_vs_상추_비교.pptx 수확량 슬라이드).

상추: 수확 시 지상부 생체중·건물중 (10/23, DAT 16)
콩:   10/6(DAT 55, R6~R7) 파괴 조사의 종실 건물중, 종실 수, 꼬투리 수, 100립 건물중(= 20립 샘플 종실 D.W ÷ 종실 수 × 100)
통계: 이원 ANOVA(침수 × 관수) + Tukey(일원 ANOVA P<0.05일 때만 문자)
출력: intermediate/yield_stats.csv, figures/yield.png
"""
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from config import DATA, INTER, FIG, ORDER
from stats2x2 import tukey_letters, twoway

warnings.filterwarnings('ignore')
b = pd.read_csv(DATA / '10_생육_밭콩_파괴조사.csv').rename(columns={'Treatment': '처리'})
b = b[b.날짜 == '2026-10-06'].copy()
b['종실DW'] = b['알 D.W']; b['종실수'] = b['알 수']; b['꼬투리수'] = b['꼬투리 수']
b['백립중'] = b['20 알 D.W'] / b['20 알 수'] * 100
l = pd.read_csv(DATA / '11_생육_잎상추.csv')
l = l[l.날짜 == '2026-10-23'].copy()
l['처리'] = l['처리'].map({'대조구': 'ETc', '건조': 'ETc50', '침수': '침수ETc', '복합': '침수ETc50'})

ITEMS = [('lettuce', l, '지상부생체중', 'Shoot FW', 'g·plant$^{-1}$'), ('lettuce', l, '지상부건조중_전체', 'Shoot DW', 'g·plant$^{-1}$'),
         ('bean', b, '종실DW', 'Seed DW', 'g·plant$^{-1}$'), ('bean', b, '종실수', 'Seed no.', 'plant$^{-1}$'),
         ('bean', b, '꼬투리수', 'Pod no.', 'plant$^{-1}$'), ('bean', b, '백립중', '100-seed DW', 'g')]
rows = []
for crop, df, v, lab, unit in ITEMS:
    grp = {t: df.loc[df.처리 == t, v].dropna().values for t in ORDER}
    L, P = tukey_letters(grp); tw = twoway(df, v)
    for t in ORDER:
        a = grp[t]
        rows.append(dict(작물=crop, 지표=v, 라벨=lab, 단위=unit, 처리=t, 평균=a.mean(), SE=a.std(ddof=1) / np.sqrt(len(a)), n=len(a),
                         대조구대비=a.mean() / grp['ETc'].mean() * 100, Tukey=L[t], ANOVA_P=P, **tw))
st = pd.DataFrame(rows)
st.to_csv(INTER / 'yield_stats.csv', index=False)

# ---------------- figure
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.linewidth': 0.8, 'legend.frameon': False})
CROPC = {'lettuce': {'ETc': '#1F3D2B', 'ETc50': '#8FAA91', '침수ETc': '#2E7D4F', '침수ETc50': '#9FD3A8'},
         'bean': {'ETc': '#3B2618', 'ETc50': '#B9A28C', '침수ETc': '#8B5A2B', '침수ETc50': '#E0B98A'}}
ACC = {'lettuce': '#2E6B3F', 'bean': '#6B4226'}
FILLED = {'ETc': True, 'ETc50': False, '침수ETc': True, '침수ETc50': False}
HATCH = {'ETc': None, 'ETc50': None, '침수ETc': '////', '침수ETc50': '////'}
NAME = {'ETc': 'Control', 'ETc50': 'Drought', '침수ETc': 'Waterlogging', '침수ETc50': 'Combined'}
fig, axs = plt.subplots(1, 6, figsize=(7.7, 2.15), dpi=300)
for ax, (crop, _, v, lab, unit) in zip(axs, ITEMS):
    s = st[(st.작물 == crop) & (st.지표 == v)].set_index('처리')
    top = (s.평균 + s.SE).max()
    for k, t in enumerate(ORDER):
        c = CROPC[crop][t]
        ax.bar(k, s.loc[t, '평균'], 0.72, color=c if FILLED[t] else 'white', edgecolor=c, lw=1.2, hatch=HATCH[t])
        ax.errorbar(k, s.loc[t, '평균'], s.loc[t, 'SE'], color='0.25', capsize=2, lw=0.8)
        if s.ANOVA_P.iloc[0] < 0.05:
            ax.text(k, s.loc[t, '평균'] + s.loc[t, 'SE'] + top * 0.03, s.loc[t, 'Tukey'], ha='center', va='bottom', fontsize=7.5)
    P = s.ANOVA_P.iloc[0]
    ax.set_ylim(0, top * 1.22); ax.set_xticks([])
    ax.set_title(lab, fontsize=8, loc='center', color=ACC[crop], fontweight='bold')
    ax.set_ylabel(unit, fontsize=7, labelpad=1); ax.tick_params(labelsize=6.5)
    ax.set_xlabel('P<0.001' if P < 0.001 else ('P=%.3f' % P if P < 0.01 else 'P=%.2f' % P), fontsize=7, color='0.3')
fig.text(0.2, 0.84, 'Lettuce (DAT 16, harvest)', ha='center', fontsize=8, color=ACC['lettuce'], fontweight='bold')
fig.text(0.66, 0.84, 'Soybean (DAT 55, R6–R7)', ha='center', fontsize=8, color=ACC['bean'], fontweight='bold')
from matplotlib.patches import Patch
from matplotlib.legend_handler import HandlerTuple
hs = [tuple(Patch(facecolor=CROPC[c][t] if FILLED[t] else 'white', edgecolor=CROPC[c][t], hatch=HATCH[t], lw=1.1) for c in ['lettuce', 'bean']) for t in ORDER]
fig.legend(hs, [NAME[t] for t in ORDER], loc='upper center', ncol=4, fontsize=7.5, handler_map={tuple: HandlerTuple(ndivide=None, pad=0.3)},
           handlelength=2.6, columnspacing=1.4, bbox_to_anchor=(0.5, 1.0))
fig.tight_layout(rect=(0, 0, 1, 0.83), w_pad=0.6)
fig.savefig(FIG / 'yield.png'); plt.close(fig)
print('06 done')
