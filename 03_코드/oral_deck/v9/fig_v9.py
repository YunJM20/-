import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, matplotlib.dates as md
import fo_common as fc
from fo_common import *
import fo_figs as ff
pts=pd.read_csv('intermediate/li600_fluor_points.csv')
fc.PRE=pts[pts.단계=='처리 전'].copy(); fc.PRECOL.update({'npq':'NPQ','phino':'PhiNO','phinpq':'PhiNPQ'})
XL={'bean':(-8,56),'lettuce':(-3,17)}
FD='figs4/'
import os; os.makedirs(FD,exist_ok=True)
def sv(fig,n): fig.savefig(FD+n); plt.close(fig)
# ---- env (entire cultivation period)
def env_full():
    e1=pd.read_csv(R+'data/19_환경_밭콩_일별.csv'); e2=pd.read_csv(R+'로메인data/25_환경_일별.csv')
    e1['날짜']=pd.to_datetime(e1['날짜']); e2['날']=pd.to_datetime(e2['날'])
    miss=[c for c in e2.columns if '결측' in c][0]; e2=e2[e2[miss].astype(str)!='True']
    fig,axs=plt.subplots(1,2,figsize=(7.7,3.0),dpi=300)
    for ax,(c1,c2,yl) in zip(axs,[('평균기온','평균기온','Temperature (°C)'),('DLI_mol','DLI_추정(mol m-2 d-1)','DLI (mol·m$^{-2}$·day$^{-1}$)')]):
        ax.plot(e1.날짜,e1[c1],color=ACC['bean'],lw=1.4); ax.plot(e2.날,e2[c2],color=ACC['lettuce'],lw=1.4)
        ax.axvline(pd.Timestamp('2026-08-12'),color=ACC['bean'],ls=':',lw=1); ax.axvline(pd.Timestamp('2026-10-07'),color=ACC['lettuce'],ls=':',lw=1)
        ax.xaxis.set_major_locator(md.MonthLocator()); ax.xaxis.set_major_formatter(md.DateFormatter('%b %d')); ax.set_ylabel(yl); ax.set_xlabel('Date')
    legend2(fig,E_crops()+[(Line2D([],[],color='0.4',ls=':',lw=1.2),'Waterlogging start')],3,fontsize=8)
    fig.tight_layout(rect=(0,0,1,0.88)); sv(fig,'env.png')
# ---- gsw / recovery with identical axes
def pair():
    for kind in ('ts','rec'):
        fig,axs=plt.subplots(1,2,figsize=(7.5,2.55),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
        for ax,crop in zip(axs,['bean','lettuce']):
            if kind=='ts': ts_axes(ax,crop,'gsw','g$_{sw}$ (mol·m$^{-2}$·s$^{-1}$)')
            else: ff.rec_ax(ax,crop); 
            ax.set_xlim(*XL[crop])
        if kind=='rec': axs[0].set_ylabel('g$_{sw}$ (% of control)')
        if kind=='ts': legend2(fig,E_crops()+E_trt(('bean','lettuce'))+[E_pre(),E_cloud(),E_flood()],5)
        else: legend2(fig,E_crops()+ff.rec_handles(),5)
        fig.subplots_adjust(left=0.085,right=0.99,top=0.78,bottom=0.2,wspace=0.2); sv(fig,f'gsw_{kind}.png')
# ---- three-in-one light reaction time series
def phi3():
    fig,axs=plt.subplots(3,2,figsize=(7.2,5.3),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
    for r,(ind,lab) in enumerate([('phi','Φ$_{PSII}$'),('phinpq','Φ$_{NPQ}$'),('phino','Φ$_{NO}$')]):
        for c,crop in enumerate(['bean','lettuce']):
            ax=axs[r,c]; ts_axes(ax,crop,ind,lab); ax.set_xlim(*XL[crop])
            if r<2: ax.set_xlabel(''); ax.set_xticklabels([])
            if c==0: ax.set_ylabel(lab,fontsize=9)
    legend2(fig,E_crops()+E_trt(('bean','lettuce'))+[E_pre(),E_cloud(),E_flood()],5)
    fig.subplots_adjust(left=0.09,right=0.99,top=0.89,bottom=0.075,hspace=0.18,wspace=0.2); sv(fig,'phi3.png')
# ---- recap figures (per crop)
MM=pd.read_csv('intermediate/mm_phase.csv')
EMPH={'bean':{'ETc','ETc50','침수ETc50'},'lettuce':{'ETc','침수ETc50'}}
LG='#C4C4C4'
def cc(crop,t,emph=True): return CROPC[crop][t] if (not emph or t in EMPH[crop]) else LG
SHORT={'ETc':'Ctrl','ETc50':'Dr.','침수ETc':'Wl.','침수ETc50':'Comb.'}
def stack(ax,crop):
    COL={'phi':'#165F82','phinpq':'#E3A23B','phino':'#C0504D'}; NAME={'phi':'Φ$_{PSII}$','phinpq':'Φ$_{NPQ}$','phino':'Φ$_{NO}$'}
    x=0; ticks=[]; labs=[]; grp=[]
    for per in ['P1','P2']:
        trts=[t for t in ORDER if not MM[(MM.작물==crop)&(MM.구간==per)&(MM.처리==t)&(MM.지표=='phi')].empty]
        start=x
        for t in trts:
            v={i:MM[(MM.작물==crop)&(MM.구간==per)&(MM.처리==t)&(MM.지표==i)].보정평균.iloc[0] for i in COL}; s=sum(v.values()); b=0
            for i in ['phi','phino','phinpq']:
                h=v[i]/s*100; ax.bar(x,h,0.78,bottom=b,color=COL[i],edgecolor='white',lw=0.5)
                if h>4: ax.text(x,b+h/2,f'{h:.0f}',ha='center',va='center',fontsize=5.8,color='white')
                b+=h
            ticks.append(x); labs.append(SHORT[t]); x+=1
        grp.append((per,(start+x-1)/2)); x+=0.7
    ax.set_xticks(ticks); ax.set_xticklabels(labs,fontsize=6.2,rotation=0); ax.set_ylim(0,100); ax.set_ylabel('Fraction of absorbed energy (%)',fontsize=7.5); ax.tick_params(labelsize=7)
    for per,xc in grp: ax.text(xc,-17,per,ha='center',va='top',fontsize=8,fontweight='bold',color='0.35',transform=ax.transData)
    from matplotlib.patches import Patch
    return [Patch(color=COL[i]) for i in ('phi','phinpq','phino')],[NAME[i] for i in ('phi','phinpq','phino')]
def bx(ax,crop,par,dd,ps,lab,xt=False):
    q=ps[(ps.파라미터==par)&(ps.작물==crop)].set_index('처리'); tops=[]
    for k,t in enumerate(ORDER,1): tops.append(ff.box_strip(ax,k,dd[(dd.작물==crop)&(dd.처리==t)][par].dropna().values,cc(crop,t),FILLED[t],0.66))
    if q.ANOVA_P.iloc[0]<0.05:
        for k,t in enumerate(ORDER,1): ax.text(k,max(tops)*1.04,q.loc[t,'Tukey'],ha='center',fontsize=8)
    ax.set_ylim(0,max(tops)*1.25); ax.set_ylabel(lab+' (µmol m$^{-2}$ s$^{-1}$)',fontsize=7.5); ax.tick_params(labelsize=7)
    ax.set_xticks(range(1,5)); ax.set_xticklabels([SHORT[t] for t in ORDER] if xt else [],fontsize=6.2)
def recap2(crop):
    b,r=ff.yield_data(); fig=plt.figure(figsize=(12.2,3.9),dpi=300)
    gs=fig.add_gridspec(1,4,wspace=0.3,left=0.055,right=0.995,top=0.9,bottom=0.15,width_ratios=[1,1.05,0.95,0.95])
    a0=fig.add_subplot(gs[0]); a1=fig.add_subplot(gs[1]); sg=gs[2].subgridspec(2,1,hspace=0.16); a4=fig.add_subplot(gs[3])
    ff.rec_ax(a0,crop); a0.set_ylabel('g$_{sw}$ (% of control)'); a0.set_xlim(*XL[crop])
    hs,ls=stack(a1,crop); a1.legend(hs,ls,loc='upper center',bbox_to_anchor=(0.5,1.14),ncol=3,fontsize=7.5,frameon=False,handlelength=1.2,columnspacing=1.2)
    dd=pd.read_csv('data/06_ACi_파라미터.csv'); dd['date']=dd['date'].astype(str); dd=dd[dd.단계.str.replace(' ','')=='처리후']
    dd=dd[((dd.작물=='bean')&(dd.date>='2026-09-01'))|((dd.date>='2026-10-16')&(dd.date<='2026-10-19'))]
    if '제외' in dd: dd=dd[dd['제외']!=True]
    ps=pd.read_csv('intermediate/param_stats.csv')
    bx(fig.add_subplot(sg[0]),crop,'Vcmax',dd,ps,'V$_{cmax}$'); bx(fig.add_subplot(sg[1]),crop,'Jmax',dd,ps,'J$_{max}$',xt=True)
    if crop=='bean': vals={t:b.loc[b.처리==t,'알 F.W'].dropna() for t in ORDER}; lab='Seed FW (g·plant$^{-1}$)'
    else: vals={t:r.loc[r.처리==t,'지상부건조중_전체'].dropna() for t in ORDER}; lab='Shoot DW (g·plant$^{-1}$)'
    ff.bars(a4,vals,crop,lab,gray=False); a4.set_ylabel(lab,fontsize=8); a4.set_xticks(range(4)); a4.set_xticklabels([SHORT[t] for t in ORDER],fontsize=6.2)
    sv(fig,f'recap2_{crop}.png')
if __name__=='__main__':
    import sys
    for f in (sys.argv[1:] or ['env_full','pair','phi3','recap']):
        if f=='recap': recap2('bean'); recap2('lettuce')
        else: globals()[f]()
    print('ok')
