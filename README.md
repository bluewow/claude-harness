# Claude Code Workflow Kit

Claude Code의 슬래시 커맨드, 훅, 대시보드를 조합한 **기획→개발 자동화 워크플로우**입니다.

---

## 전체 흐름

```
  사용자                  Claude Code                    산출물
  ━━━━━━                  ━━━━━━━━━━                    ━━━━━━

  ┌──────────────────── 메인 워크플로우 ────────────────────┐
  │                                                         │
  │  /pm "로그인 만들자"                                     │
  │       │                                                 │
  │       ▼                                                 │
  │  ┌──────────┐  Q&A   ┌──────────┐  자동   ┌─────────┐  │
  │  │  유형    │──────→ │  기획    │──────→ │ 산출물  │  │
  │  │  감지    │  대화형 │  구체화  │  생성   │ 저장    │  │
  │  └──────────┘        └──────────┘        └────┬────┘  │
  │    idea/design         승인 요청               │       │
  │                                                ▼       │
  │                          idea.html / design.html       │
  │                          brief.md                      │
  │                                                         │
  │  /dev 008-로그인                                        │
  │       │                                                 │
  │       ▼                                                 │
  │  ┌──────────┐  분석   ┌──────────┐  검증   ┌─────────┐ │
  │  │ brief.md │──────→ │  구현    │──────→ │ 에러    │ │
  │  │ 읽기     │  백그라 │  코드    │  자동   │ 체크    │ │
  │  └──────────┘  운드   └──────────┘        └────┬────┘ │
  │                                                │       │
  │                                    complete.md ▼       │
  └────────────────────────────────────────────────────────┘

  ┌──────────────────── 빠른 위임 ─────────────────────────┐
  │                                                         │
  │  /do "버그 수정해줘"                                     │
  │       │                                                 │
  │       ▼                                                 │
  │  분석 → 구현 → 에러체크 → complete.md   (기획 생략)     │
  │                                                         │
  └─────────────────────────────────────────────────────────┘
```

---

## 커맨드 요약

### 워크플로우 커맨드

| 커맨드 | 용도 | 실행 방식 | 입력 | 산출물 |
|--------|------|-----------|------|--------|
| `/init` | 프로젝트 스캔 → CLAUDE.md 생성 | Foreground | — | CLAUDE.md |
| `/pm` | 기획 + 디자인 Q&A | Foreground (대화형) | 자연어 요청 | idea/design.html + brief.md |
| `/dev` | brief.md 기반 구현 | **Background** | 태스크 ID | complete.md |
| `/do` | 간단한 작업 직접 위임 | **Background** | 자연어 설명 | complete.md |

### 프로젝트 세팅 커맨드

| 커맨드 | 용도 | 실행 방식 | 입력 | 산출물 |
|--------|------|-----------|------|--------|
| `/create-nextjs` | Next.js 프로젝트 초기 세팅 | Foreground | 프로젝트명 | 전체 프로젝트 구조 + CLAUDE.md |
| `/check-nextjs` | Next.js 프로젝트 설정 검사 | Foreground | `--fix` / `--report` | 검사 리포트 (+ 자동 수정) |
| `/onepager` | 사업계획서/원페이저 생성 | Foreground | 주제 또는 프로젝트명 | onepager HTML |

---

## 디렉토리 구조

```
.claude/
├── commands/                        ← 슬래시 커맨드 정의
│   ├── init.md                        /init
│   ├── pm.md                          /pm
│   ├── dev.md                         /dev
│   ├── do.md                          /do
│   ├── create-nextjs.md               /create-nextjs
│   ├── check-nextjs.md                /check-nextjs
│   └── onepager.md                    /onepager
│
├── hooks/
│   └── slack-notify.js              ← Slack 알림 훅
│
├── templates/
│   ├── idea-template.html           ← /pm 신규 기능 템플릿
│   ├── design-template.html         ← /pm 개선 디자인 템플릿
│   ├── dashboard-template.html      ← /init 시 output/에 복사되는 대시보드
│   └── onepager-template.html       ← /onepager 사업계획서 템플릿
│
├── skills/                          ← 자동 활성화 스킬
│   ├── design-inspiration/            UI 작업 시 디자인 일관성 유지
│   │   ├── SKILL.md
│   │   ├── images/                    인스피레이션 이미지
│   │   └── references/                DESIGN.md (프로젝트별 자동 생성)
│   └── image-to-html/                 /image-to-html (이미지 → HTML/CSS)
│       ├── SKILL.md
│       ├── crop_sections.py
│       ├── images/
│       └── references/
│
├── settings.json                    ← 공유 설정 (permissions, hooks)
├── settings.local.json              ← 로컬 설정 (git 제외)
├── .gitignore
└── README.md
```

> 이 `.claude/` 디렉토리는 프로젝트에 불러온 **Claude Code 세팅 환경**입니다.
> 슬래시 커맨드 실행 시 산출물은 프로젝트 루트의 `output/` 폴더에 생성됩니다 (`/init` 실행 시 자동 생성).

### history.json 스키마

```jsonc
{
  "id": "001-대시보드-개선",       // 3자리 숫자 + slug
  "slug": "대시보드-개선",
  "name": "대시보드 개선",
  "path": "output/tasks/001-대시보드-개선",
  "artifacts": [                    // ← 대시보드가 이 필드로 산출물 렌더링 (HTTP 요청 없음)
    "design.html",                  //    파일명만 기록, 경로는 path에서 조합
    "brief.md",
    "complete.md"
  ],
  "logs": [
    { "phase": "디자인", "status": "완료", "date": "2026-03-13", "note": "..." },
    { "phase": "개발",   "status": "완료", "date": "2026-03-13", "note": "..." }
  ]
}
```

---

## 태스크 라이프사이클

```
  상태           배지 색상       의미
  ━━━━           ━━━━━━━        ━━━━

  진행중         🟣 보라        /pm 또는 /dev 가 작업 중
      │
      ▼
  승인대기       🟠 주황        /pm 완료, /dev 실행 대기
      │                        → 대시보드에서 "/dev [ID]" 복사 버튼 제공
      ▼
  완료           🟢 초록        /dev 구현 + 에러체크 완료
      │
      ─── 또는 ──→ 폐기  ⚪ 회색   사용자가 폐기 처리
```

---

## 설정

### settings.json (공유, git 포함)

```jsonc
{
  "permissions": {
    "allow": ["Read", "Edit", "Write", "Glob", "Grep", "Bash(*)", ...],
    "deny":  ["Bash(rm -rf /)", "Write(.env)", "Write(*.pem)"]
  },
  "hooks": {
    "Stop":        [{ "command": "node .claude/hooks/slack-notify.js" }],
    "Notification":[{ "command": "node .claude/hooks/slack-notify.js" }],
    "PreToolUse":  [{ "matcher": "AskUserQuestion", "command": "..." }]
  }
}
```

### settings.local.json (로컬 전용, git 제외)

```jsonc
{
  "env": {
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/..."
  }
}
```

---

## Slack 알림

`slack-notify.js`가 3가지 이벤트에 반응합니다:

| 이벤트 | 트리거 | Slack 메시지 |
|--------|--------|-------------|
| **Stop** | 에이전트 작업 완료 | :white_check_mark: 마지막 메시지 요약 |
| **Notification** | 알림 발생 | :bell: 알림 내용 |
| **AskUserQuestion** | 에이전트가 질문 | :raising_hand: 질문 + 선택지 |

설정 방법:
1. Slack에서 Incoming Webhook URL 생성
2. `.claude/settings.local.json`의 `SLACK_WEBHOOK_URL`에 입력

---

## 대시보드

`output/dashboard.html`을 브라우저에서 열면 태스크 현황을 확인할 수 있습니다.

- `output/history.json`을 로컬에서 읽어 렌더링 (서버 불필요)
- 상태별 필터, 검색, 다크모드 지원
- 산출물 파일 직접 열기 (다중 파일 지원)
- 승인대기 태스크에 `/dev` 복사 버튼 제공
- 가이드 팝업: 워크플로우 / 커맨드 / 산출물 3탭

---

## 빠른 시작

```bash
# 1. 프로젝트 초기화
/init

# 2. 기능 기획
/pm 로그인 페이지 만들자

# 3. 승인 후 구현
/dev 008-로그인

# 4. 또는 간단한 작업 바로 위임
/do 헤더 로고 크기 수정
```

---

## 언제 어떤 커맨드?

```
"새 기능을 기획부터"        →  /pm  →  승인  →  /dev
"기획서 있고 구현만"        →  /dev [태스크ID]
"버그/간단한 수정"          →  /do [설명]
"프로젝트 설정 초기화"      →  /init
"사업계획서 만들기"         →  /onepager [주제]
```

### Next.js 프로젝트 세팅

```
"새 Next.js 프로젝트"      →  /create-nextjs [프로젝트명]
"설정 잘 됐나 확인"        →  /check-nextjs --report
"누락된 설정 자동 수정"    →  /check-nextjs --fix
```

#### `/create-nextjs` 상세

```bash
/create-nextjs my-app
```

14단계로 프로덕션-레디 Next.js 프로젝트를 생성합니다:
- Next.js 최신 안정 버전 (WebSearch로 확인)
- shadcn/ui (base-nova) + Tailwind CSS 4
- Zustand + TanStack Query (상태관리)
- VAC 패턴 폴더 구조 (View-Action-Container)
- Pretendard 폰트 (한글 최적화)
- Global CSS 테마 시스템 (변수 변경 → 전체 반영)
- 404, error, loading 페이지
- ESLint + Prettier + TypeScript strict
- 환경변수 구조 (.env.example / .env.local)
- CLAUDE.md 자동 생성
- 빌드 검증까지 완료

#### `/check-nextjs` 상세

```bash
/check-nextjs           # 검사 + 자동 수정 (기본)
/check-nextjs --report  # 리포트만, 수정 안 함
/check-nextjs --fix     # 검사 + 자동 수정 (명시적)
```

`/create-nextjs` 기준 10개 항목을 PASS / WARN / FAIL로 검사합니다:

| # | 검사 항목 | 확인 내용 |
|---|----------|----------|
| 1 | 프로젝트 기본 구조 | package.json, next, src/app, tsconfig strict |
| 2 | 의존성 | zustand, react-query, tailwind, prettier 등 |
| 3 | 스크립트 | dev, build, lint, format, typecheck |
| 4 | 폴더 구조 (VAC) | components/ui, features, stores, providers 등 |
| 5 | 핵심 파일 | not-found, error, loading, utils.ts |
| 6 | Global CSS 테마 | :root, .dark, CSS 변수, 테마 주석 |
| 7 | 폰트 설정 | 로컬 폰트, lang="ko" |
| 8 | Provider 구조 | QueryProvider + layout 연결 |
| 9 | 설정 파일 | prettierrc, gitignore, env, CLAUDE.md |
| 10 | 빌드 검증 | `pnpm build` 성공 여부 |

`--fix` 모드: 누락 폴더/설정 파일 자동 생성, 빌드 에러 최대 3회 수정 시도 (비즈니스 코드는 수정 안 함)
