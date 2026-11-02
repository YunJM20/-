import warnings; warnings.filterwarnings('ignore')
import fo_common as fc
from fo_common import *
A=pd.read_csv('intermediate/daily_gsw_raw.csv')
CL={c:sorted(A[(A.작물==c)&(A.흐림==True)].DAT.unique()) for c in ('bean','lettuce')}
S=pd.read_csv('intermediate/soy_daily_et.csv'); G=pd.read_csv('intermediate/romaine_daily_et.csv')
YL='Daily transpiration (g·pot$^{-1}$·day$^{-1}$)'
fig,axs=plt.subplots(1,2,figsize=(11.6,2.45),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
for ax,crop in zip(axs,['bean','lettuce']):
    flood_span(ax)
    for d in CL[crop]:
        if d>=3: ax.axvspan(d-0.45,d+0.45,color=CLOUDC,lw=0,zorder=0)
    for t in ORDER:
        if crop=='bean': g=S[S.처리==t].sort_values('DAT').rename(columns={'g':'m'}); se=None
        else: g=G[G.처리==t].sort_values('DAT').rename(columns={'mean':'m'}); se=g['sem'].fillna(0)
        if g.empty: continue
        c=col(crop,t)
        if se is not None: ax.fill_between(g.DAT,g.m-se,g.m+se,color=c,alpha=0.16,lw=0)
        ax.plot(g.DAT,g.m,color=c,ls=LS[t],lw=1.3,marker=MK[t],ms=3.4,mfc=c if FILLED[t] else 'white',mec=c,mew=1)
    ax.set_xlabel('Days after waterlogging start (DAT)'); ax.set_xlim(*((-2,56) if crop=='bean' else (-0.5,17)))
    ax.set_ylim(bottom=0)
    if crop=='bean': ax.set_ylabel(YL)
    bnd=10.5; ax.axvline(bnd,color='0.55',ls=':',lw=1,zorder=1)
legend2(fig,E_crops()+E_trt(('bean','lettuce'))+[E_cloud(),E_flood()],8,fontsize=7.6)
fig.tight_layout(rect=(0,0,1,0.87),w_pad=1.5); fig.savefig('figs6/et_daily_cloud.png'); plt.close(fig)
print(CL)
