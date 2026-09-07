# Error Code / 오류 응답 정책

## 1. 문서 목적

Trend Leader의 실제 공통 오류 응답과 도메인별 machine-readable 오류 데이터를 구분한다.

중요:

현재 공통 오류 Envelope에는 독립적인 최상위 `code` 필드가 없다.

```json
{
  "success": false,
  "statusCode": 409,
  "message": "...",
  "data": {}
}
```

따라서 도메인별 분기값이 필요한 경우 `data.reason`, Request Validation의 경우 `data.errors[].type`을 사용한다.

Frontend는 사용자 표시용 `message` 문자열을 파싱하여 프로그램 분기를 만들지 않는다.

---

## 2. 공통 HTTP 오류

| HTTP Status | 용도 | 기본 처리 |
| ---: | --- | --- |
| 400 | Schema Validation과 구분되는 비즈니스 Bad Request | 공통 오류 메시지 |
| 401 | 인증 정보 없음/유효하지 않음 | 인증 정책에 따라 처리 |
| 403 | 인증되었으나 권한 없음 | 접근 제한 안내 |
| 404 | 리소스 없음 | Not Found 처리 |
| 405 | 허용되지 않은 Method | Method 오류 |
| 409 | 현재 리소스 상태와 요청의 충돌 | Domain Conflict 처리 |
| 422 | FastAPI/Pydantic Request Validation 실패 | 필드별 Validation 처리 |
| 500 | 처리되지 않은 서버 오류 | 일반 서버 오류 |
| 503 | 서비스 일시 사용 불가 | 재시도 안내 |

---

## 3. Request Validation — 422

Pydantic/FastAPI Request Validation 실패는 별도 Domain Code 하나로 뭉치지 않고 다음 구조를 사용한다.

```json
{
  "success": false,
  "statusCode": 422,
  "message": "요청 데이터가 올바르지 않습니다.",
  "data": {
    "errors": [
      {
        "field": "body.login_id",
        "message": "...",
        "type": "string_pattern_mismatch"
      }
    ]
  }
}
```

| 필드 | 역할 |
| --- | --- |
| `field` | 오류가 발생한 요청 위치 |
| `message` | 검증 오류 설명 |
| `type` | Validation 오류 유형 |

회원가입에서 다음 상황은 422로 처리한다.

```text
필수값 누락
login_id 형식 오류
password 길이 오류
password_confirm 불일치
name 형식 오류
email 형식 오류
```

기존의 `INVALID_INPUT=400`, `INVALID_PASSWORD=400`을 일반 회원가입 Request Validation의 실제 API 계약으로 사용하지 않는다.

---

## 4. Signup Conflict — 409

### DUPLICATED_LOGIN_ID

```text
HTTP Status:
409

data.field:
login_id

data.reason:
DUPLICATED_LOGIN_ID
```

예시:

```json
{
  "success": false,
  "statusCode": 409,
  "message": "이미 존재하는 데이터입니다.",
  "data": {
    "field": "login_id",
    "reason": "DUPLICATED_LOGIN_ID"
  }
}
```

### DUPLICATED_EMAIL

```text
HTTP Status:
409

data.field:
email

data.reason:
DUPLICATED_EMAIL
```

예시:

```json
{
  "success": false,
  "statusCode": 409,
  "message": "이미 존재하는 데이터입니다.",
  "data": {
    "field": "email",
    "reason": "DUPLICATED_EMAIL"
  }
}
```

### 명명 규칙

다음 과거 명칭은 사용하지 않는다.

```text
DUPLICATE_LOGIN_ID
DUPLICATE_EMAIL
```

현재 계약:

```text
DUPLICATED_LOGIN_ID
DUPLICATED_EMAIL
```

---

## 5. Check Login ID — 200 + reason

아이디 중복 확인에서 중복은 오류 응답이 아니다.

```text
GET /api/auth/check-login-id
```

사용 가능:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "사용 가능한 아이디입니다.",
  "data": {
    "login_id": "trend_user01",
    "is_available": true,
    "reason": null
  }
}
```

사용 불가:

```json
{
  "success": true,
  "statusCode": 200,
  "message": "이미 사용 중인 아이디입니다.",
  "data": {
    "login_id": "trend_user01",
    "is_available": false,
    "reason": "DUPLICATED_LOGIN_ID"
  }
}
```

즉 같은 `DUPLICATED_LOGIN_ID` reason이 사용되더라도:

```text
중복 확인 조회
→ 200

실제 Signup 충돌
→ 409
```

로 HTTP 의미가 다르다.

---

## 6. Login — 401

일반 로그인 실패는 ID 존재 여부, 비밀번호 오류, 비활성 계정 여부를 외부에 세분화하지 않는다.

```text
POST /api/auth/login
→ 401
→ 아이디 또는 비밀번호가 올바르지 않습니다.
```

현재 로그인 오류는 Signup Conflict처럼 `data.reason`으로 세분화하지 않는다.

Frontend는 이를 정상적인 로그인 실패 흐름으로 처리하며,
Authenticated API Client의 공통 세션 종료 정책과 혼동하지 않는다.

---

## 7. IntegrityError Mapping

회원가입 Service에서 모든 DB IntegrityError를 409로 변환하지 않는다.

Known MariaDB Duplicate Entry + Known Constraint만 Domain Conflict로 변환한다.

```text
uq_users_login_id
→ DUPLICATED_LOGIN_ID

uq_users_email
→ DUPLICATED_EMAIL
```

그 외:

```text
Unknown IntegrityError
→ rollback
→ re-raise
→ 공통 500
```

---

## 8. 기존/후속 도메인 오류 메모

아래 도메인 오류명은 기존 기획 문서에서 사용한 후보이며,
각 기능 실제 구현 시 현재 공통 ErrorResponse 및 도메인 계약과 다시 대조한다.

### Bookmark

```text
BOOKMARK_ALREADY_EXISTS
BOOKMARK_NOT_FOUND
```

### Trend

```text
TREND_NOT_FOUND
```

### Search

```text
SEARCH_KEYWORD_REQUIRED
SEARCH_RESULT_NOT_FOUND
```

이 항목들은 회원가입 오류 계약의 `data.reason` 구현 방식을 자동으로 적용한다고 가정하지 않는다.

---

## 9. Frontend 처리 원칙

### 하지 않는 것

```text
message === "이미 사용 중인 아이디입니다."
→ login_id 오류
```

### 사용하는 것

```text
HTTP 409
+
data.field === "login_id"
+
data.reason === "DUPLICATED_LOGIN_ID"
```

Request Validation:

```text
HTTP 422
+
data.errors[]
```

로그인 실패:

```text
HTTP 401
→ Login 화면의 인증 실패 처리
```

---

## 10. 체크리스트

- [ ] Signup `DUPLICATED_LOGIN_ID`
- [ ] Signup `DUPLICATED_EMAIL`
- [ ] 과거 `DUPLICATE_*` 명칭 제거
- [ ] Signup Validation 422 적용
- [ ] Check Login ID duplicate는 200 유지
- [ ] Frontend가 `message`를 프로그램 분기용으로 파싱하지 않음
- [ ] Unknown IntegrityError를 409로 오분류하지 않음
