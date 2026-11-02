import warnings; warnings.filterwarnings('ignore')
from fo_common import *
from matplotlib.patches import Rectangle
END={'bean':56,'lettuce':16}
# 설계: (처리, [(시작,끝,관수비율 또는 'flood')])
def plan(crop):
    e=END[crop]
    return {'ETc':[(0,e,1.0)],'ETc50':[(0,e,0.5)],'침수ETc':[(0,3,'flood'),(3,e,1.0)],'침수ETc50':[(0,3,'flood'),(3,e,0.5)]}
fig,axs=plt.subplots(1,2,figsize=(11.6,2.45),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
ROW={'ETc':3,'ETc50':2,'침수ETc':1,'침수ETc50':0}
for ax,crop in zip(axs,['bean','lettuce']):
    for t,segs in plan(crop).items():
        y=ROW[t]; c=col(crop,t)
        for a,b,v in segs:
            if v=='flood':
                ax.add_patch(Rectangle((a,y-0.32),b-a,0.64,facecolor='#F4F4F4',edgecolor='#8A8A8A',hatch='////',lw=0.8,zorder=2))
                ax.text((a+b)/2,y,'72 h',ha='center',va='center',fontsize=7.5 if crop=='lettuce' else 6.5,color='#333',bbox=dict(fc='white',ec='none',pad=0.8,alpha=0.85),zorder=3)
            else:
                h=0.64*v; ax.add_patch(Rectangle((a,y-h/2),b-a,h,facecolor=c,edgecolor='none',zorder=2))
                if b-a>5: ax.text((a+b)/2,y,f'{int(v*100)}%',ha='center',va='center',fontsize=7.5,color='white' if t in('ETc','침수ETc') else '#222',zorder=3)
    ax.set_yticks(list(ROW.values())); ax.set_yticklabels([NAME[t] for t in ROW]); ax.set_ylim(-0.6,3.6)
    ax.set_xlim(*((-2,57) if crop=='bean' else (-0.8,17))); ax.set_xlabel('Days after waterlogging start (DAT)')
    ax.axvline(10.5,color='0.55',ls=':',lw=1,zorder=1); ax.spines['left'].set_visible(False); ax.tick_params(axis='y',length=0)
    ax.text(10.5-0.4,-0.55,'P1',ha='right',va='bottom',fontsize=8,color='0.4'); ax.text(10.5+0.4,-0.55,'P2',ha='left',va='bottom',fontsize=8,color='0.4')
    ax.set_title(CN[crop],loc='left',fontsize=9,fontweight='bold',color=ACC[crop])
H=[(Patch(facecolor='#F4F4F4',edgecolor='#8A8A8A',hatch='////'),'Waterlogging 72 h (no irrigation)'),(Patch(color='0.45'),'Irrigation: 100% or 50% of previous-day ET (bar height = ratio)')]
legend2(fig,H,2,fontsize=7.8)
fig.tight_layout(rect=(0,0,1,0.88),w_pad=1.5); fig.savefig('figs6/design_timeline.png'); plt.close(fig)
