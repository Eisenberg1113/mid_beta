# Gachi (가치) - 캠퍼스 익명 활동 매칭 서비스

![Gachi Project](https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

## 📌 프로젝트 소개 (Project Definition)

### 🎯 Vision Statement
> "누구나 부담 없이 안전하게 만나는 캠퍼스 익명 취미 활동의 중심"

**Gachi**는 대학생들이 학과나 학번에 얽매이지 않고 오직 관심사를 기반으로 모일 수 있는 건강하고 안전한 캠퍼스 문화를 만들어갑니다. 
캠퍼스 내에서 운동, 게임, 스터디, 식사 등의 활동을 함께할 친구를 빠르고 안전하게 찾을 수 있도록 지원합니다.

### 🏁 Project Goals & Scope
**목표 (Goals):**
- 빠르고 간편한 인증 및 매칭 시스템 구축
- 오프라인 모임의 불편함을 해소하는 직관적인 장소/일정 조율 경험 제공
- 익명성 보장과 동시에 상호 평가, 신고 제도를 통한 커뮤니티 신뢰 확보

**범위 (Scope):**
- Google OAuth를 이용한 최소한의 가입/로그인 및 익명 닉네임 자동 부여
- 카카오맵 및 타임피커 기반의 4가지 카테고리(운동, 게임, 스터디, 식사) 모임 개설/참여
- 모임 참여자 전용 실시간 인앱 채팅 (Long Polling 또는 WebSocket)
- 매너 온도 평가 시스템 및 누적 신고(5회) 시 자동 밴(Ban) 시스템 구축
- 관리자 전용 대시보드를 통한 서비스 모니터링

### 👥 Stakeholders & Users
- **일반 사용자 (User)**: 대학생. Google 계정으로 로그인하여 모임을 만들거나 참여하고, 멤버들과 채팅 및 상호 평가를 진행하는 주 사용자.
- **관리자 (Admin)**: 서비스 운영자. Django Admin을 통해 신고 내역, 유저 상태를 관리하고 카카오맵 밀집도 대시보드를 통해 매칭이 활발한 지역을 분석하는 관리자.

### 🗺 Milestone
- **Release 1 — 인증 + 모임 기초 (MVP)**: Google OAuth 연동, 익명 닉네임 생성, 카테고리 기반 모임 개설/목록 조회, 재로그인 데이터 유지
- **Release 2 — 매칭 + 소통**: 카카오맵 연동을 통한 모임 장소 지정, 타임피커 일정 선택, 정원 확인 후 자동 참가, 실시간 인앱 채팅 활성화
- **Release 3 — 신뢰 + 관리**: 상호 매너온도 평가(👍/👎), 유저 상세 프로필 및 즐겨찾기, 유저 신고 접수 및 자동 밴 처리, 관리자 밀집도 대시보드

---

## 🚀 주요 기능

### 1. 간편한 인증 및 프로필 관리
- **Google OAuth 로그인**: 복잡한 회원가입 없이 Google 계정으로 즉시 이용 가능
- **익명성 보장**: 최초 로그인 시 익명 닉네임이 자동 생성되며, 이메일은 타인에게 노출되지 않음
- **즐겨찾기**: 마음이 맞는 유저를 기억하고 싶을 때 즐겨찾기 기능 제공

### 2. 모임 개설 및 탐색
- **카테고리 기반 모임**: 운동, 게임, 스터디, 식사 중 선택하여 모임 생성
- **위치 기반 매칭**: 카카오맵 API 연동을 통해 지도를 직접 클릭하여 정확한 모임 장소 지정
- **일정 지정**: 날짜와 시간을 지정하여 모집

### 3. 실시간 소통
- **실시간 인앱 채팅**: 모임 참여 시 즉시 전용 채팅방 활성화 (참여자 전용)
- **유저 식별 및 타임스탬프**: 보낸 사람의 닉네임과 전송 시간이 직관적으로 분리되어 표시

### 4. 커뮤니티 신뢰 및 관리 (매너 온도 & 신고)
- **매너 온도 평가 시스템**: 모임 후 참여자 상호 평가(👍/👎)를 통해 매너 온도 반영
- **유저 신고 기능**: 욕설, 노쇼, 부적절한 목적 등의 사유로 악성 유저 신고 가능
- **자동 밴(Ban) 시스템**: 동일 유저 누적 신고 5회 달성 시 계정 자동 비활성화
- **관리자 대시보드**: 밀집도 대시보드(마커 클러스터링 적용)를 통해 전체 모임 분포 한눈에 파악

---

## 🛠 기술 스택

### Backend
- **Framework**: Python, Django
- **Real-time**: Django Channels (WebSocket)
- **Database**: SQLite (기본)

### Frontend
- **Languages**: HTML5, Vanilla CSS, JavaScript
- **API 연동**: Kakao Map API (지도 및 위치 검색)

### Infrastructure & Deployment
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx

---

## 📂 주요 디렉토리 구조

```text
├── meetu/
│   ├── backend/
│   │   ├── accounts/     # 인증(OAuth), 유저 모델, 프로필, 즐겨찾기 관리
│   │   ├── chat/         # 인앱 채팅(WebSocket) 처리, 메시지 기록
│   │   ├── meetings/     # 모임 CRUD, 카카오맵 연동, 매너온도 평가
│   │   ├── reports/      # 유저 신고 접수 및 자동 밴 로직 (Signals)
│   │   ├── config/       # 프로젝트 메인 설정 및 라우팅
│   │   └── templates/    # 기능별 HTML 템플릿
│   ├── frontend/         # 정적 자원 (CSS, JS) 관리
│   ├── docker-compose.yml
│   └── .env.example
├── user_stories.md       # 전체 유저 스토리 상세 내역
├── report.md             # 프로젝트 주요 설계 및 보고서
└── project_guide.md      # 클론 코딩 가이드
```


