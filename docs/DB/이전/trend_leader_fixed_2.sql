SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE trend_leader;

USE trend_leader;

CREATE TABLE categories
(
  category_id   BIGINT                  NOT NULL AUTO_INCREMENT COMMENT '카테고리 ID 일련번호',
  parent_id     BIGINT                  NULL     COMMENT '상위 카테고리 ID',
  category_name VARCHAR                 NOT NULL COMMENT '카테고리명',
  depth         ENUM('1:대분류', '2:세부분류') NOT NULL DEFAULT '1:대분류' COMMENT '분류 단계',
  sort_order    INT                     NOT NULL DEFAULT 0 COMMENT '화면 노출 순서',
  is_active     TINYINT(1)              NOT NULL DEFAULT 0 COMMENT '사용 여부',
  PRIMARY KEY (category_id)
) COMMENT '카테고리';

CREATE TABLE oauth_accounts
(
  oauth_id         BIGINT         NOT NULL AUTO_INCREMENT COMMENT 'OAuth 계정 ID 일련번호',
  provider         ENUM('GOOGLE') NOT NULL DEFAULT 'GOOGLE' COMMENT '정보 제공자',
  provider_user_id VARCHAR        NOT NULL COMMENT '외부 서비스 사용자 식별값',
  email            VARCHAR        NOT NULL COMMENT 'OAuth 이메일',
  created_at       DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '연동일',
  user_id          BIGINT         NOT NULL COMMENT '사용자 FK',
  PRIMARY KEY (oauth_id)
) COMMENT 'OAuth 계정';

CREATE TABLE search_logs
(
  search_log_id BIGINT     NOT NULL AUTO_INCREMENT COMMENT '검색 기록 ID',
  keyword       VARCHAR    NOT NULL COMMENT '검색어',
  category_id   BIGINT     NOT NULL COMMENT '검색 당시 필터 카테고리',
  result_count  BIGINT     NOT NULL DEFAULT 0 COMMENT '검색 결과 수',
  searched_at   DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '검색 시각',
  is_deleted    TINYINT(1) NOT NULL DEFAULT 0 COMMENT '최근 검색어 삭제 여부',
  user_id       BIGINT     NOT NULL COMMENT '사용자 ID 일련번호',
  PRIMARY KEY (search_log_id)
) COMMENT '검색 기록';

CREATE TABLE trend_ai_analyses
(
  analysis_id      BIGINT                                 NOT NULL AUTO_INCREMENT COMMENT 'AI 분석 ID',
  one_line_summary TEXT                                   NOT NULL COMMENT 'AI 한줄 요약',
  reason_text      TEXT                                   NOT NULL COMMENT '유행 이유 설명',
  detail_text      LONGTEXT                               NULL     COMMENT '상세 설명',
  model_name       ENUM('GPT', 'GEMINI', 'CLAUDE', 'ETC') NOT NULL DEFAULT 'ETC' COMMENT '사용 AI 모델명',
  created_at       DATETIME                               NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '분석 생성일',
  trend_id         BIGINT                                 NOT NULL COMMENT '트렌드 정보 ID',
  PRIMARY KEY (analysis_id)
) COMMENT '트렌드 AI 분석';

CREATE TABLE trend_category_map
(
  trend_category_id BIGINT     NOT NULL AUTO_INCREMENT COMMENT '매핑 PK',
  is_primary        TINYINT(1) NOT NULL DEFAULT 0 COMMENT '대표 카테고리 여부',
  category_id       BIGINT     NOT NULL COMMENT '카테고리 ID 일련번호',
  trend_id          BIGINT     NOT NULL COMMENT '트렌드 정보 ID',
  PRIMARY KEY (trend_category_id)
) COMMENT '트렌드-카테고리 매핑 테이블';

CREATE TABLE trend_rank_snapshots
(
  rank_snapshot_id BIGINT                            NOT NULL AUTO_INCREMENT COMMENT '순위 기록 ID',
  platform         VARCHAR                           NOT NULL COMMENT '순위 기준 플랫폼',
  rank             INT                               NOT NULL COMMENT '현재 순위',
  rank_change      ENUM('UP', 'DOWN', 'SAME', 'NEW') NOT NULL DEFAULT 'NEW' COMMENT ' 바뀐 순위',
  score            INT                               NOT NULL COMMENT '트렌드 점수',
  collected_date   DATE                              NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '수집 날짜',
  collected_at     DATETIME                          NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '수집 시각',
  trend_id         BIGINT                            NOT NULL COMMENT '트렌드 정보 ID',
  PRIMARY KEY (rank_snapshot_id)
) COMMENT '트랜드 순위 스냅샷';

CREATE TABLE trend_related_keywords
(
  related_keyword_id BIGINT                                    NOT NULL AUTO_INCREMENT COMMENT '관련 키워드 ID',
  keyword            VARCHAR                                   NOT NULL COMMENT '키워드 이름',
  relation_type      ENUM('RELATED', 'HASHTAG', 'RECOMMENDED') NOT NULL AUTO_INCREMENT COMMENT '관련 요소 타입',
  sort_order         INT                                       NULL     AUTO_INCREMENT COMMENT '표시 순서',
  trend_id           BIGINT                                    NOT NULL DEFAULT 1 COMMENT '트렌드 정보 ID',
  PRIMARY KEY (related_keyword_id)
) COMMENT '관련 키워드';

ALTER TABLE trend_related_keywords
  ADD CONSTRAINT UQ_relation_type UNIQUE (relation_type);

ALTER TABLE trend_related_keywords
  ADD CONSTRAINT UQ_sort_order UNIQUE (sort_order);

CREATE TABLE trend_sources
(
  source_id    BIGINT                                  NOT NULL AUTO_INCREMENT COMMENT '출처 ID',
  source_url   TEXT                                    NOT NULL COMMENT '원문 또는 수집 URL',
  platform     ENUM('GOOGLE', 'YOUTUBE', 'SNS', 'ETC') NOT NULL DEFAULT 'ETC' COMMENT '플랫폼',
  collected_at DATETIME                                NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '수집 시각',
  trend_id     BIGINT                                  NOT NULL COMMENT '트렌드 정보 ID',
  PRIMARY KEY (source_id)
) COMMENT '트렌드 출처 정보 저장';

CREATE TABLE trends
(
  trend_id           BIGINT                   NOT NULL AUTO_INCREMENT COMMENT '트렌드 정보 ID',
  title              VARCHAR                  NOT NULL COMMENT '트렌드명 or 대표 키워드',
  summary            TEXT                     NOT NULL COMMENT '기본 요약',
  thumbnail_url      TEXT                     NULL     COMMENT '대표 이미지 URL',
  status             ENUM('ACTIVE', 'HIDDEN') NOT NULL DEFAULT 'ACTIVE' COMMENT '조회 가능 상태',
  first_collected_at DATETIME                 NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '최초 수집일',
  updated_at         DATETIME                 NULL     COMMENT '수정일',
  PRIMARY KEY (trend_id)
) COMMENT '트렌드 정보';

CREATE TABLE user
(
  user_id       BIGINT                                   NOT NULL AUTO_INCREMENT COMMENT '사용자 ID 일련번호',
  login_id      VARCHAR                                  NOT NULL COMMENT '로그인 ID',
  password_hash VARCHAR                                  NOT NULL COMMENT '비밀번호 해시값',
  name          VARCHAR                                  NOT NULL COMMENT '사용자 이름',
  email         VARCHAR                                  NULL     COMMENT '이메일 & OAuth 연동',
  status        ENUM('ACTIVE', 'WITHDRAWN', 'SUSPENDED') NOT NULL DEFAULT 'ACTIVE' COMMENT '계정 상태',
  created_at    DATETIME                                 NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '가입일',
  updated_at    DATETIME                                 NULL     COMMENT '수정일',
  PRIMARY KEY (user_id)
) COMMENT '유저';

CREATE TABLE user_interest_categories
(
  user_interest_id BIGINT   NOT NULL AUTO_INCREMENT COMMENT '사용자 관심사 ID',
  user_id          BIGINT   NOT NULL COMMENT '사용자 ID 일련번호',
  category_id      BIGINT   NOT NULL COMMENT '카테고리 ID 일련번호',
  weight           INT      NOT NULL COMMENT '관심도 가중치',
  created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '선택일',
  PRIMARY KEY (user_interest_id)
) COMMENT '사용자 관심사 카테고리';

CREATE TABLE user_interest_keywords
(
  interest_keyword_id BIGINT   NOT NULL AUTO_INCREMENT COMMENT '관심 키워드 ID',
  keyword             VARCHAR  NOT NULL COMMENT ' 사용자 추가 관심 키워드',
  weight              INT      NOT NULL DEFAULT 1 COMMENT '추천 가중치',
  created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '등록일',
  user_id             BIGINT   NOT NULL COMMENT '사용자 ID 일련번호',
  category_id         BIGINT   NOT NULL COMMENT '연결 카테고리 ID, 선택값',
  PRIMARY KEY (interest_keyword_id)
) COMMENT '사용자 관심 키워드';

CREATE TABLE user_profiles
(
  profile_id        BIGINT   NOT NULL AUTO_INCREMENT COMMENT '프로필 ID 일련번호',
  nickname          VARCHAR  NOT NULL COMMENT '화면 표시용 닉네임',
  profile_image_url TEXT     NULL     COMMENT '프로필 이미지 경로',
  updated_at        DATETIME NULL     COMMENT '수정일',
  user_id           BIGINT   NOT NULL COMMENT '사용자 FK',
  PRIMARY KEY (profile_id)
) COMMENT '유저 프로필';

CREATE TABLE user_trend_bookmarks
(
  bookmark_id BIGINT   NOT NULL AUTO_INCREMENT COMMENT '저장 ID',
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '저장일',
  trend_id    BIGINT   NOT NULL COMMENT '트렌드 정보 ID',
  user_id     BIGINT   NOT NULL COMMENT '사용자 ID 일련번호',
  PRIMARY KEY (bookmark_id)
) COMMENT '사용자 저장 트렌드';

ALTER TABLE user_profiles
  ADD CONSTRAINT FK_user_TO_user_profiles
    FOREIGN KEY (user_id)
    REFERENCES user (user_id);

ALTER TABLE oauth_accounts
  ADD CONSTRAINT FK_user_TO_oauth_accounts
    FOREIGN KEY (user_id)
    REFERENCES user (user_id);

ALTER TABLE user_interest_categories
  ADD CONSTRAINT FK_user_TO_user_interest_categories
    FOREIGN KEY (user_id)
    REFERENCES user (user_id);

ALTER TABLE user_interest_categories
  ADD CONSTRAINT FK_categories_TO_user_interest_categories
    FOREIGN KEY (category_id)
    REFERENCES categories (category_id);

ALTER TABLE user_interest_keywords
  ADD CONSTRAINT FK_user_TO_user_interest_keywords
    FOREIGN KEY (user_id)
    REFERENCES user (user_id);

ALTER TABLE user_interest_keywords
  ADD CONSTRAINT FK_categories_TO_user_interest_keywords
    FOREIGN KEY (category_id)
    REFERENCES categories (category_id);

ALTER TABLE trend_category_map
  ADD CONSTRAINT FK_categories_TO_trend_category_map
    FOREIGN KEY (category_id)
    REFERENCES categories (category_id);

ALTER TABLE trend_category_map
  ADD CONSTRAINT FK_trends_TO_trend_category_map
    FOREIGN KEY (trend_id)
    REFERENCES trends (trend_id);

ALTER TABLE trend_sources
  ADD CONSTRAINT FK_trends_TO_trend_sources
    FOREIGN KEY (trend_id)
    REFERENCES trends (trend_id);

ALTER TABLE trend_rank_snapshots
  ADD CONSTRAINT FK_trends_TO_trend_rank_snapshots
    FOREIGN KEY (trend_id)
    REFERENCES trends (trend_id);

ALTER TABLE trend_ai_analyses
  ADD CONSTRAINT FK_trends_TO_trend_ai_analyses
    FOREIGN KEY (trend_id)
    REFERENCES trends (trend_id);

ALTER TABLE user_trend_bookmarks
  ADD CONSTRAINT FK_trends_TO_user_trend_bookmarks
    FOREIGN KEY (trend_id)
    REFERENCES trends (trend_id);

ALTER TABLE user_trend_bookmarks
  ADD CONSTRAINT FK_user_TO_user_trend_bookmarks
    FOREIGN KEY (user_id)
    REFERENCES user (user_id);

ALTER TABLE search_logs
  ADD CONSTRAINT FK_user_TO_search_logs
    FOREIGN KEY (user_id)
    REFERENCES user (user_id);

ALTER TABLE trend_related_keywords
  ADD CONSTRAINT FK_trends_TO_trend_related_keywords
    FOREIGN KEY (trend_id)
    REFERENCES trends (trend_id);


SET FOREIGN_KEY_CHECKS = 1;