# 안내문

## 설치안내
- MIMIC-IV 2.2 base로 주로 작업
- `https://physionet.org/content/mimiciv/2.2/` 에서 데이터 다운로드
- `https://github.com/MIT-LCP/mimic-code/` 에서 데이터 설치 코드 다운로드
- DB는 postgreSQL에서 주로 작업
- 속도 향상을 위해 추가 인덱스 작업을 했다.
  `src/queries/additional_queries.sql`을 실행해 준다.

## 파일 및 폴더
- `src`  
  코드가 담겨있다.
- `plan.md`  
  연구계획이 담겨있다.
- `db-analysis.md`  
  DB의 여러 테이블과 레코드를 해석

## 실행
`python ./src/main.py`