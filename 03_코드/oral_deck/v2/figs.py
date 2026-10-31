import io, numpy as np
from PIL import Image
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
GREEN='#2E6B3F'; BROWN='#6B4226'
def load(n,i): return Image.open(f'/tmp/claude-0/-home-user--/f2046ef5-a5f5-5769-8dca-a4878d4046a0/scratchpad/img_{n}_{i}.png').convert('RGB')
def white_gaps(im, y0=0, minw=25, thr=245):
    a=np.array(im.convert('L'))[y0:]
    col=(a<thr).sum(axis=0); gaps=[];s=None
    for x,v in enumerate(col):
        if v==0 and s is None: s=x
        if v>0 and s is not None:
            if x-s>=minw: gaps.append((s,x))
            s=None
    if s is not None: gaps.append((s,len(col)))
    return gaps
def trim(im, pad=6, thr=245):
    a=np.array(im.convert('L')); ys,xs=np.where(a<thr)
    return im.crop((max(xs.min()-pad,0),max(ys.min()-pad,0),min(xs.max()+pad,im.width),min(ys.max()+pad,im.height)))
def hcat(ims, gap=40, height=None, bg=(255,255,255)):
    height=height or max(i.height for i in ims)
    rs=[i.resize((int(i.width*height/i.height),height),Image.LANCZOS) for i in ims]
    W=sum(r.width for r in rs)+gap*(len(rs)-1)
    c=Image.new('RGB',(W,height),bg); x=0
    for r in rs: c.paste(r,(x,0)); x+=r.width+gap
    return c
def vcat(ims, gap=20, width=None, bg=(255,255,255)):
    width=width or max(i.width for i in ims)
    rs=[i.resize((width,int(i.height*width/i.width)),Image.LANCZOS) for i in ims]
    H=sum(r.height for r in rs)+gap*(len(rs)-1)
    c=Image.new('RGB',(width,H),bg); y=0
    for r in rs: c.paste(r,(0,y)); y+=r.height+gap
    return c
def center_w(im, W, bg=(255,255,255)):
    c=Image.new('RGB',(max(W,im.width),im.height),bg); c.paste(im,((c.width-im.width)//2,0)); return c
def with_legend(legend, body):
    W=max(legend.width, body.width)
    return vcat([center_w(legend,W), center_w(body,W)], gap=10, width=W)
def to_fig(fig):
    b=io.BytesIO(); fig.savefig(b,format='png',dpi=200,bbox_inches='tight',facecolor='white'); plt.close(fig)
    b.seek(0); return Image.open(b).convert('RGB')

def comp(i6, soy_x, i1, rom_boxes, legend_h=63, y0=63, gap=70, soy_y=None, rom_y=None, legend_from='v6'):
    """soy panel(s) from v6 image i6 (x0,x1), romaine boxes from v1 image i1: list of (x0,x1)."""
    a=load('v6',i6); b=load('v1',i1)
    sy=soy_y or (y0,a.height); ry=rom_y or (y0,b.height)
    soy=trim(a.crop((soy_x[0],sy[0],soy_x[1],sy[1])),pad=4)
    roms=[trim(b.crop((x0,ry[0],x1,ry[1])),pad=4) for (x0,x1) in rom_boxes]
    body=hcat([soy]+roms,gap=gap,height=max(soy.height,*[r.height for r in roms]))
    leg=trim((a if legend_from=='v6' else b).crop((0,0,a.width,legend_h)),pad=4)
    return with_legend(leg,body)

C_CTRL='#1F3D2B'; C_DRY='#8FAA91'; C_WL='#2E7D4F'; C_COMB='#9FD3A8'
def yield_panels():
    fig,axes=plt.subplots(1,2,figsize=(4.3,2.95))
    data=[('Shoot FW',[89.9,63.5,66.3,55.4],[4.1,2.0,5.2,4.2],list('abbb'),(0,110)),
          ('Shoot DW',[6.47,5.43,4.30,3.69],[0.42,0.21,0.37,0.37],['a','ab','bc','c'],(0,8))]
    for ax,(t,m,se,let,yl) in zip(axes,data):
        x=np.arange(4)
        ax.bar(x[0],m[0],0.8,color=C_CTRL)
        ax.bar(x[1],m[1],0.8,facecolor='white',edgecolor=C_DRY,linewidth=1.6)
        ax.bar(x[2],m[2],0.8,color=C_WL)
        ax.bar(x[3],m[3],0.8,facecolor='white',edgecolor=C_COMB,hatch='////',linewidth=1.6)
        ax.errorbar(x,m,yerr=se,fmt='none',ecolor='#333333',capsize=3,lw=1.2)
        for xi,mi,si,l in zip(x,m,se,let): ax.text(xi,mi+si+yl[1]*0.02,l,ha='center',fontsize=10)
        ax.set_ylim(*yl); ax.set_xticks([]); ax.set_title(t,fontsize=11,fontweight='bold',color=GREEN)
        ax.set_ylabel('g·plant$^{-1}$',fontsize=9); ax.set_xlabel('P<0.001',fontsize=9)
        ax.spines[['top','right']].set_visible(False); ax.tick_params(labelsize=9)
    fig.suptitle('Romaine (DAT 16, harvest)',fontsize=11,fontweight='bold',color=GREEN,y=1.02)
    fig.tight_layout(); return to_fig(fig)

def irr_panel(height_in=3.4):
    fig,ax=plt.subplots(figsize=(4.4,height_in))
    labs=['ETc 100%','ETc 50%','Flooding-\nETc 100%','Flooding-\nETc 50%']; vals=[100,43,56,37]
    cols=[C_CTRL,C_DRY,C_WL,C_COMB]
    ax.bar(range(4),vals,0.65,color=cols)
    for i,v in enumerate(vals): ax.text(i,v+2,f'{v}%',ha='center',fontsize=12,fontweight='bold')
    ax.set_ylim(0,125); ax.set_xticks(range(4)); ax.set_xticklabels(labs,fontsize=9)
    ax.set_yticks([0,20,40,60,80,100,120]); ax.set_yticklabels([])
    ax.set_title('Romaine',loc='left',fontsize=12,fontweight='bold',color=GREEN)
    ax.spines[['top','right']].set_visible(False); fig.tight_layout(); return to_fig(fig)

def soy_only_33():
    import cv2
    src=load('v6',33); a=np.array(src).astype(int); R,G,B=a[...,0],a[...,1],a[...,2]
    green=(((G>R+8)&(G>B-5)&(G>60))|(G>R+25)).astype('uint8')*255
    green=cv2.dilate(green,np.ones((5,5),np.uint8),iterations=1)
    brown=(R>G+22)&(R>B+35)
    m=(green>0)&(~brown)
    yref=int(src.height*0.845)   # inside axes, near bottom (only band/white pixels)
    out=a.copy()
    bg_row=a[yref]               # per-column background (white or band gray)
    ys,xs=np.where(m)
    out[ys,xs]=bg_row[xs]
    out=out.astype('uint8'); out[15:80,640:900]=255   # remove 'Lettuce' legend entry
    return Image.fromarray(out)
