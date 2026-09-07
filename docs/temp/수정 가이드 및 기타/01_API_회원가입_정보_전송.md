# 회원가입 정보 전송

옵션: `POST`

## 1. API 기본 정보

| 항목 | 내용 |
| --- | --- |
| 도메인 | Auth |
| 기능명 | 회원가입 등록 |
| Method | `POST` |
| Endpoint | `/api/auth/signup` |
| 인증 필요 여부 | 불필요 |
| Frontend Client | `publicApiClient` |
| 관련 화면 | 회원가입 화면 |
| 설명 | 사용자가 입력한 일반 회원가입 정보를 검증하고 신규 사용자를 생성한 뒤, 자동 로그인을 위한 Access Token과 인증 Session 정보를 반환한다. |

---

## 2. 요청 Path Parameter

> 해당 없음

---

## 3. 요청 Query Parameter

> 해당 없음

---

## 4. 요청 Body

| Key | Type | 필수 | 설명 | 정책 |
| --- | --- | ---: | --- | --- |
| `login_id` | string | Y | 로그인에 사용할 아이디 | 4~50자, 영문 소문자·숫자·`_`, 첫 문자는 영문 소문자 |
| `password` | string | Y | 비밀번호 | 15~128자, 원문 trim 금지 |
| `password_confirm` | string | Y | 비밀번호 확인 | `password`와 정확히 동일해야 함 |
| `name` | string | Y | 사용자 이름 | trim 후 1~50자, Unicode 허용 |
| `email` | string \| null | N | 사용자 이메일 | 누락/NULL/공백은 `None`; 값이 있으면 `EmailStr` 기반 형식 검증 및 정규화 |

### 이메일 저장 메모

DB 컬럼:

```text
users.email
VARCHAR(255)
```

현재 Backend는 `EmailStr` 기반 검증을 사용한다.

API 문서에서는 임의의 255자 문자열을 허용한다는 의미로 해석하지 않고,
**유효한 이메일 형식 검증을 통과한 값만 저장**한다는 의미로 관리한다.

---

## 5. 응답 Body

### 5.1 성공 응답

| Key | Type | 설명 |
| --- | --- | --- |
| `success` | boolean | API 처리 성공 여부 |
| `statusCode` | number | HTTP 상태 코드 |
| `message` | string | 처리 결과 메시지 |
| `data.access_token` | string | JWT Access Token |
| `data.token_type` | string | `Bearer` |
| `data.user.user_id` | number | 생성된 사용자 ID |
| `data.user.login_id` | string | 가입한 로그인 아이디 |
| `data.user.name` | string | 사용자 이름 |
| `data.user.status` | string | 계정 상태, 신규 가입자는 `ACTIVE` |
| `data.has_selected_interests` | boolean | 관심사 선택 여부 |
| `data.next_step` | string | 다음 앱 진입 단계 |

회원가입 성공 Session Response에는 `email`을 포함하지 않는다.

---

## 6. 요청 예시

```json
{
  "login_id": "trend_user01",
  "password": "example-long-password",
  "password_confirm": "example-long-password",
  "name": "김트렌드",
  "email": null
}
```

---

## 7. 응답 예시

```json
{
  "success": true,
  "statusCode": 201,
  "message": "회원가입이 완료되었습니다.",
  "data": {
    "access_token": "<jwt>",
    "token_type": "Bearer",
    "user": {
      "user_id": 123,
      "login_id": "trend_user01",
      "name": "김트렌드",
      "status": "ACTIVE"
    },
    "has_selected_interests": false,
    "next_step": "INTEREST_SELECTION"
  }
}
```

---

## 8. 예외 응답

| 상태 코드 | 상황 | 응답 데이터 | Frontend 처리 |
| ---: | --- | --- | --- |
| 422 | 필수 입력값 누락 | `data.errors[]` | 해당 필드 오류 표시 |
| 422 | `login_id` 형식 오류 | `data.errors[]` | 아이디 조건 안내 |
| 422 | 비밀번호 길이 오류 | `data.errors[]` | 비밀번호 조건 안내 |
| 422 | `password_confirm` 불일치 | `data.errors[]` | 비밀번호 확인 필드 강조 |
| 422 | 이름 형식 오류 | `data.errors[]` | 이름 필드 오류 표시 |
| 422 | 이메일 형식 오류 | `data.errors[]` | 이메일 필드 오류 표시 |
| 409 | 로그인 ID 중복 | `field=login_id`, `reason=DUPLICATED_LOGIN_ID` | 아이디 입력란 오류 표시 및 중복확인 상태 무효화 |
| 409 | 이메일 중복 | `field=email`, `reason=DUPLICATED_EMAIL` | 이메일 입력란 오류 표시 |
| 500 | 예상하지 못한 DB/서버 오류 | 일반 오류 응답 | 입력값 유지 후 재시도 안내 |

### 8.1 Validation Error 예시

```json
{
  "success": false,
  "statusCode": 422,
  "message": "요청 데이터가 올바르지 않습니다.",
  "data": {
    "errors": [
      {
        "field": "body.login_id",
        "message": "String should match pattern ...",
        "type": "string_pattern_mismatch"
      }
    ]
  }
}
```

`message`, `type`의 세부 문자열은 검증 라이브러리에서 생성될 수 있으므로
Frontend는 필요 이상으로 문자열 전체에 강하게 결합하지 않는다.

### 8.2 로그인 ID 중복 예시

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

### 8.3 이메일 중복 예시

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

Frontend는 `message` 문자열이 아니라 `data.field`, `data.reason`을 기준으로 충돌 종류를 판별한다.

---

## 9. Frontend 처리 메모

| 구분 | 처리 내용 |
| --- | --- |
| 화면 이동 | Login → Signup 이동만 명령형 Navigation으로 수행 |
| 요청 시점 | 회원가입 화면에서 입력 검증 및 필요한 중복확인을 완료한 뒤 회원가입 버튼 클릭 시 |
| 요청 데이터 | `login_id`, `password`, `password_confirm`, `name`, `email` |
| API Client | `publicApiClient` |
| 성공 처리 | 응답을 `AuthProvider.establishSession()` 계열에 전달해 인증 세션 확립 |
| Token 저장 | Access Token을 SecureStore에 저장 |
| 화면 전환 | SignupScreen이 Interest 화면으로 직접 이동하지 않음. RootNavigator가 `AUTHENTICATED + next_step`을 기준으로 화면 Tree 선택 |
| 422 | Backend Validation Error를 필드별 오류로 변환 |
| 409 | `field/reason`으로 충돌 필드 판단 |
| Network/5xx | 입력값 유지 후 재시도 가능 |
| 비밀번호 상태 | 성공 후 `password`, `password_confirm` 메모리 상태 정리 |

### Signup 성공 후 흐름

```text
POST /auth/signup
        ↓
201 + Token + Session
        ↓
AuthProvider.establishSession()
        ↓
SecureStore Access Token 저장
        ↓
AUTHENTICATED
        ↓
RootNavigator
        ↓
next_step = INTEREST_SELECTION
        ↓
Interest Selection
```

### SecureStore 저장 실패

```text
회원가입 API 성공
→ DB 가입 완료
→ Access Token 저장 실패
```

이 경우 회원가입 API를 다시 호출하지 않는다.

```text
회원가입 완료 상태 유지
→ 세션 확립 실패 처리
→ UNAUTHENTICATED로 복구
→ Login에서 다시 로그인하도록 안내
```

---

## 10. Backend 처리 메모

| 구분 | 처리 내용 |
| --- | --- |
| FastAPI Router | `auth_router.post("/signup")` |
| 인증 처리 | 인증 전 단계이므로 Bearer 인증 불필요 |
| Service | 회원가입 Use Case와 Transaction 경계 소유 |
| Repository | 사용자 조회, `add`, `flush` |
| Password | `hash_password()` 사용, 원문 저장 금지 |
| Session | 사용자 저장 Commit 후 기존 Session 계산 로직 재사용 |
| Token | Access Token 발급 |
| 반환 데이터 | Token + Session Contract |

### 처리 흐름

```text
Request Validation
→ login_id 사전 중복 조회
→ email이 있으면 email 사전 중복 조회
→ 비밀번호 Hash
→ User 생성
→ Repository.save()
→ flush
→ commit
→ Session 계산
→ Access Token 발급
→ 201 응답
```

---

## 11. DB 처리 메모

| 테이블 | 필드 | 설명 |
| --- | --- | --- |
| `users` | `user_id` | 사용자 PK |
| `users` | `login_id` | 일반 로그인 ID, NULL이 아닌 값 UNIQUE |
| `users` | `password_hash` | 해시 처리된 비밀번호 |
| `users` | `name` | 사용자 이름 |
| `users` | `email` | 선택 이메일, NULL이 아닌 값 UNIQUE |
| `users` | `status` | 신규 사용자는 `ACTIVE` |
| `users` | `created_at` | 가입 시각 |
| `users` | `updated_at` | 수정 시각 |

회원가입 시 생성하지 않는 데이터:

```text
user_interest_categories
user_profiles
oauth_accounts
```

따라서 신규 사용자의 초기 Session:

```text
has_selected_interests = false
next_step = INTEREST_SELECTION
```

---

## 12. 중복 및 Race Condition 처리

사전 중복 조회는 최종 무결성을 보장하지 않는다.

```text
A → 동일 ID 사용 가능 확인
B → 동일 ID 사용 가능 확인

A → Signup
B → Signup
```

따라서 최종 방어는 DB UNIQUE Constraint가 담당한다.

```text
/check-login-id
→ UX 사전 확인

signup() 사전 조회
→ 빠른 중복 피드백

DB UNIQUE
→ 동시 요청 최종 방어
```

알려진 UNIQUE 위반:

```text
uq_users_login_id
→ rollback
→ 409
→ field = login_id
→ reason = DUPLICATED_LOGIN_ID

uq_users_email
→ rollback
→ 409
→ field = email
→ reason = DUPLICATED_EMAIL
```

알 수 없는 `IntegrityError`는 임의로 409로 변환하지 않고 상위로 다시 전달한다.

---

## 13. 개발 체크리스트

### Backend

- [ ] `/api/auth/signup` Router 연결
- [ ] Request Validation 422 확인
- [ ] Password Hash 확인
- [ ] email `None` 저장 확인
- [ ] login_id 사전 중복 409 확인
- [ ] email 사전 중복 409 확인
- [ ] login_id UNIQUE Race 409 확인
- [ ] email UNIQUE Race 409 확인
- [ ] 알 수 없는 IntegrityError 500 경로 확인
- [ ] Access Token 발급 확인
- [ ] `has_selected_interests=false` 확인
- [ ] `next_step=INTEREST_SELECTION` 확인

### Frontend

- [ ] `publicApiClient` 사용
- [ ] 201 성공 시 `establishSession()` 호출
- [ ] SecureStore Token 저장
- [ ] 직접 Interest Navigation 없음
- [ ] 422 필드 오류 처리
- [ ] 409 `field/reason` 처리
- [ ] Network/5xx 입력 유지
- [ ] SecureStore 저장 실패 시 Signup API 재호출 없음

### 실제 기기

- [ ] 정상 가입 후 Login 화면을 다시 거치지 않음
- [ ] Interest Selection 표시
- [ ] Android Back으로 Signup/Login 복귀 불가
