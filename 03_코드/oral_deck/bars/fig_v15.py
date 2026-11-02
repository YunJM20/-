import warnings; warnings.filterwarnings('ignore')
import numpy as np
import fig_v13 as F
from fo_common import *
# geometry of the existing panel ① in the recap image (12.2 x 3.9 in, placed at slide (0.55, 2.35))
fig0=plt.figure(figsize=(12.2,3.9)); gs=fig0.add_gridspec(1,4,wspace=0.3,left=0.055,right=0.995,top=0.9,bottom=0.15,width_ratios=[1.15,0.8,0.95,0.95])
l,r=gs.get_grid_positions(fig0)[2][0],gs.get_grid_positions(fig0)[3][0]; plt.close(fig0)
AX_W=(r-l)*12.2; AX_L=l*12.2; print('axes width in',round(AX_W,2),'left offset in',round(AX_L,2))
PAD=0.85
def one(crop,fname):
    st,P=F.stats('gsw',crop,'P2'); W=AX_W+PAD+0.05; H=3.9
    fig=plt.figure(figsize=(W,H),dpi=300); ax=fig.add_axes([PAD/W,0.15,AX_W/W,0.75]); top=0
    for k,t in enumerate(ORDER):
        m,se,lt=st[t]
        if t in ('ETc','침수ETc'): c=CROPC[crop][t]
        else: c=GRAY[t]
        if FILLED[t]: ax.bar(k,m,0.72,color=c)
        else: ax.bar(k,m,0.72,facecolor='white',edgecolor=c,linewidth=1.6,hatch='////' if t=='침수ETc50' else None)
        ax.errorbar(k,m,se,color='#333',capsize=3,lw=1.1); top=max(top,m+se)
        if P<0.05: ax.text(k,m+se,lt,ha='center',va='bottom',fontsize=9)
    ax.set_ylim(0,top*1.22); ax.set_xlim(-0.6,3.6); ax.set_xticks(range(4)); ax.set_xticklabels([F.SHORT[t] for t in ORDER],fontsize=8)
    ax.set_ylabel('g$_{sw}$ (mol·m$^{-2}$·s$^{-1}$)',fontsize=9); ax.tick_params(axis='y',labelsize=8)
    fig.savefig('figs5/'+fname); plt.close(fig); print(fname,W,H,round(P,4),{k:(round(v[0],3),v[2]) for k,v in st.items()})
one('bean','gsw_P2_bean.png'); one('lettuce','gsw_P2_lettuce.png')
