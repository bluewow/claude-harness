---
description: 프로젝트 스캔 → CLAUDE.md 자동 생성/업데이트
---

당신은 프로젝트 분석 전문가입니다. 기존 프로젝트를 스캔하고 CLAUDE.md를 생성합니다.

**CLAUDE.md는 이 프로젝트의 모든 에이전트(/dev, /do, /pm 등)가 참조하는 유일한 프로젝트 문서입니다.**
**에이전트가 코드를 이해하고, 컨벤션을 지키고, 빌드/테스트를 실행하는 데 필요한 모든 정보를 담아야 합니다.**

---

## Step 1: 프로젝트 스캔

루트 및 1~2depth 서브 디렉토리에서 빌드/설정 파일을 탐색합니다:

| 파일 | 기술 스택 |
|:-----|:---------|
| package.json | Node.js (React, Vue, Next.js, Nuxt, Express 등) |
| pom.xml | Java (Spring Boot, Maven) |
| build.gradle(.kts) | Java/Kotlin (Spring Boot, Gradle) |
| requirements.txt / pyproject.toml | Python (Django, FastAPI, Flask 등) |
| go.mod | Go |
| Cargo.toml | Rust |
| composer.json | PHP (Laravel 등) |
| Gemfile | Ruby (Rails 등) |

- 빌드 파일이 하나도 없으면 "프로젝트 파일을 찾을 수 없습니다." 안내 후 중단
- **여러 프로젝트가 감지되면** 각 프로젝트를 개별 분석한 뒤, 하나의 CLAUDE.md에 통합

## Step 2: 구조 및 코드 심층 분석

각 프로젝트(또는 단일 프로젝트)에 대해 **충분히 깊이** 분석합니다:

### 2-1. 디렉토리 구조
- 1~3 depth 폴더 구조 스캔
- 아키텍처 패턴 감지 (MVC, Clean Architecture, Feature-based, Layered 등)
- 각 폴더의 역할 파악

### 2-2. 코드 컨벤션 (최소 10~15개 파일 읽기)
- **네이밍**: 파일명(PascalCase, kebab-case), 변수/함수(camelCase, snake_case), 클래스/인터페이스
- **파일 구조**: 컴포넌트 파일 내부 구성 순서 (imports → types → component → styles → export)
- **상태 관리**: 사용 라이브러리, 패턴 (store, context, hooks 등)
- **API 패턴**: 엔드포인트 구조, 요청/응답 형식, 에러 처리
- **타입 시스템**: TypeScript strict mode 여부, 타입 정의 위치 및 패턴

### 2-3. 스타일 시스템 (프론트엔드인 경우)
- CSS 프레임워크 (Tailwind, styled-components, CSS Modules 등)
- 디자인 토큰 위치 (tailwind.config, theme 파일, CSS variables)
- **핵심 색상 팔레트**: primary, secondary, background, text, accent 등 실제 HEX 값 추출
- **타이포그래피**: 폰트 패밀리, 주요 사이즈/웨이트
- **레이아웃 규칙**: 간격 체계, 반응형 브레이크포인트, 그리드 시스템
- **컴포넌트 스타일 패턴**: 공통 컴포넌트의 스타일링 방식

### 2-4. 빌드 & 개발 환경
- 패키지 매니저 (npm, yarn, pnpm, bun 등)
- 빌드 명령어, 개발 서버 명령어
- 린트/포맷 명령어 및 설정
- 테스트 프레임워크 및 실행 명령어
- 정적 분석 도구 (TypeScript, ESLint 규칙 등)

### 2-5. 의존성 & 라이브러리
- 핵심 의존성 목록 (프레임워크, UI 라이브러리, 상태관리, HTTP 클라이언트 등)
- 내부 유틸/헬퍼 위치

## Step 3: CLAUDE.md 생성

→ **CLAUDE.md 생성 규칙** 섹션 참조.

---

## CLAUDE.md 생성 규칙

### 핵심 원칙

CLAUDE.md는 **에이전트의 작업 매뉴얼**입니다. 다음 질문에 답할 수 있어야 합니다:
1. 이 프로젝트는 어떤 기술 스택인가? → `Tech Stack`
2. 코드가 어디에 있고 어떤 구조인가? → `Project Structure`
3. 코드를 어떤 패턴으로 작성해야 하는가? → `Patterns & Conventions`
4. 스타일/디자인은 어떻게 적용하는가? → `Style Guide`
5. 빌드/테스트/린트는 어떻게 실행하는가? → `Dev Commands`
6. 주요 라이브러리/유틸은 무엇이 있는가? → `Key Dependencies`

### 단일 프로젝트 템플릿

```markdown
# [프로젝트명]

## Tech Stack
- **Runtime**: [Node.js 20 / Python 3.12 / Java 21 / ...]
- **Framework**: [Next.js 14 / FastAPI / Spring Boot 3 / ...]
- **Language**: [TypeScript (strict) / Python / Java / ...]
- **Styling**: [Tailwind CSS 3.x / styled-components / ...]
- **Database**: [PostgreSQL / MongoDB / SQLite / ...]
- **ORM/ODM**: [Prisma / TypeORM / SQLAlchemy / ...]
- **State Management**: [Zustand / Redux Toolkit / React Context / ...]
- **Package Manager**: [pnpm / npm / yarn / ...]

## Project Structure
[1~3 depth 디렉토리 트리 + 각 폴더 역할 한줄 설명]
[아키텍처 패턴: MVC / Clean Architecture / Feature-based 등]

## Patterns & Conventions

### Naming
| 대상 | 규칙 | 예시 |
|:-----|:-----|:-----|
| 파일명 (컴포넌트) | [PascalCase/kebab-case] | [Button.tsx / button.tsx] |
| 파일명 (유틸) | [camelCase/kebab-case] | [formatDate.ts / format-date.ts] |
| 폴더명 | [kebab-case/camelCase] | [user-profile / userProfile] |
| 변수/함수 | [camelCase/snake_case] | [getUserName / get_user_name] |
| 상수 | [UPPER_SNAKE_CASE] | [API_BASE_URL] |
| 타입/인터페이스 | [PascalCase] | [UserProfile, IUserService] |

### File Organization
[컴포넌트 파일 내부 구성 순서]
[import 정렬 규칙]
[export 패턴 (default vs named)]

### Component Pattern (프론트엔드)
[컴포넌트 작성 패턴 — 함수형/클래스, props 타입 정의 방식]
[상태 관리 접근 패턴]
[이벤트 핸들러 네이밍]

### API Pattern (백엔드)
[엔드포인트 구조: RESTful / GraphQL]
[라우트 구성 패턴]
[에러 처리 패턴]
[요청 검증 방식]

### Error Handling
[에러 처리 전략 — try/catch, Error boundary, global handler]
[에러 타입 정의 방식]

### Testing
[테스트 파일 위치 (__tests__/, *.test.ts, *.spec.ts)]
[테스트 패턴 — unit, integration, e2e]
[테스트 네이밍 규칙]

## Style Guide
[프론트엔드가 있는 경우에만 작성]

### Design Tokens
- **Token 위치**: [tailwind.config.ts / theme.ts / variables.css / ...]

### Colors
| 이름 | HEX | 용도 |
|:-----|:----|:-----|
| primary | #XXXXXX | 주 액션, 버튼, 링크 |
| secondary | #XXXXXX | 보조 액션 |
| background | #XXXXXX | 페이지 배경 |
| foreground | #XXXXXX | 기본 텍스트 |
| muted | #XXXXXX | 비활성, 보조 텍스트 |
| accent | #XXXXXX | 강조, 성공 |
| destructive | #XXXXXX | 삭제, 에러 |
| border | #XXXXXX | 테두리 |

### Typography
| 용도 | 크기 | 두께 | 행간 |
|:-----|:-----|:-----|:-----|
| heading-1 | [px/rem] | [weight] | [leading] |
| body | [px/rem] | [weight] | [leading] |
| caption | [px/rem] | [weight] | [leading] |

- **Font Family**: [Pretendard / Inter / ...]

### Spacing & Layout
- **기본 간격 단위**: [4px / 8px 기반]
- **브레이크포인트**: [sm: 640px, md: 768px, lg: 1024px, ...]
- **컨테이너 최대 너비**: [max-w-xxx]
- **카드 스타일**: [border-radius, shadow, border]

### Reusable Components
[프로젝트에 이미 존재하는 공통 컴포넌트 목록과 경로]
[사용법 요약 — props가 아닌 "이런 상황에 이 컴포넌트를 쓸 것"]

## Key Dependencies
[핵심 외부 라이브러리와 용도 — 에이전트가 새 코드에서 재사용해야 할 것]
| 라이브러리 | 용도 |
|:-----------|:-----|
| [이름] | [용도] |

## Dev Commands
| 명령 | 설명 |
|:-----|:-----|
| `[명령어]` | 개발 서버 실행 |
| `[명령어]` | 프로덕션 빌드 |
| `[명령어]` | 린트 실행 |
| `[명령어]` | 린트 자동 수정 |
| `[명령어]` | 테스트 실행 |
| `[명령어]` | 타입 체크 |
| `[명령어]` | 정적 분석 (있는 경우) |
```

목표: 80~150줄. 각 섹션은 실제 코드에서 발견된 패턴만 기록.

### 멀티 프로젝트 (같은 폴더에 여러 프로젝트가 있는 경우)

하나의 루트 CLAUDE.md에 모든 프로젝트를 통합합니다.

```markdown
# [전체 프로젝트명]

## Overview
[전체 구성 한줄 요약 — 프론트/백엔드 구분, 통신 방식]

## Projects

### [프로젝트A 폴더명] — [역할]

#### Tech Stack
[기술 스택 — 단일 프로젝트와 동일한 상세 수준]

#### Structure
[핵심 디렉토리 구조]

#### Patterns
[주요 컨벤션 — 네이밍, 파일 구조, API/컴포넌트 패턴]

#### Style Guide
[프론트엔드인 경우만: 색상, 타이포, 레이아웃, 공통 컴포넌트]

#### Commands
[빌드/실행/테스트 명령어]

### [프로젝트B 폴더명] — [역할]
[동일 구조로 작성]

## Shared
[프로젝트 간 공통 타입, API 계약, 공유 유틸 경로]
[프론트-백엔드 데이터 모델 매핑]

## Dev Commands (전체)
| 명령 | 설명 |
|:-----|:-----|
| `[명령어]` | 전체 개발 서버 실행 |
| `[명령어]` | 전체 빌드 |
```

목표: 프로젝트당 30~40줄, 전체 200줄 이내.

---

## Rules

- 감지되지 않는 항목은 추측하지 말 것 — 해당 섹션 자체를 생략
- 코드 수정 금지 (CLAUDE.md 생성만)
- 실제 코드에서 발견된 패턴만 기록
- 코드 예시 블록 사용 금지 — 규칙/경로/패턴명으로 기술
- **Style Guide의 Colors는 반드시 실제 HEX 값을 추출하여 기록** — /pm의 design 유형에서 사용
- **Dev Commands는 반드시 실행 가능한 명령어를 기록** — /dev, /do의 에러 체크에서 사용
- **Reusable Components는 경로와 용도를 기록** — /dev 구현 시 중복 생성 방지
- 기존 CLAUDE.md가 있으면 AskUserQuestion으로 덮어쓸지 확인
- 완료 후 생성된 CLAUDE.md 내용을 요약 출력

## Output

```
프로젝트 스캔 완료

감지된 스택: [기술 스택 요약]
프로젝트 수: [N개]
분석한 파일: [N개]
생성된 파일: CLAUDE.md (루트)

이제 /pm, /dev, /do 명령을 사용할 수 있습니다.
```
