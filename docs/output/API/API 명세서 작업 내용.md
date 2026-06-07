| API 그룹   | 세부 API       | Method       | Endpoint 예시                                 | 상태 |
| -------- | ------------ | ------------ | ------------------------------------------- | -- |
| Auth     | 회원가입 등록      | POST         | `/api/auth/signup`                          | 완료 |
| Auth     | 아이디 중복 확인    | GET          | `/api/auth/check-login-id`                  | 완료 |
| Auth     | 로그인          | POST         | `/api/auth/login`                           | 완료 |
| Auth     | 구글 로그인       | POST         | `/api/auth/google-login`                    | 완료 |
| Auth     | 로그아웃         | POST         | `/api/auth/logout`                          | 완료 |
| User     | 내 정보 조회      | GET          | `/api/users/me`                             | 완료 |
| User     | 회원 정보 수정     | PATCH        | `/api/users/me`                             | 완료 |
| User     | 비밀번호 변경      | PATCH        | `/api/users/me/password`                    | 완료 |
| User     | 회원 탈퇴        | DELETE       | `/api/users/me`                             | 완료 |
| Interest | 카테고리 목록 조회   | GET          | `/api/categories`                           | 예정 |
| Interest | 관심사 저장       | POST         | `/api/users/me/interests`                   | 예정 |
| Interest | 기존 관심사 조회    | GET          | `/api/users/me/interests`                   | 예정 |
| Interest | 관심사 수정       | PUT 또는 PATCH | `/api/users/me/interests`                   | 예정 |
| Trend    | 맞춤 트렌드 목록 조회 | GET          | `/api/trends/recommended`                   | 예정 |
| Trend    | 전체 트렌드 목록 조회 | GET          | `/api/trends`                               | 예정 |
| Trend    | 트렌드 상세 조회    | GET          | `/api/trends/{trend_id}`                    | 예정 |
| Bookmark | 트렌드 저장 등록    | POST         | `/api/trends/{trend_id}/bookmark`           | 예정 |
| Bookmark | 트렌드 저장 해제    | DELETE       | `/api/trends/{trend_id}/bookmark`           | 예정 |
| Bookmark | 저장 트렌드 목록 조회 | GET          | `/api/users/me/bookmarks`                   | 예정 |
| Search   | 트렌드 검색 실행    | GET          | `/api/trends/search`                        | 예정 |
| Search   | 최근 검색어 조회    | GET          | `/api/users/me/search-logs`                 | 예정 |
| Search   | 검색 기록 삭제     | DELETE       | `/api/users/me/search-logs/{search_log_id}` | 예정 |
