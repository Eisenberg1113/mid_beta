# 🎓 캠퍼스 익명 활동 매칭 서비스 — 프로젝트 가이드

> Django + PostgreSQL + Nginx + Docker Compose 기반  
> 수업 제시 기술 스택을 활용한 웹 애플리케이션 설계 가이드

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|---|---|
| 서비스명 | **MeetU** — 캠퍼스 익명 취미 매칭 서비스 |
| 핵심 기능 | Google OAuth 로그인, 모임 생성/매칭, 인앱 채팅, 매너온도, 관리자 대시보드 |
| 대상 사용자 | 대학생 (USER), 운영 관리자 (Admin) |
| 인증 방식 | Google OAuth 2.0 (django-allauth) — 닉네임만 타 유저에게 노출 |

---

## 2. 기술 스택 및 역할

```
[ 브라우저 ]
     │  HTTP/HTTPS
     ▼
[ Nginx ]  ← 정적 파일 서빙 (CSS, JS, 지도 UI)
     │  리버스 프록시 (8000 포트)
     ▼
[ Django (Gunicorn / Daphne) ]  ← 비즈니스 로직, REST API, WebSocket
     │
     ▼
[ PostgreSQL ]  ← 유저, 모임, 채팅, 신고 데이터 영구 저장
```

| 기술 | 역할 |
|---|---|
| **Django** | 인증, 모임 CRUD, 채팅, 신고, 관리자 기능 |
| **PostgreSQL** | 모든 데이터 영구 저장 (세션, 모임, 매너온도 등) |
| **Nginx** | 정적 파일 서빙, Django로 리버스 프록시 |
| **Docker Compose** | 3개 컨테이너(nginx, web, db) 통합 관리 |
| **HTML/CSS/JS** | 카테고리 선택 UI, 지도 API, 달력, 채팅 UI |

---

## 3. 디렉토리 구조

```
meetu/
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── accounts/          # 유저, Google OAuth
│   ├── meetings/          # 모임 생성/매칭
│   ├── chat/              # 인앱 채팅
│   ├── reports/           # 신고 시스템
│   └── templates/
│       └── *.html
└── frontend/
    ├── static/
    │   ├── css/
    │   └── js/
    └── index.html
```

---

## 4. Docker Compose 구성

```yaml
# docker-compose.yml
version: '3.9'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: meetu
      POSTGRES_USER: meetu_user
      POSTGRES_PASSWORD: meetu_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: ./backend
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./backend:/app
      - static_volume:/app/staticfiles
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgres://meetu_user:meetu_pass@db:5432/meetu
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/staticfiles
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
```

---

## 5. Nginx 설정

```nginx
# nginx/nginx.conf
server {
    listen 80;

    # 정적 파일 직접 서빙
    location /static/ {
        alias /staticfiles/;
    }

    # Django로 리버스 프록시
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 6. Django 핵심 모델 설계

```python
# accounts/models.py
class UserProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname   = models.CharField(max_length=20, unique=True)   # 타 유저에게 노출
    manner     = models.FloatField(default=36.5)
    favorites  = models.ManyToManyField('self', blank=True)
    # user.email은 서버만 보관, API로 절대 노출 안 함

# meetings/models.py
class Meeting(models.Model):
    CATEGORY_CHOICES = [('운동','운동'), ('게임','게임'), ('스터디','스터디'), ('식사','식사')]
    host      = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    category  = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location  = models.JSONField()         # {lat, lng, name}
    schedule  = models.DateTimeField()
    max_members = models.IntegerField(default=4)
    created_at  = models.DateTimeField(auto_now_add=True)

class MeetingMember(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    user    = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

# chat/models.py
class ChatMessage(models.Model):
    meeting   = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    sender    = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content   = models.TextField()         # 텍스트 필터링 적용
    sent_at   = models.DateTimeField(auto_now_add=True)

# reports/models.py
class Report(models.Model):
    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reports_sent')
    target   = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reports_received')
    reason   = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 7. Google OAuth 설정

```python
# settings.py
INSTALLED_APPS = [
    ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

AUTHENTICATION_BACKENDS = ['allauth.account.auth_backends.AuthenticationBackend']
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}
LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
```

```python
# accounts/signals.py — 최초 로그인 시 닉네임 자동 생성
from allauth.socialaccount.signals import social_account_added
from django.dispatch import receiver

@receiver(social_account_added)
def create_profile(request, sociallogin, **kwargs):
    user = sociallogin.user
    if not hasattr(user, 'userprofile'):
        import random, string
        nick = 'user_' + ''.join(random.choices(string.ascii_lowercase, k=6))
        UserProfile.objects.create(user=user, nickname=nick)
```

---

## 8. Release 계획

### Release 1 — 인증 + 모임 기초 (MVP)
| 항목 | 내용 |
|---|---|
| 인증 | Google OAuth 로그인, 닉네임 설정 온보딩 |
| 모임 생성 | 카테고리 선택형 UI (텍스트 입력 없음) |
| 모임 목록 | 카테고리/날짜 필터 |
| 인프라 | Docker Compose 3-container 구성 완료 |

### Release 2 — 매칭 + 소통
| 항목 | 내용 |
|---|---|
| 지도 | Kakao Maps API 위치 마킹, 좌표만 DB 저장 |
| 달력/타임피커 | 일정 선택 UI |
| 채팅 | 인앱 메신저 (Long Polling 또는 Django Channels) |

### Release 3 — 신뢰 + 관리
| 항목 | 내용 |
|---|---|
| 파트너 재연결 | 매칭 이력, 즐겨찾기 |
| 매너온도 | 선택형 평가, 조작 방지 |
| 관리자 | 신고 누적 자동 밴, 밀집도 대시보드 |

---

## 9. API 엔드포인트 설계

```
# 인증
GET  /accounts/google/login/       # Google OAuth 시작
GET  /accounts/google/callback/    # OAuth 콜백

# 모임
GET  /api/meetings/                # 모임 목록
POST /api/meetings/                # 모임 생성
GET  /api/meetings/<id>/           # 모임 상세
POST /api/meetings/<id>/join/      # 참가 신청

# 채팅
GET  /api/meetings/<id>/messages/  # 메시지 목록
POST /api/meetings/<id>/messages/  # 메시지 전송

# 유저
GET  /api/users/me/                # 내 프로필
PATCH /api/users/me/               # 닉네임 수정
GET  /api/users/<id>/history/      # 매칭 이력

# 신고
POST /api/reports/                 # 신고 접수

# 관리자
GET  /admin/                       # Django Admin 대시보드
```

---

## 10. 실행 방법

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env에 GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET 입력

# 2. 빌드 및 실행
docker-compose up --build

# 3. DB 마이그레이션
docker-compose exec web python manage.py migrate

# 4. 정적 파일 수집
docker-compose exec web python manage.py collectstatic --noinput

# 5. 접속
# http://localhost
```

---

## 11. 익명성 보장 설계 원칙

| 레이어 | 처리 방식 |
|---|---|
| **서버 DB** | Google 이메일/ID 저장 (재매칭, 밴 처리용) |
| **API 응답** | 닉네임 + 매너온도만 노출, 이메일 절대 미포함 |
| **채팅 필터** | 전화번호/이메일 패턴 감지 시 메시지 차단 |
| **매칭 이력** | user_id 기반 저장, 화면엔 닉네임만 표시 |

> 결론: **서버 기준 실명 / 유저 간 익명** — 당근마켓과 동일한 구조

---

## 12. 프론트엔드 디자인 스펙

> 최종 결과물 구현 시 아래 스펙을 반드시 반영할 것

### 스타일 방향
- **레퍼런스**: Linear, Notion 스타일의 세련된 스타트업 랜딩 페이지
- **테마**: 다크 배경 기반, 깔끔한 레이아웃

### 색상
| 역할 | 값 | 용도 |
|---|---|---|
| 메인 컬러 | `#4F46E5` (Indigo) | 버튼, 강조, 포인트 |
| 포인트 컬러 | `#06B6D4` (Cyan) | 보조 강조, 아이콘 |
| 배경 | `#0A0A0F` | 페이지 배경 |
| 서피스 | `#111118` | 카드 배경 |
| 보더 | `rgba(255,255,255,0.07)` | 카드 테두리 |

### 폰트
```css
font-family: 'Pretendard', 'Noto Sans KR', -apple-system, sans-serif;
```
- Pretendard 우선 적용, 없으면 Noto Sans KR 폴백
- 제목: `font-weight: 900`, `letter-spacing: -0.03em`
- 본문: `font-weight: 400~500`, `line-height: 1.6`

### CSS 프레임워크
- **Tailwind CSS** (CDN 또는 빌드 모두 허용)
- 커스텀 CSS는 CSS 변수로 관리

### 반응형
- 모바일 기준점: `768px` (md 브레이크포인트)
- 히어로 타이틀: `clamp(2.5rem, 6vw, 4.5rem)` 유동 크기
- 그리드: 모바일 1열 → 데스크탑 2~3열

### 인터랙션
| 요소 | 효과 |
|---|---|
| 페이지 진입 | `fadeInUp` 순차 애니메이션 (stagger 0.15s) |
| 스크롤 | `IntersectionObserver` 기반 reveal (opacity + translateY) |
| 기능 카드 hover | `translateY(-4px)` + 보더 컬러 전환 |
| CTA 버튼 hover | `translateY(-2px)` + 글로우 강화 |
| 기술 스택 아이템 hover | 보더 컬러 → 해당 기술 테마 컬러 |

### 페이지 섹션 구성 순서
1. **Navigation** — 고정 상단바, backdrop-blur
2. **Hero** — 배지 + 메인 카피 + CTA 버튼 + 통계
3. **핵심 기능** — 6개 카드 그리드
4. **사용 방법** — 3단계 스텝
5. **기술 스택** — 스택 목록 + 아키텍처 흐름도
6. **릴리즈 로드맵** — Release 1~3 타임라인
7. **Footer**

### 배경 장식 요소
- 그리드 패턴: `rgba(79,70,229,0.04)` 선, `60px` 간격
- 글로우 오브: `radial-gradient` + `filter: blur(60px)`
- 노이즈 텍스처: SVG feTurbulence 오버레이 (opacity 0.4)
- 섹션 구분: 그라디언트 `<hr>` (`transparent → rgba(255,255,255,0.08) → transparent`)

---

## 13. Claude Code 구현 지시사항

> 이 가이드를 Claude Code에게 전달할 때 반드시 읽혀야 할 섹션

### 환경변수
- API 키, 시크릿 값은 **절대 하드코딩 금지**
- 모든 민감 값은 `.env.example`로 대체해서 작성할 것
- 실제 `.env` 파일은 `.gitignore`에 반드시 포함

```
# .env.example
SECRET_KEY=your-django-secret-key
DATABASE_URL=postgres://meetu_user:meetu_pass@db:5432/meetu
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
KAKAO_MAP_API_KEY=your-kakao-map-api-key
```

### 채팅 구현 방식
- **Long Polling** 으로 구현 (Django Channels, WebSocket 사용 안 함)
- 복잡도를 낮추고 Release 1 완성에 집중

### 프론트엔드 방식
- **Django Template** 기반으로 구현 (React, Vue 사용 안 함)
- 모든 HTML 파일은 `backend/templates/` 폴더에 위치
- 정적 파일(CSS, JS)은 `frontend/static/` 에 위치
- Tailwind CSS는 CDN으로 불러올 것

### 구현 우선순위
- **Release 1만 완성 코드로 작성**
- Release 2, 3 해당 위치에는 아래 형식으로 TODO 주석 표시

```python
# TODO [Release 2]: Kakao Maps API 위치 마킹 구현
# TODO [Release 3]: 매너온도 평가 시스템 구현
```

### 디렉토리 생성 규칙
- 가이드의 섹션 3 디렉토리 구조를 그대로 따를 것
- 임의로 폴더/파일 추가하지 말 것

### 완성 기준 체크리스트 (Release 1)
- [ ] `docker-compose up --build` 후 `http://localhost` 접속 가능
- [ ] Google OAuth 로그인 → 닉네임 설정 → 대시보드 이동
- [ ] 모임 생성 (카테고리 선택형, 텍스트 입력 필드 없음)
- [ ] 모임 목록 조회 + 카테고리 필터
- [ ] 섹션 12 디자인 스펙 (다크테마, Indigo/Cyan 컬러, Pretendard 폰트) 반영

---

## 14. 주요 의존성

```
# requirements.txt
Django>=4.2
psycopg2-binary       # PostgreSQL 드라이버
django-allauth        # Google OAuth
djangorestframework   # REST API
gunicorn              # WSGI 서버
django-environ        # 환경변수 관리
channels              # WebSocket (채팅 Release 2용, 선택)
```
