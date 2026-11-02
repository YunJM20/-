# redleaf_loader_예시 (참고용, 그대로는 실행되지 않음)

레드립 잎상추 때 **원자료 → 표준 DataFrame → 마스터 엑셀/분석 CSV**로 만든 코드이다. 경로(`C:\Users\...`)와 다른 모듈(`cmp_data`, `duncan_lib` 등)에 의존하므로 **로직과 열 이름·라벨 규칙을 참고해 로메인용으로 새로 작성**한다.

- `lettuce_data.py` : LI-600 gsw·형광 / 암적응 / A-Ci·A-Q 파라미터 / LI-6800 곡선 / 증산량 / 관수량 / 환경 / 캐노피 로더, 라벨 파서(`parse_label`: CL/DL/WL/WDL, 품종 문자 R/L), 시각 정규화(`norm_time`: 8자리 zero-pad).
- `build_all.py` : 마스터 엑셀(시트 0~13) 생성.
- `fitcorr.py` : 보정 gsw 추정(레드립용 보정식 탐색).
- `cmp_cloud_흐린날CI.py` : 흐린 날 판정(CI = 측정 구간 평균 SW ÷ 같은 시각대 ±10일 90분위수 SW). 온실 외부 일사계 SW 시계열이 필요하다.
- `export_cowork_분석CSV.py` : 분석용 CSV(01~09 …) 열 구성.
