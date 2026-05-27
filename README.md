# Claude Code Workflow Kit

> 🚀 **Claude Code 기획 → 개발 자동화 워크플로우 킷**

---

## 💡 왜 만들었나요?

> "기획서 따로, 코드 따로, 진행상황 공유 따로"
> — 1인 개발자 · 소규모 팀의 **컨텍스트 스위칭 비용** 을 0에 가깝게.

자연어 요청 한 줄에서 **기획 → 코드 → 검증 → 알림** 까지 한 호흡으로 처리합니다.

---

## ⚙️ 핵심 파이프라인

```
/pm "로그인 만들자"   →   brief.md   →   /dev   →   complete.md   →   📢 Slack
   (기획 Q&A)         (명세 잠금)    (백그라운드 코딩)   (빌드 검증)
```

| 단계             | 커맨드                    | 산출물                      | 실행 방식           |
| ---------------- | ------------------------- | --------------------------- | ------------------- |
| 🧭 **기획**      | `/pm [요청]`              | `brief.md`, `*.html` 시안   | Foreground (대화형) |
| 💻 **개발**      | `/dev [태스크ID]`         | 소스 코드 + `complete.md`   | Background          |
| 🩹 **단축 수정** | `/do [작업]`              | `complete.md`               | Background          |
| 🏗️ **초기 세팅** | `/setup:init`, `/setup:create-nextjs` | `CLAUDE.md`, 보일러플레이트 | Foreground          |

---

## 📂 디렉토리 규약

```
.claude/
├── commands/     # 슬래시 커맨드 명세
│   ├── pm.md     #   /pm — 기획 (foreground)
│   ├── dev.md    #   /dev — 개발 (background, /pm 승인 시 자동 실행)
│   ├── do.md     #   /do — 단순 수정 (background)
│   └── setup/    #   /setup:init · create-nextjs · check-nextjs · onepager
├── hooks/        # Stop · Notification 훅 (slack-notify.js)
├── skills/       # 자동 활성화 스킬 (design-system 등)
├── templates/    # idea / design / dashboard / onepager HTML 템플릿
└── settings.json # 권한 · 훅 · 환경변수

output/
├── meta.json     # 프로젝트 정보 (이름·스택·생성일) — 단일/멀티 프로젝트 모두 표현
├── history.json  # 태스크 이력 (모든 명령의 단일 진실 소스)
├── dashboard.html # 3-탭 대시보드 (개요·진행내역·산출물) — 새로고침으로 동기화
└── tasks/        # 태스크별 산출물 격리 (idea.html · design.html · brief.md · complete.md)
```

---

## ✨ 특징

- 🧩 **컨텍스트 격리** — `/pm` 은 별도 Foreground 에이전트로 메인 세션을 더럽히지 않음
- 🔔 **Slack 실시간 통지** — 작업 완료(Stop) · 질문 대기(AskUserQuestion) 자동 알림
- 📐 **표준 산출물** — `brief.md`, `complete.md`, `history.json` 으로 모든 태스크 추적 가능
- 📊 **3-탭 대시보드** — 개요(KPI·즉시처리)·진행내역(활동 스트림)·산출물(카드 갤러리) 통합 뷰
- 🏗️ **단일/멀티 프로젝트** — `meta.json` 의 `projects[]` 배열로 web/api/admin 같은 멀티 구조 지원
- 🛡️ **안전 권한 설정** — `.env`, `*.pem`, `rm -rf /` 등 위험 작업 기본 차단

---

## 📖 자세히 보기

[**기술 문서 및 아키텍처 사양서 →**](https://bluewow.github.io/my-claude/)
