# Data Source: 국가법령정보센터 (law.go.kr) Open API

Legal Trend Radar collects **real** Korean court precedent (판례) search-result
metadata from the government-operated Open API at https://open.law.go.kr.

## Endpoints used

### 1. List search (`lawSearch.do`)
```
GET http://www.law.go.kr/DRF/lawSearch.do
```
| Param | Meaning |
|---|---|
| `OC` | Your registered Open API user id (the local part of your registered email) |
| `target` | `prec` (판례) |
| `type` | `JSON` |
| `search` | `1` = search by case name, `2` = full text search |
| `query` | Search keyword |
| `display` | Results per page (max ~100) |
| `page` | Page number |
| `org` | Court organization code filter (optional) |
| `curt` | Court name filter (optional) |
| `JO` | Article/clause filter (optional) |
| `sort` | Sort order (optional) |
| `prncYd` | Decision-date range filter, format `YYYYMMDD~YYYYMMDD` |
| `nb` | Case number filter (optional) |
| `datSrcNm` | Data source name filter (optional) |

Official guide: https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=precListGuide

### 2. Detail (`lawService.do`)
```
GET http://www.law.go.kr/DRF/lawService.do
```
| Param | Meaning |
|---|---|
| `OC` | Same as above |
| `target` | `prec` |
| `type` | `JSON` |
| `ID` | `판례일련번호` (precedent serial id) from a list-search result |

Official guide: https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=precInfoGuide

## Authentication

`OC` is obtained by registering at https://open.law.go.kr and is **not** a
secret API key in the traditional sense, but this project still treats it as
a required, non-hardcoded configuration value: it must be set as
`LAW_API_OC` in a repo-root `.env` file (see `.env.example`). The codebase
never hardcodes it and never falls back to fake data when it is missing.

## Default collection scope

- Keywords: 계약, 계약해제, 계약해지, 손해배상, 위약금, 채무불이행
- Date range: `DEFAULT_START_DATE=2016-01-01` to `DEFAULT_END_DATE=2026-12-31`
  (configurable via `.env` or CLI flags)

## Known caveats (see also reports/REPORT.md "Limitations")

- The database does not include every ruling ever issued - only what courts
  choose to publish.
- Search-result counts are influenced by keyword overlap: a single case can
  match multiple keywords and is deduplicated by `precedent_id` where possible.
- Indexing/search-system changes on law.go.kr's side can shift historical
  counts independent of real-world litigation activity.
