# Trend Leader Schema Decisions

## 문서 상태

- 상태: Working Draft
- 대상 버전: ERD v2
- DBMS: MariaDB
- ORM: SQLAlchemy 2.x
- Migration: Alembic

## 기준 산출물

- 설계 단계: ERD v2 + 본 문서
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

### SD-006 카테고리 계층 구조

* 카테고리 계층은 `categories.parent_id` 자기 참조 관계로 표현한다.
* `parent_id IS NULL`인 카테고리를 대분류로 판단한다.
* `parent_id IS NOT NULL`인 카테고리를 세부분류로 판단한다.
* `parent_id`와 중복되는 상태를 저장하지 않기 위해 `depth` 컬럼은 제거한다.
* 초기 버전에서는 대분류와 세부분류의 2단계까지만 허용하며, Service 계층에서 3단계 이상의 생성을 제한한다.
* 신규 카테고리는 기본적으로 사용할 수 있도록 `is_active`의 기본값을 `1`로 설정한다.

### SD-007 사용자 관심 카테고리 저장 방식

* 사용자의 초기 관심사는 `user_interest_categories`에 저장한다.
* 사용자와 카테고리 조합은 중복될 수 없도록 `(user_id, category_id)` 복합 UNIQUE 제약을 사용한다.
* 초기 버전에서는 선택 여부만 저장하며 별도의 관심도 가중치를 계산하지 않는다.
* 이에 따라 `user_interest_categories.weight` 컬럼은 제거한다.
* 관심사 저장 및 수정 시 존재하는 활성 카테고리인지를 Service 계층에서 검증한다.
* 초기 관심사 선택 화면에서는 대분류 카테고리만 선택할 수 있도록 제한한다.

### SD-008 사용자 관심 키워드 기능 연기

* `user_interest_keywords`는 초기 MVP 구현 범위에서 제외한다.
* 현재 API와 화면 흐름은 관심 카테고리 선택만 사용한다.
* 사용자 관심 키워드는 클릭, 조회, 저장 등의 활동 데이터를 활용한 추천 고도화 단계에서 다시 설계한다.
* 따라서 ERD v2와 초기 SQLAlchemy ORM 및 Alembic Migration에는 `user_interest_keywords`를 포함하지 않는다.

### SD-009 트렌드 중복 식별 방식

* 트렌드의 사용자 표시 제목은 `trends.title`에 저장한다.
* 중복 식별에는 Service 계층에서 정규화한 `trends.normalized_title`을 사용한다.
* 제목 정규화 시 앞뒤 공백 제거, 연속 공백 축소, 대소문자 통일, 불필요한 구분자 제거를 수행한다.
* 초기 MVP에서는 `normalized_title`에 UNIQUE 제약을 적용한다.
* 같은 정규화 제목의 트렌드가 다시 수집되면 새로운 트렌드를 생성하지 않고 기존 트렌드의 `last_collected_at`을 갱신한다.
* 의미가 다르지만 정규화 결과가 같은 예외는 운영 과정에서 수동으로 식별하며, 별칭 및 병합 기능은 후속 버전에서 설계한다.

### SD-010 트렌드 수집 시각 관리

* 트렌드가 최초로 발견된 시각은 `first_collected_at`에 저장한다.
* 같은 트렌드가 다시 발견된 가장 최근 시각은 `last_collected_at`에 저장한다.
* `updated_at`은 제목, 요약, 썸네일, 상태 등 트렌드 자체 정보가 변경된 시각을 의미한다.
* 수집 직후 AI 분석이 완료되지 않을 수 있으므로 `trends.summary`는 NULL을 허용한다.

### SD-011 트렌드 출처 저장 방식

* 하나의 트렌드는 여러 개의 출처를 가질 수 있다.
* 수집 플랫폼은 `trend_sources.platform`에 `VARCHAR(30)`으로 저장하고, 허용값은 백엔드 enum으로 제한한다.
* 외부 플랫폼이 제공하는 고유 식별자는 `external_id`에 저장한다.
* 출처 중복 식별을 위해 플랫폼과 외부 식별자 또는 정규화 URL을 조합한 SHA-256 값을 `source_key`에 저장한다.
* 동일 트렌드에 같은 출처가 중복 저장되지 않도록 `(trend_id, source_key)` 복합 UNIQUE 제약을 사용한다.
* 외부 플랫폼의 추가가 DB ENUM 변경으로 이어지지 않도록 플랫폼은 MariaDB ENUM으로 저장하지 않는다.

### SD-012 트렌드 카테고리 매핑

* 트렌드와 카테고리는 `trend_category_map`을 통해 다대다 관계로 연결한다.
* 동일 트렌드와 카테고리 조합은 중복될 수 없도록 `(trend_id, category_id)` 복합 UNIQUE 제약을 사용한다.
* 하나의 트렌드에는 여러 카테고리를 연결할 수 있지만 대표 카테고리는 하나만 허용한다.
* 대표 카테고리 하나만 허용하는 규칙은 Service 계층에서 검증한다.
* 트렌드 카테고리 연결 시각은 `created_at`에 저장한다.

### SD-013 트렌드 순위 스냅샷

* 플랫폼별 트렌드 순위는 현재값을 덮어쓰지 않고 `trend_rank_snapshots`에 시계열로 누적한다.
* 순위 컬럼명은 `rank` 대신 `ranking`을 사용한다.
* 수집 날짜와 수집 시각을 중복 저장하지 않고 `snapshot_at` 하나로 통일한다.
* 순위 변동 방향 ENUM 대신 이전 순위와 현재 순위의 차이를 나타내는 `rank_delta`를 저장한다.
* `rank_delta`는 `이전 순위 - 현재 순위`로 계산하며, 양수는 상승, 음수는 하락, 0은 동일, NULL은 신규 진입을 의미한다.
* 플랫폼이 제공하는 점수의 소수 값을 보존할 수 있도록 `score`는 `DECIMAL(12, 4)`로 저장한다.
* 동일 시점의 중복 스냅샷을 방지하기 위해 `(trend_id, platform, snapshot_at)` 복합 UNIQUE 제약을 사용한다.

### SD-014 AI 분석 결과 버전 관리

* 하나의 트렌드는 여러 개의 AI 분석 결과를 가질 수 있다.
* AI 분석 결과는 생성 이후 수정하지 않는 불변 데이터로 관리한다.
* 분석 내용이 변경되거나 재분석이 필요한 경우 기존 행을 수정하지 않고 새로운 분석 버전을 생성한다.
* 분석 버전은 `analysis_version`에 저장한다.
* 동일 트렌드에서 분석 버전이 중복되지 않도록 `(trend_id, analysis_version)` 복합 UNIQUE 제약을 사용한다.
* 초기 MVP에서는 성공한 AI 분석 결과만 `trend_ai_analyses`에 저장한다.
* 분석 작업의 대기, 실행, 실패 상태 관리는 비동기 분석 기능 도입 시 별도의 작업 테이블로 분리한다.

### SD-015 현재 AI 분석 선택 방식

* 트렌드 상세 조회에서는 해당 트렌드의 `analysis_version`이 가장 큰 분석 결과를 현재 분석으로 사용한다.
* 현재 분석을 별도로 표시하는 `is_current` 컬럼은 사용하지 않는다.
* 분석 결과가 존재하지 않으면 트렌드 상세 API의 `ai_analysis`는 NULL을 반환한다.
* AI 분석이 없는 경우 `trends.summary`를 기본 설명으로 사용할 수 있다.

### SD-016 AI 모델 및 프롬프트 정보

* AI 제공자는 `model_provider`에 `VARCHAR(30)`으로 저장한다.
* 사용한 실제 모델 설정명은 `model_name`에 `VARCHAR(100)`으로 저장한다.
* 모델 추가 또는 변경이 DB 스키마 변경으로 이어지지 않도록 모델 정보에는 MariaDB ENUM을 사용하지 않는다.
* AI 분석에 사용한 프롬프트 버전은 `prompt_version`에 저장한다.
* `trends.summary`는 기본 또는 수집 기반 요약이며, `trend_ai_analyses.one_line_summary`는 AI가 생성한 상세 화면용 요약으로 구분한다.

### SD-017 관련 키워드와 분석 버전 연결

* 관련 키워드는 트렌드에 직접 연결하지 않고 해당 키워드를 생성한 AI 분석에 연결한다.
* `trend_related_keywords.trend_id`는 제거하고 `analysis_id`를 외래 키로 사용한다.
* 하나의 AI 분석은 여러 관련 키워드를 가질 수 있다.
* 키워드 원문은 `keyword`, 중복 비교용 정규화 값은 `normalized_keyword`에 저장한다.
* 동일 분석에 같은 키워드가 중복 저장되지 않도록 `(analysis_id, normalized_keyword)` 복합 UNIQUE 제약을 사용한다.
* 키워드 유형은 `RELATED`, `HASHTAG`, `RECOMMENDED`로 구분한다.
* 트렌드 상세 조회에서는 현재 AI 분석에 연결된 관련 키워드만 반환한다.


## 보류 사항

- 사용자 북마크 중복 및 삭제 정책
- 검색 기록 보존 및 삭제 정책
- 전체 테이블 복합 UNIQUE와 조회 인덱스 물리 반영


## 유니크 키 반영 사항

(trend_id, category_id)
(trend_id, source_key)
(trend_id, platform, snapshot_at)

UNIQUE(trend_id, analysis_version)
INDEX(trend_id, analysis_version)

UNIQUE(analysis_id, normalized_keyword)
INDEX(analysis_id, keyword_type, sort_order)

```
__table_args__ = (
    UniqueConstraint(
        "trend_id",
        "source_key",
        name="uq_trend_sources_trend_source_key",
    ),
)
```
이전과 같이 반영하기

## 트렌드 요약 VS AI 요약

trends.summary
- 수집 데이터 또는 기본 설명
- 목록 카드와 AI 분석 전 fallback에 사용
- NULL 허용

trend_ai_analyses.one_line_summary
- AI가 생성한 최신 분석 요약
- 트렌드 상세 화면에 사용
- 분석 행에서는 NOT NULL