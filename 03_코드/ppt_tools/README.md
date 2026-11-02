# ppt_tools

- `v6lib.py` : python-pptx 헬퍼 — `clone_slide`(슬라이드 복제, 그림 파트 복사), `swap_pic`(그림 교체, 폭·위치 지정), `set_text`(단락 설정, `_{x}` 아래첨자·`^{x}` 위첨자 표기), `set_title/set_eyebrow`, `cell_set`, `add_col/add_rows/del_row/set_widths/set_row_h`, `reorder`.
- `fmt_lib.py` : 슬라이드 전체 텍스트의 지표 기호(Vcmax, gsw, ΦPSII, Fv/Fm, m⁻² 등)를 아래·위첨자 run으로 변환.
- `export_slides.ps1` : (Windows + PowerPoint) 지정한 슬라이드를 PNG로 내보내 눈으로 확인. `-src 파일 -outdir 폴더 -slides "1,2,5"`. PowerPoint가 없으면 LibreOffice `soffice --headless --convert-to pdf` 후 이미지 변환으로 대체.
- `slides_to_md.py` : PPT의 슬라이드별 텍스트·표를 마크다운으로 추출(자료집 만들 때).
- `예시_*.py` : 실제로 v6 슬라이드를 고친 스크립트들(표 재구성, 괄호 표기, 그림 교체). **경로·값이 이 프로젝트용으로 박혀 있으므로 구조만 참고.**
- 템플릿 PPT(`01_양식_템플릿\콩_vs_상추_비교_v6.pptx`)는 항상 복사본으로 작업.
- 표 행을 복제할 때 `a:extLst`(rowId)가 중복되면 PowerPoint가 표를 그리지 않는다 → 복제 행에서 제거.
