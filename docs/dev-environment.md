# 개발환경 가이드

로컬 개발환경 구성, 실행 방법, 자주 나온 질문 정리.

---

## 1. 구성 요약

Docker Compose 하나로 4개 서비스를 띄운다.

| 서비스 | 기술 | 포트 | 비고 |
|---|---|---|---|
| `db` | PostgreSQL 16 + pgvector | 5432 | 최초 기동 시 `vector` 확장 자동 설치 |
| `backend` | Python 3.12, FastAPI | 8000 | 코드 수정 시 자동 재시작 (`--reload`) |
| `ai` | Python 3.12, FastAPI, LangChain 1.x | 8001 | RAG·멀티모달 담당. 구조는 backend와 동일. 백엔드는 `AI_BASE_URL`(`http://ai:8001`)로 호출 |
| `frontend` | React 19, TypeScript, Vite | 5173 | 코드 수정 시 화면 자동 반영, `/api/*` → 백엔드 프록시 |

사전 준비물: **Docker Desktop만** 있으면 된다. 로컬에 Python·Node·PostgreSQL을 따로 설치할 필요 없음.

---

## 2. 실행 방법

### 처음 한 번

```bash
docker compose up --build
```

`.env` 없이도 기본값으로 뜬다. API 키가 필요할 때만 레포 루트에 `.env`를 직접 만든다.

### `.env` (선택)

`.env`와 `.env.example`은 모두 레포에 올리지 않는다. 필요한 변수만 골라 루트에 `.env`로 작성한다.

```bash
# DB (로컬 개발용 기본값과 같음)
POSTGRES_USER=odor
POSTGRES_PASSWORD=odor
POSTGRES_DB=odor

# 호스트 포트 (충돌 시 변경)
DB_PORT=5432
BACKEND_PORT=8000
AI_PORT=8001
FRONTEND_PORT=5173

APP_ENV=local

# 외부 API 키 — 발급·보관 방법은 '4. 주의사항 > API 키 관리' 참고
AIRKOREA_API_KEY=
LLM_API_KEY=
```

### 동작 확인

| 확인 항목 | 주소 / 명령 | 기대 결과 |
|---|---|---|
| 백엔드 헬스체크 | http://localhost:8000/health | `{"status":"ok","db":{"status":"ok","pgvector":"0.8.x"}}` |
| API 문서 (Swagger) | http://localhost:8000/docs | FastAPI 자동 문서 |
| AI 헬스체크 | http://localhost:8001/health | 백엔드와 같은 형식 |
| AI API 문서 | http://localhost:8001/docs | FastAPI 자동 문서 |
| 프론트엔드 | http://localhost:5173 | 헬스체크 결과가 화면에 표시됨 |
| 백엔드 테스트 | `docker compose exec backend pytest -q` | 전부 passed |
| AI 테스트 | `docker compose exec ai pytest -q` | 전부 passed |
| 프론트 타입 검사 | `docker compose exec frontend npx tsc --noEmit` | 에러 없음 |

### 자주 쓰는 명령

| 하고 싶은 것 | 명령 |
|---|---|
| 백그라운드 실행 | `docker compose up -d` |
| 로그 보기 | `docker compose logs -f backend` |
| 종료 | `docker compose down` |
| DB까지 완전 초기화 | `docker compose down -v` (DB 데이터 삭제됨, 주의) |
| DB 접속 | `docker compose exec db psql -U odor -d odor` |
| 백엔드·AI 라이브러리 추가 | `backend/requirements.txt` 또는 `ai/requirements.txt`에 추가 → `docker compose up --build` |
| 프론트 라이브러리 추가 | `docker compose exec frontend npm install <패키지명>` |

### 프론트엔드 패키지 동기화

프론트엔드는 컨테이너 시작 시 `npm ci`를 실행하여
`node_modules` 볼륨을 `package-lock.json`과 동기화합니다.

팀원이 추가·변경한 패키지를 Git으로 받아온 뒤에는 다음 명령으로 다시 실행합니다.

```bash
docker compose up -d --build frontend
```

설치가 끝난 뒤 Vite가 시작되므로 잠시 기다려주세요.
별도 Compose 프로젝트명을 사용 중이라면 명령에 동일한 `-p 프로젝트명`을 붙입니다.

---

## 3. 폴더 구조

```
.
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── api/health.py   # /health
│   │   └── core/config.py  # 환경변수 설정
│   ├── db/init/            # DB 최초 기동 시 실행되는 SQL
│   ├── samples/            # 실제 API 응답 원본 (키 제거)
│   ├── mocks/              # 개발 테스트 전용 목업
│   └── tests/
├── ai/                     # RAG·멀티모달 (backend와 같은 구조)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── api/health.py   # /health
│   │   └── core/config.py  # 환경변수 설정
│   └── tests/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts      # /api 프록시 설정
│   └── src/
└── docs/
```

---

## 4. 주의사항

- **`.env`, `.env.example`은 커밋하지 않는다.** API 키는 `.env`에만 넣는다. `AIRKOREA_API_KEY`는 backend에만, `LLM_API_KEY`는 ai에만 전달된다. `.gitignore`에 등록되어 있음.
- **Compose 프로젝트명은 `odor-chatbot`으로 고정되어 있다.** 레포를 다른 이름(특히 한글) 폴더에 클론해도 컨테이너·볼륨 이름이 같고, 빈 프로젝트명 오류도 나지 않는다.
- **`backend/db/init/*.sql`은 DB 볼륨이 비어 있을 때 1회만 실행된다.** SQL을 수정했으면 `docker compose down -v` 후 다시 올려야 반영된다.
- **포트는 `127.0.0.1`에만 열려 있다.** 내 컴퓨터에서만 접속되고, 같은 네트워크의 다른 기기에서는 DB·API에 접속할 수 없다. DB 기본 비밀번호가 공개값(`odor`)이라 일부러 막아 둔 것이니 `0.0.0.0`으로 바꾸지 않는다.
- **포트 충돌 시** `.env`의 `DB_PORT`, `BACKEND_PORT`, `AI_PORT`, `FRONTEND_PORT`를 바꾼다.
- **macOS에서 프론트 파일 변경이 반영 안 되면** `docker-compose.yml`의 frontend 환경변수에 `USE_POLLING: "true"` 추가.

### API 키 관리

키를 카톡·슬랙·디스코드 같은 **팀 채팅방에 올리지 않는다.** 대화 기록에 영구히 남고, 검색되고, 나중에 들어온 사람도 볼 수 있다.

| 키 | 받는 방법 |
|---|---|
| `AIRKOREA_API_KEY` | **각자 발급.** 공공데이터포털(data.go.kr)에서 에어코리아 API를 개인 계정으로 활용신청한다. 무료이고 공유할 필요가 없다. |
| `LLM_API_KEY` | **공유 금고로 전달.** Bitwarden·1Password 같은 비밀번호 관리자의 팀 공유 기능을 쓴다. 회사에서 키를 제공하면 회사 안내를 따른다. |

부득이하게 채팅으로 보냈다면:
- 받은 사람이 `.env`에 옮긴 즉시 메시지를 삭제한다.
- LLM 제공사 콘솔에서 **사용 한도(spending limit)** 를 걸어 둔다. 새어 나가도 피해가 제한된다.
- 키가 새어 나간 게 의심되면 바로 폐기하고 재발급한다.

### 보안 규칙

- **API 키는 루트 `.env`에만.** 서비스 폴더(`backend/.env` 등)에 만들어도 `.dockerignore`로 이미지에는 안 들어가지만, 혼동을 막기 위해 루트 하나만 쓴다.
- **프론트엔드 환경변수에 `VITE_` 접두사를 함부로 쓰지 않는다.** Vite는 `VITE_`로 시작하는 변수를 브라우저 번들에 그대로 넣는다. 키·비밀번호는 절대 `VITE_`로 만들지 않는다. dev 서버 설정용 변수는 `PROXY_TARGET`처럼 접두사 없이 쓴다.
- **`backend/samples/` 커밋 전 `serviceKey` 확인.** 공공데이터포털 API는 키를 URL에 담는다. 자세한 규칙은 `backend/samples/README.md`.
- **`DATABASE_URL`은 필수값.** `config.py`에 기본값이 없어 누락 시 바로 에러가 난다. 에러 메시지에는 다른 설정값이 찍히지 않는다. 단, compose로 실행하면 compose가 기본 비밀번호로 값을 채워 넘기므로 이 검사는 compose 없이 직접 실행할 때만 동작한다.
- **DB 기본 비밀번호(`odor`)는 로컬 전용.** 이 compose 파일은 개발용이다. 서버 배포 시에는 배포용 compose를 따로 만들고 비밀번호를 필수값(`${POSTGRES_PASSWORD:?}`)으로 바꾼다.

### 비밀값 검사 (수동)

API 키가 섞이지 않았는지 gitleaks로 검사한다. 레포 루트에서 실행한다. `git` 모드는 커밋된 이력만 보므로, 커밋 전에는 `--staged`를 붙여 `git add` 한 파일을 검사한다.

```bash
# 커밋 전: git add 한 파일 검사
docker run --rm -v "$PWD:/repo" ghcr.io/gitleaks/gitleaks:v8.30.1 git /repo --staged --config /repo/.gitleaks.toml --redact

# 푸시 전: 커밋 이력 전체 검사
docker run --rm -v "$PWD:/repo" ghcr.io/gitleaks/gitleaks:v8.30.1 git /repo --config /repo/.gitleaks.toml --redact
```

`no leaks found`가 나오면 정상이다.

---

## 5. FAQ

### Q1. pgvector와 ChromaDB는 역할이 같은가?

**역할은 같다.** 둘 다 임베딩 벡터를 저장하고 질문과 가장 비슷한 청크를 찾아주는 벡터 저장소다. 차이는 어디에 붙어 있느냐다.

| | pgvector | ChromaDB |
|---|---|---|
| 정체 | PostgreSQL 확장 기능 | 벡터 검색 전용 별도 DB |
| 데이터 위치 | 일반 테이블과 같은 DB | 따로 보관 |
| 조회 방법 | SQL로 벡터 검색 + 조건 필터를 한 번에 | Python API + 메타데이터 필터 |
| 장점 | DB 하나라 관리 단순, 조인·트랜잭션 가능 | 설치·사용이 쉬워 실험이 빠름 |
| 단점 | SQL·인덱스 설정을 직접 해야 함 | 다른 데이터와 따로 놀아 동기화 부담 |

**이 프로젝트는 pgvector를 기본으로 한다.**

- **한곳에서 필터링:** 근거 메타데이터(기관, 조문, 시행일, 기준시점, 이용조건)를 벡터와 같은 곳에 두고 바로 거를 수 있다. 예: "현재 시행 중인 조문만" 검색이 SQL 한 줄.
- **DB 하나로 끝:** API 캐시, 측정값, 평가 기록도 어차피 PostgreSQL에 들어간다.
- **이미 설치됨:** 추가 작업이 없다.

RAG 실험 단계(청크 분할, 임베딩 모델 비교)에서 Chroma를 잠깐 쓰는 건 괜찮다. 단, 검색 결과는 반드시 `RetrievalResult` 형식으로 돌려주는 인터페이스 뒤에 둬서 나중에 교체해도 다른 모듈이 영향을 받지 않게 한다.

> ⚠️ **한국어 키워드 검색은 별도로 챙겨야 한다.** 법령 검색은 "제8조" 같은 정확한 용어 대응을 위해 벡터 + BM25 하이브리드 검색이 권장되는데, PostgreSQL 기본 전문검색에는 한국어 형태소 분석기가 없다. 선택지:
> - DB 확장 추가 (`pg_bigm`, `pg_trgm`)
> - Python에서 형태소 분석기(예: kiwi) + BM25 라이브러리로 키워드 점수를 따로 계산

### Q2. Gradle 세팅이 필요한가?

**필요 없다.** Gradle은 Java/Kotlin 프로젝트(Spring Boot, 안드로이드 앱)의 빌드·의존성 관리 도구다. 이 프로젝트 스택에는 Java가 없다.

Gradle 역할을 하는 도구는 영역별로 이미 들어가 있다.

| 영역 | 언어 | 의존성 관리 | 파일 |
|---|---|---|---|
| 백엔드 | Python (FastAPI) | pip | `backend/requirements.txt` |
| 프론트엔드 | TypeScript (React) | npm | `frontend/package.json`, `package-lock.json` |
| 실행 환경 전체 | — | Docker Compose | `docker-compose.yml` |

Gradle이 필요해지는 경우는 다음뿐이며, 현재 계획서 기준으로는 모두 해당 없음.

- 백엔드를 Spring으로 바꾸기로 한 경우
- 안드로이드 네이티브 앱을 따로 만드는 경우 (키오스크 연동은 MVP 범위 밖)
- 기업 멘토 측에서 Java 기반을 요구하는 경우
