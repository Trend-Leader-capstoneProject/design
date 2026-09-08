# Trend Leader ERD v2.1 변경 검토 보고서

- 검토 기준일: 2026-09-07
- 기준 ERD: `trend_leader_erd_v2_working.vuerd.json`
- 결과 상태: Category Taxonomy/Trend Mapping 설계 반영, ERD 작업본 및 실제 ORM/Alembic 동기화 전

## 1. 결론

기존 `categories.category_name UNIQUE`는 계층형 Taxonomy에서 서로 다른 상위 카테고리 아래 같은 표시명을 둘 수 없으므로 다음 구조를 표현하지 못한다.

```text
음식
└─ 기타

게임
└─ 기타
```

따라서 `category_name` 전역 UNIQUE 제거 방향은 유지한다.

다만 기존 v2.1 작업안에서 모든 카테고리에 `category_code VARCHAR(50) NOT NULL UNIQUE`를 부여하고 세부분류에 `FOOD_OTHER`, `GAME_OTHER` 같은 코드를 생성하려던 방향은 현재 기능 설계 및 `feature/dev` 구현과 충돌하므로 철회한다.

현재 기준은 다음과 같다.

| 항목 | 현재 목표 |
| --- | --- |
| 표시명 | `category_name VARCHAR(100) NOT NULL`, 전역 UNIQUE 아님 |
| 안정 식별자 | 대분류만 `category_code` 사용 |
| 대분류 코드 | `FASHION`, `FOOD`, `IT_DIGITAL`, `ENTERTAINMENT`, `BEAUTY`, `GAME` |
| 세부분류 코드 | `NULL` 허용 |
| DB Identity | 모든 Category는 `category_id` |
| 계층 | `parent_id` 자기 참조 유지 |
| 활성 상태·정렬 | `is_active`, `sort_order` 유지 |

## 2. 설계안별 비교

| 선택지 | 장점 | 문제 | 판정 |
| --- | --- | --- | --- |
| `category_name` 전역 UNIQUE 유지 | 단순함 | 다른 분기의 `기타`가 충돌함 | 제외 |
| `UNIQUE(parent_id, category_name)`만 적용 | 하위 카테고리는 부모별 중복 허용 | MariaDB UNIQUE의 NULL 처리 때문에 루트 이름 중복까지 단독으로 완전히 표현하기 어려움 | 단독 적용 보류 |
| 모든 Category에 전역 `category_code` 부여 | 환경 간 안정 식별자 확보 | 현재 대분류 전용 `CategoryCode` 계약과 충돌하고 세부분류 코드 관리 비용이 증가 | 제외 |
| 대분류만 `category_code`, 세부분류는 `category_id + parent_id` | 현재 구현과 일치하고 MVP 복잡도가 낮음 | 세부분류의 환경 간 안정 코드가 필요해지면 후속 설계 필요 | 현재 MVP 채택 |

같은 부모 아래 동일한 표시명은 도메인 중복으로 간주한다. 다만 이를 DB에서 어떤 물리 제약으로 강제할지는 Category Admin 기능과 MariaDB 제약 특성을 함께 검토해 별도 구현 설계에서 확정한다. 현재 MVP에는 Category 관리 API가 없으므로 Seed/Migration 검증 및 Service 규칙으로 방어한다.

## 3. Category Taxonomy 역할

Category는 `무슨 주제 영역인가`를 표현하는 분류 체계로 한정한다.

예:

```text
게임
├─ 모바일 게임
├─ PC·온라인 게임
├─ 콘솔 게임
├─ e스포츠
└─ 기타
```

`신제품`, `업데이트`, `이벤트`, `밈`, `논란`, `콜라보`처럼 현상의 성격을 나타내는 값은 Category에 넣지 않는다. 해당 값들은 Trend Attribute 별도 설계 대상으로 보류한다.

`기타`는 각 대분류 안에서 현재 Taxonomy가 표현하지 못하는 항목을 임시 수용하는 fallback으로 사용할 수 있다. 반복적으로 `기타`에 쌓이는 주제가 생기면 신규 세부분류 후보로 재검토한다.

## 4. Trend-Category Mapping 반영

`trend_category_map`의 M:N 구조는 유지한다.

현재 확정 방향은 다음과 같다.

- 하나의 Trend에는 여러 구체적인 세부분류를 연결할 수 있다.
- 서로 다른 대분류에 속한 세부분류를 한 Trend에 함께 연결할 수도 있다.
- Trend에 세부분류를 연결한 경우 해당 부모 대분류를 중복 매핑하지 않는다.
- 사용자의 관심사는 활성 대분류만 저장한다.
- 맞춤 추천은 사용자 관심 대분류의 활성 하위 세부분류 ID 집합으로 확장한 뒤 `trend_category_map`과 매칭한다.
- 하나의 Trend가 같은 관심 대분류 아래 여러 세부분류에 매칭되더라도 결과는 `trend_id` 기준으로 중복 제거한다.
- 대표 Category의 비즈니스 의미는 현재 MVP에서 사용하지 않는다.
- 기존 `is_primary` 컬럼은 즉시 제거하지 않되, 실제 Use Case가 생길 때까지 기본적으로 `false`로 취급한다.

## 5. Hashtag/Keyword 경계

Hashtag는 Category가 아니다.

현재 MVP에서 AI가 생성하거나 추천한 해시태그는 `trend_related_keywords`의 `keyword_type = HASHTAG`로 유지하고 검색·탐색 보조에 활용한다.

실제 외부 Source에서 관측된 해시태그는 AI 분석 결과와 같은 의미로 저장하지 않는다. 실제 Source Hashtag 저장 요구가 생기면 `trend_sources`와 연결되는 별도 구조를 설계한다.

## 6. 변경이 필요하지 않은 영역

### 일반 회원가입

확정안의 `users` 구조는 현재 ERD와 일치한다.

- `login_id`: NULL 허용 + UNIQUE
- `password_hash`: NULL 허용
- `email`: NULL 허용 + UNIQUE
- `status`: 기본값 `ACTIVE`
- `withdrawn_at`, `withdraw_reason`: 존재

비밀번호/이메일 검증 규칙은 API Schema와 Service의 경계 규칙이며 이번 ERD 변경 대상이 아니다.

### 인증 세션 관리와 로그아웃

확정안은 Stateless Access Token 구조를 유지하고 별도 Session/Refresh Token/Revocation 테이블을 만들지 않는다. 이번 변경과 무관하다.

### 관심사 조회와 수정

확정안은 기존 `user_interest_categories`를 그대로 사용한다.

- `UNIQUE(user_id, category_id)` 유지
- `weight` 없음 유지
- `created_at` 유지
- 저장/수정 가능한 관심사는 활성 대분류만 허용
- GET/PUT, diff 수정, Row Lock, bounded retry는 Service/Repository/Transaction 동작이며 새 컬럼을 요구하지 않음

## 7. 함께 발견한 문서/구현 불일치

현재 `feature/dev`의 `CategoryCode`는 대분류 6개만 정의하고, Backend/Frontend Category 계약은 세부분류 `category_code = NULL`을 허용한다.

따라서 다음 v2.1 산출물은 현재 설계와 불일치할 수 있어 후속 동기화 대상이다.

- `schema_decisions_v2.1.md`의 과거 all-node category code 기술: 본 보고서와 함께 수정 대상
- `trend_leader_erd_v2.1_working.vuerd.json`: `category_code VARCHAR(50) NOT NULL` 또는 모든 Category 코드 전제를 확인해 수정 필요
- ERD v2.1 이미지: JSON 수정 후 재생성 필요

또한 `Trend_Leader_fixed.sql`은 `depth`, `weight`, `user_interest_keywords` 등 과거 구조를 포함하므로 현재 수정 기준으로 사용하지 않는다.

## 8. 실제 구현 반영 순서

최신 `feature/dev` ORM과 Alembic Revision을 기준으로 다음 순서로 진행한다.

1. 현재 `categories.category_name` 전역 UNIQUE의 실제 제약 이름과 DB 적용 상태 확인
2. 기존 데이터에서 같은 부모 아래 동일 `category_name` 중복 여부 검증
3. `category_name` 전역 UNIQUE 제거 Migration 작성
4. 대분류 6개의 `category_code`가 NOT NULL/UNIQUE인지 검증
5. 세부분류 `category_code = NULL` 계약 유지
6. `음식 > 기타`와 `게임 > 기타`가 동시에 저장되는 Integration Test 추가
7. 같은 부모 아래 동일 표시명은 Seed/Service 검증에서 거부되는지 테스트
8. 카테고리 목록 API 및 관심사 API 전체 회귀 테스트
9. 이후 Trend 추천 구현 시 대분류 → 활성 세부분류 확장 조회와 `trend_id` 중복 제거 적용

모든 세부분류에 코드를 Backfill하고 `category_code NOT NULL`로 강제하는 Migration은 수행하지 않는다.

## 9. 이번 산출물의 경계

이번 수정은 Category Taxonomy와 Trend Mapping에 대한 최신 설계 결정을 문서화한 것이다.

아직 완료로 판정하지 않는 항목:

- ERD JSON/이미지 동기화
- 실제 DB Migration 완료
- Backend/Frontend 계약 반영 완료
- Seed 최종 목록 확정 및 반영
- Trend Attribute 설계
- 실제 Source Hashtag 저장 구조
- 맞춤 Trend API 구현 및 테스트

실제 코드 반영 전에는 최신 `dev` HEAD와 working tree를 기준으로 제약 이름, 기존 데이터, API 응답 필드를 다시 확인한다.
