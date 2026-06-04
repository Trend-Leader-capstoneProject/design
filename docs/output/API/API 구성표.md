| 화면/기능        | API 그룹        | 주요 API 후보                   | 관련 DB 테이블                                                                          |
| ------------ | ------------- | --------------------------- | ---------------------------------------------------------------------------------- |
| 로그인          | Auth API      | 로그인, 구글 로그인                 | `users`, `oauth_accounts`                                                          |
| 회원가입         | Auth API      | 일반 회원가입, 아이디 중복 확인          | `users`, 필요 시 `user_profiles`                                                      |
| 로그인 후 관심사 선택 | Interest API  | 카테고리 목록 조회, 관심사 저장          | `categories`, `user_interest_categories`                                           |
| 관심사 기반 트렌드 탭 | Trend API     | 맞춤 트렌드 목록 조회, 날짜/카테고리 필터 조회 | `trends`, `trend_category_map`, `trend_rank_snapshots`, `user_interest_categories` |
| 최신 이슈/전체 트렌드 | Trend API     | 전체 트렌드 목록 조회                | `trends`, `trend_rank_snapshots`                                                   |
| 트렌드 저장       | Bookmark API  | 저장 등록, 저장 해제, 저장 목록 조회      | `user_trend_bookmarks`, `trends`                                                   |
| 트렌드 검색       | Search API    | 검색 실행, 최근 검색어 조회, 검색 기록 삭제  | `search_logs`, `trends`, `categories`                                              |
| 검색 결과 상세     | Trend API     | 트렌드 상세 조회, 북마크 상태 조회        | `trends`, `trend_ai_analyses`, `trend_sources`, `user_trend_bookmarks`             |
| 트렌드 상세 조회    | Trend API     | 상세 정보, AI 요약, 유행 이유, 출처 조회  | `trends`, `trend_ai_analyses`, `trend_sources`                                     |
| 사이드탭/마이페이지   | User API      | 내 정보 조회, 로그아웃, 회원탈퇴 이동      | `users`, `user_profiles`                                                           |
| 비밀번호 변경      | User API      | 비밀번호 검증 및 변경                | `users.password_hash`, `users.updated_at`                                          |
| 관심사 재설정      | Interest API  | 기존 관심사 조회, 관심사 수정           | `categories`, `user_interest_categories`                                           |

