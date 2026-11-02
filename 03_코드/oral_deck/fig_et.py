import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, openpyxl, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
R='/home/user/-/'
CROPC={'lettuce':{'ETc':'#1F3D2B','ETc50':'#8FAA91','침수ETc':'#2E7D4F','침수ETc50':'#9FD3A8'},'bean':{'ETc':'#3B2618','ETc50':'#B9A28C','침수ETc':'#8B5A2B','침수ETc50':'#E0B98A'}}
ACC={'lettuce':'#2E6B3F','bean':'#6B4226'}
MK={'ETc':'o','ETc50':'o','침수ETc':'s','침수ETc50':'s'}; FIL={'ETc':True,'ETc50':False,'침수ETc':True,'침수ETc50':False}; LS={'ETc':'-','ETc50':'-','침수ETc':(0,(4,1.6)),'침수ETc50':(0,(4,1.6))}
NAME={'ETc':'Control','ETc50':'Drought','침수ETc':'Waterlogging','침수ETc50':'Combined'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.8,'legend.frameon':False})
def sh(f,n):
    ws=openpyxl.load_workbook(R+f,data_only=True,read_only=True)[n]; X=[r for r in ws.iter_rows(values_only=True) if any(x is not None for x in r)]
    return pd.DataFrame(X[1:],columns=X[0])
f1='증산량/증산량_로메인상추_1007-1010.xlsx'; f2='증산량/증산량_로메인상추_1011-1023.xlsx'
a1=sh(f1,'증산량(ETc,침ETc)').dropna(subset=['날짜']); a2=sh(f2,'증산량(ETc,침ETc)'); b2=sh(f2,'관수량(ETc50,침ETc,침50)')
rows=[]
# 대조·침수: 증산량 시트의 '증산량(g)' (전날 관수 후 − 당일 관수 전)
for df,col in [(a1,'증산량(g)'),(a2,'증산량(g)')]:
    for r in df.itertuples(index=False):
        d=dict(zip(df.columns,r))
        if d['Treatment'] in('ETc','침수 ETc') and d[col] is not None and not pd.isna(d[col]):
            rows.append(dict(날짜=d['날짜'],처리={'ETc':'ETc','침수 ETc':'침수ETc'}[d['Treatment']],반복=int(d['Repeat']),et=float(d[col])))
# 건조·복합: 관수량 시트 (전날 관수 후 − 당일 관수 전, 연속일만)
b=b2[b2.Treatment.isin(['ETc 50','침수50'])].copy(); b['Repeat']=b.Repeat.astype(int); b['d']=pd.to_datetime(b.날짜)
for (t,rep),g in b.groupby(['Treatment','Repeat']):
    g=g.sort_values('d').set_index('d')
    for d0 in g.index[1:]:
        prev=d0-pd.Timedelta(days=1)
        if prev in g.index:
            rows.append(dict(날짜=d0.strftime('%Y-%m-%d'),처리={'ETc 50':'ETc50','침수50':'침수ETc50'}[t],반복=rep,et=float(g.loc[prev,'관수 후(g)']-g.loc[d0,'관수 전(g)'])))
E_=pd.DataFrame(rows); E_['DAT']=(pd.to_datetime(E_.날짜)-pd.Timestamp('2026-10-07')).dt.days
G=E_.groupby(['처리','DAT']).et.agg(['mean','sem','count']).reset_index(); G.to_csv('intermediate/romaine_daily_et.csv',index=False)
print(G.pivot(index='DAT',columns='처리',values='mean').round(0).to_string()); print(G.groupby('처리')['count'].agg(['min','max']).to_string())
# soybean (loadcell, mm/day -> g/pot/day with 38.01 g/mm)
s=pd.read_csv(R+'data/17_밭콩_일물소모_로드셀vsEC5.csv'); s['DAT']=(pd.to_datetime(s.date)-pd.Timestamp('2026-08-12')).dt.days; s['g']=s.lc_mm*38.01
S=s.rename(columns={'t':'처리'}); S=S[S.g>0]
S.to_csv('intermediate/soy_daily_et.csv',index=False)
fig,axs=plt.subplots(1,3,figsize=(7.7,3.0),dpi=300,gridspec_kw={'width_ratios':[0.75,1.45,1.0]})
ax=axs[0]; xx=np.arange(3); irr={'bean':[40,87,44],'lettuce':[43,56,37]}
for i,crop in enumerate(['lettuce','bean']):
    xs=xx+(i-0.5)*0.38; ax.bar(xs,irr[crop],0.36,color=ACC[crop])
    for xi,v in zip(xs,irr[crop]): ax.text(xi,v+2,f'{v}',ha='center',fontsize=6.8)
ax.axhline(50,color='#B5651D',lw=1,ls=':'); ax.text(2.55,52,'design 50%',fontsize=6,color='#B5651D',ha='right',va='bottom')
ax.set_xticks(xx,['Dr.','Wl.','Comb.'],fontsize=7.5); ax.set_ylim(0,112); ax.set_ylabel('Cumulative irrigation\n(% of control)',fontsize=8); ax.set_title('Irrigation applied',loc='left',fontsize=9,fontweight='bold')
ax.legend([Patch(color=ACC['lettuce']),Patch(color=ACC['bean'])],['Romaine','Soybean'],fontsize=6.5,loc='upper left',bbox_to_anchor=(0.0,1.02),ncol=1)
ax=axs[1]; ax.axvspan(0,3,color='#E6E6E6',lw=0)
for t in ['ETc','ETc50','침수ETc']:
    g=S[S.처리==t].sort_values('DAT'); c=CROPC['bean'][t]
    ax.plot(g.DAT,g.g,color=c,ls=LS[t],lw=1.1,marker=MK[t],ms=2.6,mfc=c if FIL[t] else 'white',mec=c,mew=0.8)
ax.set_title('Soybean daily transpiration',loc='left',fontsize=9,fontweight='bold',color=ACC['bean']); ax.set_ylabel('g·pot$^{-1}$·day$^{-1}$',fontsize=8); ax.set_xlabel('DAT')
ax=axs[2]; ax.axvspan(0,3,color='#E6E6E6',lw=0)
for t in ['ETc','ETc50','침수ETc','침수ETc50']:
    g=G[G.처리==t].sort_values('DAT'); c=CROPC['lettuce'][t]
    ax.fill_between(g.DAT,g['mean']-g['sem'].fillna(0),g['mean']+g['sem'].fillna(0),color=c,alpha=0.15,lw=0)
    ax.plot(g.DAT,g['mean'],color=c,ls=LS[t],lw=1.2,marker=MK[t],ms=2.8,mfc=c if FIL[t] else 'white',mec=c,mew=0.8)
ax.set_title('Romaine',loc='left',fontsize=9,fontweight='bold',color=ACC['lettuce']); ax.set_xlabel('DAT'); ax.set_ylabel('g·pot$^{-1}$·day$^{-1}$',fontsize=8)
hs=[tuple(Line2D([],[],color=CROPC[c][t],lw=1.4,ls=LS[t],marker=MK[t],ms=4.5,mfc=CROPC[c][t] if FIL[t] else 'white',mec=CROPC[c][t]) for c in ('lettuce','bean')) for t in ['ETc','ETc50','침수ETc','침수ETc50']]
from matplotlib.legend_handler import HandlerTuple
fig.legend(hs,[NAME[t] for t in ['ETc','ETc50','침수ETc','침수ETc50']],loc='upper center',ncol=4,fontsize=7.6,handler_map={tuple:HandlerTuple(ndivide=None,pad=0.3)},handlelength=3.0,columnspacing=1.6)
fig.tight_layout(rect=(0,0,1,0.9),w_pad=0.8); fig.savefig('figs2/et_daily.png'); plt.close(fig)
