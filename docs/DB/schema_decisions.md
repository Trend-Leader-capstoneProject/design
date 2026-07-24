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


## 보류 사항

- 사용자 관심 키워드 기능 포함 여부
- 트렌드 중복 식별 방식
- AI 분석 버전 관리 방식