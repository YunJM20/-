import numpy as np
from scipy.stats import studentized_range
def duncan(groups, alpha=0.05):
    """groups: dict name->array. returns dict name->letters (a = highest mean)."""
    names=[k for k in groups if len(groups[k])>0]
    means={k:np.mean(groups[k]) for k in names}; ns={k:len(groups[k]) for k in names}
    N=sum(ns.values()); kk=len(names)
    sse=sum(((np.asarray(groups[k])-means[k])**2).sum() for k in names); dfe=N-kk; mse=sse/dfe
    order=sorted(names,key=lambda k:-means[k])
    # significance matrix
    sig={}
    for i in range(kk):
        for j in range(i+1,kk):
            p=j-i+1; a_p=1-(1-alpha)**(p-1)
            a,b=order[i],order[j]
            nh=2/(1/ns[a]+1/ns[b])
            q=studentized_range.ppf(1-a_p,p,dfe)
            sig[(a,b)]=(means[a]-means[b])>q*np.sqrt(mse/nh)
    # letters via homogeneous ranges
    ranges=[]
    for i in range(kk):
        j=i
        while j+1<kk and not any(sig[(order[x],order[y])] for x in range(i,j+2) for y in range(x+1,j+2)): j+=1
        if not any(set(range(i,j+1))<=set(r) for r in ranges): ranges.append(list(range(i,j+1)))
    lets={k:'' for k in names}
    for li,r in enumerate(ranges):
        for x in r: lets[order[x]]+=chr(97+li)
    return lets
