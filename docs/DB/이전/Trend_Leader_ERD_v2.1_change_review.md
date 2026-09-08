# Trend Leader ERD v2.1 변경 검토 보고서

- 검토 기준일: 2026-09-07
- 기준 ERD: `trend_leader_erd_v2_working.vuerd.json`
- 결과 상태: ERD 작업본 수정 완료, 실제 ORM/Alembic 반영 전

## 1. 결론

지금까지 확정된 회원가입, 인증 세션 관리, 관심사 조회·수정 설계를 현재 ERD v2와 대조한 결과, 실제 컬럼 변경이 필요한 부분은 `categories`의 식별 정책 한 곳이다.

기존 `categories.category_name UNIQUE`는 서로 다른 상위 카테고리 아래에 같은 표시명을 둘 수 없으므로 다음 구조를 표현하지 못한다.

```text
음식
└─ 기타

게임
└─ 기타
```

따라서 ERD v2.1 작업본은 표시명과 시스템 식별자를 분리했다.

| 항목 | v2 | v2.1 작업본 |
| --- | --- | --- |
| 표시명 | `category_name VARCHAR(100) NOT NULL UNIQUE` | `category_name VARCHAR(100) NOT NULL` |
| 안정 식별자 | 없음 | `category_code VARCHAR(50) NOT NULL UNIQUE` |
| 계층 | `parent_id` 자기 참조 | 유지 |
| 활성 상태·정렬 | `is_active`, `sort_order` | 유지 |

## 2. 설계안별 비교

| 선택지 | 장점 | 문제 | 판정 |
| --- | --- | --- | --- |
| `category_name` 전역 UNIQUE 유지 | 가장 단순함 | 다른 분기의 `기타`가 충돌함 | 제외 |
| `UNIQUE(parent_id, category_name)`만 적용 | 하위 카테고리는 부모별 중복 허용 | MariaDB UNIQUE는 NULL을 여러 개 허용하므로 `parent_id IS NULL`인 대분류 이름 중복을 완전히 막지 못함 | 단독 적용 제외 |
| `category_code` 전역 UNIQUE + 표시명 비 UNIQUE | 이름과 식별 책임이 분리되고 이름 변경에도 참조가 안정적임 | 같은 부모 안의 표시명 중복은 별도 정책이 필요함 | 현재 MVP 채택 |

현재 MVP에는 Category Admin 기능이 없으므로 같은 부모 안의 표시명 중복은 Seed/Migration 검증으로 막는다. Admin 기능을 도입할 때는 해당 규칙을 별도 불변조건으로 확정하고 DB 강제 방식까지 다시 검토한다.

## 3. 코드 체계

`category_code`는 다음 규칙을 사용한다.

- 형식: 영문 대문자, 숫자, 밑줄을 사용하는 UPPER_SNAKE_CASE
- 길이: 최대 50자
- 역할: Seed, 내부 정책, 환경 간 데이터 매핑에 사용하는 안정 식별자
- 변경: 표시명만 바뀌는 경우 자동 변경하지 않음
- 중복: 전체 카테고리에서 허용하지 않음

예시:

| 계층 | 표시명 | 코드 |
| --- | --- | --- |
| 대분류 | 음식 | `FOOD` |
| 세부분류 | 기타 | `FOOD_OTHER` |
| 대분류 | 게임 | `GAME` |
| 세부분류 | 기타 | `GAME_OTHER` |

## 4. 변경이 필요하지 않은 영역

### 일반 회원가입

확정안의 `users` 구조는 현재 ERD와 일치한다.

- `login_id`: NULL 허용 + UNIQUE
- `password_hash`: NULL 허용
- `email`: NULL 허용 + UNIQUE
- `status`: 기본값 `ACTIVE`
- `withdrawn_at`, `withdraw_reason`: 존재

비밀번호 15~128자, 이메일 형식/길이 같은 규칙은 API Schema와 Service의 경계 규칙이며 ERD 컬럼 추가 대상이 아니다. `email VARCHAR(255)`는 이미 반영되어 있다.

### 인증 세션 관리와 로그아웃

확정안은 Stateless Access Token 구조를 유지하고 별도 Session/Refresh Token/Revocation 테이블을 만들지 않는다. 따라서 ERD에 인증 세션 테이블을 추가하지 않았다.

### 관심사 조회와 수정

확정안은 기존 `user_interest_categories`를 그대로 사용한다.

- `UNIQUE(user_id, category_id)` 유지
- `weight` 없음 유지
- `created_at` 유지
- GET/PUT, diff 수정, Row Lock, bounded retry는 Service/Repository/Transaction 동작이며 새 컬럼을 요구하지 않음

## 5. 함께 발견한 문서 불일치

다음 자료는 현재 ERD의 수정 기준으로 사용하면 안 된다.

- `Trend_Leader_fixed.sql`: `depth`, `weight`, `user_interest_keywords`, 오래된 기본값과 컬럼을 포함한 과거 SQL이다.
- `README.md`: Database 주요 테이블에 MVP에서 제외된 `user_interest_keywords`가 아직 남아 있다.
- `API명세서_노션링크_20260816기준.pdf`: 상세 계약 자체가 아니라 Notion 페이지 목록과 링크를 담은 색인 문서다.

위 항목 중 실제 프로젝트 README와 Notion을 수정할 때는 최신 `dev` 코드 및 Migration을 다시 확인해야 한다.

## 6. 실제 구현 반영 순서

현재 저장소의 ORM과 Alembic Revision을 확인한 뒤 다음 순서로 반영한다.

1. `category_code`를 일시적으로 NULL 허용으로 추가
2. 기존 카테고리 코드 Backfill
3. NULL 및 중복 검증
4. `category_code` NOT NULL + UNIQUE 적용
5. `category_name` 전역 UNIQUE 제거
6. ORM, Category Response Schema, Seed 데이터 동기화 여부 확인
7. `음식 > 기타`와 `게임 > 기타`가 함께 저장되는 Integration Test 추가
8. 기존 관심사 API 회귀 테스트 실행

기존 데이터가 있는 DB에 `NOT NULL UNIQUE` 컬럼을 즉시 추가하면 Backfill 전에 Migration이 실패할 수 있으므로 단계적으로 처리한다.

## 7. 이번 산출물의 경계

이번 수정은 첨부된 설계 문서와 ERD를 기준으로 한 목표 스키마 작업본이다. 현재 `dev` 저장소의 ORM, Alembic, Seed, Category API 구현 파일은 제공되지 않았으므로 다음은 완료로 판정하지 않는다.

- 실제 DB Migration 완료
- Backend/Frontend 계약 반영 완료
- 테스트 통과
- 기능 완료

실제 코드 반영 전에는 최신 `dev` HEAD와 working tree를 기준으로 제약 이름, 기존 데이터, API 응답 필드를 다시 확인해야 한다.
