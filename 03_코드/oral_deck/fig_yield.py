import sys; sys.path.insert(0,'.')
from figs import *
a=load('v6',23)
leg=trim(a.crop((0,0,a.width,58)),pad=4)
soy=trim(a.crop((795,59,a.width,a.height)),pad=4)
rom=yield_panels()
body=hcat([rom,soy],gap=50,height=max(rom.height,soy.height))
img=with_legend(leg,body); img.save('an/figs2/yield_cmp.png'); print(img.size)
