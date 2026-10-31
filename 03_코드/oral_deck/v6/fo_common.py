import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.legend_handler import HandlerTuple
R='/home/user/-/'
ORDER=['ETc','ETc50','침수ETc','침수ETc50']
NAME={'ETc':'Control','ETc50':'Drought','침수ETc':'Waterlogging','침수ETc50':'Combined'}
CROPC={'lettuce':{'ETc':'#1F3D2B','ETc50':'#8FAA91','침수ETc':'#2E7D4F','침수ETc50':'#9FD3A8'},'bean':{'ETc':'#3B2618','ETc50':'#B9A28C','침수ETc':'#8B5A2B','침수ETc50':'#E0B98A'}}
ACC={'lettuce':'#2E6B3F','bean':'#6B4226'}; CN={'lettuce':'Romaine','bean':'Soybean'}
MK={'ETc':'o','ETc50':'o','침수ETc':'s','침수ETc50':'s'}; FILLED={'ETc':True,'ETc50':False,'침수ETc':True,'침수ETc50':False}
LS={'ETc':'-','ETc50':'-','침수ETc':(0,(4,1.6)),'침수ETc50':(0,(4,1.6))}
PREC='#9A9A9A'; CLOUDC='#E9E9E9'
GRAY={'ETc50':'#CBCBCB','침수ETc50':'#B0B0B0'}; GLW=0.9; GMS=3.0   # 10p: 건조·복합 = 회색
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.8,
  'xtick.major.width':0.8,'ytick.major.width':0.8,'legend.frameon':False})
def col(crop,t): return CROPC[crop][t]
def handle(crops,t,line=True,gray=False):
    hs=[]
    for c in crops:
        cc=(GRAY[t] if (gray and t in GRAY) else CROPC[c][t])
        hs.append(Line2D([],[],color=cc,lw=1.6 if line else 0,ls=LS[t] if line else 'none',marker=MK[t],ms=5.5,mfc=cc if FILLED[t] else 'white',mec=cc,mew=1.3))
    return tuple(hs)
def rowwise(hs,ls,ncol):
    n=len(hs); nr=-(-n//ncol); grid=[[None]*ncol for _ in range(nr)]
    for i,(h,l) in enumerate(zip(hs,ls)): grid[i//ncol][i%ncol]=(h,l)
    H=[];L=[]
    for c in range(ncol):
        for r in range(nr):
            e=grid[r][c]
            if e is None: H.append(Line2D([],[],lw=0)); L.append('')
            else: H.append(e[0]); L.append(e[1])
    return H,L
def E_trt(crops,trts=ORDER,line=True,gray=False): return [(handle(crops,t,line,gray),NAME[t]) for t in trts]
E_pre=lambda: (Line2D([],[],color=PREC,lw=1.2,ls='--',marker='x',ms=5),'Pre-treatment')
E_cloud=lambda: (Patch(color=CLOUDC),'Cloudy (CI<0.5)')
FLOODKW=dict(facecolor='#F4F4F4',edgecolor='#A8A8A8',hatch='////',linewidth=0)
E_flood=lambda: (Patch(facecolor='#F4F4F4',edgecolor='#A8A8A8',hatch='////',linewidth=0),'Waterlogging period')
def flood_span(ax,x0=0,x1=3): ax.axvspan(x0,x1,zorder=0,**FLOODKW)
E_crops=lambda crops=('bean','lettuce'): [(Patch(color=ACC[c]),CN[c]) for c in crops]
def legend2(fig,ents,ncol,fontsize=7.2,y=1.0,hl=2.6,cs=1.1,tup=True):
    H,L=rowwise([e[0] for e in ents],[e[1] for e in ents],ncol)
    fig.legend(H,L,loc='upper center',bbox_to_anchor=(0.5,y),ncol=ncol,fontsize=fontsize,handler_map={tuple:HandlerTuple(ndivide=None,pad=0.3)},handlelength=hl,columnspacing=cs,handletextpad=0.5,labelspacing=0.35)
A04=pd.read_csv('intermediate/daily_stats.csv'); A04=A04[A04.지표!='gsw']; A04=pd.concat([A04,pd.read_csv('intermediate/daily_gsw_raw.csv')],ignore_index=True); A04=A04[~((A04.작물=='lettuce')&(A04.DAT<1))]
PRE=pd.read_csv('data/02b_LI600_처리전_개별측정.csv'); PRECOL={'gsw':'gsw_해석용','phi':'PhiPS2','fs':'Fs','etr':'ETR'}
def ts_axes(ax,crop,ind,ylab=None,gray=False):
    s=A04[(A04.지표==ind)&(A04.작물==crop)]
    flood_span(ax)
    for d in s[s.흐림==True].DAT.unique():
        x0,x1=max(d-0.45,3.0),d+0.45
        if x1>x0: ax.axvspan(x0,x1,color=CLOUDC,lw=0,zorder=0)
    for t in ORDER:
        g=s[s.처리==t].sort_values('DAT')
        if g.empty: continue
        c=GRAY[t] if (gray and t in GRAY) else col(crop,t)
        ax.fill_between(g.DAT,g.평균-g.SE,g.평균+g.SE,color=c,alpha=0.16,lw=0)
        ax.plot(g.DAT,g.평균,color=c,ls=LS[t],lw=1.5,marker=MK[t],ms=4.2,mfc=c if FILLED[t] else 'white',mec=c,mew=1.1)
    pr=PRE[PRE.작물==crop][PRECOL[ind]].dropna(); px=-5 if crop=='bean' else -1.5
    ax.errorbar(px,pr.mean(),pr.sem(),fmt='x',color=PREC,ms=5,capsize=2,lw=1)
    ymax=max((s.평균+s.SE).max(),pr.mean()+pr.sem()); ymin=min((s.평균-s.SE).min(),pr.mean()-pr.sem()); span=ymax-ymin
    for d,g in s.groupby('DAT'):
        if g['당일_ANOVA_P_Holm'].iloc[0]<0.05: ax.text(d,(g.평균+g.SE).max()+span*0.04,'*',ha='center',va='bottom',fontsize=10,color='0.2')
    ax.set_ylim(ymin-span*0.05,ymax+span*0.2)
    bnd=10.5; ax.axvline(bnd,color='0.55',ls=':',lw=1,zorder=1)
    ax.text(bnd-0.8,ax.get_ylim()[0],'P1',ha='right',va='bottom',fontsize=8,color='0.4'); ax.text(bnd+0.8,ax.get_ylim()[0],'P2',ha='left',va='bottom',fontsize=8,color='0.4')
    ax.set_xlabel('Days after waterlogging start (DAT)')
    if ylab and crop=='bean': ax.set_ylabel(ylab)
def ts_fig2(ind,ylab,fname,size=(7.5,3.0)):
    fig,axs=plt.subplots(1,2,figsize=size,dpi=300,gridspec_kw={'width_ratios':[1.25,1]})
    for ax,crop in zip(axs,['bean','lettuce']): ts_axes(ax,crop,ind,ylab)
    legend2(fig,E_crops()+E_trt(('bean','lettuce'))+[E_pre(),E_cloud(),E_flood()],5)
    fig.tight_layout(rect=(0,0,1,0.85),w_pad=1.5); fig.savefig('figs2/'+fname); plt.close(fig)
if __name__=='__main__':
    ts_fig2('gsw','g$_{sw}$ (mol·m$^{-2}$·s$^{-1}$)','ts_gsw.png',size=(7.5,3.0))
    ts_fig2('phi','Φ$_{PSII}$','ts_phi.png',size=(7.5,3.0))
    ts_fig2('fs','F$_s$','ts_fs.png',size=(7.5,3.0))
    ts_fig2('etr','ETR (µmol·m$^{-2}$·s$^{-1}$)','ts_etr.png',size=(7.5,3.0))
    print('ts ok')
