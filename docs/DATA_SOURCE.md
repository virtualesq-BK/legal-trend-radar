# 데이터 출처: 국가법령정보센터 (law.go.kr) Open API

Legal Trend Radar는 정부가 운영하는 Open API(https://open.law.go.kr)에서
**실제** 한국 법원 판례 검색결과 메타데이터를 수집합니다.

## 사용하는 엔드포인트

### 1. 목록 검색 (`lawSearch.do`)
```
GET http://www.law.go.kr/DRF/lawSearch.do
```
| 파라미터 | 의미 |
|---|---|
| `OC` | 등록한 Open API 사용자 id (등록 이메일의 `@` 앞부분) |
| `target` | `prec` (판례) |
| `type` | `JSON` |
| `search` | `1` = 사건명 검색, `2` = 본문 검색 |
| `query` | 검색 키워드 |
| `display` | 페이지당 결과 수 (최대 약 100) |
| `page` | 페이지 번호 |
| `org` | 법원 조직 코드 필터 (선택) |
| `curt` | 법원명 필터 (선택) |
| `JO` | 조/항 필터 (선택) |
| `sort` | 정렬 순서 (선택) |
| `prncYd` | 판결일자 범위 필터, 형식 `YYYYMMDD~YYYYMMDD` |
| `nb` | 사건번호 필터 (선택) |
| `datSrcNm` | 데이터 출처명 필터 (선택) |

공식 가이드: https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=precListGuide

### 2. 상세 조회 (`lawService.do`)
```
GET http://www.law.go.kr/DRF/lawService.do
```
| 파라미터 | 의미 |
|---|---|
| `OC` | 위와 동일 |
| `target` | `prec` |
| `type` | `JSON` |
| `ID` | 목록 검색 결과의 `판례일련번호` |

공식 가이드: https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=precInfoGuide

## 인증

`OC`는 https://open.law.go.kr에 가입해 발급받으며, 전통적인 의미의 비밀
API 키는 아니지만 이 프로젝트는 여전히 하드코딩하지 않는 필수 설정값으로
취급합니다: 레포 루트의 `.env` 파일에 `LAW_API_OC`로 설정해야 합니다
(`.env.example` 참고). 코드베이스는 이를 절대 하드코딩하지 않으며, 값이
없을 때 가짜 데이터로 대체하지도 않습니다.

## 기본 수집 범위

- 키워드: 계약, 계약해제, 계약해지, 손해배상, 위약금, 채무불이행
- 기간: `DEFAULT_START_DATE=2016-01-01` ~ `DEFAULT_END_DATE=2026-12-31`
  (`.env` 또는 CLI 플래그로 변경 가능)

## 알려진 한계 (reports/REPORT.md의 "한계점" 섹션도 참고)

- 데이터베이스에는 선고된 모든 판결이 포함되지 않으며, 법원이 공개하기로
  선택한 판결만 포함됩니다.
- 검색결과 건수는 키워드 중복의 영향을 받습니다: 하나의 사건이 여러
  키워드에 매칭될 수 있으며, 가능한 경우 `precedent_id` 기준으로 중복
  제거합니다.
- law.go.kr 측의 색인/검색 시스템 변경은 실제 소송 활동과 무관하게
  과거 건수를 변동시킬 수 있습니다.
