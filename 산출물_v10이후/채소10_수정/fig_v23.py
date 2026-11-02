# 13·14p 총정리: 4개 그래프를 각각 따로 저장 (기공 P2 막대, 명반응, 광합성 능력, 생육/수량)
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
import fig_v9 as g
import fig_v13 as F
import fo_figs as ff
from fo_common import *
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
W,H=2.9,3.9; L,R,B,T=0.30,0.975,0.15,0.90
dd=pd.read_csv('data/06_ACi_파라미터.csv'); dd['date']=dd['date'].astype(str); dd=dd[dd.단계.str.replace(' ','')=='처리후']
dd=dd[((dd.작물=='bean')&(dd.date>='2026-09-01'))|((dd.date>='2026-10-16')&(dd.date<='2026-10-19'))]
if '제외' in dd: dd=dd[dd['제외']!=True]
ps=pd.read_csv('intermediate/param_stats.csv'); b,r=ff.yield_data()
def newfig(): return plt.figure(figsize=(W,H),dpi=300)
def p1(crop):
    st,P=F.stats('gsw',crop,'P2'); fig=newfig(); ax=fig.add_axes([L,B,R-L,T-B]); top=0
    for k,t in enumerate(ORDER):
        m,se,lt=st[t]; c=CROPC[crop][t]
        if FILLED[t]: ax.bar(k,m,0.72,color=c)
        else: ax.bar(k,m,0.72,facecolor='white',edgecolor=c,linewidth=1.6,hatch='////' if t=='침수ETc50' else None)
        ax.errorbar(k,m,se,color='#333',capsize=3,lw=1.1); top=max(top,m+se)
        if P<0.05: ax.text(k,m+se,lt,ha='center',va='bottom',fontsize=9)
    ax.set_ylim(0,top*1.22); ax.set_xlim(-0.6,3.6); ax.set_xticks(range(4)); ax.set_xticklabels([F.SHORT[t] for t in ORDER],fontsize=8)
    ax.set_ylabel('g$_{sw}$ (mol·m$^{-2}$·s$^{-1}$)',fontsize=9); ax.tick_params(axis='y',labelsize=8)
    if crop=='lettuce': ax.yaxis.set_major_locator(MultipleLocator(0.05)); ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    fig.savefig(f'{crop}_1_gsw.png'); plt.close(fig)
def stack(n,hs):
    fig=newfig(); gs=fig.add_gridspec(n,1,left=L,right=R,top=T,bottom=B,hspace=hs); return fig,[fig.add_subplot(gs[i]) for i in range(n)]
def p2(crop):
    fig,axs=stack(3,0.12)
    for k,(ind,lab) in enumerate([('phi','Φ$_{PSII}$'),('phinpq','Φ$_{NPQ}$'),('phino','Φ$_{NO}$')]): g.dots(axs[k],crop,ind,lab,xt=(k==2))
    fig.savefig(f'{crop}_2_light.png'); plt.close(fig)
def p3(crop):
    fig,axs=stack(2,0.16)
    for ax,par,lab,xt in ((axs[0],'Vcmax','V$_{cmax}$',False),(axs[1],'Jmax','J$_{max}$',True)):
        q=ps[(ps.파라미터==par)&(ps.작물==crop)].set_index('처리'); tops=[]
        for k,t in enumerate(ORDER,1): tops.append(ff.box_strip(ax,k,dd[(dd.작물==crop)&(dd.처리==t)][par].dropna().values,CROPC[crop][t],FILLED[t],0.66))
        if q.ANOVA_P.iloc[0]<0.05:
            for k,t in enumerate(ORDER,1): ax.text(k,max(tops)*1.04,q.loc[t,'Tukey'],ha='center',fontsize=8)
        ax.set_ylim(0,max(tops)*1.25); ax.set_ylabel(lab+' (µmol m$^{-2}$ s$^{-1}$)',fontsize=7.5); ax.tick_params(labelsize=7)
        ax.set_xticks(range(1,5)); ax.set_xticklabels([F.SHORT[t] for t in ORDER] if xt else [],fontsize=6.5)
    fig.savefig(f'{crop}_3_photo.png'); plt.close(fig)
def p4(crop):
    fig=newfig(); ax=fig.add_axes([L,B,R-L,T-B])
    if crop=='bean': vals={t:b.loc[b.처리==t,'알 F.W'].dropna() for t in ORDER}; lab='Seed FW (g·plant$^{-1}$)'
    else: vals={t:r.loc[r.처리==t,'지상부건조중_전체'].dropna() for t in ORDER}; lab='Shoot DW (g·plant$^{-1}$)'
    ff.bars(ax,vals,crop,lab,gray=False); ax.set_ylabel(lab,fontsize=8); ax.set_xticks(range(4)); ax.set_xticklabels([F.SHORT[t] for t in ORDER],fontsize=6.5)
    fig.savefig(f'{crop}_4_growth.png'); plt.close(fig)
for c in ('bean','lettuce'): p1(c); p2(c); p3(c); p4(c)
