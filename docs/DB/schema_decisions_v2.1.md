# Trend Leader Schema Decisions v2.1

## 문서 상태

- 상태: Working Update - Category Taxonomy / Trend Mapping 반영, ORM·Alembic 검증 전
- 대상 버전: ERD v2.1
- 기준일: 2026-09-07
- DBMS: MariaDB
- ORM: SQLAlchemy 2.x
- Migration: Alembic
- 기반 동결 태그: `erd-v2-freeze`
- 변경 목적: 계층형 카테고리의 표시명 정책, 대분류 식별 코드, 트렌드-세부분류 매핑 정책을 현재 MVP 설계와 일치시키기 위함

## v2.1 변경 요약

- ERD v2의 초기 동결 기록은 그대로 보존한다.
- `categories.category_name`의 전역 UNIQUE를 제거하는 방향으로 변경한다.
- `category_name`은 사용자에게 보여 주는 표시명으로 사용하며 전역 식별자로 사용하지 않는다.
- 서로 다른 부모 아래에서는 같은 표시명을 허용한다. 예: `음식 > 기타`, `게임 > 기타`.
- `category_code`는 대분류의 안정적인 시스템 식별자에만 사용한다.
- 현재 대분류 코드는 `FASHION`, `FOOD`, `IT_DIGITAL`, `ENTERTAINMENT`, `BEAUTY`, `GAME` 6개를 기준으로 한다.
- 세부분류는 `category_code = NULL`을 허용하고 `category_id`와 `parent_id` 관계로 식별한다.
- 하나의 트렌드는 여러 구체적인 세부분류와 연결할 수 있다.
- 트렌드에는 부모 대분류를 중복 매핑하지 않고, 맞춤 추천 시 사용자 관심 대분류의 활성 하위 세부분류 범위로 확장하여 조회한다.
- 대표 카테고리(`is_primary`)의 비즈니스 사용은 실제 Use Case가 생길 때까지 보류한다.
- 이 문서는 목표 스키마와 도메인 규칙을 정의한다. 실제 ORM과 Alembic 반영 여부는 대상 브랜치 최신 HEAD에서 별도로 검증한다.

## 기준 산출물

- 설계 단계: ERD v2.1 + 본 문서 + 기능별 카테고리 Taxonomy/Trend 매핑 설계 문서
- 구현 단계: SQLAlchemy ORM + Alembic
- SQL 파일: 참고 또는 검증용 산출물

## 확정 사항

### SD-001 테이블 명명 규칙

- 테이블명은 snake_case 복수형을 사용한다.
- `user`는 `users`로 변경한다.
- SQLAlchemy 클래스명은 단수형 PascalCase를 사용한다.
- 예: `users` → `User`

### SD-002 기존 파일 처리

- 기존 ERD 및 SQL은 archive에 보관한다.
- 기존 SQL 파일은 초기 마이그레이션 생성 기준으로 사용하지 않는다.

### SD-003 사용자 인증 저장 방식

- 일반 로그인과 OAuth 사용자는 동일한 `users` 테이블에서 관리한다.
- `login_id`와 `password_hash`는 OAuth 전용 사용자를 위해 NULL을 허용한다.
- 일반 회원가입 시에는 Service 계층에서 `login_id`와 비밀번호 입력을 필수로 검증한다.
- OAuth 전용 사용자는 하나 이상의 `oauth_accounts` 행을 가져야 한다.
- 별도의 `auth_type` 컬럼은 추가하지 않는다.
- 하나의 사용자가 일반 로그인과 OAuth 로그인을 함께 사용할 수 있도록 설계한다.

### SD-004 OAuth 계정 연결 정책

- OAuth 계정 식별은 `(provider, provider_user_id)` 조합을 기준으로 한다.
- 기존 OAuth 계정이 있으면 연결된 사용자로 로그인한다.
- 신규 OAuth 로그인에서 검증된 이메일이 기존 사용자 이메일과 같으면 해당 사용자에게 OAuth 계정을 연결한다.
- 일치하는 사용자가 없으면 신규 `users`와 `oauth_accounts`를 생성한다.

### SD-005 회원 탈퇴 정책

- 회원 탈퇴는 `users.status = 'WITHDRAWN'`로 처리하는 소프트 삭제 방식을 사용한다.
- 탈퇴 시각은 `withdrawn_at`에 저장한다.
- 선택적으로 입력받은 탈퇴 사유는 `withdraw_reason`에 저장한다.
- 탈퇴 사용자의 Access Token은 이후 인증에서 거부한다.
- 관련 데이터의 익명화 및 보존 기간은 별도 정책으로 결정한다.

### SD-006 카테고리 계층 구조와 식별 정책

- 카테고리 계층은 `categories.parent_id` 자기 참조 관계로 표현한다.
- `parent_id IS NULL`인 카테고리를 대분류로 판단한다.
- `parent_id IS NOT NULL`인 카테고리를 세부분류로 판단한다.
- `parent_id`와 중복되는 상태를 저장하지 않기 위해 `depth` 컬럼은 사용하지 않는다.
- 초기 버전에서는 대분류와 세부분류의 2단계까지만 허용하며, 3단계 이상 계층은 허용하지 않는다.
- 신규 카테고리는 기본적으로 사용할 수 있도록 `is_active`의 기본값을 `1`로 설정한다.
- `category_name`은 사용자에게 표시하는 이름이며 전역 식별자로 사용하지 않는다.
- 서로 다른 부모 카테고리 아래에서는 같은 `category_name`을 허용한다.
- 같은 부모 아래의 동일한 `category_name`은 도메인 중복으로 간주하여 허용하지 않는다.
- `category_code`는 대분류의 안정적인 시스템 식별자에만 사용한다.
- 대분류의 `category_code`는 NOT NULL이며 전역 UNIQUE를 유지한다.
- 현재 대분류 코드는 `FASHION`, `FOOD`, `IT_DIGITAL`, `ENTERTAINMENT`, `BEAUTY`, `GAME` 6개를 사용한다.
- 세부분류의 `category_code`는 NULL을 허용한다.
- 세부분류의 DB Identity는 `category_id`이며, 소속 대분류는 `parent_id`로 판별한다.
- 표시명 변경만으로 대분류 `category_code`를 자동 변경하지 않는다. 코드 변경은 데이터 참조 영향을 검토하는 명시적 Migration으로 수행한다.
- 세부분류에 안정 코드가 필요한 외부 연동·환경 간 매핑 요구가 실제로 생기면 별도 설계로 다시 검토한다.
- 같은 부모 아래 이름 중복을 DB에서 어떤 물리 제약으로 강제할지는 MariaDB NULL/UNIQUE 특성과 Category 관리 기능 범위를 확인한 뒤 별도 구현 설계에서 확정한다. 현재 MVP에서는 Seed/Migration 검증과 Service 규칙으로 방어한다.

### SD-007 사용자 관심 카테고리 저장 방식

- 사용자의 초기 관심사는 `user_interest_categories`에 저장한다.
- 사용자와 카테고리 조합은 중복될 수 없도록 `(user_id, category_id)` 복합 UNIQUE 제약을 사용한다.
- 초기 버전에서는 선택 여부만 저장하며 별도의 관심도 가중치를 계산하지 않는다.
- 이에 따라 `user_interest_categories.weight` 컬럼은 제거한다.
- 관심사 저장 및 수정 시 존재하는 활성 카테고리인지를 Service 계층에서 검증한다.
- 초기 관심사 선택 및 수정에서는 활성 대분류 카테고리만 선택할 수 있도록 제한한다.

### SD-008 사용자 관심 키워드 기능 연기

- `user_interest_keywords`는 초기 MVP 구현 범위에서 제외한다.
- 현재 API와 화면 흐름은 관심 카테고리 선택만 사용한다.
- 사용자 관심 키워드는 클릭, 조회, 저장 등의 활동 데이터를 활용한 추천 고도화 단계에서 다시 설계한다.
- 따라서 ERD v2.1 목표 스키마에도 `user_interest_keywords`를 포함하지 않는다.

### SD-009 트렌드 중복 식별 방식

- 트렌드의 사용자 표시 제목은 `trends.title`에 저장한다.
- 중복 식별에는 Service 계층에서 정규화한 `trends.normalized_title`을 사용한다.
- 제목 정규화 시 앞뒤 공백 제거, 연속 공백 축소, 대소문자 통일, 불필요한 구분자 제거를 수행한다.
- 초기 MVP에서는 `normalized_title`에 UNIQUE 제약을 적용한다.
- 같은 정규화 제목의 트렌드가 다시 수집되면 새로운 트렌드를 생성하지 않고 기존 트렌드의 `last_collected_at`을 갱신한다.
- 의미가 다르지만 정규화 결과가 같은 예외는 운영 과정에서 수동으로 식별하며, 별칭 및 병합 기능은 후속 버전에서 설계한다.

### SD-010 트렌드 수집 시각 관리

- 트렌드가 최초로 발견된 시각은 `first_collected_at`에 저장한다.
- 같은 트렌드가 다시 발견된 가장 최근 시각은 `last_collected_at`에 저장한다.
- `updated_at`은 제목, 요약, 썸네일, 상태 등 트렌드 자체 정보가 변경된 시각을 의미한다.
- 수집 직후 AI 분석이 완료되지 않을 수 있으므로 `trends.summary`는 NULL을 허용한다.

### SD-011 트렌드 출처 저장 방식

- 하나의 트렌드는 여러 개의 출처를 가질 수 있다.
- 수집 플랫폼은 `trend_sources.platform`에 `VARCHAR(30)`으로 저장하고, 허용값은 백엔드 enum으로 제한한다.
- 외부 플랫폼이 제공하는 고유 식별자는 `external_id`에 저장한다.
- 출처 중복 식별을 위해 플랫폼과 외부 식별자 또는 정규화 URL을 조합한 SHA-256 값을 `source_key`에 저장한다.
- 동일 트렌드에 같은 출처가 중복 저장되지 않도록 `(trend_id, source_key)` 복합 UNIQUE 제약을 사용한다.
- 외부 플랫폼의 추가가 DB ENUM 변경으로 이어지지 않도록 플랫폼은 MariaDB ENUM으로 저장하지 않는다.

### SD-012 트렌드 카테고리 매핑

- 트렌드와 카테고리는 `trend_category_map`을 통해 다대다 관계로 연결한다.
- 동일 트렌드와 카테고리 조합은 중복될 수 없도록 `(trend_id, category_id)` 복합 UNIQUE 제약을 사용한다.
- 하나의 트렌드에는 여러 구체적인 세부분류 카테고리를 연결할 수 있다.
- 하나의 트렌드가 서로 다른 대분류에 속한 세부분류들과 동시에 연결되는 것도 허용한다.
- 트렌드가 세부분류에 연결된 경우 해당 세부분류의 부모 대분류를 `trend_category_map`에 중복 저장하지 않는다.
- 대표 카테고리의 비즈니스 의미와 선정 규칙은 MVP에서 사용하지 않고 보류한다.
- 기존 `is_primary` 컬럼은 즉시 제거하지 않으며, 대표 카테고리 Use Case가 확정되기 전까지 기본적으로 `false`로 취급한다.
- 카드에서 카테고리 2~3개를 표시하는 UI 정책은 대표 카테고리 도메인 규칙과 분리한다.
- 트렌드 카테고리 연결 시각은 `created_at`에 저장한다.

### SD-013 트렌드 순위 스냅샷

- 플랫폼별 트렌드 순위는 현재값을 덮어쓰지 않고 `trend_rank_snapshots`에 시계열로 누적한다.
- 순위 컬럼명은 `rank` 대신 `ranking`을 사용한다.
- 수집 날짜와 수집 시각을 중복 저장하지 않고 `snapshot_at` 하나로 통일한다.
- 순위 변동 방향 ENUM 대신 이전 순위와 현재 순위의 차이를 나타내는 `rank_delta`를 저장한다.
- `rank_delta`는 `이전 순위 - 현재 순위`로 계산하며, 양수는 상승, 음수는 하락, 0은 동일, NULL은 신규 진입을 의미한다.
- 플랫폼이 제공하는 점수의 소수 값을 보존할 수 있도록 `score`는 `DECIMAL(12, 4)`로 저장한다.
- 동일 시점의 중복 스냅샷을 방지하기 위해 `(trend_id, platform, snapshot_at)` 복합 UNIQUE 제약을 사용한다.

### SD-014 AI 분석 결과 버전 관리

- 하나의 트렌드는 여러 개의 AI 분석 결과를 가질 수 있다.
- AI 분석 결과는 생성 이후 수정하지 않는 불변 데이터로 관리한다.
- 분석 내용이 변경되거나 재분석이 필요한 경우 기존 행을 수정하지 않고 새로운 분석 버전을 생성한다.
- 분석 버전은 `analysis_version`에 저장한다.
- 동일 트렌드에서 분석 버전이 중복되지 않도록 `(trend_id, analysis_version)` 복합 UNIQUE 제약을 사용한다.
- 초기 MVP에서는 성공한 AI 분석 결과만 `trend_ai_analyses`에 저장한다.
- 분석 작업의 대기, 실행, 실패 상태 관리는 비동기 분석 기능 도입 시 별도의 작업 테이블로 분리한다.

### SD-015 현재 AI 분석 선택 방식

- 트렌드 상세 조회에서는 해당 트렌드의 `analysis_version`이 가장 큰 분석 결과를 현재 분석으로 사용한다.
- 현재 분석을 별도로 표시하는 `is_current` 컬럼은 사용하지 않는다.
- 분석 결과가 존재하지 않으면 트렌드 상세 API의 `ai_analysis`는 NULL을 반환한다.
- AI 분석이 없는 경우 `trends.summary`를 기본 설명으로 사용할 수 있다.

### SD-016 AI 모델 및 프롬프트 정보

- AI 제공자는 `model_provider`에 `VARCHAR(30)`으로 저장한다.
- 사용한 실제 모델 설정명은 `model_name`에 `VARCHAR(100)`으로 저장한다.
- 모델 추가 또는 변경이 DB 스키마 변경으로 이어지지 않도록 모델 정보에는 MariaDB ENUM을 사용하지 않는다.
- AI 분석에 사용한 프롬프트 버전은 `prompt_version`에 저장한다.
- `trends.summary`는 기본 또는 수집 기반 요약이며, `trend_ai_analyses.one_line_summary`는 AI가 생성한 상세 화면용 요약으로 구분한다.

### SD-017 관련 키워드와 분석 버전 연결

- 관련 키워드는 트렌드에 직접 연결하지 않고 해당 키워드를 생성한 AI 분석에 연결한다.
- `trend_related_keywords.trend_id`는 제거하고 `analysis_id`를 외래 키로 사용한다.
- 하나의 AI 분석은 여러 관련 키워드를 가질 수 있다.
- 키워드 원문은 `keyword`, 중복 비교용 정규화 값은 `normalized_keyword`에 저장한다.
- 동일 분석에 같은 키워드가 중복 저장되지 않도록 `(analysis_id, normalized_keyword)` 복합 UNIQUE 제약을 사용한다.
- 키워드 유형은 `RELATED`, `HASHTAG`, `RECOMMENDED`로 구분한다.
- MVP에서 `HASHTAG`는 AI 분석이 생성하거나 추천한 해시태그 표현을 의미하며 검색·탐색 보조에 활용한다.
- 실제 외부 Source에서 관측된 해시태그는 AI 분석 결과와 같은 의미로 저장하지 않는다. 실제 Source Hashtag 저장 요구가 생기면 별도 구조를 설계한다.
- 트렌드 상세 조회에서는 현재 AI 분석에 연결된 관련 키워드만 반환한다.

### SD-018 사용자 트렌드 북마크 저장 방식

- 사용자와 트렌드의 북마크 관계는 `user_trend_bookmarks`에 저장한다.
- 하나의 사용자가 같은 트렌드를 중복 저장할 수 없도록 `(user_id, trend_id)` 복합 UNIQUE 제약을 사용한다.
- 북마크 등록 API는 동일한 북마크가 이미 존재하는 경우 중복 행을 생성하지 않고 기존 북마크 상태를 반환한다.
- 북마크 해제 시 해당 행을 물리적으로 삭제한다.
- 북마크에는 별도의 `is_deleted`, `deleted_at`, `updated_at` 컬럼을 추가하지 않는다.
- 같은 트렌드를 해제한 뒤 다시 저장하면 새로운 북마크 행과 생성 시각을 기록한다.

### SD-019 최근 검색어 저장 방식

- `search_logs`는 초기 MVP에서 사용자별 최근 검색어를 저장하는 용도로 사용한다.
- 사용자가 입력한 원문은 `keyword`, 중복 비교용 정규화 값은 `normalized_keyword`에 저장한다.
- 같은 사용자의 동일한 정규화 검색어가 중복 저장되지 않도록 `(user_id, normalized_keyword)` 복합 UNIQUE 제약을 사용한다.
- 같은 검색어를 다시 실행하면 새 행을 추가하지 않고 기존 행의 원문, 카테고리, 결과 수, 검색 시각을 갱신한다.
- 카테고리 필터 없이 검색할 수 있도록 `category_id`는 NULL을 허용한다.
- 검색 결과 수는 `result_count`에 마지막 검색 실행 결과를 저장한다.
- 최근 검색어는 `searched_at` 내림차순으로 조회한다.

### SD-020 최근 검색어 삭제 및 보존 정책

- 사용자가 검색 기록 삭제를 요청하면 해당 `search_logs` 행을 물리적으로 삭제한다.
- 검색 기록에는 별도의 `is_deleted` 컬럼을 사용하지 않는다.
- 최근 검색어는 사용자당 최대 20개를 유지한다.
- 새로운 검색어 저장 후 최대 개수를 초과한 오래된 검색어는 삭제한다.
- 향후 검색 이벤트 분석이 필요하면 최근 검색어 테이블을 확장하지 않고 별도의 `search_events` 테이블을 설계한다.

### SD-021 카테고리 Taxonomy와 맞춤 추천 매칭

- Category는 `무슨 주제 영역인가`를 표현하는 분류 체계로 한정한다.
- `신제품`, `업데이트`, `이벤트`, `밈`, `논란`, `콜라보`처럼 현상의 성격을 나타내는 값은 Category에 포함하지 않는다.
- 위와 같은 현상형 메타데이터의 구조화 여부는 Trend Attribute 별도 설계로 보류한다.
- 사용자의 관심사는 활성 대분류만 저장한다.
- 트렌드에는 가능한 구체적인 세부분류만 연결한다.
- 맞춤 추천은 사용자 관심 대분류의 활성 하위 세부분류 ID 집합을 구한 뒤 `trend_category_map`과 매칭한다.
- 하나의 트렌드가 같은 관심 대분류 아래 여러 세부분류에 매칭되더라도 결과 목록에서는 `trend_id` 기준으로 중복 반환하지 않는다.
- `기타` 세부분류는 각 대분류 안에서 현재 Taxonomy가 표현하지 못하는 항목을 임시 수용하는 fallback으로 사용할 수 있다.
- `기타`에 반복적으로 누적되는 주제가 생기면 신규 세부분류 후보로 재검토한다.
- 세부분류 Seed의 정확한 최종 목록은 기능별 Taxonomy 문서에서 관리한다.

## ORM 및 Migration 반영 사항

- 아래의 복합 UNIQUE, 조회 인덱스, 외래 키 삭제 정책은 SQLAlchemy ORM과 Alembic Migration에서 물리적으로 반영한다.
- ERD Editor에는 PK, FK, 컬럼 및 관계를 표현하고, 복합 제약과 조회 인덱스의 최종 기준은 본 문서로 관리한다.
- 현재 ERD v2.1 작업본에 모든 카테고리용 `category_code VARCHAR(50) NOT NULL`이 남아 있다면 본 문서와 불일치하므로 후속 ERD 동기화 대상이다.

## 유니크 키 반영 사항

### 복합

```text
oauth_accounts
UNIQUE(provider, provider_user_id)

user_interest_categories
UNIQUE(user_id, category_id)

trend_category_map
UNIQUE(trend_id, category_id)

trend_sources
UNIQUE(trend_id, source_key)

trend_rank_snapshots
UNIQUE(trend_id, platform, snapshot_at)

trend_ai_analyses
UNIQUE(trend_id, analysis_version)

user_trend_bookmarks
UNIQUE(user_id, trend_id)

search_logs
UNIQUE(user_id, normalized_keyword)

trend_related_keywords
UNIQUE(analysis_id, normalized_keyword)
```

### 개별

```text
users.login_id
users.email
user_profiles.user_id
categories.category_code  # 대분류 값에 대해서만 사용, 세부분류 NULL 허용
trends.normalized_title
```

`categories.category_name`은 전역 개별 UNIQUE 대상에서 제외한다.

## 조회 인덱스

```text
categories
INDEX(parent_id, is_active, sort_order)
INDEX(parent_id, category_name)

trends
INDEX(status, last_collected_at)

trend_category_map
INDEX(category_id, trend_id)

trend_rank_snapshots
INDEX(platform, snapshot_at, ranking)
INDEX(trend_id, snapshot_at)

user_trend_bookmarks
INDEX(user_id, created_at)

search_logs
INDEX(user_id, searched_at)

trend_related_keywords
INDEX(analysis_id, keyword_type, sort_order)
```

## ERD v2.1 Migration 영향

현재 `feature/dev` 구현은 대분류 6개용 `CategoryCode`와 세부분류 `category_code = NULL`을 이미 전제로 하고 있으므로, 모든 세부분류에 별도 코드를 Backfill하는 Migration은 수행하지 않는다.

현재 코드와 Migration을 다시 확인한 뒤 다음 순서로 반영한다.

1. `categories.category_name`의 기존 전역 UNIQUE 제약 이름과 현재 DB 적용 상태를 확인한다.
2. 기존 데이터에서 같은 부모 아래 동일한 `category_name` 중복이 없는지 검증한다.
3. `category_name`의 전역 UNIQUE 제약을 제거한다.
4. 대분류 `category_code` 6개가 NOT NULL이고 중복되지 않는지 검증한다.
5. 세부분류의 `category_code`가 NULL인 현재 계약을 유지한다.
6. `음식 > 기타`와 `게임 > 기타`처럼 서로 다른 부모 아래 같은 표시명을 함께 저장할 수 있는 Integration Test를 추가한다.
7. 같은 부모 아래 동일한 표시명은 Seed/Service 검증에서 거부되는지 테스트한다.
8. 기존 카테고리 목록 및 관심사 API 회귀 테스트를 실행한다.

실제 제약 이름과 Alembic Revision은 대상 브랜치의 현재 ORM 및 Migration을 확인해 결정한다.

## 외래키 삭제 정책

| 부모 관계 | 권장 정책 |
| --- | --- |
| `users → user_profiles` | `CASCADE` |
| `users → oauth_accounts` | `CASCADE` |
| `users → user_interest_categories` | `CASCADE` |
| `users → user_trend_bookmarks` | `CASCADE` |
| `users → search_logs` | `CASCADE` |
| `categories → categories.parent_id` | `RESTRICT` |
| `categories → user_interest_categories` | `RESTRICT` |
| `categories → trend_category_map` | `RESTRICT` |
| `categories → search_logs` | `SET NULL` |
| `trends → trend_category_map` | `CASCADE` |
| `trends → trend_sources` | `CASCADE` |
| `trends → trend_rank_snapshots` | `CASCADE` |
| `trends → trend_ai_analyses` | `CASCADE` |
| `trends → user_trend_bookmarks` | `CASCADE` |
| `trend_ai_analyses → trend_related_keywords` | `CASCADE` |

## 트렌드 요약 VS AI 요약

`trends.summary`
- 수집 데이터 또는 기본 설명
- 목록 카드와 AI 분석 전 fallback에 사용
- NULL 허용

`trend_ai_analyses.one_line_summary`
- AI가 생성한 최신 분석 요약
- 트렌드 상세 화면에 사용
- 분석 행에서는 NOT NULL

## DB 코멘트 작성 기준

PK
→ "{대상} ID 일련번호"

FK
→ "{관계 대상 또는 역할} ID"

시간
→ "생성 시각", "수정 시각", "검색 실행 시각"

Boolean
→ "{상태} 여부"

정규화 값
→ "중복 비교용 정규화 {대상}"
