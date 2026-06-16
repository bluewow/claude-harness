# Claude Code Workflow Kit

> 🚀 **Claude Code 기획 → 개발 자동화 워크플로우 킷**

---

## 💡 왜 만들었나요?

> "기획서 따로, 코드 따로, 진행상황 공유 따로"
> — 1인 개발자 · 소규모 팀의 **컨텍스트 스위칭 비용** 을 0에 가깝게.

자연어 요청 한 줄에서 **분류 → (시안) → 구현 → 검증 → 알림** 까지 한 호흡으로 처리합니다.

---

## ⚙️ 핵심 파이프라인

`/task` 하나가 요청을 **plan(시안 먼저)** 과 **do(바로 구현)** 으로 자동 분류합니다.

```
/task "로그인 만들자"
   └─ 분류 ─┬─ plan → 시안 html(.output/plans/) → ✅승인 ─┐
            │                                              ├─ 구현 → 검증 → 📢 Slack
            └─ do ─────────────────────────────────────────┘
```

| 모드            | 트리거                          | 산출물                          | 동작                                  |
| --------------- | ------------------------------- | ------------------------------- | ------------------------------------- |
| 🧭 **plan**     | 새 화면·리디자인·결정 옵션 다수 | `.output/plans/NNN-[slug].html` | idea/design 시안 생성 → 브라우저 오픈 → 승인 게이트 → 구현 |
| ⚡ **do**       | 버그·텍스트·로직·작은 수정      | 코드 변경                       | 시안 없이 바로 구현                   |
| 🔍 **에러 체크** | 두 모드 공통                    | 완료 보고(채팅)                 | `typecheck` · `lint` · `test` (`--build` 시 빌드 추가) |

```
/task <요청> [--mode plan|do] [--build]
```

- `--mode plan|do` — 자동 분류를 건너뛰고 모드 강제
- `--build` — 에러 체크에 프로덕션 빌드 추가 (기본은 typecheck/lint/test 만)

---

## 📂 디렉토리 규약

```
.claude/
├── commands/
│   ├── task.md            #   /task — plan/do 통합 워크플로우
│   └── setup/             #   /setup:init · create-nextjs · check-nextjs · onepager
├── hooks/
│   └── slack-notify.js    # Stop · Notification · PreToolUse(AskUserQuestion) → Slack
├── skills/
│   └── design-system/     # 디자인 토큰 자동 활성화 스킬 (+ references/design.md)
├── templates/             # idea · design · onepager HTML 템플릿
├── settings.json          # 권한(allow/deny) · 훅 · env (팀 공유)
└── settings.local.json    # SLACK_WEBHOOK_URL 등 로컬 비밀 (.gitignore)

.output/
└── plans/
    ├── index.html         # 시안 인덱스 — plan 실행마다 자동 갱신(최근이 위)
    └── NNN-[slug].html    # plan 모드 UI 시안 (idea = 신규 / design = 개선)
```

> `/setup:onepager` 는 `.output/onepager.html` 로 별도 출력합니다.

---

## ✨ 특징

- 🎯 **단일 진입점** — `/task` 하나가 plan/do 를 자동 분류, 애매하면 1회만 질문
- 🧭 **plan 모드 시안 게이트** — idea/design 자동 판정 → html 시안 → 브라우저 자동 오픈 → 승인/수정/폐기 후 구현
- ⚡ **do 모드 직행** — 버그·텍스트·백엔드 로직은 시안 없이 바로 구현
- 🔍 **자동 에러 체크** — 구현 후 `typecheck`·`lint`·`test` 자동 실행, `--build` 로 빌드까지
- 🔔 **Slack 실시간 통지** — 작업 완료(Stop) · 일반 알림(Notification) · 질문 대기(AskUserQuestion) Block Kit 메시지
- 🎨 **design-system 스킬** — 코드의 디자인 토큰(globals.css/tailwind.config/theme)을 단일 진실 소스로, UI 작업 시 자동 활성화
- 🛡️ **안전 권한 설정** — 위험한 `git`(force/reset --hard) · `rm -rf` · `sudo` · `publish` · `.env`/`*.pem`/secret 쓰기 기본 차단

---

## 📖 자세히 보기

로컬 기술 문서: [**index.html**](./index.html) 를 브라우저로 열면 인터랙티브 아키텍처 사양서를 볼 수 있습니다.
