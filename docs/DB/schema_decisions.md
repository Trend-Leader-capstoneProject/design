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

## 보류 사항

- OAuth 사용자의 login_id 정책
- password_hash NULL 허용 정책
- 사용자 관심 키워드 기능 포함 여부
- 트렌드 중복 식별 방식
- AI 분석 버전 관리 방식