import warnings; warnings.filterwarnings('ignore')
import fo_common as fc
from fo_common import *
import fo_figs as ff
d=pd.read_csv('intermediate/daily_fvfm.csv'); d['흐림']=False; D=d
fc.A04=pd.concat([fc.A04,d],ignore_index=True)
XL={'bean':(-2.5,32),'lettuce':(-3.6,17.5)}
YL='F$_v$/F$_m$'
from matplotlib.lines import Line2D as L2
def split29(ax):
    for ln in list(ax.lines):
        x=np.asarray(ln.get_xdata(),float)
        if len(x)>2 and x.max()==29 and (x==8).any():
            y=np.asarray(ln.get_ydata(),float); kw=dict(color=ln.get_color(),marker=ln.get_marker(),ms=ln.get_markersize(),mfc=ln.get_markerfacecolor(),mec=ln.get_markeredgecolor(),mew=ln.get_markeredgewidth(),ls='none')
            ln.set_data(x[x<29],y[x<29]); ax.plot(x[x==29],y[x==29],**kw)
    from matplotlib.collections import PolyCollection
    cols=[(c.get_facecolor()[0].copy(),c) for c in ax.collections if isinstance(c,PolyCollection) and c.get_hatch() is None]
    for _,c in cols: c.remove()
    sub=D[D.작물=='bean']
    for t in ORDER:
        g=sub[sub.처리==t].sort_values('DAT'); cc=col('bean',t)
        for m in (g.DAT<29,g.DAT>=29):
            h=g[m]
            if len(h)>1: ax.fill_between(h.DAT,h.평균-h.SE,h.평균+h.SE,color=cc,alpha=0.16,lw=0)
            elif len(h)==1: ax.errorbar(h.DAT,h.평균,h.SE,color=cc,lw=1,capsize=0,zorder=1)
def ts():
    fig,axs=plt.subplots(1,2,figsize=(7.5,2.55),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
    for ax,crop in zip(axs,['bean','lettuce']):
        fc.ts_axes(ax,crop,'fvfm',YL); split29(ax) if crop=='bean' else None; ax.set_xlim(*XL[crop])
        lo,hi=ax.get_ylim(); ax.set_ylim(lo,hi)
    legend2(fig,E_crops()+E_trt(('bean','lettuce'))+[E_flood()],4)
    fig.tight_layout(rect=(0,0,1,0.84),w_pad=1.5); fig.savefig('figs6/fvfm_ts.png'); plt.close(fig)
def rec():
    fig,axs=plt.subplots(1,2,figsize=(7.5,2.55),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
    for ax,crop in zip(axs,['bean','lettuce']):
        ff.rec_ax(ax,crop,ylim=(95,102),path=f'intermediate/recovery_fvfm_{crop}.csv'); split29(ax) if crop=='bean' else None; ax.set_xlim(*XL[crop])
    axs[0].set_ylabel('F$_v$/F$_m$ (% of control)')
    legend2(fig,E_crops()+ff.rec_handles(),4)
    fig.tight_layout(rect=(0,0,1,0.84),w_pad=1.5); fig.savefig('figs6/fvfm_rec.png'); plt.close(fig)
import os; os.makedirs('figs6',exist_ok=True); ts(); rec()
