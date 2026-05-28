# 기능상세명세서 작성 요청

**User:** Anonymous  
**Created:** 5/11/2026 9:59:12  
**Updated:** 5/13/2026 21:11:04  
**Exported:** 5/28/2026 9:38:10  
**Link:** [https://chatgpt.com/g/g-p-69a8fc0a720881918ee40d1fc7e9bda5/c/6a0129a9-2394-83ec-9bd7-79cd7f8b2e3f](https://chatgpt.com/g/g-p-69a8fc0a720881918ee40d1fc7e9bda5/c/6a0129a9-2394-83ec-9bd7-79cd7f8b2e3f)  

## Prompt:
2026. 5. 11. 오전 9:59:11

![메인(홈화면) - 게임 선택 시(예시).png](https://chatgpt.com/backend-api/estuary/content?id=file_00000000e3b07209adbb2fb45b2965a8&ts=494424&p=fs&cid=1&sig=b19e9b52577366cf9c2e91db2ad94e26e9879afac4aa2c4d7478db83d1d7eae7&v=0)

![메인(홈화면).png](https://chatgpt.com/backend-api/estuary/content?id=file_0000000055c47206b7734d433e357ae0&ts=494424&p=fs&cid=1&sig=0e43441c9590fe1f0a3b9dc4c4b79d445fc04e84b0b990676c7eb21b54fa03a5&v=0)

이 화면에 대해 프로젝트 지침에 따라 기능상세명세서를 작성해주실래요? 발표 ppt 붙여넣기가 가능하게끔

## Response:
2026. 5. 11. 오전 9:59:12

> **Analyzing feature spec for recommendation list screen**
>
> The user is asking to provide a concise answer in Korean based on project guidelines for a trend recommendation feature. It seems like they're referring to a screen that shows a list of trends for a home or category. I’ll mention assumptions like the selected category or date filter, with API examples for reference. No need for personal context or creation of PPTX slides.
>
> Thought for 8s

아래 내용은 **메인 홈 화면 / 내 관심사 기반 맞춤 트렌드 조회 기능** 기준으로 발표 PPT에 바로 붙여넣기 가능한 형태입니다.

```md
[내 관심사 기반 맞춤 트렌드 조회 기능]

가정:
- 사용자는 로그인된 상태이며, 회원가입 또는 마이페이지에서 관심 분야를 미리 선택한 상태이다.
- 화면의 관심 분야 탭은 사용자의 관심사 또는 서비스 기본 카테고리를 기반으로 제공된다.
- 트렌드 목록은 날짜, 관심 분야, 사용자 관심사 데이터를 기준으로 조회된다.

1. 기능 개요
- 사용자가 선택한 관심 분야에 따라 오늘의 맞춤 트렌드를 조회하는 기능이다.
- 사용자는 게임, IT/디지털, 엔터테인먼트 등의 분야별 트렌드를 확인할 수 있으며, 급상승 키워드는 AI 분석 화면으로 연결될 수 있다.
- 개인 관심사 기반으로 트렌드 정보를 우선 노출하여 사용자에게 필요한 최신 이슈만 빠르게 제공하는 것을 목표로 한다.

2. 로직 부분 - 처리 방식
- 사용자가 홈 화면에 진입하면 프론트엔드는 로그인 사용자 정보와 기본 관심 분야를 기준으로 트렌드 목록을 요청한다.
- 사용자가 관심 분야 탭을 선택하면 selectedCategory 상태값이 변경되고, 해당 분야의 트렌드 목록을 다시 조회한다.
- 날짜 드롭다운에서 오늘/이전 날짜를 선택하면 selectedDate 상태값이 변경되며, 선택 날짜 기준의 트렌드 데이터를 요청한다.
- 프론트엔드 주요 상태값 예시:
  - selectedCategory
  - selectedDate
  - trendList
  - loading
  - error
- FastAPI 서버는 사용자 ID, 선택 카테고리, 날짜 정보를 기준으로 DB 또는 외부 트렌드 수집 데이터를 조회한다.
- 성공 시 프론트엔드는 순위, 제목, 분야, 상승/하락 상태를 카드 형태로 렌더링한다.
- 사용자가 트렌드 카드를 누르면 트렌드 상세 화면 또는 AI 분석 결과 화면으로 이동한다.

3. 데이터 부분 - DB 저장 방식
- 저장되는 데이터:
  - 사용자 관심 분야
  - 날짜별 트렌드 키워드
  - 카테고리별 트렌드 순위
  - 사용자별 추천 트렌드 결과
- 예상 테이블 예시:
  - users
  - user_interests
  - trend_items
  - trend_rank_snapshots
  - user_trend_recommendations
- 주요 필드 예시:
  - user_interests: user_id, category_id, created_at
  - trend_items: trend_id, title, category_id, source, created_at
  - trend_rank_snapshots: trend_id, rank, rank_change, collected_date
  - user_trend_recommendations: user_id, trend_id, score, recommended_at
- 저장된 관심 분야와 트렌드 순위 데이터는 이후 개인 맞춤 추천, 저장 목록, 검색 결과, AI 분석 기능에서 활용될 수 있다.

4. 대안 시나리오 - 예외 처리
- 입력값 누락:
  - category 또는 date 값이 없으면 기본 관심 분야와 오늘 날짜를 기준으로 조회한다.
- 네트워크 오류:
  - 트렌드 목록을 불러오지 못했다는 안내 메시지를 표시하고 재시도 버튼을 제공한다.
- 인증 오류:
  - 로그인 토큰이 만료된 경우 로그인 화면으로 이동시키거나 재로그인을 요청한다.
- 서버 저장 실패:
  - 추천 결과 저장에 실패하더라도 조회 화면은 유지하고, 서버 로그에 실패 원인을 기록한다.
- 중복 요청:
  - 사용자가 탭을 빠르게 여러 번 누르는 경우 loading 상태에서 추가 요청을 제한한다.
- 잘못된 데이터 요청:
  - 존재하지 않는 카테고리나 날짜 요청 시 빈 목록 메시지 또는 기본 카테고리 데이터를 반환한다.

5. API 예시

Method:
GET

URL:
/api/v1/trends/recommendations?category=game&date=2026-05-03

Request Header:
Authorization: Bearer {access_token}

Response Body:
{
  "success": true,
  "message": "맞춤 트렌드 조회 성공",
  "data": {
    "selectedCategory": "game",
    "selectedDate": "2026-05-03",
    "trends": [
      {
        "trendId": 1,
        "rank": 1,
        "title": "신윤섭 롤 티어 챌린저 승급",
        "category": "게임",
        "source": "인벤",
        "rankChange": "UP",
        "isAiAnalysisAvailable": true
      },
      {
        "trendId": 2,
        "rank": 2,
        "title": "FC 온라인 런칭 이벤트",
        "category": "게임",
        "source": "넥슨 FC 온라인",
        "rankChange": "DOWN",
        "isAiAnalysisAvailable": true
      }
    ]
  }
}

6. 발표용 한 줄 설명
- 사용자의 관심 분야와 선택 날짜를 기준으로 맞춤형 트렌드 목록을 조회하고, 주요 트렌드는 AI 분석 화면으로 연결되는 홈 화면 기능입니다.
```

## Prompt:
2026. 5. 11. 오전 10:54:21

으음 업데이트된 지침에 따라 다시 한번 부탁드릴게요!

## Response:
2026. 5. 11. 오전 10:54:21

> **Clarifying instructions for concise feature spec table**
>
> The user wants the answer in Korean with concise, clear feature specs. I need to follow the exact format of a table with five rows for each feature, possibly multiple tables for separate features like "홈 화면 관심 분야별 맞춤 트렌드 조회," "날짜 필터," "하단 탭 이동," and so on. I should keep descriptions short, very minimal. No API examples unless specifically asked.
>
> **Preparing concise feature spec for PPT**
>
> I need to mention the frontend (React Native), backend (FastAPI), and database (MySQL/MariaDB). The format should include a single table, likely for "내 트렌드 홈 화면", "관심 분야 필터 기반 트렌드 목록 조회," and other visible elements like the side menu icon, logo, and dropdowns. The spec should be concise, without over-speculating about features not on the screen. I'll use markdown tables for simplicity.
>
> Thought for 7s

아래는 **업데이트된 지침 기준**으로 다시 정리한 기능상세명세서입니다.  
발표 PPT에 붙여넣기 좋도록 **표 중심 + 간결한 문장**으로 작성했습니다.

---

[내 관심사 맞춤 트렌드 홈]

| 번호 | 기능 구분 | 기능 명세 |
|---|---|---|
| 1 | 화면 이동 | 사용자는 로그인 후 홈 화면으로 진입하며, 하단 탭의 **내 트렌드** 버튼을 통해 해당 화면으로 이동한다. 좌측 상단 메뉴 버튼을 누르면 사이드 메뉴 화면으로 이동할 수 있다. |
| 2 | 화면 기능 | 사용자는 관심 분야 탭을 선택하여 게임, IT/디지털, 엔터테인먼트 등 분야별 맞춤 트렌드를 확인한다. 날짜 선택 버튼을 통해 특정 날짜의 트렌드 목록을 조회한다. |
| 3 | 데이터 처리 | React Native에서 선택한 `category`, `date`, 로그인 사용자 정보를 FastAPI로 전달한다. 서버는 예시로 `user_interests`, `trend_items`, `trend_rank_snapshots` 테이블을 조회하여 맞춤 트렌드 목록을 반환한다. |
| 4 | 등록/저장/조회 | 관심 분야 탭 또는 날짜 변경 시 FastAPI가 해당 조건의 트렌드 데이터를 조회한다. 조회 성공 시 순위, 트렌드 제목, 분야, 출처, 상승·하락 상태를 카드 목록에 반영한다. |
| 5 | 예외 처리 | 관심 분야나 날짜 값이 없으면 기본 관심 분야와 오늘 날짜로 조회한다. 네트워크 오류, 인증 만료, 데이터 없음, 잘못된 카테고리 요청 시 안내 문구를 표시하고 재요청 또는 로그인 화면 이동을 처리한다. |

가정:
- 사용자는 로그인된 상태이며, 관심 분야 정보가 사전에 저장되어 있다고 가정한다.
- DB 테이블명은 예시이며, 실제 구현 시 `users`, `categories`, `trends`, `trend_rank_logs` 등으로 변경될 수 있다.
- 화면의 “클릭 시 AI 분석을 볼 수 있어요!” 문구를 기준으로, 트렌드 카드를 클릭하면 상세 분석 화면으로 이동하는 흐름을 포함하였다.

---

[관심 분야 탭 선택 기능]

| 번호 | 기능 구분 | 기능 명세 |
|---|---|---|
| 1 | 화면 이동 | 사용자는 홈 화면 상단의 관심 분야 탭 영역에서 원하는 분야 버튼을 선택한다. 선택된 탭은 현재 화면 안에서 목록만 갱신되며 별도 화면 이동은 발생하지 않는다. |
| 2 | 화면 기능 | 사용자는 게임, IT/디지털, 엔터테인먼트 등 분야별 트렌드를 전환하여 확인한다. 선택된 분야는 강조 표시되어 현재 조회 기준을 인식할 수 있다. |
| 3 | 데이터 처리 | React Native는 선택한 분야 값을 `selectedCategory` 상태로 관리하고 FastAPI에 조회 요청을 보낸다. 서버는 예시로 `categories.category_id`와 `trend_items.category_id`를 기준으로 데이터를 필터링한다. |
| 4 | 등록/저장/조회 | 탭 클릭 시 해당 분야의 트렌드 목록을 서버에서 조회한다. 조회 결과는 기존 목록을 대체하여 순위 카드 형태로 다시 렌더링된다. |
| 5 | 예외 처리 | 존재하지 않는 분야 값이 전달되면 기본 분야 또는 빈 목록을 반환한다. 빠른 연속 클릭으로 중복 요청이 발생하지 않도록 로딩 상태에서는 추가 요청을 제한한다. |

가정:
- 관심 분야 탭은 가로 스크롤 형태로 제공된다고 가정한다.
- 사용자의 관심 분야와 서비스 기본 카테고리가 함께 노출될 수 있다.

---

[트렌드 카드 상세 이동 기능]

| 번호 | 기능 구분 | 기능 명세 |
|---|---|---|
| 1 | 화면 이동 | 사용자는 트렌드 카드 영역을 클릭하여 해당 트렌드의 상세 화면 또는 AI 분석 화면으로 이동한다. |
| 2 | 화면 기능 | 카드에는 순위, 트렌드 제목, 관련 분야, 출처, 상승·하락 표시가 제공된다. 사용자는 현재 어떤 트렌드가 급상승 또는 하락 중인지 확인할 수 있다. |
| 3 | 데이터 처리 | React Native는 선택한 `trendId`를 FastAPI에 전달한다. 서버는 예시로 `trend_items`, `trend_rank_snapshots`, `trend_ai_analysis` 테이블을 조회하여 상세 정보를 반환한다. |
| 4 | 등록/저장/조회 | 카드 클릭 시 트렌드 상세 데이터와 AI 분석 가능 여부를 조회한다. 조회 성공 시 상세 화면에 분석 결과, 관련 키워드, 순위 변화 정보를 표시한다. |
| 5 | 예외 처리 | `trendId`가 없거나 삭제된 트렌드인 경우 상세 정보를 찾을 수 없다는 안내를 표시한다. AI 분석 데이터가 없으면 기본 트렌드 정보만 우선 표시한다. |

가정:
- 화면 문구상 AI 분석 연결 기능이 존재한다고 가정하였다.
- AI 분석 결과는 즉시 생성하거나 사전 저장된 결과를 조회하는 방식 중 하나로 구현할 수 있다.

## Prompt:
2026. 5. 12. 오후 1:16:00

![관심 분야 선택 화면 -  미선택.png](https://chatgpt.com/backend-api/estuary/content?id=file_00000000ae38720980e7304069f6899c&ts=494424&p=fs&cid=1&sig=a4abf913613bd6a8af68e20c3cb925d6304f12757231403b57b81b026f2d6d22&v=0)

![관심 분야 선택 화면 - 선택 시.png](https://chatgpt.com/backend-api/estuary/content?id=file_000000007e387209a1b53a3657d7a6b4&ts=494424&p=fs&cid=1&sig=1f82e685449ec05c7d7b20d3df262aa32d785ba2a19ed7db9131a15be98b485a&v=0)

![20260514_TrendLeader_UI_UX_기능상세명세서.jpg](https://chatgpt.com/backend-api/estuary/content?id=file_000000007eb87209aadb1cac8d596912&ts=494424&p=fs&cid=1&sig=f6e9ace7da4f768e925ec5679daaaef273f7a144f359a4b40dfecc90fa17f071&v=0)

감사합니다.
ppt 예시와 같이 들어갈 수 있도록 두 화면도 기능상세명세를 부탁드릴게요.

## Response:
2026. 5. 12. 오후 1:16:01

> **Analyzing the "Interests Selection Screen"**
>
> The user is asking for a PPT-style answer with two screens, likely unselected and selected states. I’ll create a concise table, covering the specified components like React Native, FastAPI, MySQL/MariaDB. The "관심 분야 선택 및 저장" title will reflect the screen design. A simple table will work for the copy.
>
> Thought for 9s

아래는 **PPT 예시 표에 바로 넣을 수 있는 축약형 기능상세명세**입니다.  
두 화면은 같은 기능의 **미선택 상태 / 선택 상태**이므로 하나의 기능 명세로 통합하는 것이 발표자료에 더 깔끔합니다.

---

[관심 분야 선택]

| 번호 | 기능 구분 | 기능 명세 |
|---|---|---|
| 1 | 화면 이동 | 사용자가 회원가입 또는 최초 로그인 후 관심 분야 설정 화면으로 이동한다. 최소 1개 이상 선택 후 **선택 완료** 버튼을 누르면 맞춤 트렌드 홈 화면으로 이동한다. |
| 2 | 화면 기능 | 사용자는 패션, 음식, IT/디지털, 엔터테인먼트, 뷰티, 게임 중 관심 분야를 선택할 수 있다. 선택된 분야는 테두리와 아이콘 색상이 강조되어 미선택 상태와 구분된다. |
| 3 | 데이터 처리 | React Native에서 선택한 관심 분야 목록을 `selectedInterests` 상태로 관리하고, 선택 완료 시 FastAPI로 `user_id`, `category_ids`를 전달한다. 서버는 예시로 `user_interests` 테이블에 사용자 관심 분야를 저장한다. |
| 4 | 등록/저장/조회 | **선택 완료** 버튼 클릭 시 FastAPI가 선택된 관심 분야를 저장한다. 저장 성공 시 해당 관심 분야를 기준으로 맞춤 트렌드 추천 데이터를 조회할 수 있도록 홈 화면에 반영한다. |
| 5 | 예외 처리 | 관심 분야를 선택하지 않은 경우 버튼을 비활성화하거나 “최소 1개 이상 선택해주세요” 안내를 표시한다. 네트워크 오류, 인증 만료, 저장 실패 시 오류 메시지를 표시하고 재시도를 유도한다. |

가정:
- 해당 화면은 최초 회원가입 이후 또는 관심 분야 미설정 사용자가 진입하는 초기 설정 화면으로 가정한다.
- DB 테이블명은 예시이며, 실제 구현 시 `users`, `categories`, `user_interest_categories` 등으로 변경될 수 있다.
- 화면상 6개 분야만 확인되므로, 추가 카테고리 기능은 포함하지 않았다.
- 선택 완료 후 이동 화면은 맞춤 트렌드 홈 화면으로 가정하였다.

## Prompt:
2026. 5. 12. 오후 4:38:51

![로그인 화면.png](https://chatgpt.com/backend-api/estuary/content?id=file_00000000e0647206add8baef9ff1654c&ts=494424&p=fs&cid=1&sig=b3b934b97e64b05836ef048fdd5f005b29d2127fbde514a88811783dcf1e8245&v=0)

![회원가입 화면.png](https://chatgpt.com/backend-api/estuary/content?id=file_0000000013207206b1f555aa22d18524&ts=494424&p=fs&cid=1&sig=6e4a748ae0d8074aedb7f9572192407989389341f2ada1cd66cfe20341e6e77d&v=0)

감사합니다. 다음은 로그인, 회원가입 화면을 요청하고자 해요

## Response:
2026. 5. 12. 오후 4:38:52

아래는 **PPT 예시 표에 바로 넣을 수 있는 축약형 기능상세명세**입니다.

---

[로그인]

| 번호 | 기능 구분 | 기능 명세 |
|---|---|---|
| 1 | 화면 이동 | 사용자가 앱 실행 후 로그인 화면으로 진입한다. **회원가입** 텍스트를 누르면 회원가입 화면으로 이동하고, 로그인 성공 시 관심 분야 선택 또는 홈 화면으로 이동한다. |
| 2 | 화면 기능 | 사용자는 아이디와 비밀번호를 입력한 뒤 **로그인** 버튼을 눌러 인증을 요청한다. 하단의 **구글 계정으로 가입하기** 버튼을 통해 구글 계정 기반 가입 또는 로그인을 진행할 수 있다. |
| 3 | 데이터 처리 | React Native에서 입력한 `login_id`, `password`를 FastAPI로 전달한다. 서버는 예시로 `users` 테이블의 계정 정보와 비밀번호 해시값을 검증한다. |
| 4 | 등록/저장/조회 | 로그인 성공 시 FastAPI가 사용자 정보와 인증 토큰을 반환한다. 프론트엔드는 토큰을 저장하고, 사용자의 관심 분야 설정 여부에 따라 관심 분야 선택 화면 또는 홈 화면으로 이동한다. |
| 5 | 예외 처리 | 아이디 또는 비밀번호 누락 시 입력 안내 문구를 표시한다. 인증 실패, 네트워크 오류, 탈퇴 또는 정지 계정, 토큰 발급 실패 시 로그인 실패 메시지를 표시한다. |

가정:
- 로그인 성공 후 관심 분야가 없는 사용자는 관심 분야 선택 화면으로 이동한다고 가정한다.
- DB 테이블명은 예시이며, 실제 구현 시 `users`, `user_auth`, `oauth_accounts` 등으로 변경될 수 있다.
- 구글 버튼은 화면 문구 기준으로 소셜 가입 또는 소셜 로그인 흐름에 연결되는 기능으로 가정하였다.

---

[회원가입]

| 번호 | 기능 구분 | 기능 명세 |
|---|---|---|
| 1 | 화면 이동 | 사용자가 로그인 화면의 **회원가입** 텍스트를 눌러 회원가입 화면으로 이동한다. 가입 완료 시 관심 분야 선택 화면 또는 로그인 화면으로 이동한다. |
| 2 | 화면 기능 | 사용자는 이름, 아이디, 비밀번호, 비밀번호 확인을 입력한다. **중복 확인** 버튼으로 아이디 사용 가능 여부를 확인하고, **회원가입** 버튼으로 계정을 생성한다. |
| 3 | 데이터 처리 | React Native에서 `name`, `login_id`, `password`, `password_confirm` 값을 FastAPI로 전달한다. 서버는 비밀번호를 해시 처리한 뒤 예시로 `users` 테이블에 회원 정보를 저장한다. |
| 4 | 등록/저장/조회 | 중복 확인 시 FastAPI가 아이디 존재 여부를 조회한다. 회원가입 성공 시 신규 사용자 정보가 저장되고, 이후 관심 분야 설정을 위한 초기 화면으로 이동한다. |
| 5 | 예외 처리 | 필수 입력값 누락, 아이디 중복, 비밀번호 불일치, 비밀번호 형식 오류, 네트워크 오류, 저장 실패 시 안내 문구를 표시하고 가입 요청을 중단한다. |

가정:
- 회원가입 후 바로 관심 분야 선택 화면으로 이동하는 흐름을 우선 가정한다.
- DB 테이블명은 예시이며, 실제 구현 시 `users`, `user_profiles`, `oauth_accounts` 등으로 변경될 수 있다.
- 구글 계정 가입은 별도 OAuth 인증 후 사용자 기본 정보를 저장하는 방식으로 확장 가능하다.

## Prompt:
2026. 5. 13. 오후 7:10:57

![트렌드 정보(검색어 조회 결과가 없을 때).png](https://chatgpt.com/backend-api/estuary/content?id=file_00000000e4747209bed263060b749980&ts=494424&p=fs&cid=1&sig=f003c5537ccb5740958174d6ef14674d7ef17a1ee494c0058486030cea4bd351&v=0)

![트렌드 정보(검색어가 있을 때).png](https://chatgpt.com/backend-api/estuary/content?id=file_00000000018072099a61ce84f5fa2c73&ts=494424&p=fs&cid=1&sig=474168edae92d5371c9da9fed41a80ee4a369c38b90b66db7dfb28ee5efa7a1a&v=0)

![트렌드 정보(초기 화면).png](https://chatgpt.com/backend-api/estuary/content?id=file_000000001ef87209a9ff00ceb80008b3&ts=494424&p=fs&cid=1&sig=6b1a52606a05125e4361f9d95416b0ad341e6b2adef593b271afb5264ff066a1&v=0)

![트렌드 정보(최근 검색어 있을 경우).png](https://chatgpt.com/backend-api/estuary/content?id=file_00000000d4d87209a67ec5f1b89215c5&ts=494424&p=fs&cid=1&sig=c59d51e31529bb66c873f24a2f0de91e7f7a6f8e8c27c4497369f4517569e1fc&v=0)

감사합니다! 이번엔 트렌드 정보 검색 기능인데, 가능할까요?

## Response:
2026. 5. 13. 오후 7:10:57

가능합니다. 아래는 **트렌드 정보 검색 화면 전체 흐름**을 하나의 발표용 기능상세명세로 정리한 버전입니다.  
이미지 기준으로 **초기 화면 / 최근 검색어 / 검색 결과 있음 / 검색 결과 없음** 상태를 함께 반영했습니다.

---

[트렌드 정보 검색]

| 번호 | 기능 구분 | 기능 명세 |
|---|---|---|
| 1 | 화면 이동 | 사용자는 하단 탭의 **검색** 버튼을 통해 트렌드 검색 화면으로 이동한다. 검색 결과 카드 선택 시 트렌드 상세 또는 AI 요약 화면으로 이동할 수 있다. |
| 2 | 화면 기능 | 사용자는 검색창에 키워드를 입력하여 트렌드를 조회한다. 초기 화면에서는 관심사 기반 추천 검색어와 최근 검색어를 확인하고, 결과 화면에서는 카테고리 필터와 트렌드 목록을 확인한다. |
| 3 | 데이터 처리 | React Native에서 `keyword`, `category`, `user_id`를 FastAPI로 전달한다. 서버는 예시로 `trends`, `trend_ai_analysis`, `search_logs`, `user_interests` 테이블을 조회하여 검색 결과와 추천 검색어를 반환한다. |
| 4 | 등록/저장/조회 | 검색 실행 시 FastAPI가 키워드 기반 트렌드 목록을 조회하고, 검색어는 예시로 `search_logs`에 저장한다. 조회 성공 시 결과 개수, 카테고리 필터, 트렌드 카드, AI 요약, 해시태그를 화면에 반영한다. |
| 5 | 예외 처리 | 검색어가 비어 있으면 추천 검색어 또는 최근 검색어를 우선 표시한다. 검색 결과가 없으면 “검색 결과가 없어요” 문구와 추천 검색어, 내 관심사 트렌드 보기, 최신 이슈 둘러보기 버튼을 제공한다. 네트워크 오류나 인증 만료 시 안내 메시지와 재시도 처리를 제공한다. |

가정:
- 검색 화면은 하단 탭의 **검색** 메뉴를 통해 접근하는 화면으로 가정한다.
- 검색 결과 카드의 별 아이콘은 트렌드 저장 기능과 연결될 수 있다고 가정한다.
- DB 테이블명은 예시이며, 실제 구현 시 `trend_items`, `trend_keywords`, `trend_search_logs`, `trend_bookmarks` 등으로 변경될 수 있다.
- 기획서의 관심사 기반 트렌드 탐색 방향을 기준으로, 추천 검색어는 사용자 관심사와 최근 조회 데이터를 활용하는 방식으로 정리하였다. `interest_based_trend_app_plan.md`

---

[최근 검색어 관리]

| 번호 | 기능 구분 | 기능 명세 |
|---|---|---|
| 1 | 화면 이동 | 사용자가 검색 탭에 진입하면 검색 기록이 있는 경우 최근 검색어 영역이 함께 표시된다. 최근 검색어를 누르면 해당 키워드로 검색 결과 화면으로 이동한다. |
| 2 | 화면 기능 | 사용자는 최근 검색어 목록을 확인하고, 각 검색어 오른쪽의 삭제 버튼을 통해 개별 검색어를 제거할 수 있다. 검색 기록이 없으면 “아직 검색하거나 조회된 내용이 없어요” 문구를 표시한다. |
| 3 | 데이터 처리 | React Native는 화면 진입 시 `user_id`를 기준으로 FastAPI에 최근 검색어 조회를 요청한다. 서버는 예시로 `search_logs` 테이블에서 사용자별 최근 검색어를 조회한다. |
| 4 | 등록/저장/조회 | 검색 성공 시 해당 키워드는 최근 검색어로 저장된다. 삭제 버튼 클릭 시 FastAPI가 해당 검색 기록을 삭제하고, 성공 시 화면 목록에서 즉시 제거한다. |
| 5 | 예외 처리 | 최근 검색어 조회 실패 시 빈 상태 화면을 표시하거나 재시도 안내를 제공한다. 삭제 실패 시 기존 목록을 유지하고 “삭제에 실패했습니다” 안내를 표시한다. |

가정:
- 최근 검색어는 로그인 사용자 기준으로 저장된다고 가정한다.
- 화면상 전체 삭제 버튼은 보이지 않으므로 개별 삭제 기능만 포함하였다.

---

[검색 결과 필터 및 트렌드 카드]

| 번호 | 기능 구분 | 기능 명세 |
|---|---|---|
| 1 | 화면 이동 | 사용자가 검색어를 입력하거나 추천 검색어를 선택하면 검색 결과 목록 화면으로 전환된다. 결과 카드 선택 시 해당 트렌드 상세 화면으로 이동한다. |
| 2 | 화면 기능 | 사용자는 전체, 음식, 여행, 패션 등 카테고리 필터를 선택해 결과를 좁혀볼 수 있다. 각 카드에서는 키워드, 분야, 상승 상태, AI 요약, 해시태그, 저장 버튼을 확인할 수 있다. |
| 3 | 데이터 처리 | React Native는 `keyword`, `selectedCategory`, `page` 값을 FastAPI로 전달한다. 서버는 예시로 `trends`, `categories`, `trend_ai_analysis`, `user_bookmarks` 테이블을 조합해 결과를 반환한다. |
| 4 | 등록/저장/조회 | 카테고리 필터 변경 시 조건에 맞는 검색 결과를 재조회한다. 별 아이콘 클릭 시 FastAPI가 예시로 `user_bookmarks`에 저장하고, 성공 시 아이콘 상태를 변경한다. |
| 5 | 예외 처리 | 선택한 카테고리에 결과가 없으면 빈 결과 화면을 표시한다. 저장 실패, 중복 저장, 로그인 만료, 서버 응답 지연 시 사용자에게 안내하고 기존 화면 상태를 유지한다. |

가정:
- 검색 결과의 AI 요약은 사전에 저장된 분석 결과를 조회하거나, 필요 시 FastAPI에서 AI 분석 요청 후 반환하는 방식으로 구현할 수 있다.
- 결과 개수와 카테고리 필터는 서버 응답 기준으로 동적으로 표시된다고 가정한다.



---
Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)