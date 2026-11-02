import warnings; warnings.filterwarnings('ignore')
from fo_common import *
S=pd.read_csv('intermediate/soy_daily_et.csv'); S['ec']=S.ec_mm*38.01
fig,axs=plt.subplots(1,3,figsize=(11.6,2.6),dpi=250,sharey=True)
for ax,t in zip(axs,['ETc','ETc50','침수ETc']):
    g=S[S.처리==t].sort_values('DAT'); c=col('bean',t)
    ax.plot(g.DAT,g.g,color=c,marker='o',ms=3,lw=1.2,label='Load cell'); h=g.dropna(subset=['ec'])
    ax.plot(h.DAT,h.ec,color='0.45',marker='^',ms=3,lw=1,ls='--',label='EC5-derived')
    ax.set_title(NAME[t],loc='left',fontsize=9); ax.set_xlabel('DAT'); ax.legend(fontsize=7)
axs[0].set_ylabel('Daily water use (g·pot$^{-1}$·day$^{-1}$)')
fig.tight_layout(); fig.savefig('figs6/bean_loadcell_vs_EC5.png'); plt.close(fig)
print(S[S.DAT.between(21,27)].pivot(index='DAT',columns='처리',values=['g','ec']).round(0))
print(S.groupby('처리')[['g','ec']].apply(lambda d:d.dropna().corr().iloc[0,1]))
