"""발표 슬라이드용 그래프 전체 생성 (figures/*.png).

색: 작물별 계열(상추 초록, 콩 갈색). 관수량 100% = 진한 색, 50% = 연한 색.
    침수·복합 = 사각형 마커 + 점선, 50% 관수 = 속이 빈 마커. 범례는 그림 상단 가운데.
입력: data/*.csv 와 intermediate/*.csv (01~03 스크립트 결과)

출력 ↔ 슬라이드
  ts_gsw.png 8, recovery.png 9, ts_phi.png 10, li600_npq.png 11, params.png 12, growth.png 13,
  check.png 7, fluor_trt.png A1, fluor_pool.png A2, lsp.png A3, ts_fs.png A4, ts_etr.png A5
"""
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerTuple
from config import DATA, INTER, FIG

warnings.filterwarnings('ignore')
D = str(DATA) + '/'
P = L = str(INTER) + '/'
O = str(FIG) + '/'

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.linewidth': 0.8, 'xtick.major.width': 0.8, 'ytick.major.width': 0.8, 'legend.frameon': False,
                     'axes.titlesize': 9.5, 'axes.titleweight': 'bold', 'axes.titlelocation': 'left'})
ORDER = ['ETc', 'ETc50', '침수ETc', '침수ETc50']
NAME = {'ETc': 'Control', 'ETc50': 'Drought', '침수ETc': 'Waterlogging', '침수ETc50': 'Combined'}
SHORT = {'ETc': 'Control', 'ETc50': 'Drought', '침수ETc': 'Waterlog.', '침수ETc50': 'Combined'}
NEU = {'ETc': '#3A3A3A', 'ETc50': '#A39A8C'}
CROPC = {'lettuce': {'ETc': '#1F3D2B', 'ETc50': '#8FAA91', '침수ETc': '#2E7D4F', '침수ETc50': '#9FD3A8'},
         'bean': {'ETc': '#3B2618', 'ETc50': '#B9A28C', '침수ETc': '#8B5A2B', '침수ETc50': '#E0B98A'}}
ACC = {'lettuce': '#2E6B3F', 'bean': '#6B4226'}
CROPN = {'lettuce': 'Lettuce', 'bean': 'Soybean'}
MK = {'ETc': 'o', 'ETc50': 'o', '침수ETc': 's', '침수ETc50': 's'}
FILLED = {'ETc': True, 'ETc50': False, '침수ETc': True, '침수ETc50': False}
LS = {'ETc': '-', 'ETc50': '-', '침수ETc': (0, (4, 1.6)), '침수ETc50': (0, (4, 1.6))}
PREC = '#9A9A9A'


def col(crop, t):
    return CROPC[crop][t]


def handle(crop, t, line=True):
    c = col(crop, t)
    return Line2D([], [], color=c, lw=1.6 if line else 0, ls=LS[t] if line else 'none', marker=MK[t], ms=5.5,
                  mfc=c if FILLED[t] else 'white', mec=c, mew=1.3)


CLOUDC = '#E9E9E9'


def top_legend(fig, line=True, pre=True, crops=('lettuce', 'bean'), y=1.0, ncol=None, cloudy=False):
    hs, ls = [], []
    for t in ORDER:
        hs.append(tuple(handle(c, t, line) for c in crops))
        ls.append(NAME[t])
    if pre:
        hs.append(Line2D([], [], color=PREC, lw=1.2 if line else 0, ls='--' if line else 'none', marker='x', ms=5))
        ls.append('Pre-treatment')
    if cloudy:
        from matplotlib.patches import Patch
        hs.append(Patch(color=CLOUDC)); ls.append('Cloudy (CI<0.5)')
    fig.legend(hs, ls, loc='upper center', bbox_to_anchor=(0.5, y), ncol=ncol or len(ls), fontsize=8,
               handler_map={tuple: HandlerTuple(ndivide=None, pad=0.3)}, handlelength=3.2, columnspacing=1.6)


def box_strip(ax, x, vals, c, filled, w=0.62):
    vals = np.asarray(vals, float); vals = vals[~np.isnan(vals)]
    if len(vals) >= 4:
        bp = ax.boxplot([vals], positions=[x], widths=w, patch_artist=True, showfliers=False,
                        medianprops={'color': c, 'lw': 1.4}, whiskerprops={'color': c, 'lw': 1},
                        capprops={'color': c, 'lw': 1}, boxprops={'lw': 1, 'edgecolor': c})
        bp['boxes'][0].set_facecolor(c); bp['boxes'][0].set_alpha(0.22 if filled else 0.10)
    else:
        m = vals.mean(); se = vals.std(ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0
        ax.errorbar(x, m, se, fmt='_', color=c, ms=18, mew=1.6, capsize=3, lw=1.1, zorder=3)
    rng = np.random.default_rng(1)
    jit = rng.uniform(-w * 0.28, w * 0.28, len(vals))
    ax.scatter(x + jit, vals, s=13, color=c if filled else 'white', edgecolor=c, lw=0.9, zorder=4)
    return vals.max() if len(vals) else np.nan


# ------------------------------------------------------------------ time series (gsw, phi, fs, etr)
A04 = pd.read_csv(L + 'daily_stats.csv')   # 00_li600_daily_phase.py 결과 (흐린 날 포함 전체, Holm 보정 P)
PRE = pd.read_csv(D + '02b_LI600_처리전_개별측정.csv')
PRECOL = {'gsw': 'gsw_해석용', 'phi': 'PhiPS2', 'fs': 'Fs', 'etr': 'ETR'}


def ts_fig(ind, ylab, fname, size=(7.5, 2.8)):
    fig, axs = plt.subplots(1, 2, figsize=size, dpi=300, gridspec_kw={'width_ratios': [1.25, 1]})
    for ax, crop in zip(axs, ['bean', 'lettuce']):
        s = A04[(A04.지표 == ind) & (A04.작물 == crop)]
        ax.axvspan(0, 3, color='#E6E6E6', lw=0, zorder=0)
        for d in s[s.흐림 == True].DAT.unique():
            ax.axvspan(d - 0.45, d + 0.45, color=CLOUDC, lw=0, zorder=0)
        for t in ORDER:
            g = s[s.처리 == t].sort_values('DAT')
            if g.empty: continue
            c = col(crop, t)
            ax.fill_between(g.DAT, g.평균 - g.SE, g.평균 + g.SE, color=c, alpha=0.16, lw=0)
            ax.plot(g.DAT, g.평균, color=c, ls=LS[t], lw=1.5, marker=MK[t], ms=4.2, mfc=c if FILLED[t] else 'white', mec=c, mew=1.1)
        pr = PRE[PRE.작물 == crop][PRECOL[ind]].dropna()
        px = -5 if crop == 'bean' else -1.5
        ax.errorbar(px, pr.mean(), pr.sem(), fmt='x', color=PREC, ms=5, capsize=2, lw=1)
        ymax = (s.평균 + s.SE).max(); ymin = (s.평균 - s.SE).min()
        ymax = max(ymax, pr.mean() + pr.sem()); ymin = min(ymin, pr.mean() - pr.sem())
        span = ymax - ymin
        for d, g in s.groupby('DAT'):
            if g['당일_ANOVA_P_Holm'].iloc[0] < 0.05:
                ax.text(d, (g.평균 + g.SE).max() + span * 0.04, '*', ha='center', va='bottom', fontsize=10, color='0.2')
        ax.set_ylim(ymin - span * 0.05, ymax + span * 0.2)
        bnd = 9.5 if crop == 'bean' else 10.5   # 침수 종료 후 7일 경계
        ax.axvline(bnd, color='0.55', ls=':', lw=1, zorder=1)
        ax.text(bnd - 0.8, ax.get_ylim()[0], 'P1', ha='right', va='bottom', fontsize=8, color='0.4')
        ax.text(bnd + 0.8, ax.get_ylim()[0], 'P2', ha='left', va='bottom', fontsize=8, color='0.4')
        ax.set_title(CROPN[crop], color=ACC[crop])
        ax.set_xlabel('Days after waterlogging start (DAT)')
        if crop == 'bean': ax.set_ylabel(ylab)
    top_legend(fig, line=True, pre=True, cloudy=True)
    fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=1.5)
    fig.savefig(O + fname); plt.close(fig)


ts_fig('gsw', 'g$_{sw}$ (mol·m$^{-2}$·s$^{-1}$)', 'ts_gsw.png')
ts_fig('phi', 'Φ$_{PSII}$', 'ts_phi.png')
ts_fig('fs', 'F$_s$', 'ts_fs.png', size=(7.52, 2.8))
ts_fig('etr', 'ETR (µmol·m$^{-2}$·s$^{-1}$)', 'ts_etr.png', size=(7.52, 2.8))

# ------------------------------------------------------------------ recovery ratio
a = A04[A04.지표 == 'gsw']
fig, ax = plt.subplots(figsize=(7.7, 3.5), dpi=300)
ax.axvspan(0, 3, color='#E6E6E6', lw=0); ax.text(1.5, 182, 'Water-\nlogging\n(3 d)', ha='center', va='top', fontsize=6.5, color='0.35')
for d in a[a.흐림 == True].DAT.unique():
    ax.axvspan(d - 0.4, d + 0.4, color=CLOUDC, lw=0, zorder=0)
ax.axhline(100, color='0.45', lw=0.8, ls='--'); ax.text(52.5, 103, 'Control = 100%', fontsize=7.5, color='0.4', ha='right', va='bottom')
res = {}
for crop in ['bean', 'lettuce']:
    g = a[a.작물 == crop].pivot_table(index='DAT', columns='처리', values='평균')
    r = (g['침수ETc'] / g['ETc'] * 100).dropna(); res[crop] = r; c = ACC[crop]
    x = r.index.values; y = r.values
    if crop == 'bean':
        e = x <= 9
        ax.plot(x[e], y[e], '-s', color=c, ms=5, lw=1.8, zorder=3)
        ax.plot([9, 17], [r[9], r[17]], ':', color=c, lw=1.4)   # DAT 10~16 측정 없음
        ax.plot(x[~e], y[~e], '-s', color=c, ms=5, lw=1.8, zorder=3)
    else:
        ax.plot(x, y, '-s', color=c, ms=5, lw=1.8, zorder=3)
        for d in (7, 8): ax.plot([d], [r[d]], 's', ms=5, mfc='white', mec=c, mew=1.3, zorder=4)
    q = a[(a.작물 == crop) & (a.처리 == 'ETc')].set_index('DAT')['침수vs대조_P_Holm']
    for d in x:
        if q.get(d, 1) < 0.05:
            ax.text(d, r[d] - 15, '*', ha='center', color=c, fontsize=11, fontweight='bold')
ax.annotate(f"DAT 9: {res['bean'][9]:.0f}%\n(not recovered)", xy=(9, res['bean'][9]), xytext=(11.5, 22), fontsize=8, color=ACC['bean'], arrowprops=dict(arrowstyle='->', color=ACC['bean'], lw=1))
ax.annotate('Recovered by\nDAT 7–8', xy=(8, res['lettuce'][8]), xytext=(3.6, 145), fontsize=8, color=ACC['lettuce'], arrowprops=dict(arrowstyle='->', color=ACC['lettuce'], lw=1))
ax.annotate(f"DAT 23: {res['bean'][23]:.0f}%", xy=(23, res['bean'][23]), xytext=(25, 135), fontsize=8, color=ACC['bean'], arrowprops=dict(arrowstyle='->', color=ACC['bean'], lw=1))
ax.set_xlim(-1, 53); ax.set_ylim(0, 185)
ax.set_xlabel('Days after waterlogging start (DAT)'); ax.set_ylabel('g$_{sw}$ of waterlogged plants\n(% of control)')
from matplotlib.patches import Patch
hs = [Line2D([], [], color=ACC[c], marker='s', lw=1.8, ms=5) for c in ['lettuce', 'bean']] + [Patch(color=CLOUDC)]
fig.legend(hs, ['Lettuce', 'Soybean', 'Cloudy (CI<0.5)'], loc='upper center', ncol=3, fontsize=8.5, bbox_to_anchor=(0.5, 1.0))
fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(O + 'recovery.png'); plt.close(fig)

# ------------------------------------------------------------------ LI-600 NPQ / PhiNO box+strip
pts = pd.read_csv(P + 'li600_fluor_points.csv'); per = pd.read_csv(P + 'li600_fluor_period.csv')
fig, axs = plt.subplots(2, 2, figsize=(7.5, 4.3), dpi=300)
for j, crop in enumerate(['bean', 'lettuce']):
    for i, (m, yl) in enumerate([('NPQ', 'NPQ'), ('PhiNO', 'Φ$_{NO}$')]):
        ax = axs[i, j]; pos = 0; ticks = []; tops = []
        for pr_ in ['P1', 'P2']:
            q = per[(per.작물 == crop) & (per.지표 == m) & (per.구간 == pr_)].set_index('처리')
            days = [int(v) for v in str(q['포함DAT'].iloc[0]).split(',')]
            s = pts[(pts.작물 == crop) & (pts.단계 == '처리 후') & (pts.DAT.isin(days))]
            start = pos
            for t in ORDER:
                if t not in q.index: continue
                top = box_strip(ax, pos, s.loc[s.처리 == t, m].values, col(crop, t), FILLED[t])
                tops.append((pos, top, q.loc[t, '문자'])); pos += 1
            P_ = q.처리P.iloc[0]
            ticks.append(((start + pos - 1) / 2, {'P1': 'P1', 'P1b': 'P1 (4 trt.)', 'P2': 'P2'}[pr_] + '\n(' + ('P<0.001' if P_ < 0.001 else 'P=%.3f' % P_) + ')'))
            pos += 0.8
        ymax = max(t_[1] for t_ in tops); ymin = ax.get_ylim()[0]
        for x_, top, lt in tops: ax.text(x_, ymax * 1.06, lt, ha='center', va='bottom', fontsize=8)
        ax.set_ylim(min(0, ymin), ymax * 1.2)
        ax.set_xticks([t_[0] for t_ in ticks], [t_[1] for t_ in ticks], fontsize=7.5); ax.set_ylabel(yl)
        if i == 0: ax.set_title(CROPN[crop], color=ACC[crop])
top_legend(fig, line=False, pre=False)
fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig(O + 'li600_npq.png'); plt.close(fig)

# ------------------------------------------------------------------ A-Ci / A-Q parameters (box+strip, pre = gray)
aci = pd.read_csv(D + '06_ACi_파라미터.csv'); aq = pd.read_csv(D + '07_AQ_파라미터.csv'); dun = pd.read_csv(D + '08_ACi_AQ_파라미터_Duncan.csv'); pst = pd.read_csv(L + 'param_stats.csv')  # 처리 전 값은 08, 문자는 Tukey(05)
def postf(df):
    df = df.copy(); df['date'] = df['date'].astype(str)
    p_ = df[df.단계.str.replace(' ', '') == '처리후']
    # 콩: 9월 파라미터 엑셀 '선택적 데이터' 시트(9/2~9/17)만 사용, 8월 A-Ci(8/19~8/21)는 측정 시기가 달라 제외
    p_ = p_[((p_.작물 == 'bean') & (p_.date >= '2026-09-01')) | ((p_.date >= '2026-10-16') & (p_.date <= '2026-10-19'))]
    return p_[p_['제외'] != True] if '제외' in p_ else p_
aci_p, aq_p = postf(aci), postf(aq)
PARS = [('Vcmax', aci_p, 'V$_{cmax}$ (µmol·m$^{-2}$·s$^{-1}$)'), ('Jmax', aci_p, 'J$_{max}$ (µmol·m$^{-2}$·s$^{-1}$)'), ('Rd', aci_p, 'R$_d$ (A-Ci)'),
        ('Amax', aq_p, 'A$_{max}$ (µmol·m$^{-2}$·s$^{-1}$)'), ('alpha', aq_p, 'α (quantum yield)')]
fig, axs = plt.subplots(2, 5, figsize=(7.7, 3.08), dpi=300)
for i, crop in enumerate(['bean', 'lettuce']):
    for j, (p_, df, lab) in enumerate(PARS):
        ax = axs[i, j]; dd = dun[(dun.파라미터 == p_) & (dun.작물 == crop)].set_index('처리')
        ax.errorbar(0, dd['처리전_평균'].iloc[0], dd['처리전_SE'].iloc[0], fmt='x', color=PREC, ms=5, capsize=2, lw=1)
        tops = []
        for k, t in enumerate(ORDER, start=1):
            v = df[(df.작물 == crop) & (df.처리 == t)][p_].dropna().values
            tops.append(box_strip(ax, k, v, col(crop, t), FILLED[t], w=0.66))
        ym = max(tops + [dd['처리전_평균'].iloc[0]])
        for k, t in enumerate(ORDER, start=1): ax.text(k, ym * 1.07, pst[(pst.파라미터 == p_) & (pst.작물 == crop)].set_index('처리').loc[t, 'Tukey'], ha='center', fontsize=6.5)
        ax.set_ylim(0, ym * 1.2); ax.set_xticks([]); ax.tick_params(labelsize=6.5)
        if i == 0: ax.set_title(lab, fontsize=7, loc='center', fontweight='normal')
        if j == 0: ax.set_ylabel(CROPN[crop], color=ACC[crop], fontweight='bold', fontsize=8)
top_legend(fig, line=False, pre=True)
fig.tight_layout(rect=(0, 0, 1, 0.88), w_pad=0.6, h_pad=0.6); fig.savefig(O + 'params.png'); plt.close(fig)

# ------------------------------------------------------------------ growth lollipop (% change vs control)
g = pd.read_csv(L + 'growth_stats.csv')   # 05_growth_param_stats.py (이원 ANOVA + Tukey)
panels = [('lettuce', 'Lettuce (DAT 16)', (-62, 30), [(16, '지상부생체중', 'Shoot FW'), (16, '지상부건조중_전체', 'Shoot DW'),
                                                      (16, '엽면적', 'Leaf area'), (16, '엽수', 'Leaf no.')]),
          ('bean', 'Soybean', (-62, 30), [(20, '생식기관DW', 'Pod + seed DW, DAT 20'),
                                           (55, '지상부총DW', 'Total shoot DW, DAT 55'), (55, '종실DW', 'Seed DW, DAT 55'),
                                           (55, '잎줄기FW', 'Leaf + stem FW, DAT 55 (ref.)')])]
fig, axs = plt.subplots(1, 2, figsize=(7.7, 3.5), dpi=300)
for ax, (crop, title, xl, items) in zip(axs, panels):
    for i, (dat, ind, lab) in enumerate(items):
        s = g[(g.작물 == crop) & (g.DAT == dat) & (g.지표 == ind)].set_index('처리'); Pv = s.ANOVA_P.iloc[0]; Pi = s.상호작용P.iloc[0]
        Pw = s['침수P'].iloc[0]
        ptxt = ('P<0.001' if Pv < 0.001 else ('P=%.3f' if Pv < 0.01 else 'P=%.2f') % Pv) + \
               ('; W×I P=%.3f' % Pi if Pi < 0.05 else ('; W P=%.3f' % Pw if Pv >= 0.05 and Pw < 0.05 else ''))
        ax.text(xl[0], i - 0.42, '%s  (%s)' % (lab, ptxt), fontsize=6.6, va='center', color='0.2')
        for k, t in enumerate(['ETc50', '침수ETc', '침수ETc50']):
            v = s.loc[t, '대조구대비'] - 100; y = i + (k - 1) * 0.2 + 0.08; c = col(crop, t)
            ax.plot([0, v], [y, y], color=c, lw=1.6, ls=LS[t])
            ax.plot(v, y, MK[t], color=c, mfc=c if FILLED[t] else 'white', mec=c, ms=5.5, mew=1.2)
            if Pv < 0.05:
                ax.text(v - 2.2 if v < 0 else v + 2.2, y, s.loc[t, 'Tukey'], fontsize=6.5, va='center', ha='right' if v < 0 else 'left', color='0.25')
        if Pv < 0.05:
            ax.text(xl[1], i - 0.42, 'Control: ' + s.loc['ETc', 'Tukey'], fontsize=6.5, va='center', ha='right', color='0.4')
    ax.axvline(0, color='0.35', lw=0.9)
    ax.set_yticks([]); ax.set_ylim(len(items) - 0.5, -0.72)
    ax.spines['left'].set_visible(False)
    ax.set_xlim(*xl); ax.set_xlabel('% change vs control')
    ax.set_title(title, color=ACC[crop])
top_legend(fig, line=True, pre=False)
fig.tight_layout(rect=(0, 0, 1, 0.9)); fig.savefig(O + 'growth.png'); plt.close(fig)

# ------------------------------------------------------------------ treatment check
fig, axs = plt.subplots(1, 2, figsize=(7.7, 3.0), dpi=300, gridspec_kw={'width_ratios': [1.35, 1]})
# 대조구 대비 누적 관수량(%)과 처리 기간 환경 평균: data/21·25 요약 JSON 값(콩 8/16~10/6, 상추 10/12~10/22)
ax = axs[0]; irr = {'bean': [40, 87, 44], 'lettuce': [60, 93, 44]}; x = np.arange(3)
for i, crop in enumerate(['lettuce', 'bean']):
    xs = x + (i - 0.5) * 0.36
    ax.bar(xs, irr[crop], 0.34, color=ACC[crop])
    for xi, v in zip(xs, irr[crop]): ax.text(xi, v + 2, f'{v}%', ha='center', fontsize=7.5)
ax.axhline(50, color='#B5651D', lw=1, ls=':'); ax.text(2.62, 52, 'design\n50%', fontsize=7, color='#B5651D', va='bottom', ha='right')
ax.set_xticks(x, ['Drought\n(ET 50%)', 'Waterlogging\n(→ ET 100%)', 'Combined\n(→ ET 50%)'], fontsize=8)
ax.set_ylabel('Cumulative irrigation\n(% of control)'); ax.set_ylim(0, 110); ax.set_title('Irrigation applied')
ax = axs[1]
for k, (lab, bv, lv) in enumerate([('Mean air\ntemp. (°C)', 28.4, 18.2), ('DLI\n(mol·m$^{-2}$·d$^{-1}$)', 22.0, 17.8)]):
    ax.bar(k - 0.18, lv, 0.34, color=ACC['lettuce']); ax.bar(k + 0.18, bv, 0.34, color=ACC['bean'])
    ax.text(k - 0.18, lv + 0.6, f'{lv}', ha='center', fontsize=7.5); ax.text(k + 0.18, bv + 0.6, f'{bv}', ha='center', fontsize=7.5)
ax.set_xticks([0, 1], ['Mean air\ntemp. (°C)', 'DLI\n(mol·m$^{-2}$·d$^{-1}$)'], fontsize=8); ax.set_ylim(0, 33); ax.set_title('Environment (DAT 0–16)')
from matplotlib.patches import Patch
fig.legend([Patch(color=ACC['lettuce']), Patch(color=ACC['bean'])], ['Lettuce', 'Soybean'], loc='upper center', ncol=2, fontsize=8.5)
fig.tight_layout(rect=(0, 0, 1, 0.9)); fig.savefig(O + 'check.png'); plt.close(fig)

# ------------------------------------------------------------------ LI-6800 fluorescence curves (A1/A2)
for mode in ['trt', 'pool']:
    sm = pd.read_csv(L + f'fluor_summary_{mode}.csv', header=[0, 1], index_col=[0, 1, 2, 3])
    mp = pd.read_csv(L + f'fluor_minP_{mode}.csv').set_index(['작물', '지표'])['minP']
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 4.36), dpi=300, sharex=True)
    for j, crop in enumerate(['bean', 'lettuce']):
        for i, (m, yl) in enumerate([('NPQ', 'NPQ'), ('PhiNO', 'Φ$_{NO}$')]):
            ax = axs[i, j]
            pre = sm.loc[(crop, '처리 전')]
            pre = pre.groupby(level=1).first()
            ax.errorbar(pre.index, pre[(m, 'mean')], pre[(m, 'sem')], color=PREC, ls='--', marker='x', ms=4, lw=1, capsize=1.5)
            for t in ORDER:
                s = sm.loc[(crop, '처리 후', t)]; c = col(crop, t)
                ax.fill_between(s.index, s[(m, 'mean')] - s[(m, 'sem')], s[(m, 'mean')] + s[(m, 'sem')], color=c, alpha=0.15, lw=0)
                ax.plot(s.index, s[(m, 'mean')], color=c, ls=LS[t], lw=1.4, marker=MK[t], ms=3.6, mfc=c if FILLED[t] else 'white', mec=c, mew=1)
            if j == 0: ax.set_ylabel(yl)
            if i == 0: ax.set_title(CROPN[crop], color=ACC[crop])
            if i == 1: ax.set_xlabel('PPFD (µmol·m$^{-2}$·s$^{-1}$)')
            ax.text(1.0, 1.02, 'min P = %.3f' % mp.loc[(crop, m)], transform=ax.transAxes, ha='right', va='bottom', fontsize=7.5, color='0.35')
    top_legend(fig, line=True, pre=True)
    fig.tight_layout(rect=(0, 0, 1, 0.92)); fig.savefig(O + f'fluor_{mode}.png'); plt.close(fig)

# ------------------------------------------------------------------ LSP (A3)
r = pd.read_csv(L + 'fits_flag.csv'); st = pd.read_csv(L + 'lsp_stats.csv'); Ap = pd.read_csv(L + 'A_points.csv')
def nrh(I, a_, th, Pm, Rd):
    x_ = a_ * I + Pm; return (x_ - np.sqrt(np.maximum(x_ * x_ - 4 * th * a_ * I * Pm, 0))) / (2 * th) - Rd
fig, axs = plt.subplots(2, 2, figsize=(7.4, 4.36), dpi=300, gridspec_kw={'height_ratios': [1.25, 1]})
I = np.linspace(0, 1600, 400)
for j, crop in enumerate(['bean', 'lettuce']):
    ax = axs[0, j]; keep = r[(r.작물 == crop) & (~r.제외)]
    for key in ['pre'] + ORDER:
        if key == 'pre': s = keep[keep.단계 == '처리 전']; c = PREC; ls_ = '--'; mk = 'x'; fil = True
        else: s = keep[(keep.단계 == '처리 후') & (keep.처리 == key)]; c = col(crop, key); ls_ = LS[key]; mk = MK[key]; fil = FILLED[key]
        pts_ = Ap[Ap.curve.isin(s.곡선)].copy(); pts_['Qr'] = pts_.Q.round(-1)
        m_ = pts_.groupby('Qr')['A'].agg(['mean', 'sem'])
        y = np.mean([nrh(I, *row) for row in s[['alpha', 'theta', 'Pgmax', 'Rd']].values], axis=0)
        ax.plot(I, y, color=c, ls=ls_, lw=1.3)
        ax.errorbar(m_.index, m_['mean'], m_['sem'], fmt=mk, color=c, ms=3.2, capsize=1.2, lw=0.7, mfc=c if fil else 'white', mec=c)
        q = s.LSP_Q80.mean(); ax.plot([q], [np.interp(q, I, y)], marker='v', color=c, ms=7, mec='white', mew=0.6, zorder=5)
    ax.set_title(CROPN[crop], color=ACC[crop]); ax.set_xlabel('PPFD (µmol·m$^{-2}$·s$^{-1}$)', fontsize=7.5)
    if j == 0: ax.set_ylabel('A (µmol CO$_2$·m$^{-2}$·s$^{-1}$)', fontsize=7.5)
    ax.axhline(0, color='0.75', lw=0.6)
    ax.text(1.0, 1.02, '▼ = LSP (Q80)', transform=ax.transAxes, ha='right', va='bottom', fontsize=7.5, color='0.35')
    b = axs[1, j]; s = st[(st.작물 == crop) & (st.지표 == 'LSP_Q80')].set_index('처리')
    b.errorbar(0, s['처리전_평균'].iloc[0], s['처리전_SE'].iloc[0], fmt='x', color=PREC, ms=5, capsize=2)
    for k, t in enumerate(ORDER, start=1):
        v = keep[(keep.단계 == '처리 후') & (keep.처리 == t)].LSP_Q80.values
        box_strip(b, k, v, col(crop, t), FILLED[t], w=0.62)
        b.text(k, 1420, s.loc[t, 'Tukey'], ha='center', fontsize=8)
    b.set_ylim(0, 1550); b.set_xticks(range(5), ['Pre', 'Control', 'Drought', 'Waterlog.', 'Combined'], fontsize=7)
    if j == 0: b.set_ylabel('LSP (µmol·m$^{-2}$·s$^{-1}$)', fontsize=7.5)
    b.text(1.0, 1.02, 'ANOVA P = %.3f' % s['ANOVA_P'].iloc[0], transform=b.transAxes, ha='right', va='bottom', fontsize=7.5, color='0.35')
top_legend(fig, line=True, pre=True)
fig.tight_layout(rect=(0, 0, 1, 0.92), h_pad=0.8); fig.savefig(O + 'lsp.png'); plt.close(fig)
print('done')
