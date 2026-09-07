# 아이디 중복 확인

옵션: `GET`

## 1. API 기본 정보

| 항목 | 내용 |
| --- | --- |
| 도메인 | Auth |
| 기능명 | 아이디 중복 확인 |
| Method | `GET` |
| Endpoint | `/api/auth/check-login-id` |
| 인증 필요 여부 | 불필요 |
| Frontend Client | `publicApiClient` |
| 관련 화면 | 회원가입 화면 |
| 설명 | 회원가입 화면에서 입력한 `login_id`가 이미 존재하는지 조회하여 사용 가능 여부를 반환한다. |

---

## 2. 요청 Path Parameter

> 해당 없음

---

## 3. 요청 Query Parameter

| Key | Type | 필수 | 설명 | 정책 |
| --- | --- | ---: | --- | --- |
| `login_id` | string | Y | 중복 여부를 확인할 로그인 ID | 4~50자, 영문 소문자·숫자·`_`, 첫 문자는 영문 소문자 |

---

## 4. 요청 Body

> 해당 없음

---

## 5. 응답 Body

| Key | Type | 설명 |
| --- | --- | --- |
| `success` | boolean | API 처리 성공 여부 |
| `statusCode` | number | HTTP 상태 코드 |
| `message` | string | 처리 결과 메시지 |
| `data.login_id` | string | 중복 확인 대상 로그인 ID |
| `data.is_available` | boolean | 사용 가능 여부 |
| `data.reason` | string \| null | 사용 불가 사유 |

사용 불가 사유:

```text
DUPLICATED_LOGIN_ID
```

---

## 6. 요청 예시

```text
GET /api/auth/check-login-id?login_id=trend_user01
```

---

## 7. 응답 예시

### 사용 가능한 ID

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

### 이미 사용 중인 ID

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

중복된 ID도 조회 자체는 정상적으로 완료된 것이므로 `409`가 아니라 `200 OK`를 사용한다.

---

## 8. 예외 응답

| 상태 코드 | 상황 | 처리 |
| ---: | --- | --- |
| 422 | `login_id` 누락 | Validation Error 반환 |
| 422 | 길이/허용 문자/첫 글자 규칙 위반 | Validation Error 반환 |
| 500 | DB 조회 또는 서버 오류 | 일반 서버 오류 반환 |

---

## 9. Frontend 처리 메모

| 구분 | 처리 내용 |
| --- | --- |
| 요청 시점 | 로그인 ID 입력 후 중복 확인 버튼 클릭 |
| API Client | `publicApiClient` |
| 성공 + available | 사용 가능 메시지 표시 |
| 성공 + duplicate | 사용 중 메시지 표시 |
| 입력값 변경 | 기존 중복 확인 결과 즉시 무효화 |
| Network/5xx | 사용 가능 상태로 임의 확정하지 않고 재시도 안내 |
| 저장 위치 | 중복 확인 결과는 화면 상태만 사용하며 DB 저장하지 않음 |

중복 확인 이후 사용자가 `login_id`를 변경하면:

```text
isLoginIdChecked = false
isLoginIdAvailable = false 또는 미확정
```

상태로 되돌린다.

---

## 10. Backend 처리 메모

```text
Request
→ login_id Validation
→ users.login_id 조회
→ 존재 여부 판단
→ CheckLoginIdData 반환
```

계정 상태와 관계없이 `users.login_id`가 이미 존재하면 현재 MVP에서는 사용 불가로 판단한다.

```text
ACTIVE
→ 사용 불가

WITHDRAWN
→ 사용 불가

SUSPENDED
→ 사용 불가
```

탈퇴 사용자 ID 재사용 정책은 회원 탈퇴 기능 설계에서 별도로 재검토한다.

---

## 11. DB 처리 메모

| 테이블 | 필드 | 설명 |
| --- | --- | --- |
| `users` | `user_id` | 사용자 PK |
| `users` | `login_id` | 중복 확인 대상 |
| `users` | `status` | 현재 계정 상태 |

`users.login_id`의 UNIQUE Constraint가 최종 중복 저장을 방지한다.

중복 확인 API는 저장을 수행하지 않는다.

---

## 12. Race Condition 주의

`/check-login-id`에서 `is_available=true`였다는 사실은 이후 Signup 성공을 보장하지 않는다.

```text
중복 확인
→ available

그 사이 다른 요청이 동일 ID 가입

현재 사용자 Signup
→ DB UNIQUE 충돌
→ 409 DUPLICATED_LOGIN_ID
```

따라서 Frontend는 Signup 409를 정상적인 충돌 경로로 처리해야 한다.

---

## 13. 개발 체크리스트

- [ ] Endpoint 연결
- [ ] Query `login_id` 계약 확인
- [ ] 4~50자 규칙 확인
- [ ] 잘못된 형식 422 확인
- [ ] 없는 ID → `is_available=true`
- [ ] 존재 ID → `is_available=false`
- [ ] `reason=DUPLICATED_LOGIN_ID`
- [ ] WITHDRAWN 사용자 ID도 사용 불가
- [ ] SUSPENDED 사용자 ID도 사용 불가
- [ ] login_id 수정 시 Frontend 중복확인 상태 초기화
- [ ] Signup에서도 최종 중복 방어
