L=open('07_v13_review.py',encoding='utf-8').read().split('\n')
seg='\n'.join(L[:113])+'\n'+'\n'.join(L[157:232])
seg=seg.replace("'Lettuce'","'Romaine'").replace("Lettuce P1 signal size","Romaine P1 signal size").replace("'Soybean' if crop == 'bean' else 'Lettuce'","'Soybean' if crop == 'bean' else 'Romaine'")
import re as _re
_i=seg.index("for _v in ['Fs', \"Fm'\", 'ratio']:"); _j=seg.index("개체값\n",_i)+len("개체값\n")
_new='''_U=pd.read_csv('user_adj_1b.csv'); _U['날짜']=_U['날짜'].astype(str)
_k=['날짜','처리','반복','Time']; L1['날짜']=L1['날짜'].astype(str)
L1=L1.merge(_U[_k+["Fs_PAR·기온보정","Fm'_PAR·기온보정","Fm'/Fs_PAR·기온보정"]],on=_k,how='left')
L1['Fs']=L1['Fs_PAR·기온보정']; L1["Fm'"]=L1["Fm'_PAR·기온보정"]; L1['ratio']=L1["Fm'/Fs_PAR·기온보정"]
'''
seg=seg[:_i]+_new+seg[_j:]
exec(compile(seg,'07_seg','exec'))
print('07 ok')
