# 🎓 Gachi — 캠퍼스 익명 활동 매칭 서비스 결과 보고서

> **프로젝트명**: Gachi  
> **작성일**: 2026년 4월 29일  
> **기술 스택**: Django + PostgreSQL + Nginx + Docker Compose

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|---|---|
| 서비스명 | **Gachi** — 캠퍼스 익명 취미 매칭 서비스 |
| 핵심 기능 | Google OAuth 로그인, 모임 생성/매칭, 인앱 채팅, 매너온도, 관리자 대시보드 |
| 대상 사용자 | 대학생 (User), 운영 관리자 (Admin) |
| 인증 방식 | Google OAuth 2.0 (`django-allauth`) — 닉네임만 타 유저에게 노출 |
| 접속 URL | `http://localhost` (Docker Compose 실행 후) |

---

## 2. 시스템 아키텍처

```
[ 브라우저 ]
     │  HTTP (port 80)
     ▼
[ Nginx ]  ← 정적 파일 서빙 (/static/)
     │  리버스 프록시 (port 8000)
     ▼
[ Django (Gunicorn) ]  ← 비즈니스 로직, REST API, Long Polling 채팅
     │  workers=2, threads=8
     ▼
[ PostgreSQL 15 ]  ← 유저, 모임, 채팅, 신고 데이터 영구 저장
```

### 컨테이너 구성 (Docker Compose)

| 컨테이너 | 이미지 | 역할 |
|---|---|---|
| `meetu-db-1` | `postgres:15` | 데이터베이스 서버 |
| `meetu-web-1` | 커스텀 빌드 (`backend/Dockerfile`) | Django 애플리케이션 서버 |
| `meetu-nginx-1` | `nginx:alpine` | 리버스 프록시 + 정적 파일 서빙 |

---

## 3. 기술 스택 상세

| 기술 | 버전 | 역할 |
|---|---|---|
| **Django** | ≥ 4.2 | 인증, 모임 CRUD, 채팅, 신고, 관리자 기능 |
| **PostgreSQL** | 15 | 모든 데이터 영구 저장 |
| **Nginx** | Alpine | 정적 파일 서빙, 리버스 프록시 |
| **Docker Compose** | 3.9 | 3-컨테이너 통합 관리 |
| **django-allauth** | 최신 | Google OAuth 2.0 소셜 로그인 |
| **djangorestframework** | 최신 | 채팅 REST API |
| **Gunicorn** | 최신 | WSGI 서버 (멀티 스레드) |
| **django-environ** | 최신 | 환경변수 관리 |
| **Tailwind CSS** | CDN | UI 스타일링 |
| **Kakao Maps SDK** | v2 | 위치 선택 + 밀집도 대시보드 |
| **Flatpickr** | 최신 | 날짜/시간 선택 UI |

---

## 4. 디렉토리 구조

```
meetu/
├── docker-compose.yml          # 컨테이너 오케스트레이션
├── .env                        # 환경변수 (Git 미포함)
├── .env.example                # 환경변수 템플릿
├── .gitignore
├── nginx/
│   └── nginx.conf              # Nginx 설정
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/                 # Django 설정
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── accounts/               # 유저 프로필, 즐겨찾기
│   │   ├── models.py           # UserProfile
│   │   ├── views.py            # 프로필, 유저 상세, 즐겨찾기
│   │   ├── urls.py
│   │   └── signals.py          # 유저 생성 시 프로필 자동 생성
│   ├── meetings/               # 모임 생성/매칭/평가
│   │   ├── models.py           # Meeting, MeetingMember, Evaluation
│   │   ├── views.py            # 목록, 생성, 참가, 매너 평가
│   │   ├── urls.py
│   │   └── admin.py            # 밀집도 대시보드 커스텀 뷰
│   ├── chat/                   # 인앱 채팅
│   │   ├── models.py           # ChatMessage
│   │   ├── views.py            # Long Polling API
│   │   ├── urls.py
│   │   └── serializers.py      # DRF 시리얼라이저
│   ├── reports/                # 신고 시스템
│   │   ├── models.py           # Report + 자동 밴 시그널
│   │   ├── views.py            # 신고 접수
│   │   └── urls.py
│   └── templates/
│       ├── base.html           # 공통 레이아웃 (다크 테마)
│       ├── index.html          # 랜딩 페이지
│       ├── socialaccount/      # Google 로그인 커스텀 UI
│       ├── meetings/           # 모임 목록, 생성
│       ├── chat/               # 채팅 화면
│       ├── accounts/           # 프로필, 유저 상세
│       ├── reports/            # 신고 페이지
│       └── admin/              # 밀집도 대시보드
└── frontend/
    ├── static/
    │   ├── css/                # 커스텀 CSS (확장용)
    │   └── js/                 # 커스텀 JS (확장용)
    └── index.html
```

---

## 5. 데이터 모델 설계

```
┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│    User      │1────1│  UserProfile  │*────*│  UserProfile  │
│  (Django)    │      │  - nickname   │      │  (favorites)  │
│              │      │  - manner     │      │               │
└─────────────┘      └──────┬───────┘      └───────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
        ┌─────▼─────┐ ┌────▼────┐ ┌──────▼──────┐
        │  Meeting   │ │ Report  │ │ ChatMessage │
        │ - category │ │ -reason │ │ - content   │
        │ - location │ │ -target │ │ - sent_at   │
        │ - schedule │ └─────────┘ └─────────────┘
        └─────┬──────┘
              │
     ┌────────┼────────┐
     │                 │
┌────▼──────┐   ┌──────▼──────┐
│MeetingMember│ │  Evaluation  │
│ - joined_at │ │ - score      │
└─────────────┘ │ - evaluator  │
                │ - evaluatee  │
                └──────────────┘
```

### 주요 모델 설명

| 모델 | 설명 |
|---|---|
| `UserProfile` | 유저 프로필 (닉네임, 매너온도, 즐겨찾기 M2M) |
| `Meeting` | 모임 정보 (카테고리, 위치 JSON, 일정, 최대 인원) |
| `MeetingMember` | 모임 참여 기록 |
| `Evaluation` | 모임별 유저 상호 평가 (unique_together로 중복 방지) |
| `ChatMessage` | 채팅 메시지 |
| `Report` | 유저 신고 (post_save 시그널로 5회 누적 시 자동 밴) |

---

## 6. Release별 구현 결과

### Release 1 — 인증 + 모임 기초 (MVP)

| 기능 | 구현 내용 | 상태 |
|---|---|---|
| Google OAuth 로그인 | `django-allauth` 기반 소셜 로그인 | ✅ |
| 닉네임 자동 생성 | `post_save` 시그널로 유저 생성 시 자동 부여 | ✅ |
| 재로그인 계정 유지 | 이메일 기반 자동 연결 설정 | ✅ |
| 모임 생성 | 카테고리 선택형 UI (텍스트 입력 없음) | ✅ |
| 모임 목록 + 필터 | 전체/운동/게임/스터디/식사 카테고리 필터 | ✅ |
| 랜딩 페이지 | 다크 테마, 글로우 효과, 반응형 디자인 | ✅ |
| Docker 인프라 | 3-컨테이너 구성 완료 | ✅ |

### Release 2 — 매칭 + 소통

| 기능 | 구현 내용 | 상태 |
|---|---|---|
| 카카오맵 위치 선택 | 지도 클릭 → 좌표/주소 자동 저장 (JSONField) | ✅ |
| 달력/타임피커 | Flatpickr (한국어 로케일, 다크 테마) | ✅ |
| 인앱 채팅 | Long Polling 방식 (Django REST Framework) | ✅ |
| 모임 참가 | 정원 확인 후 자동 멤버 등록 → 채팅방 입장 | ✅ |

### Release 3 — 신뢰 + 관리

| 기능 | 구현 내용 | 상태 |
|---|---|---|
| 매너온도 평가 | 👍(+0.5°C) / 👎(-0.5°C), 모임별 1회 제한 | ✅ |
| 유저 신고 | 선택형 신고 사유 (욕설, 노쇼, 부적절 목적, 기타) | ✅ |
| 자동 밴 | 신고 5회 누적 시 `is_active=False` 자동 처리 | ✅ |
| 내 프로필 | 매칭 이력 + 즐겨찾기 목록 조회 | ✅ |
| 유저 상세 | 타 유저 프로필 조회 + 즐겨찾기 토글 | ✅ |
| 관리자 대시보드 | 카카오맵 마커 클러스터링 밀집도 시각화 | ✅ |

---

## 7. 주요 API 엔드포인트

| Method | URL | 기능 |
|---|---|---|
| GET | `/` | 랜딩 페이지 (비로그인) / 모임 목록 리다이렉트 (로그인) |
| GET | `/accounts/google/login/` | Google OAuth 시작 |
| GET | `/meetings/` | 모임 목록 (카테고리 필터 지원) |
| POST | `/meetings/create/` | 모임 생성 |
| GET | `/meetings/<id>/join/` | 모임 참가 |
| GET | `/meetings/<id>/chat/` | 채팅방 화면 |
| GET | `/api/meetings/<id>/messages/?last_id=N` | 새 메시지 조회 (Long Polling) |
| POST | `/api/meetings/<id>/messages/` | 메시지 전송 |
| POST | `/meetings/<id>/evaluate/<user_id>/` | 매너 평가 |
| GET | `/accounts/profile/` | 내 프로필 |
| GET | `/accounts/profile/<user_id>/` | 유저 상세 |
| POST | `/accounts/profile/<user_id>/favorite/` | 즐겨찾기 토글 |
| GET/POST | `/reports/submit/<user_id>/` | 유저 신고 |
| GET | `/admin/` | Django 관리자 페이지 |
| GET | `/admin/meetings/meeting/density-dashboard/` | 밀집도 대시보드 |

---

## 8. 프론트엔드 디자인

### 디자인 스펙 적용 현황

| 항목 | 스펙 | 적용 |
|---|---|---|
| 테마 | 다크 배경 기반 | ✅ `#0A0A0F` 배경 |
| 메인 컬러 | `#4F46E5` (Indigo) | ✅ 버튼, 강조, 포인트 |
| 포인트 컬러 | `#06B6D4` (Cyan) | ✅ 보조 강조, 닉네임 |
| 폰트 | Pretendard → Noto Sans KR 폴백 | ✅ CDN 로드 |
| CSS 프레임워크 | Tailwind CSS | ✅ CDN 사용 |
| 배경 장식 | 그리드 패턴 + 글로우 오브 | ✅ |
| 인터랙션 | hover 시 translateY + 글로우 | ✅ |
| 반응형 | 모바일 1열 → 데스크탑 2~3열 그리드 | ✅ |

### 주요 화면 구성

| 페이지 | 설명 |
|---|---|
| 랜딩 (`/`) | 히어로 섹션 + 6개 핵심 기능 카드 |
| 모임 목록 (`/meetings/`) | 카테고리 필터 탭 + 카드 그리드 |
| 모임 생성 (`/meetings/create/`) | 카테고리 선택 + 카카오맵 + 달력 |
| 채팅방 (`/meetings/<id>/chat/`) | 참여자 목록 + 실시간 메시지 + 평가/신고 버튼 |
| 내 프로필 (`/accounts/profile/`) | 모임 이력 + 즐겨찾기 멤버 |
| 유저 상세 (`/accounts/profile/<id>/`) | 닉네임 + 매너온도 + 즐겨찾기/신고 |
| 신고 (`/reports/submit/<id>/`) | 선택형 신고 사유 라디오 버튼 |
| Google 로그인 확인 | Gachi 다크 테마 커스텀 UI |
| 관리자 대시보드 | 카카오맵 마커 클러스터링 지도 |

---

## 9. 익명성 보장 설계

| 레이어 | 처리 방식 |
|---|---|
| **서버 DB** | Google 이메일/ID 저장 (재매칭, 밴 처리용) |
| **API 응답** | 닉네임 + 매너온도만 노출, 이메일 절대 미포함 |
| **채팅 UI** | 닉네임만 표시, 개인정보 노출 없음 |
| **매칭 이력** | user_id 기반 저장, 화면엔 닉네임만 표시 |

> **설계 원칙**: 서버 기준 실명 / 유저 간 익명 — 당근마켓과 동일한 구조

---

## 10. 보안 점검

| 항목 | 상태 | 설명 |
|---|---|---|
| 환경변수 관리 | ✅ | `.env` 파일로 분리, `.gitignore` 포함 |
| `.env.example` | ✅ | 더미 값으로 템플릿 제공 |
| API 키 하드코딩 | ✅ 없음 | `django-environ`으로 안전하게 로드 |
| CSRF 보호 | ✅ | 모든 POST 폼에 `{% csrf_token %}` 적용 |
| 로그인 필수 | ✅ | 모든 주요 뷰에 `@login_required` 데코레이터 |
| 자기 자신 평가 방지 | ✅ | 서버 측 검증 |
| 자기 자신 신고 방지 | ✅ | 서버 측 검증 |
| 중복 평가 방지 | ✅ | DB `unique_together` 제약 조건 |

---

## 11. 실행 방법

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env에 실제 GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, KAKAO_MAP_API_KEY 입력

# 2. 빌드 및 실행
docker-compose up --build

# 3. DB 마이그레이션
docker-compose exec web python manage.py migrate

# 4. 정적 파일 수집
docker-compose exec web python manage.py collectstatic --noinput

# 5. 관리자 계정 생성 (선택)
docker-compose exec web python manage.py createsuperuser

# 6. 접속
# http://localhost
```

---

## 12. 의존성 목록

```
# requirements.txt
Django>=4.2
psycopg2-binary       # PostgreSQL 드라이버
django-allauth        # Google OAuth 소셜 로그인
djangorestframework   # REST API (채팅)
gunicorn              # WSGI 서버
django-environ        # 환경변수 관리
requests              # HTTP 요청
PyJWT                 # JWT 토큰 처리
```

---

## 13. 결론

Gachi 프로젝트는 Release 1(MVP)부터 Release 3(신뢰+관리)까지 **총 3단계의 릴리즈를 모두 성공적으로 구현 완료**하였습니다.

Docker Compose 기반의 3-컨테이너 아키텍처 위에 Google OAuth 인증, 카카오맵 위치 기반 모임 생성, Long Polling 실시간 채팅, 매너온도 평가 시스템, 신고 누적 자동 밴, 관리자 밀집도 대시보드 등 프로젝트 가이드에서 요구한 **모든 기능을 빠짐없이 구현**하였으며, 디자인 스펙(다크 테마, Indigo/Cyan 컬러, Pretendard 폰트, 인터랙션 효과)도 충실하게 반영하였습니다.

특히, 서버 기준 실명 / 유저 간 익명이라는 설계 원칙을 일관되게 적용하여 **프라이버시와 안전성을 모두 확보**한 캠퍼스 매칭 서비스를 완성하였습니다.
