# 회원가입 정보 전송

URL 엔드포인트: /api/auth/signup
옵션: POST

## 1. API 기본 정보

| 항목 | 내용 |
| --- | --- |
| 도메인 | Auth |
| 기능명 | 회원가입 등록 |
| Method | POST |
| Endpoint | `/api/auth/signup` |
| 인증 필요 여부 | 불필요 |
| 관련 화면 | 회원가입 화면 |
| 설명 | 사용자가 입력한 아이디, 이름, 비밀번호, 이메일 선택값을 기반으로 신규 계정을 생성한다. 비밀번호는 원문 저장 없이 해시 처리 후 `users.password_hash`에 저장한다. |

---

## 2. 요청 Path Parameter

| Key | Type | 필수 | 설명 |
| --- | --- | --- | --- |
|  |  |  |  |

> 해당 없음
> 

---

## 3. 요청 Query Parameter

| Key | Type | 필수 | 설명 |
| --- | --- | --- | --- |
|  |  |  |  |

> 해당 없음
> 

---

## 4. 요청 Body

| Key | Type | 필수 | 설명 |
| --- | --- | --- | --- |
| `login_id` | string | Y | 사용자가 로그인에 사용할 아이디 |
| `password` | string | Y | 사용자가 입력한 비밀번호 |
| `password_confirm` | string | Y | 비밀번호 확인값 |
| `name` | string | Y | 사용자 이름 |
| `email` | string | null | N | 사용자 이메일, 선택 입력값 |

---

## 5. 응답 Body

| Key | Type | 설명 |
| --- | --- | --- |
| `success` | boolean | API 처리 성공 여부 |
| `statusCode` | number | HTTP 상태 코드 |
| `message` | string | 처리 결과 메시지 |
| `data.user_id` | number | 생성된 사용자 ID |
| `data.login_id` | string | 가입한 로그인 아이디 |
| `data.name` | string | 사용자 이름 |
| `data.email` | string | null | 사용자 이메일 |
| `data.status` | string | 계정 상태값, 기본값 `ACTIVE` |
| `data.next_step` | string | 다음 이동 단계, 예: `INTEREST_SELECTION` |

---

## 6. 요청 예시

```json
{
  "login_id": "trend_user01",
  "password": "Password123!",
  "password_confirm": "Password123!",
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
    "user_id": 1,
    "login_id": "trend_user01",
    "name": "김트렌드",
    "email": null,
    "status": "ACTIVE",
    "next_step": "INTEREST_SELECTION"
  }
}
```

---

## 8. 예외 응답

| 상태 코드 | 상황 | 메시지 예시 | 프론트 처리 |
| --- | --- | --- | --- |
| 400 | 필수 입력값 누락 | 아이디, 비밀번호, 이름을 입력해주세요. | 입력 누락 필드 안내 |
| 400 | 비밀번호 불일치 | 비밀번호와 비밀번호 확인값이 일치하지 않습니다. | 비밀번호 확인 입력란 강조 |
| 400 | 비밀번호 형식 오류 | 비밀번호 형식이 올바르지 않습니다. | 비밀번호 조건 안내 |
| 409 | 아이디 중복 | 이미 사용 중인 아이디입니다. | 아이디 입력란 하단 오류 표시 |
| 409 | 이메일 중복 | 이미 사용 중인 이메일입니다. | 이메일 입력란 하단 오류 표시 |
| 500 | 서버 오류 | 서버 오류가 발생했습니다. | 재시도 안내 |

---

## 9. Frontend 처리 메모

| 구분 | 처리 내용 |
| --- | --- |
| 화면 이동 | 로그인 화면에서 회원가입 버튼 클릭 시 회원가입 화면으로 이동 |
| 요청 시점 | 사용자가 회원가입 화면에서 회원가입 버튼을 클릭할 때 요청 |
| 요청 데이터 | `login_id`, `password`, `password_confirm`, `name`, `email` |
| 성공 처리 | 회원가입 성공 메시지를 표시하고 관심사 선택 화면으로 이동 |
| 실패 처리 | 입력값 누락, 비밀번호 불일치, 아이디 중복 메시지를 Alert 또는 입력 필드 하단에 표시 |
| 저장 위치 | 회원가입 자체는 토큰 저장 없음. 자동 로그인 정책을 적용할 경우 SecureStore/AsyncStorage 저장 여부 별도 결정 |

---

## 10. Backend 처리 메모

| 구분 | 처리 내용 |
| --- | --- |
| FastAPI Router | `auth_router.post("/signup")` |
| Service 로직 | 입력값 검증 → 아이디 중복 확인 → 이메일 값이 있으면 이메일 중복 확인 → 비밀번호 해시 처리 → 사용자 생성 |
| DB 처리 | `users` 테이블에 `login_id`, `password_hash`, `name`, `email`, `status` 저장 |
| 인증 처리 | 회원가입 API는 인증 없이 접근 가능 |
| 반환 데이터 | 생성된 사용자 기본 정보와 다음 이동 단계 반환 |

---

## 11. DB 처리 메모

| 테이블 예시 | 필드 예시 | 설명 |
| --- | --- | --- |
| `users` | `user_id` | 사용자 PK, 자동 증가 |
| `users` | `login_id` | 로그인 아이디, 중복 불가 |
| `users` | `password_hash` | 해시 처리된 비밀번호 |
| `users` | `name` | 사용자 이름 |
| `users` | `email` | 이메일, 선택값 |
| `users` | `status` | 계정 상태, 기본값 `ACTIVE` |
| `users` | `created_at` | 가입일 |
| `users` | `updated_at` | 수정일 |

※ `password`와 `password_confirm`은 요청 검증용 값이며 DB에 저장하지 않는다.

※ 실제 DB에는 원문 비밀번호가 아니라 해시값만 저장한다.

---

## 12. 개발 체크리스트

- [ ]  Endpoint 확정
- [ ]  Request 값 확정
- [ ]  Response 값 확정
- [ ]  아이디 중복 검사 방식 확정
- [ ]  이메일 선택값 처리 방식 확인
- [ ]  비밀번호 해시 처리 방식 확인
- [ ]  회원가입 성공 후 관심사 선택 화면 이동 확인
- [ ]  DB 저장/조회 방식 확인
- [ ]  테스트 완료