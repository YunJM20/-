import warnings; warnings.filterwarnings('ignore')
import numpy as np
import fig_v13 as F
from fo_common import *
TR=['ETc50','침수ETc','침수ETc50']
def pct_panel(ax,ind,crop,xlab=True,ylab=True):
    xpos=0; ticks=[]; labs=[]; groups=[]; top=0; bounds=[]
    for per in ['P1','P2']:
        st,P=F.stats(ind,crop,per); mc,sc,lc=st['ETc']; start=xpos
        for t in TR:
            if t not in st: continue
            m,se,l=st[t]; r=m/mc*100; sr=r*np.sqrt((se/m)**2+(sc/mc)**2); c=CROPC[crop][t]
            if FILLED[t]: ax.bar(xpos,r,0.78,color=c)
            else: ax.bar(xpos,r,0.78,facecolor='white',edgecolor=c,linewidth=1.5,hatch='////' if t=='침수ETc50' else None)
            ax.errorbar(xpos,r,sr,color='#333',capsize=2.5,lw=1); top=max(top,r+sr)
            if P<0.05 and not (set(l)&set(lc)): ax.text(xpos,r+sr,'*',ha='center',va='bottom',fontsize=11)
            ticks.append(xpos); labs.append(F.SHORT[t]); xpos+=1
        groups.append((per,(start+xpos-1)/2)); bounds.append((start,xpos-1)); xpos+=0.9
    ax.axhline(100,color='0.4',ls='--',lw=0.9,zorder=0)
    mid=(bounds[0][1]+bounds[1][0])/2; ax.axvline(mid,color='0.55',ls=':',lw=1.1,zorder=0)
    ax.set_ylim(0,max(top*1.15,125)); ax.set_xlim(-0.7,bounds[1][1]+0.7); ax.set_xticks(ticks); ax.set_xticklabels(labs if xlab else [],fontsize=6.5); ax.tick_params(axis='y',labelsize=7)
    if ylab: ax.set_ylabel(F.LAB[ind].split(' (')[0]+' (% of control)',fontsize=8.5)
    if xlab:
        for per,xc in groups: ax.text(xc,-0.2,per,ha='center',va='top',fontsize=8.5,fontweight='bold',color='0.35',transform=ax.get_xaxis_transform())
def make(inds,size,fname,adjust):
    r=len(inds); wr=[4+0.9,6+0.9]
    fig,axs=plt.subplots(r,2,figsize=size,dpi=300,gridspec_kw={'width_ratios':wr}); axs=np.atleast_2d(axs)
    for i,ind in enumerate(inds):
        for j,crop in enumerate(['bean','lettuce']): pct_panel(axs[i,j],ind,crop,xlab=(i==r-1),ylab=(j==0))
    hs=[(tuple(Patch(color=CROPC[c][t]) if FILLED[t] else Patch(facecolor='white',edgecolor=CROPC[c][t],lw=1.4,hatch='////' if t=='침수ETc50' else None) for c in ('bean','lettuce')),NAME[t]) for t in TR]
    legend2(fig,E_crops()+hs+[(Line2D([],[],color='0.4',ls='--',lw=1),'Control = 100%'),(Line2D([],[],color='none',marker='$*$',mfc='0.2',mec='0.2',ms=7),'differs from control')],3 if r==1 else 4,fontsize=7.2,hl=2.0)
    fig.subplots_adjust(**adjust); fig.savefig('figs5/'+fname); plt.close(fig)
make(['gsw'],(7.5,2.55),'pct_gsw.png',dict(left=0.09,right=0.99,top=0.74,bottom=0.25,wspace=0.22))
make(['phi','phinpq','phino'],(7.2,5.3),'pct_phi3.png',dict(left=0.095,right=0.99,top=0.88,bottom=0.085,hspace=0.2,wspace=0.22))
print('ok')
