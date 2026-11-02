"""로메인상추_종합데이터.xlsx '1b_LI600_보정값' 시트 → user_adj_1b.csv (사용자 PAR·기온 보정값; run_figs2.py가 사용)"""
import openpyxl, pandas as pd
wb = openpyxl.load_workbook('로메인상추_종합데이터.xlsx', data_only=True, read_only=True)
R = list(wb['1b_LI600_보정값'].iter_rows(values_only=True))
u = pd.DataFrame(R[7:], columns=list(R[6])).dropna(subset=['작물'])
u.to_csv('user_adj_1b.csv', index=False)
