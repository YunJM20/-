"""v12 재검토 반영 분석·그림 (구두발표 v13).

1. LI-600 구간 통합 점검: 측정일을 반복으로 한 검정(처리별 측정일 평균 ~ 침수 × 관수 + 측정일),
   처리 × 측정일 상호작용, 처리별 광도 기울기 차이 → intermediate/phase_robust.csv
2. 콩 P2 ΦPSII 광도 의존: ΦPSII ~ 처리 × PAR(Qamb, 선형) + 측정일 + 기온(Tair), PPFD 300·1200 예측값(9/4 기준) → phi_light_pred.csv
3. 상추 P1(DAT 5~10) 형광 신호 크기: Fs, Fm′, 암적응 Fm, Fm′/Fs → lettuce_signal.csv
4. 상추 생육 손실 환산: RGR(대조구, DAT 0 → 16), 생장 손실 일수, 침수구 gsw 결손 적분(DAT 1~8) → lettuce_path.csv
5. 그림: check2.png(관수량 + 상추 포트 무게), phi_light.png, fvfm_signal.png, lettuce_path.png
"""
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.legend_handler import HandlerTuple
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from scipy import stats
from config import DATA, INTER, FIG, ORDER, PHASE_END, load_li600, common_days
from stats2x2 import WL, IR

warnings.filterwarnings('ignore')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.linewidth': 0.8, 'legend.frameon': False, 'axes.titlesize': 9.5, 'axes.titleweight': 'bold',
                     'axes.titlelocation': 'left'})
NAME = {'ETc': 'Control', 'ETc50': 'Drought', '침수ETc': 'Waterlogging', '침수ETc50': 'Combined'}
CROPC = {'lettuce': {'ETc': '#1F3D2B', 'ETc50': '#8FAA91', '침수ETc': '#2E7D4F', '침수ETc50': '#9FD3A8'},
         'bean': {'ETc': '#3B2618', 'ETc50': '#B9A28C', '침수ETc': '#8B5A2B', '침수ETc50': '#E0B98A'}}
ACC = {'lettuce': '#2E6B3F', 'bean': '#6B4226'}
MK = {'ETc': 'o', 'ETc50': 'o', '침수ETc': 's', '침수ETc50': 's'}
FILLED = {'ETc': True, 'ETc50': False, '침수ETc': True, '침수ETc50': False}
LS = {'ETc': '-', 'ETc50': '-', '침수ETc': (0, (4, 1.6)), '침수ETc50': (0, (4, 1.6))}
CLOUDC = '#E9E9E9'


def handle(crop, t, line=True):
    c = CROPC[crop][t]
    return Line2D([], [], color=c, lw=1.6 if line else 0, ls=LS[t] if line else 'none', marker=MK[t], ms=5,
                  mfc=c if FILLED[t] else 'white', mec=c, mew=1.2)


def legend(fig, crops, line=True, extra=(), y=1.0):
    hs = [tuple(handle(c, t, line) for c in crops) for t in ORDER] + [e[0] for e in extra]
    ls = [NAME[t] for t in ORDER] + [e[1] for e in extra]
    fig.legend(hs, ls, loc='upper center', bbox_to_anchor=(0.5, y), ncol=len(ls), fontsize=7.8,
               handler_map={tuple: HandlerTuple(ndivide=None, pad=0.3)}, handlelength=3.0 if len(crops) > 1 else 2.2, columnspacing=1.4)


# ================================================================ 1. 구간 통합 점검
x = load_li600(); x = x[(x.Qamb > 0)].dropna(subset=['Tair']).copy(); x['lq'] = x.Qamb; x['tq'] = x.Tair
x['W'] = x.처리.map(WL); x['I'] = x.처리.map(IR)
COLS = {'gsw': 'gsw_해석용(0 이하 제외)', 'phi': 'PhiPS2', 'etr': 'ETR'}


def phase(crop, ph):
    b = x[(x.작물 == crop) & (x.DAT >= 1)]
    s = b[b.DAT <= PHASE_END[crop]] if ph == 'P1' else b[b.DAT > PHASE_END[crop]]
    return common_days(s)


rows = []
for crop in ['bean', 'lettuce']:
    for ph in ['P1', 'P2']:
        s = phase(crop, ph)
        for k, c in COLS.items():
            d = s.dropna(subset=[c]).rename(columns={c: 'y'})
            four = d.처리.nunique() == 4
            m = d.groupby(['날짜', '처리', 'W', 'I']).y.mean().reset_index()
            a = anova_lm(smf.ols('y ~ C(W)*C(I) + C(날짜)' if four else 'y ~ C(W) + C(날짜)', m).fit(), typ=2)['PR(>F)']
            m1 = smf.ols('y ~ C(처리) + C(날짜) + lq + tq', d).fit()
            pTD = anova_lm(m1, smf.ols('y ~ C(처리)*C(날짜) + lq + tq', d).fit()).iloc[1, -1]
            pSL = anova_lm(m1, smf.ols('y ~ C(처리)*lq + C(날짜) + tq', d).fit()).iloc[1, -1]
            for t, g in d.groupby('처리'):
                rows.append(dict(작물=crop, 국면=ph, 지표=k, 처리=t, 원평균=g.y.mean(), SE=g.y.sem(), n=len(g), 날짜수=d.날짜.nunique(),
                                 블록_침수P=a.get('C(W)'), 블록_관수P=a.get('C(I)'), 블록_상호작용P=a.get('C(W):C(I)'),
                                 처리x날짜P=pTD, 처리x광도P=pSL))
pd.DataFrame(rows).to_csv(INTER / 'phase_robust.csv', index=False)

# ================================================================ 2. 콩 P2 ΦPSII 광도 의존
s = phase('bean', 'P2').rename(columns={'PhiPS2': 'y'}).dropna(subset=['y'])
mq = smf.ols('y ~ C(처리)*lq + C(날짜) + tq', s).fit()
pred = []
for q in [300, 1200]:
    g = pd.DataFrame({'처리': ORDER, 'lq': float(q), 'tq': float(s.tq.mean()), '날짜': '2026-09-04'})
    pr = mq.get_prediction(g).summary_frame()
    for t, mu, se in zip(ORDER, pr['mean'], pr['mean_se']):
        pred.append(dict(PPFD=q, 처리=t, 예측=mu, SE=se))
a3 = anova_lm(smf.ols('y ~ C(W)*C(I)*lq + C(날짜) + tq', s).fit(), typ=2)['PR(>F)']
pred = pd.DataFrame(pred); pred['W×I×PAR_P'] = a3['C(W):C(I):lq']; pred['I×PAR_P'] = a3['C(I):lq']
pred.to_csv(INTER / 'phi_light_pred.csv', index=False)

# ================================================================ 3. 상추 형광 신호 크기 (P1 = DAT 5~10)
L1 = x[(x.작물 == 'lettuce') & (x.DAT.between(5, 10))].copy(); L1['ratio'] = L1["Fm'"] / L1.Fs
f = pd.read_csv(DATA / '03_암적응_FvFm_개별측정.csv')
fd = f[(f.작물 == 'lettuce') & (f.날짜.between('2026-10-12', '2026-10-17'))]
import statsmodels.formula.api as _smf
L1 = L1.dropna(subset=['Tair']).copy(); L1['cell'] = L1['날짜'].astype(str) + '_' + L1['처리']
for _v in ['Fs', "Fm'", 'ratio']:
    _d = L1.dropna(subset=[_v]); _m = _smf.ols(f'Q("{_v}") ~ C(cell) + Qamb + Tair', _d).fit()
    L1[_v] = L1[_v] + _m.params['Qamb'] * (_d.Qamb.mean() - L1.Qamb) + _m.params['Tair'] * (_d.Tair.mean() - L1.Tair)   # PAR·기온 보정 개체값
sig = []
for lab, df, v in [('Fs', L1, 'Fs'), ("Fm′", L1, "Fm'"), ('Fm (dark)', fd, 'Fm'), ('Fm′/Fs', L1, 'ratio'), ('Fv/Fm', fd, 'Fv/Fm')]:
    grp = {t: df.loc[df.처리 == t, v].dropna() for t in ORDER}
    P = stats.f_oneway(*grp.values()).pvalue
    for t in ORDER:
        a = grp[t]
        sig.append(dict(지표=lab, 처리=t, 평균=a.mean(), SE=a.sem(), 대조구대비=a.mean() / grp['ETc'].mean() * 100,
                        SE_pct=a.sem() / grp['ETc'].mean() * 100, P=P))
sig = pd.DataFrame(sig); sig.to_csv(INTER / 'lettuce_signal.csv', index=False)

# ================================================================ 4. 상추 생육 손실 환산
l = pd.read_csv(DATA / '11_생육_잎상추.csv')
dw0 = l[(l.날짜 == '2026-10-07')]['지상부건조중_전체'].mean()
dw = l[l.날짜 == '2026-10-23'].groupby('처리')['지상부건조중_전체'].mean()
rgr = np.log(dw['대조구'] / dw0) / 16
dl = pd.read_csv(INTER / 'daily_stats.csv'); g = dl[(dl.지표 == 'gsw') & (dl.작물 == 'lettuce')].pivot_table(index='DAT', columns='처리', values='평균')
ratio = (g['침수ETc'] / g['ETc']).dropna()
deficit = (1 - ratio.loc[1:8]).clip(lower=0).sum()
path = dict(DW0=dw0, DW_control=dw['대조구'], DW_waterlog=dw['침수'], DW_combined=dw['복합'], RGR=rgr,
            손실일수_침수=np.log(dw['대조구'] / dw['침수']) / rgr, 손실일수_복합=np.log(dw['대조구'] / dw['복합']) / rgr,
            gsw결손_일수=deficit, 탄소손실_추정_일수=deficit * 0.5)
pd.Series(path).to_csv(INTER / 'lettuce_path.csv', header=['값'])

# ================================================================ 5a. check2.png : 관수량 + 상추 포트 무게
h = pd.read_csv(DATA / '36_잎상추_로드셀_시간별무게.csv'); h['t'] = pd.to_datetime(h['시각'])
h = h[h.t.dt.hour == 5].set_index('t')
cols = {'ETc': '잎상추 ETc(kg)', 'ETc50': '잎상추 ETc50(kg)', '침수ETc': '잎상추 침수ETc(kg)', '침수ETc50': '잎상추 침수ETc50(kg)'}
base = h.loc['2026-10-07 05:00']
fig, axs = plt.subplots(1, 2, figsize=(7.7, 3.0), dpi=300, gridspec_kw={'width_ratios': [1, 1.25]})
ax = axs[0]; irr = {'bean': [40, 87, 44], 'lettuce': [60, 93, 44]}; xx = np.arange(3)
for i, crop in enumerate(['lettuce', 'bean']):
    xs = xx + (i - 0.5) * 0.36
    ax.bar(xs, irr[crop], 0.34, color=ACC[crop])
    for xi, v in zip(xs, irr[crop]): ax.text(xi, v + 2, f'{v}%', ha='center', fontsize=7)
ax.axhline(50, color='#B5651D', lw=1, ls=':'); ax.text(2.6, 52, 'design\n50%', fontsize=6.5, color='#B5651D', va='bottom', ha='right')
ax.set_xticks(xx, ['Drought', 'Waterlogging', 'Combined'], fontsize=7.5)
ax.set_ylabel('Cumulative irrigation to pots\n(% of control)', fontsize=7.5); ax.set_ylim(0, 110); ax.set_title('Irrigation applied')
ax.legend([Patch(color=ACC['lettuce']), Patch(color=ACC['bean'])], ['Lettuce', 'Soybean'], fontsize=7, loc='upper right', ncol=2)
ax = axs[1]
dat = (h.index - pd.Timestamp('2026-10-07 05:00')).days
ax.axvspan(0, 3, color='#E6E6E6', lw=0); ax.text(1.5, 1.85, 'Water-\nlogging\n(pots in tubs)', ha='center', va='top', fontsize=6, color='0.35')
ax.axhline(0, color='0.5', lw=0.7, ls='--')
for t in ORDER:
    y = (h[cols[t]] - base[cols[t]]).values.copy()
    if t in ('침수ETc', '침수ETc50'): y[(dat >= 1) & (dat <= 3)] = np.nan
    if t == 'ETc': y[(dat >= 11) & (dat <= 14)] = np.nan   # 10/18~10/21 대조구 로드셀 이상값
    c = CROPC['lettuce'][t]
    ax.plot(dat, y, color=c, ls=LS[t], lw=1.4, marker=MK[t], ms=3.5, mfc=c if FILLED[t] else 'white', mec=c, mew=1)
ax.set_xlim(-3.5, 16.5); ax.set_ylim(-1.5, 2.0)
ax.set_xlabel('DAT'); ax.set_ylabel('Δ pot weight vs. DAT 0\n(kg, 4 pots, 05:00)', fontsize=7.5)
ax.set_title('Lettuce pot weight')
ax.legend([handle('lettuce', t) for t in ORDER], [NAME[t] for t in ORDER], fontsize=6.5, loc='lower left', ncol=2, handlelength=2.2)
fig.tight_layout(w_pad=1.5); fig.savefig(FIG / 'check2.png'); plt.close(fig)

# ================================================================ 5b. phi_light.png
A04 = pd.read_csv(INTER / 'daily_stats.csv')
fig, axs = plt.subplots(1, 3, figsize=(7.7, 2.8), dpi=300, gridspec_kw={'width_ratios': [1.15, 1, 0.95]})


def ts(ax, crop, ind='phi'):
    s_ = A04[(A04.지표 == ind) & (A04.작물 == crop)]
    ax.axvspan(0, 3, color='#E6E6E6', lw=0, zorder=0)
    for d in s_[s_.흐림 == True].DAT.unique(): ax.axvspan(d - 0.45, d + 0.45, color=CLOUDC, lw=0, zorder=0)
    for t in ORDER:
        q = s_[s_.처리 == t].sort_values('DAT')
        if q.empty: continue
        c = CROPC[crop][t]
        ax.fill_between(q.DAT, q.평균 - q.SE, q.평균 + q.SE, color=c, alpha=0.16, lw=0)
        ax.plot(q.DAT, q.평균, color=c, ls=LS[t], lw=1.3, marker=MK[t], ms=3.4, mfc=c if FILLED[t] else 'white', mec=c, mew=1)
    for d, q in s_.groupby('DAT'):
        if q['당일_ANOVA_P_Holm'].iloc[0] < 0.05:
            ax.text(d, (q.평균 + q.SE).max() + 0.01, '*', ha='center', va='bottom', fontsize=9, color='0.2')
    bnd = PHASE_END[crop] + 0.5
    ax.axvline(bnd, color='0.55', ls=':', lw=1)
    ax.set_xlabel('DAT'); ax.set_title(('Soybean' if crop == 'bean' else 'Lettuce'), color=ACC[crop])


ts(axs[0], 'bean'); axs[0].set_ylabel('Φ$_{PSII}$'); axs[0].set_ylim(0.25, 0.85)
ax = axs[1]
I = np.linspace(80, 1900, 60)
for t in ORDER:
    q = s[s.처리 == t]; c = CROPC['bean'][t]
    ax.scatter(q.Qamb, q.y, s=8, color=c if FILLED[t] else 'white', edgecolor=c, lw=0.7, marker=MK[t], alpha=0.75)
    Ii = I[(I >= q.Qamb.min()) & (I <= q.Qamb.max())]
    gg = pd.DataFrame({'처리': t, 'lq': Ii, 'tq': float(s.tq.mean()), '날짜': '2026-09-04'})
    ax.plot(Ii, mq.predict(gg), color=c, ls=LS[t], lw=1.6)
ax.set_xticks([0, 500, 1000, 1500, 2000], ['0', '500', '1000', '1500', '2000']); ax.axvline(1200, color='0.6', lw=0.7, ls=':')
ax.set_xlabel('Q$_{amb}$ (µmol·m$^{-2}$·s$^{-1}$)'); ax.set_ylim(0.25, 0.85)
ax.set_title('Soybean P2: light dependence', color=ACC['bean'])
ax.text(0.03, 0.04, 'Trt × PAR: P<0.001', transform=ax.transAxes, fontsize=6.8, color='0.3')
ts(axs[2], 'lettuce'); axs[2].set_ylim(0.25, 0.85)
legend(fig, ('lettuce', 'bean'), extra=[(Patch(color=CLOUDC), 'Cloudy (CI<0.5)')])
fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=0.8); fig.savefig(FIG / 'phi_light.png'); plt.close(fig)

# ================================================================ 5c. fvfm_signal.png
fv = f.copy(); fv = fv[~((fv.작물 == 'bean') & (fv.날짜 == '2026-09-28'))]
fig, axs = plt.subplots(1, 3, figsize=(7.7, 2.75), dpi=300, gridspec_kw={'width_ratios': [1.15, 0.95, 1.05]})
for ax, crop in zip(axs[:2], ['bean', 'lettuce']):
    q = fv[fv.작물 == crop]
    ax.axvspan(0, 3, color='#E6E6E6', lw=0, zorder=0)
    for t in ORDER:
        g_ = q[q.처리 == t].groupby('DAT')['Fv/Fm'].agg(['mean', 'sem']).reset_index()
        if g_.empty: continue
        c = CROPC[crop][t]
        ax.errorbar(g_.DAT, g_['mean'], g_['sem'], color=c, ls=LS[t], lw=1.2, marker=MK[t], ms=3.4, mfc=c if FILLED[t] else 'white',
                    mec=c, mew=1, capsize=1.2, elinewidth=0.7)
    for d, gg in q.groupby('DAT'):
        if gg.처리.nunique() > 1:
            p_ = stats.f_oneway(*[a['Fv/Fm'].dropna() for _, a in gg.groupby('처리')]).pvalue
            if p_ < 0.05: ax.text(d, gg.groupby('처리')['Fv/Fm'].mean().max() + 0.006, '*', ha='center', fontsize=9, color='0.2')
    ax.set_ylim(0.79, 0.87); ax.set_xlabel('DAT'); ax.set_title('Soybean' if crop == 'bean' else 'Lettuce', color=ACC[crop])
    if crop == 'bean': ax.set_ylabel('F$_v$/F$_m$ (dark-adapted)')
ax = axs[2]
labs = ['Fs', "Fm′", 'Fm (dark)', 'Fm′/Fs']
for k, t in enumerate(['ETc50', '침수ETc', '침수ETc50']):
    q = sig[sig.처리 == t].set_index('지표').loc[labs]; c = CROPC['lettuce'][t]
    xs = np.arange(len(labs)) + (k - 1) * 0.26
    ax.bar(xs, q.대조구대비 - 100, 0.24, color=c if FILLED[t] else 'white', edgecolor=c, lw=1, hatch='////' if t == '침수ETc50' else None)
    ax.errorbar(xs, q.대조구대비 - 100, q.SE_pct, fmt='none', color='0.3', lw=0.7, capsize=1.2)
ax.axhline(0, color='0.3', lw=0.8)
P = sig.drop_duplicates('지표').set_index('지표').P
ax.set_xticks(range(len(labs)), ['F$_s$', 'F$_m$′', 'F$_m$\n(dark)', 'F$_m$′/F$_s$'], fontsize=7.5)
for i, lb in enumerate(labs):
    ax.text(i, 9, 'P<0.001' if P[lb] < 0.001 else 'P=%.2f' % P[lb], ha='center', fontsize=6.3, color='0.3')
ax.set_ylim(-22, 13); ax.set_ylabel('% vs control', fontsize=7.5)
ax.set_title('Lettuce P1 signal size', color=ACC['lettuce'])
legend(fig, ('lettuce', 'bean'))
fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=0.8); fig.savefig(FIG / 'fvfm_signal.png'); plt.close(fig)

# ================================================================ 5d. lettuce_path.png (캐노피: SAM 분할 결과, data/37)
from stats2x2 import tukey_letters, twoway
cp = pd.read_csv(DATA / '37_잎상추_캐노피_SAM.csv')          # 캐노피커버_잎상추/canopy_results_SAM_*.xlsx
cw = cp.pivot_table(index=['처리', 'rep'], columns='DAT', values='PCA_cm2')
cw['RGR'] = np.log(cw[16] / cw[5]) / 11                      # DAT 5 → 16 캐노피 상대확장속도
rg = {t: cw.loc[t, 'RGR'].values for t in ORDER}
rL, rP = tukey_letters(rg); rTW = twoway(cw.reset_index(), 'RGR')
cm = cp.groupby(['DAT', '처리']).PCA_cm2.mean().unstack()
c_rgr = np.log(cm.loc[16, 'ETc'] / cm.loc[5, 'ETc']) / 11
cdP = {d_: stats.f_oneway(*[g_.PCA_cm2 for _, g_ in cp[cp.DAT == d_].groupby('처리')]).pvalue for d_ in sorted(cp.DAT.unique())}
path.update(캐노피손실일수_DAT5_침수=np.log(cm.loc[5, 'ETc'] / cm.loc[5, '침수ETc']) / c_rgr,
            캐노피손실일수_DAT5_복합=np.log(cm.loc[5, 'ETc'] / cm.loc[5, '침수ETc50']) / c_rgr,
            gsw결손_DAT1_5=(1 - ratio.loc[1:5]).clip(lower=0).sum(), 대조구_캐노피RGR=c_rgr)
pd.Series(path).to_csv(INTER / 'lettuce_path.csv', header=['값'])
rows_ = []
for t in ORDER:
    for d_ in sorted(cp.DAT.unique()):
        q = cp[(cp.DAT == d_) & (cp.처리 == t)]
        rows_.append(dict(처리=t, DAT=d_, PCA_cm2=q.PCA_cm2.mean(), SE=q.PCA_cm2.sem(), 대조구대비=q.PCA_cm2.mean() / cm.loc[d_, 'ETc'] * 100,
                          redness=q.redness.mean(), ExG=q.ExG.mean(), 날짜_ANOVA_P=cdP[d_]))
    rows_.append(dict(처리=t, DAT='RGR 5→16', PCA_cm2=rg[t].mean(), SE=rg[t].std(ddof=1) / np.sqrt(len(rg[t])), Tukey=rL[t], 날짜_ANOVA_P=rP, **rTW))
pd.DataFrame(rows_).to_csv(INTER / 'lettuce_canopy.csv', index=False)

fig, axs = plt.subplots(1, 3, figsize=(7.7, 2.75), dpi=300, gridspec_kw={'width_ratios': [1.1, 1.05, 0.85]})
ax = axs[0]
r10 = ratio.loc[1:10] * 100
ax.axvspan(0, 3, color='#E6E6E6', lw=0)
ax.fill_between(r10.index, r10.values, 100, where=r10.values < 100, color=CROPC['lettuce']['침수ETc'], alpha=0.25, lw=0, interpolate=True)
ax.plot(r10.index, r10.values, '-s', color=ACC['lettuce'], ms=4, lw=1.6)
ax.axhline(100, color='0.45', lw=0.8, ls='--')
ax.text(5.2, 62, 'deficit ≈ %.1f d' % deficit, fontsize=7.5, color=ACC['lettuce'])
ax.set_ylim(0, 135); ax.set_xlim(-0.3, 10.5); ax.set_xlabel('DAT'); ax.set_ylabel('% of control', fontsize=8)
ax.set_title('Waterlogged g$_{sw}$', color=ACC['lettuce'])
ax = axs[1]
ax.axvspan(0, 3, color='#E6E6E6', lw=0)
ax.axhline(100, color='0.45', lw=0.8, ls='--')
for t in ['ETc50', '침수ETc', '침수ETc50']:
    q = cp[cp.처리 == t].groupby('DAT').PCA_cm2.agg(['mean', 'sem']); c = CROPC['lettuce'][t]
    ax.errorbar(q.index, q['mean'] / cm['ETc'] * 100, q['sem'] / cm['ETc'] * 100, color=c, ls=LS[t], lw=1.4, marker=MK[t], ms=4,
                mfc=c if FILLED[t] else 'white', mec=c, mew=1, capsize=1.5, elinewidth=0.7)
dwr = dw / dw['대조구'] * 100
for t, k in [('침수ETc', '침수'), ('침수ETc50', '복합'), ('ETc50', '건조')]:
    c = CROPC['lettuce'][t]
    ax.plot(17.4, dwr[k], marker='D', ms=4.5, color=c if FILLED[t] else 'white', mec=c, mew=1)
ax.text(17.4, 102, 'DW', ha='center', fontsize=6.5, color='0.35')
for d_ in cm.index:
    if cdP[d_] < 0.05: ax.text(d_, 109, '*', ha='center', fontsize=9, color='0.2')
ax.set_xlim(-0.5, 18.4); ax.set_ylim(50, 115); ax.set_xticks([0, 5, 8, 12, 16])
ax.set_xlabel('DAT'); ax.set_title('Projected leaf area (% of control)', color=ACC['lettuce'], fontsize=8.8)
ax = axs[2]
for k, t in enumerate(ORDER):
    c = CROPC['lettuce'][t]; m_ = rg[t].mean(); se = rg[t].std(ddof=1) / np.sqrt(len(rg[t]))
    ax.bar(k, m_, 0.7, color=c if FILLED[t] else 'white', edgecolor=c, lw=1.1, hatch='////' if t == '침수ETc50' else None)
    ax.errorbar(k, m_, se, color='0.3', capsize=2, lw=0.8)
    ax.text(k, m_ + se + 0.003, rL[t], ha='center', fontsize=7.5)
ax.set_xticks([]); ax.set_ylim(0, 0.13); ax.set_ylabel('d$^{-1}$', fontsize=8)
ax.set_title('Canopy RGR, DAT 5→16', color=ACC['lettuce'], fontsize=8.8)
ax.text(0.5, -0.1, 'P=%.3f (W P=%.3f)' % (rP, rTW['침수P']), transform=ax.transAxes, ha='center', fontsize=6.8, color='0.3')
legend(fig, ('lettuce',))
fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=0.8); fig.savefig(FIG / 'lettuce_path.png'); plt.close(fig)
print('07 done', {k: round(float(v), 3) for k, v in path.items()})
