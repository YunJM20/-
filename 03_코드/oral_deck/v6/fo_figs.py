import sys; sys.path.insert(0,'.')
from fo_common import *
import matplotlib.dates as md
from matplotlib.patches import Patch
from stats2x2 import tukey_letters
import os
os.makedirs('figs3',exist_ok=True)
FD='figs3/'; FLOOD='#D2D2D2'
def save(fig,n,rect=None):
    if rect: fig.tight_layout(rect=rect,w_pad=1.0)
    fig.savefig(FD+n); plt.close(fig)
# ---------- env
def env():
    e1=pd.read_csv(R+'data/19_환경_밭콩_일별.csv'); e2=pd.read_csv(R+'로메인data/25_환경_일별.csv')
    e1['날짜']=pd.to_datetime(e1['날짜']); e2['날']=pd.to_datetime(e2['날'])
    miss=[c for c in e2.columns if '결측' in c][0]
    e2=e2[~e2[miss].astype(str).str.contains('True|결측|1',na=False)] if e2[miss].dtype==object else e2[e2[miss]==False]
    fig,axs=plt.subplots(1,2,figsize=(7.7,3.0),dpi=300)
    for ax,(c1,c2,yl) in zip(axs,[('평균기온','평균기온','Mean air temp. (°C)'),('DLI_mol','DLI_추정(mol m-2 d-1)','DLI (mol·m$^{-2}$·day$^{-1}$)')]):
        s=e1[e1.날짜>='2026-08-12']; ax.plot(s.날짜,s[c1],color=ACC['bean'],lw=1.5)
        t=e2[e2.날>='2026-10-07']; ax.plot(t.날,t[c2],color=ACC['lettuce'],lw=1.5)
        ax.axvline(pd.Timestamp('2026-08-12'),color=ACC['bean'],ls=':',lw=1); ax.axvline(pd.Timestamp('2026-10-07'),color=ACC['lettuce'],ls=':',lw=1)
        ax.xaxis.set_major_locator(md.MonthLocator()); ax.xaxis.set_major_formatter(md.DateFormatter('%b %d')); ax.set_ylabel(yl); ax.set_xlabel('Date (2026)')
    legend2(fig,E_crops()+[(Line2D([],[],color='0.4',ls=':',lw=1.2),'Waterlogging start')],3,fontsize=8)
    save(fig,'env.png',(0,0,1,0.88))
# ---------- irrigation + cumulative transpiration
def cum():
    import openpyxl
    fig,axs=plt.subplots(1,3,figsize=(7.7,3.0),dpi=300,gridspec_kw={'width_ratios':[0.8,1.2,1.0]})
    ax=axs[0]; xx=np.arange(3); irr={'bean':[40,87,44],'lettuce':[43,56,37]}
    for i,crop in enumerate(['lettuce','bean']):
        xs=xx+(i-0.5)*0.38; ax.bar(xs,irr[crop],0.36,color=ACC[crop])
        for xi,v in zip(xs,irr[crop]): ax.text(xi,v+2,f'{v}',ha='center',fontsize=7)
    ax.set_xticks(xx,['Dr.','Wl.','Comb.'],fontsize=7.5); ax.set_ylim(0,112); ax.set_ylabel('Cumulative irrigation (% of control)',fontsize=7.5)
    # soybean: load-cell irrigation 8/16-10/6 (DAT 4-55), mm x 38.01 g/mm
    d=pd.read_csv(R+'data/23_밭콩_일별_관수량_마스터시트17.csv',encoding='utf-8-sig'); d=d[d['Scored (Aug 16-)'].astype(str).str.startswith('Yes')&(d.Date<='2026-10-06')]
    p_=d.pivot_table(index='Date',columns='Treatment',values='Load cell irrigation (mm)',aggfunc='sum'); p_.index=(pd.to_datetime(p_.index)-pd.Timestamp('2026-08-12')).days
    mp={'ETc':'ETc 100%','ETc50':'ETc 50%','침수ETc':'Flooding-ETc 100%','침수ETc50':'Flooding-ETc 50%'}
    ax=axs[1]; flood_span(ax); out={}
    for t in ORDER:
        cs=(p_[mp[t]]*38.01/1000).cumsum(); out[('bean',t)]=cs.iloc[-1]; ax.plot(cs.index,cs.values,color=CROPC['bean'][t],ls=LS[t],lw=1.5)
    ax.set_xlabel('Days after waterlogging start (DAT)'); ax.set_ylabel('Cumulative irrigation (kg·pot$^{-1}$)',fontsize=7.5)
    # romaine: 10/12-10/22 (DAT 5-15); control = load-cell mean irrigation, others = irrigation sheet
    def sh(f,n):
        ws=openpyxl.load_workbook(R+f,data_only=True,read_only=True)[n]; X=[r for r in ws.iter_rows(values_only=True) if any(x is not None for x in r)]; return pd.DataFrame(X[1:],columns=X[0])
    f2='증산량/증산량_로메인상추_1011-1023.xlsx'
    b=sh(f2,'관수량(ETc50,침ETc,침50)'); b['d']=pd.to_datetime(b['날짜']); b['g']=pd.to_numeric(b['관수량(g)'],errors='coerce'); b=b[b.d<='2026-10-22']
    c=sh(f2,'로드셀관수량(ETc)'); c['d']=pd.to_datetime(c['날짜']); c=c[c.d<='2026-10-22']
    ser={'ETc':c.set_index('d')['평균관수량(g)'].astype(float),'ETc50':b[b.Treatment=='ETc 50'].groupby('d').g.mean(),'침수ETc':b[b.Treatment=='침수 ETc'].groupby('d').g.mean(),'침수ETc50':b[b.Treatment=='침수50'].groupby('d').g.mean()}
    ax=axs[2]; flood_span(ax)
    for t in ORDER:
        s=ser[t].fillna(0); s.index=(s.index-pd.Timestamp('2026-10-07')).days; cs=s.cumsum(); out[('lettuce',t)]=cs.iloc[-1]; ax.plot(cs.index,cs.values,color=CROPC['lettuce'][t],ls=LS[t],lw=1.5)
    ax.set_xlim(0,16); ax.set_xlabel('DAT'); ax.set_ylabel('Cumulative irrigation (g·pot$^{-1}$)',fontsize=7.5)
    print({k:round(v,1) for k,v in out.items()})
    legend2(fig,E_crops()+E_trt(('bean','lettuce')),3,fontsize=7.5)
    save(fig,'irr_cum.png',(0,0,1,0.84))

def rec_ax(ax,crop,ylim=None,lw=1.5):
    r=pd.read_csv(f'intermediate/recovery_raw_{crop}.csv'); flood_span(ax); ax.axhline(100,color='0.45',lw=0.8,ls='--')
    for t in ['침수ETc','ETc50','침수ETc50']:
        g=r[r.처리==t].sort_values('DAT'); gr=t in GRAY; col=GRAY[t] if gr else CROPC[crop][t]; fil=t=='침수ETc'
        kw=dict(color=col,ls=LS[t],lw=GLW if gr else lw,marker=MK[t],ms=GMS if gr else 4.2,mfc=col if fil else 'white',mec=col,mew=0.8 if gr else 1.1,zorder=2 if gr else 3)
        if crop=='bean' and t=='침수ETc':
            e=g.DAT<=9; ax.plot(g.DAT[e],g.ratio[e],**kw); ax.plot([9,17],[g[g.DAT==9].ratio.iloc[0],g[g.DAT==17].ratio.iloc[0]],':',color=col,lw=1.2); ax.plot(g.DAT[~e],g.ratio[~e],**kw)
        else: ax.plot(g.DAT,g.ratio,**kw)
        for _,rw in g[g.pH<0.05].iterrows(): ax.text(rw.DAT,rw.ratio-14,'*',ha='center',color=col if not gr else '#9A9A9A',fontsize=9 if gr else 10,fontweight='bold')
    ax.set_ylim(0,200 if crop=='bean' else 190); ax.set_xlabel('Days after waterlogging start (DAT)')

def rec_handles():
    h=[(tuple(Line2D([],[],color=CROPC[c]['침수ETc'],lw=1.6,ls=LS['침수ETc'],marker='s',ms=5.5) for c in ('bean','lettuce')),'Waterlogging'),
       (Line2D([],[],color=GRAY['ETc50'],lw=1.2,marker='o',ms=4,mfc='white',mew=0.9),'Drought'),
       (Line2D([],[],color=GRAY['침수ETc50'],lw=1.2,ls=LS['침수ETc50'],marker='s',ms=4,mfc='white',mew=0.9),'Combined'),
       (Line2D([],[],color='0.45',lw=0.9,ls='--'),'Control (100%)'),E_flood()]
    return h
def rec():
    fig,axs=plt.subplots(1,2,figsize=(7.7,3.5),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
    for ax,crop in zip(axs,['bean','lettuce']): rec_ax(ax,crop)
    axs[0].set_ylabel('g$_{sw}$ (% of control)')
    legend2(fig,E_crops()+rec_handles(),4,fontsize=7.5); save(fig,'recovery.png',(0,0,1,0.86))
# ---------- parameters 2x4 with A-PPFD and LSP
def box_strip(ax,x,vals,c,filled,w=0.62):
    vals=np.asarray(vals,float); vals=vals[~np.isnan(vals)]
    if len(vals)>=4:
        bp=ax.boxplot([vals],positions=[x],widths=w,patch_artist=True,showfliers=False,medianprops={'color':c,'lw':1.4},whiskerprops={'color':c,'lw':1},capprops={'color':c,'lw':1},boxprops={'lw':1,'edgecolor':c})
        bp['boxes'][0].set_facecolor(c); bp['boxes'][0].set_alpha(0.22 if filled else 0.10)
    else:
        m=vals.mean(); se=vals.std(ddof=1)/np.sqrt(len(vals)) if len(vals)>1 else 0
        ax.errorbar(x,m,se,fmt='_',color=c,ms=14,mew=1.6,capsize=3,lw=1.1,zorder=3)
    jit=np.random.default_rng(1).uniform(-w*0.28,w*0.28,len(vals)); ax.scatter(x+jit,vals,s=11,color=c if filled else 'white',edgecolor=c,lw=0.9,zorder=4)
    return vals.max()
def nrh(I,a_,th,Pm,Rd):
    x_=a_*I+Pm; return (x_-np.sqrt(np.maximum(x_*x_-4*th*a_*I*Pm,0)))/(2*th)-Rd
def params(gray=False):
    D='data/'
    aci=pd.read_csv(D+'06_ACi_파라미터.csv'); aq=pd.read_csv(D+'07_AQ_파라미터.csv'); dun=pd.read_csv(D+'08_ACi_AQ_파라미터_Duncan.csv'); pst=pd.read_csv('intermediate/param_stats.csv')
    def post(df):
        df=df.copy(); df['date']=df['date'].astype(str); q=df[df.단계.str.replace(' ','')=='처리후']
        q=q[((q.작물=='bean')&(q.date>='2026-09-01'))|((q.date>='2026-10-16')&(q.date<='2026-10-19'))]
        return q[q['제외']!=True] if '제외' in q else q
    src={'Vcmax':post(aci),'Jmax':post(aci),'Rd':post(aci),'Amax':post(aq),'alpha':post(aq)}
    labs=[('Vcmax','V$_{cmax}$ (µmol m$^{-2}$ s$^{-1}$)'),('Jmax','J$_{max}$ (µmol m$^{-2}$ s$^{-1}$)'),('Rd','R$_d$ (µmol m$^{-2}$ s$^{-1}$)'),('Amax','A$_{max}$ (µmol m$^{-2}$ s$^{-1}$)'),('alpha','α (mol mol$^{-1}$)')]
    fig,axs=plt.subplots(2,5,figsize=(7.8,3.4),dpi=300); tbl=[]
    for i,crop in enumerate(['bean','lettuce']):
        for j,(par,lab) in enumerate(labs):
            ax=axs[i,j]; dd=dun[(dun.파라미터==par)&(dun.작물==crop)].set_index('처리'); pre=dd['처리전_평균'].iloc[0]
            ax.errorbar(0,pre,dd['처리전_SE'].iloc[0],fmt='x',color=PREC,ms=5,capsize=2,lw=1); tops=[pre]
            ps=pst[(pst.파라미터==par)&(pst.작물==crop)].set_index('처리'); sig=ps.ANOVA_P.iloc[0]<0.05
            for k,t in enumerate(ORDER,1):
                tops.append(box_strip(ax,k,src[par][(src[par].작물==crop)&(src[par].처리==t)][par].dropna().values,CROPC[crop][t],FILLED[t],0.66))
                tbl.append((crop,par,t,ps.loc[t,'평균'],ps.loc[t,'Tukey'] if sig else '',pre))
            ym=max(tops)
            if sig:
                for k,t in enumerate(ORDER,1): ax.text(k,ym*1.05,ps.loc[t,'Tukey'],ha='center',fontsize=7)
            ax.set_ylim(0,ym*1.22); ax.set_xticks([]); ax.tick_params(labelsize=6); ax.set_ylabel(lab,fontsize=6.3)
    legend2(fig,E_crops()+E_trt(('bean','lettuce'),line=False)+[(Line2D([],[],color=PREC,marker='x',ls='--',lw=1.2),'Pre-treatment')],4,fontsize=7)
    fig.tight_layout(rect=(0,0,1,0.88),w_pad=0.5,h_pad=0.6); fig.savefig(FD+'params.png'); plt.close(fig)
    pd.DataFrame(tbl,columns=['crop','par','trt','mean','letter','pre']).to_csv('intermediate/params_table.csv',index=False)

def bars(ax,vals,crop,ylab,letters=True,gray=False,ymax=None):
    ms=[];tops=[]
    for k,t in enumerate(ORDER):
        v=vals[t]; m=v.mean(); se=v.sem(); c=GRAY[t] if (gray and t in GRAY) else CROPC[crop][t]
        if FILLED[t]: ax.bar(k,m,0.78,color=c)
        else: ax.bar(k,m,0.78,facecolor='white',edgecolor=c,linewidth=1.5,hatch='////' if t=='침수ETc50' else None)
        ax.errorbar(k,m,se,color='#333',capsize=2.5,lw=1); tops.append(m+se); ms.append(m)
    let,P=tukey_letters(vals)
    if letters and len(set(let.values()))>1:
        for k,t in enumerate(ORDER): ax.text(k,tops[k]*1.02,let[t],ha='center',fontsize=8)
    ax.set_ylim(0,max(tops)*1.2); ax.set_xticks([]); ax.set_ylabel(ylab,fontsize=7); ax.tick_params(labelsize=6.5)
    return ms,P
def yield_data():
    b=pd.read_csv(R+'data/54_생육_밭콩_파괴조사_이상값제거.csv',encoding='utf-8-sig').rename(columns={'Treatment':'처리'}); b=b[b.날짜=='2026-10-06'].copy()
    b['hs']=b['20 알 F.W']/b['20 알 수']*100
    r=pd.read_csv(R+'로메인data/11_생육_로메인상추.csv',encoding='utf-8-sig'); r=r[r.날짜=='2026-10-23']
    return b,r
def yieldfig():
    b,r=yield_data(); fig,axs=plt.subplots(1,6,figsize=(7.7,2.3),dpi=300); rows=[]
    sp=[('bean',b,'알 F.W','Seed FW (g·plant$^{-1}$)'),('bean',b,'알 D.W','Seed DW (g·plant$^{-1}$)'),('bean',b,'알 수','Seed no. (plant$^{-1}$)'),('bean',b,'꼬투리 수','Pod no. (plant$^{-1}$)'),
        ('lettuce',r,'지상부생체중_전체','Shoot FW (g·plant$^{-1}$)'),('lettuce',r,'지상부건조중_전체','Shoot DW (g·plant$^{-1}$)')]
    for ax,(crop,df,col,lab) in zip(axs,sp):
        vals={t:df.loc[df.처리==t,col].dropna() for t in ORDER}; ms,P=bars(ax,vals,crop,lab); let,_=tukey_letters(vals); ls_=[let[t] for t in ORDER]; ls_=ls_ if len(set(ls_))>1 else ['','','','']
        rows.append([crop,lab]+[round(m,2) for m in ms]+[round((m/ms[0]-1)*100,1) for m in ms[1:]]+[round(P,4)]+ls_)
    pd.DataFrame(rows,columns=['crop','var','ETc','ETc50','침수ETc','침수ETc50','d_ETc50','d_침수','d_복합','P','l0','l1','l2','l3']).to_csv('intermediate/yield_table.csv',index=False); print(pd.DataFrame(rows).to_string())
    hs=[(tuple(Patch(color=CROPC[c][t]) if FILLED[t] else Patch(facecolor='white',edgecolor=CROPC[c][t],lw=1.4,hatch='////' if t=='침수ETc50' else None) for c in ('bean','lettuce')),NAME[t]) for t in ORDER]
    legend2(fig,E_crops()+hs,3,fontsize=7.5,hl=2.0)
    for h in fig.legends[0].legend_handles[:0]: pass
    fig.tight_layout(rect=(0,0,1,0.76),w_pad=0.6); fig.savefig(FD+'yield.png'); plt.close(fig)
# ---------- recap per crop
def recap(crop):
    b,r=yield_data(); fig=plt.figure(figsize=(12.2,3.6),dpi=300); gs=fig.add_gridspec(1,4,wspace=0.32,left=0.055,right=0.995,top=0.86,bottom=0.15)
    a0=fig.add_subplot(gs[0]); a1=fig.add_subplot(gs[1]); sg=gs[2].subgridspec(2,1,hspace=0.18); a2=fig.add_subplot(sg[0]); a3=fig.add_subplot(sg[1]); a4=fig.add_subplot(gs[3])
    rec_ax(a0,crop); a0.set_ylabel('g$_{sw}$ (% of control)')
    ts_axes(a1,crop,'phi','Φ$_{PSII}$',gray=False); a1.set_ylabel('Φ$_{PSII}$')
    dd=pd.read_csv('data/06_ACi_파라미터.csv'); dd['date']=dd['date'].astype(str); dd=dd[dd.단계.str.replace(' ','')=='처리후']
    dd=dd[((dd.작물=='bean')&(dd.date>='2026-09-01'))|((dd.date>='2026-10-16')&(dd.date<='2026-10-19'))]
    if '제외' in dd: dd=dd[dd['제외']!=True]
    ps=pd.read_csv('intermediate/param_stats.csv')
    for ax,par,lab in [(a2,'Vcmax','V$_{cmax}$'),(a3,'Jmax','J$_{max}$')]:
        q=ps[(ps.파라미터==par)&(ps.작물==crop)].set_index('처리'); tops=[]
        for k,t in enumerate(ORDER,1): tops.append(box_strip(ax,k,dd[(dd.작물==crop)&(dd.처리==t)][par].dropna().values,CROPC[crop][t],FILLED[t],0.66))
        if q.ANOVA_P.iloc[0]<0.05:
            for k,t in enumerate(ORDER,1): ax.text(k,max(tops)*1.04,q.loc[t,'Tukey'],ha='center',fontsize=8)
        ax.set_ylim(0,max(tops)*1.25); ax.set_xticks([]); ax.set_ylabel(lab+' (µmol m$^{-2}$ s$^{-1}$)',fontsize=7.5); ax.tick_params(labelsize=7)
    if crop=='bean': vals={t:b.loc[b.처리==t,'알 F.W'].dropna() for t in ORDER}; lab='Seed FW (g·plant$^{-1}$)'
    else: vals={t:r.loc[r.처리==t,'지상부건조중_전체'].dropna() for t in ORDER}; lab='Shoot DW (g·plant$^{-1}$)'
    bars(a4,vals,crop,lab,gray=False); a4.set_ylabel(lab,fontsize=8)
    def hd(t,gray): 
        c=GRAY[t] if gray else CROPC[crop][t]; return Line2D([],[],color=c,marker=MK[t],mfc=c if FILLED[t] else 'white',ls=LS[t],lw=1.6 if not gray else 1.1,ms=5.5 if not gray else 4)
    ents=[(hd('ETc',False),'Control'),(hd('침수ETc',False),'Waterlogging'),((hd('ETc50',True),hd('ETc50',False)),'Drought'),((hd('침수ETc50',True),hd('침수ETc50',False)),'Combined')]
    legend2(fig,ents,4,fontsize=8.5,hl=3.0,cs=2.5); fig.savefig(FD+f'recap_{crop}.png'); plt.close(fig)

def aq():
    d=pd.read_csv('data/09_LI6800_광곡선_개별점.csv'); d=d.dropna(subset=['Qin','A']); d['Q']=d.Qin.round(-1)
    fig,axs=plt.subplots(1,2,figsize=(7.5,3.0),dpi=300,gridspec_kw={'width_ratios':[1,1]})
    for ax,crop in zip(axs,['bean','lettuce']):
        s=d[d.작물==crop]
        for key in ['처리 전']+ORDER:
            g=s[s.처리==key] if key=='처리 전' else s[(s.단계2=='처리 후')&(s.처리==key)]
            m=g.groupby('Q').A.agg(['mean','sem']).reset_index()
            if key=='처리 전': c=PREC; kw=dict(ls='--',marker='x',ms=4,mfc=c)
            else: c=col(crop,key); kw=dict(ls=LS[key],marker=MK[key],ms=3.8,mfc=c if FILLED[key] else 'white')
            ax.errorbar(m.Q,m['mean'],m['sem'],color=c,mec=c,lw=1.3,capsize=1.5,elinewidth=0.7,**kw)
        ax.set_xlabel('PPFD (µmol m$^{-2}$ s$^{-1}$)'); 
        if crop=='bean': ax.set_ylabel('A (µmol CO$_2$ m$^{-2}$ s$^{-1}$)')
    legend2(fig,E_crops()+E_trt(('bean','lettuce'))+[E_pre()],4,fontsize=7.2); save(fig,'aq.png',(0,0,1,0.85))
if __name__=='__main__':
    import sys
    for f in (sys.argv[1:] or ['env','cum','rec','params','yieldfig','recap','aq']):
        if f=='recap': recap('bean'); recap('lettuce')
        elif f=='params': params()
        else: globals()[f]()
    print('ok')
