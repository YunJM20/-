import warnings; warnings.filterwarnings('ignore')
import fo_common as fc
from fo_common import *
A=pd.read_csv('intermediate/daily_gsw_raw.csv')
CL={c:sorted(A[(A.작물==c)&(A.흐림==True)].DAT.unique()) for c in ('bean','lettuce')}
D='/home/user/-/data/'
m=pd.read_csv(D+'23_밭콩_일별_관수량_마스터시트17.csv'); m=m[m['Scored (Aug 16-)']=='Yes']
m=m[~m.Status.str.startswith(('No irrigation','Skipped'))]   # 관수 안 한 날 = 결측
m['DAT']=(pd.to_datetime(m.Date)-pd.Timestamp('2026-08-12')).dt.days
m['t']=m.Treatment.map({'ETc 100%':'ETc','ETc 50%':'ETc50','Flooding-ETc 100%':'침수ETc','Flooding-ETc 50%':'침수ETc50'}); m['v']=m['Load cell irrigation (g)']
l=pd.read_csv(D+'13_잎상추_일별_관수량_로드셀CSV.csv'); l['DAT']=(pd.to_datetime(l.날짜)-pd.Timestamp('2026-10-07')).dt.days
l['t']=l['처리(한글)'].map({'대조구':'ETc','건조':'ETc50','침수':'침수ETc','복합':'침수ETc50'}); l['v']=l['사용값(g/개체)']
fig,axs=plt.subplots(1,2,figsize=(11.6,2.45),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
for ax,crop,d in zip(axs,['bean','lettuce'],[m,l]):
    flood_span(ax)
    for x in CL[crop]:
        if x>=3: ax.axvspan(x-0.45,x+0.45,color=CLOUDC,lw=0,zorder=0)
    for t in ORDER:
        g=d[d.t==t].sort_values('DAT'); c=col(crop,t)
        full=pd.DataFrame({'DAT':range(int(g.DAT.min()),int(g.DAT.max())+1)}).merge(g[['DAT','v']],how='left')  # 빠진 날은 선을 끊음
        ax.plot(full.DAT,full.v,color=c,ls=LS[t],lw=1.3,marker=MK[t],ms=3.4,mfc=c if FILLED[t] else 'white',mec=c,mew=1)
    ax.set_xlabel('Days after waterlogging start (DAT)'); ax.set_xlim(*((-2,56) if crop=='bean' else (-0.5,17))); ax.set_ylim(bottom=0)
    ax.set_ylabel('Daily irrigation (g·%s$^{-1}$·day$^{-1}$)'%('pot' if crop=='bean' else 'plant'))
    ax.axvline(10.5,color='0.55',ls=':',lw=1,zorder=1)
legend2(fig,E_crops()+E_trt(('bean','lettuce'))+[E_cloud(),E_flood()],8,fontsize=7.6)
fig.tight_layout(rect=(0,0,1,0.87),w_pad=1.5); fig.savefig('figs6/irr_daily_cloud.png'); plt.close(fig)
