"""LI-600 명적응 형광(Fs, Fm', ΦPSII)과 가장 가까운 날짜의 야간 암적응 Fo·Fm(처리별 평균)으로
NPQ, qP, qN, qL, ΦNO, ΦNPQ 계산 (수식: gsw, 형광\\LI-600 형광_함수.xlsx 와 동일) + 초기/후기 Duncan.

입력: data/02_LI600_개별측정.csv, 02b_LI600_처리전_개별측정.csv, 03_암적응_FvFm_개별측정.csv,
      05_구간별_Duncan.csv(구간 DAT 정의), gsw, 형광\\1016 콩 형광.xlsx
출력: intermediate/li600_fluor_points.csv, li600_fluor_period.csv

규칙
- 콩 9/28 암적응 값은 LI-6800 측정이므로 제외하고, 대신 LI-600 10/16 암적응 원자료를 추가
- 같은 거리면 이전 날짜 우선, 처리 전 곡선은 대조구(상추는 10/7) 값 사용
- 흐린 날 포함 전체 측정일, 국면별로 모든 처리가 측정된 날만 사용
- 국면 비교: v ~ 처리 + 측정일 + 선형 PAR(Qamb) + 기온(Tair) 보정 평균·Tukey 문자 (stats2x2.ancova)
"""
import warnings
import numpy as np
import openpyxl
import pandas as pd
from scipy import stats
from config import DATA, INTER, ORDER, RAW_BEAN_DARK_1016, load_li600, common_days
from stats2x2 import ancova

warnings.filterwarnings('ignore')
x = load_li600()   # 흐린 날 포함 전체
pre = pd.read_csv(DATA / '02b_LI600_처리전_개별측정.csv')
pre['처리'] = '처리 전'
x = pd.concat([x.assign(단계='처리 후'), pre.assign(단계='처리 전')], ignore_index=True)
x['date'] = pd.to_datetime(x['날짜'])

f = pd.read_csv(DATA / '03_암적응_FvFm_개별측정.csv')
f = f[~((f.작물 == 'bean') & (f.날짜 == '2026-09-28'))]
ws = openpyxl.load_workbook(RAW_BEAN_DARK_1016, data_only=True, read_only=True)['dark']
add = pd.DataFrame([dict(작물='bean', 날짜='2026-10-16', 처리=r[7], Fo=float(r[23]), Fm=float(r[24]))
                    for r in list(ws.iter_rows(values_only=True))[3:] if r[23] not in (None, '') and r[7] in ORDER])
f = pd.concat([f, add], ignore_index=True)
f['date'] = pd.to_datetime(f['날짜'])
fm = f.groupby(['작물', 'date', '처리'])[['Fo', 'Fm']].mean().reset_index()


def pick(crop, date, trt):
    c = fm[(fm.작물 == crop) & (fm.처리 == ('ETc' if trt == '처리 전' else trt))].copy()
    if crop == 'lettuce':
        c = c[c.date == pd.Timestamp('2026-10-07')] if trt == '처리 전' else c[c.date > pd.Timestamp('2026-10-07')]
    c['d'] = (c.date - date).dt.days
    c['k'] = c.d.abs() * 10 + (c.d > 0)
    r = c.sort_values('k').iloc[0]
    return r.Fo, r.Fm, r.date.strftime('%m-%d'), int(r.d)


x[['Fo_dark', 'Fm_dark', '암적응날짜', '날짜차(일)']] = pd.DataFrame([pick(r.작물, r.date, r.처리) for r in x.itertuples()], index=x.index)
Fs, Fmp, Fo, Fm = x['Fs'], x["Fm'"], x['Fo_dark'], x['Fm_dark']
x['NPQ'] = (Fm - Fmp) / Fmp
x["Fo'"] = Fo / ((Fm - Fo) / Fm + Fo / Fmp)
x['qP'] = (Fmp - Fs) / (Fmp - x["Fo'"])
x['qN'] = (Fm - Fmp) / (Fm - x["Fo'"])
x['qL'] = x['qP'] * x["Fo'"] / Fs
x['PhiNO'] = 1 / (x['NPQ'] + 1 + x['qL'] * (Fm / Fo - 1))
x['PhiNPQ'] = 1 - x['PhiPS2'] - x['PhiNO']
x.to_csv(INTER / 'li600_fluor_points.csv', index=False)

# 국면: P1 = 침수 시작~침수 종료 후 7일(콩 DAT 1~9, 상추 DAT 1~10), P2 = 그 이후. 모든 처리가 측정된 날만 사용
from config import PHASE_END as END
out = []
for crop in ['bean', 'lettuce']:
    base = x[(x.작물 == crop) & (x.단계 == '처리 후') & (x.DAT >= 1)]
    sets = [('P1', base[base.DAT <= END[crop]]), ('P2', base[base.DAT > END[crop]])]
    if crop == 'bean':   # 민감도: 콩 P2에서 10/2(DAT 51) 제외
        sets.append(('P2_no51', base[(base.DAT > END[crop]) & (base.DAT != 51)]))
    for per, s in sets:
        s = common_days(s)
        days = sorted(int(v) for v in s.DAT.dropna().unique())
        for m in ['NPQ', 'PhiNO', 'PhiNPQ', 'qP', 'qL']:
            r, P = ancova(s, m)
            prv = x[(x.작물 == crop) & (x.단계 == '처리 전')][m].dropna()
            for _, row in r.iterrows():
                out.append(dict(작물=crop, 구간=per, 지표=m, **row.to_dict(), **P,
                                처리전=prv.mean(), 포함DAT=','.join(str(v) for v in days)))
pd.DataFrame(out).to_csv(INTER / 'li600_fluor_period.csv', index=False)
print('03 done')
