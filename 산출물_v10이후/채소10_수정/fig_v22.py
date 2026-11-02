import warnings; warnings.filterwarnings('ignore')
import fo_common as fc
from fo_common import *
import fo_figs as ff
XL={'bean':(-8,56),'lettuce':(-3.6,17.5)}
fig,axs=plt.subplots(1,2,figsize=(7.5,2.55),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
for ax,crop in zip(axs,['bean','lettuce']): fc.ts_axes(ax,crop,'gsw','g$_{sw}$ (mol·m$^{-2}$·s$^{-1}$)'); ax.set_xlim(*XL[crop])
legend2(fig,E_crops()+E_trt(('bean','lettuce'))+[E_cloud(),E_flood()],5); fig.tight_layout(rect=(0,0,1,0.84),w_pad=1.5); fig.savefig('figs7/gsw_ts.png'); plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(7.5,2.55),dpi=300,gridspec_kw={'width_ratios':[1.5,1]})
for ax,crop in zip(axs,['bean','lettuce']): ff.rec_ax(ax,crop); ax.set_xlim(*XL[crop])
axs[0].set_ylabel('g$_{sw}$ (% of control)'); legend2(fig,E_crops()+ff.rec_handles(),5); fig.tight_layout(rect=(0,0,1,0.84),w_pad=1.5); fig.savefig('figs7/gsw_rec.png'); plt.close(fig)
