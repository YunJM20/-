import pandas as pd, numpy as np, openpyxl
R='/home/user/-/'
def sh(f,n):
    ws=openpyxl.load_workbook(R+f,data_only=True,read_only=True)[n]; X=[r for r in ws.iter_rows(values_only=True) if any(x is not None for x in r)]
    return pd.DataFrame(X[1:],columns=X[0])
f1='증산량/증산량_로메인상추_1007-1010.xlsx'; f2='증산량/증산량_로메인상추_1011-1023.xlsx'
a1=sh(f1,'증산량(ETc,침ETc)').dropna(subset=['날짜']); a1=a1.rename(columns={'무게(g)':'관수 전(g)'})
a2=sh(f2,'증산량(ETc,침ETc)'); b2=sh(f2,'관수량(ETc50,침ETc,침50)')
MAP={'ETc':'ETc','침수 ETc':'침수ETc','ETc 50':'ETc50','침수50':'침수ETc50'}
rows=[]
for df,keep in [(a1,['ETc','침수 ETc']),(a2,['ETc','침수 ETc']),(b2,['ETc 50','침수50'])]:
    d=df[df.Treatment.isin(keep)]
    for r in d.itertuples(): rows.append(dict(날짜=r.날짜,처리=MAP[r.Treatment],반복=int(r.Repeat),w=float(getattr(r,'_4') if False else r[4])))
W=pd.DataFrame(rows)   # 대조·침수: 증산량 시트 전 포트(10/12까지 1~3번, 10/13부터 1~6번), 건조·복합: 관수량 시트(3→4반복). 침수 7~10번은 관수 결과 확인용이라 제외
W['DAT']=(pd.to_datetime(W.날짜)-pd.Timestamp('2026-10-07')).dt.days
W=W.dropna(subset=['w'])
G=W.groupby(['처리','DAT']).w.agg(['mean','sem','count']).reset_index(); G.to_csv('intermediate/romaine_potweight.csv',index=False)
print(G.groupby('처리')['count'].agg(['min','max']).to_string()); print(G.pivot(index='DAT',columns='처리',values='mean').round(0).to_string())
# ---- figure: 07_v13_review.py 5a style
L=open('07_v13_review.py',encoding='utf-8').read().split('\n')
head='\n'.join(L[:51])
five='\n'.join(L[126:157])
i=five.index("ax = axs[1]"); j=five.index("fig.tight_layout(w_pad=1.5)")
left=five[five.index("h = pd.read_csv"):i]
left=left[left.index("fig, axs"):]
new_right='''ax = axs[1]
ax.axvspan(0, 3, color='#E6E6E6', lw=0); ax.text(1.5, 1530, 'Water-\\nlogging\\n(pots in tubs)', ha='center', va='top', fontsize=6, color='0.35')
for t in ORDER:
    g = G[G.처리 == t].sort_values('DAT'); c = CROPC['lettuce'][t]
    ax.fill_between(g.DAT, g['mean'] - g['sem'].fillna(0), g['mean'] + g['sem'].fillna(0), color=c, alpha=0.16, lw=0)
    ax.plot(g.DAT, g['mean'], color=c, ls=LS[t], lw=1.4, marker=MK[t], ms=3.5, mfc=c if FILLED[t] else 'white', mec=c, mew=1)
ax.axvline(5.5, color='0.55', ls=':', lw=1, zorder=1); ax.text(5.7, 1530, 'more pots\\nfrom DAT 6', fontsize=6, color='0.4', va='top')
ax.set_xlim(-0.8, 16.8); ax.set_ylim(300, 1550); ax.set_xticks([0, 5, 10, 15])
ax.set_xlabel('DAT'); ax.set_ylabel('Pot weight before irrigation\\n(g, mean ± SE)', fontsize=7.5)
ax.set_title('Romaine pot weight')
ax.legend([handle('lettuce', t) for t in ORDER], [NAME[t] for t in ORDER], fontsize=6.5, loc='lower left', bbox_to_anchor=(0.0, 0.0), ncol=2, handlelength=2.2)
'''
seg=head+'\n'+left.replace("'lettuce': [60, 93, 44]","'lettuce': [43, 56, 37]").replace("['Lettuce', 'Soybean']","['Romaine', 'Soybean']")+new_right+"fig.tight_layout(w_pad=1.5); fig.savefig(FIG / 'check2.png'); plt.close(fig)\n"
exec(compile(seg,'5a_new','exec')); print('ok')
# ---- slide 25 third panel (v1 style: no shared legend, title only)
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(2.9,2.5),dpi=300)
ax.axvspan(0,3,color='#E6E6E6',lw=0)
for t in ORDER:
    g=G[G.처리==t].sort_values('DAT'); c=CROPC['lettuce'][t]
    ax.errorbar(g.DAT,g['mean'],g['sem'].fillna(0),color=c,ls=LS[t],lw=1.4,marker=MK[t],ms=3.5,mfc=c if FILLED[t] else 'white',mec=c,mew=1,capsize=1.5,elinewidth=0.8)
ax.set_xlabel('DAT'); ax.set_ylabel('Pot weight before irrigation (g)',fontsize=7.5); ax.set_title('Pot weight',loc='center')
ax.axvline(5.5,color='0.55',ls=':',lw=1); ax.set_xticks([0,5,10,15]); fig.tight_layout(); fig.savefig(FIG/'potweight_panel.png'); plt.close(fig)
