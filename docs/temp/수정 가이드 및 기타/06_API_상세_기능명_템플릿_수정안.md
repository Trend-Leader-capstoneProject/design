# (API 상세 기능명)

옵션: `GET | POST | PUT | PATCH | DELETE`

## 1. API 기본 정보

| 항목 | 내용 |
| --- | --- |
| 도메인 |  |
| 기능명 |  |
| Method |  |
| Endpoint |  |
| 인증 필요 여부 |  |
| Frontend Client | `publicApiClient` / `authenticatedApiClient` / 해당 없음 |
| 관련 화면 |  |
| 설명 |  |

---

## 2. 요청 Path Parameter

| Key | Type | 필수 | 설명 |
| --- | --- | --- | --- |
|  |  |  |  |

> 해당 없으면 "해당 없음"만 남긴다.

---

## 3. 요청 Query Parameter

| Key | Type | 필수 | 설명 | 정책 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

> 해당 없으면 "해당 없음"만 남긴다.

---

## 4. 요청 Body

| Key | Type | 필수 | 설명 | 정책 |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

> 해당 없으면 "해당 없음"만 남긴다.

---

## 5. 응답 Body

| Key | Type | 설명 |
| --- | --- | --- |
| `success` | boolean | 처리 성공 여부 |
| `statusCode` | number | HTTP 상태 코드 |
| `message` | string | 처리 결과 메시지 |
| `data` | object \| null | API별 실제 응답 데이터 |

API별 `data.*` 필드를 아래에 추가한다.

---

## 6. 요청 예시

```text
요청 예시
```

---

## 7. 응답 예시

```json
{
  "success": true,
  "statusCode": 200,
  "message": "",
  "data": {}
}
```

---

## 8. 예외 응답

이 표에는 **해당 Endpoint에서 실제 발생할 수 있는 상태 코드만 작성한다.**

모든 API에 400/401/403/404를 기계적으로 복사하지 않는다.

| 상태 코드 | 상황 | Machine-readable Data | Frontend 처리 |
| ---: | --- | --- | --- |
|  |  |  |  |

### 상태 코드 작성 기준

```text
400
→ Pydantic Schema Validation이 아닌 비즈니스 Bad Request가 실제 존재할 때

401
→ 인증이 필요한 Endpoint에서 인증 실패 가능 시

403
→ 인증은 되었지만 권한 거부가 실제 존재할 때

404
→ 요청 대상 리소스가 실제로 없을 수 있을 때

409
→ 중복/현재 상태 충돌 등 Domain Conflict

422
→ FastAPI/Pydantic Request Validation

500
→ 예상하지 못한 서버 오류

503
→ 일시적 서비스 사용 불가를 실제로 반환할 때
```

### Validation Error 예시

```json
{
  "success": false,
  "statusCode": 422,
  "message": "요청 데이터가 올바르지 않습니다.",
  "data": {
    "errors": [
      {
        "field": "body.example",
        "message": "...",
        "type": "..."
      }
    ]
  }
}
```

### Domain Conflict 예시

필요한 Endpoint에서만 작성한다.

```json
{
  "success": false,
  "statusCode": 409,
  "message": "...",
  "data": {
    "field": "example",
    "reason": "DOMAIN_REASON"
  }
}
```

Frontend는 가능하면 `message` 문자열이 아닌 machine-readable 데이터를 사용한다.

---

## 9. Frontend 처리 메모

| 구분 | 처리 내용 |
| --- | --- |
| 화면 이동 |  |
| 요청 시점 |  |
| 요청 데이터 |  |
| API Client |  |
| 성공 처리 |  |
| Validation 처리 |  |
| Domain Error 처리 |  |
| Network/5xx |  |
| 저장 위치 |  |

---

## 10. Backend 처리 메모

| 구분 | 처리 내용 |
| --- | --- |
| FastAPI Router |  |
| Request/Response Schema |  |
| Service 로직 |  |
| Repository |  |
| Transaction 책임 |  |
| 인증 처리 |  |
| 반환 데이터 |  |

---

## 11. DB 처리 메모

| 테이블 | 필드 | 설명 |
| --- | --- | --- |
|  |  |  |

### 제약 및 동시성

필요한 경우 다음을 명시한다.

```text
UNIQUE
FOREIGN KEY
Transaction
Race Condition
Idempotency
```

---

## 12. Backend ↔ Frontend 계약 체크

- [ ] Endpoint와 Method 일치
- [ ] Request 필드명 일치
- [ ] Response 필드명 일치
- [ ] HTTP Status 일치
- [ ] Validation Error 구조 일치
- [ ] Domain Error의 `reason` 또는 구조 일치
- [ ] 인증 Client 선택 일치
- [ ] Navigation 책임 위치 일치

---

## 13. 개발 체크리스트

- [ ] Endpoint 확정
- [ ] Request 값 확정
- [ ] Response 값 확정
- [ ] Validation 정책 확정
- [ ] 예외 케이스 확정
- [ ] DB 저장/조회 방식 확인
- [ ] Transaction 경계 확인
- [ ] 동시성/중복 방어 필요 여부 확인
- [ ] Frontend 연결 확인
- [ ] 테스트 완료
- [ ] 실제 동작 검증 완료
