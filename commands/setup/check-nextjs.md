---
description: "Next.js 프로젝트 설정 검사 — create-nextjs 기준으로 누락/오류 체크 후 사용자에게 수정 여부 확인"
argument-hint: "(인자 불필요)"
---

# Check Next.js Project Setup

`/setup:create-nextjs`가 제시하는 프로젝트 설정 기준으로 현재 프로젝트를 검사합니다.
각 항목을 PASS / WARN / FAIL로 판정한 뒤, 발견된 WARN/FAIL 에 대해 사용자에게 수정 여부를 물어봅니다.

---

## 실행 흐름

1. **검사** — 아래 [검사 항목] 10개 영역을 순서대로 검사 (항상 실행)
2. **결과 출력** — 검사 결과 테이블 + WARN/FAIL 상세 표시
3. **수정 여부 확인** — WARN/FAIL이 1개 이상이면 `AskUserQuestion`으로 진행 방식을 묻는다:

   ```
   question: "발견된 항목을 어떻게 처리할까요?"
   options:
     - label: "모두 자동 수정"
       description: "아래 명시된 [수정 동작]을 일괄 수행합니다 (설정 파일만, 비즈니스 코드 불변)"
     - label: "항목별로 선택"
       description: "각 WARN/FAIL 항목마다 수정 여부를 개별 확인"
     - label: "수정 안 함 (리포트만)"
       description: "결과만 확인하고 종료"
   ```

4. **수정 수행** — 선택에 따라 진행:
   - **모두 자동 수정** → 각 검사 영역의 [수정 동작] 을 순차 수행
   - **항목별로 선택** → WARN/FAIL 항목마다 `AskUserQuestion`으로 "이 항목을 수정할까요?" (Yes/No) 확인 후 수행
   - **수정 안 함** → Step 5로 바로 이동
5. **최종 리포트** — 어떤 항목이 수정됐고 어떤 항목이 남았는지 요약 출력

**WARN/FAIL이 0개인 경우**: Step 3~4를 건너뛰고 "모두 통과 ✅" 메시지로 종료.

---

## 검사 항목 (Checklist)

아래 항목을 **순서대로** 검사합니다. 각 항목마다 판정 기준이 명시되어 있습니다.

---

### 1. 프로젝트 기본 구조

| 검사 | PASS 조건 | FAIL 조건 |
|:-----|:----------|:----------|
| `package.json` 존재 | 파일 존재 | 없으면 검사 중단 — "Next.js 프로젝트가 아닙니다" 출력 |
| `next` 의존성 | dependencies에 `next` 존재 | 없으면 검사 중단 |
| `src/` 디렉토리 | `src/app/` 존재 | FAIL |
| `tsconfig.json` | 파일 존재 + `strict: true` | WARN (strict 아니면) |

---

### 2. 의존성 (Dependencies)

package.json의 dependencies / devDependencies를 읽고 확인:

| 패키지 | 위치 | PASS | FAIL |
|:-------|:-----|:-----|:-----|
| `next` | dependencies | 존재 | 없음 |
| `react`, `react-dom` | dependencies | 존재 | 없음 |
| `zustand` | dependencies | 존재 | WARN — "상태관리 라이브러리 없음" |
| `@tanstack/react-query` | dependencies | 존재 | WARN — "서버 상태 관리 없음" |
| `tailwindcss` | devDependencies | 존재 | FAIL |
| `typescript` | devDependencies | 존재 | FAIL |
| `prettier` | devDependencies | 존재 | WARN |
| `eslint` | devDependencies | 존재 | WARN |
| `shadcn` | dependencies | 존재 | WARN — "shadcn/ui 미설치" |

**수정 동작**: FAIL/WARN 패키지를 `pnpm add` / `pnpm add -D`로 설치

---

### 3. 스크립트 (Scripts)

package.json `scripts` 필드 확인:

| 스크립트 | 기대값 포함 | 판정 |
|:---------|:-----------|:-----|
| `dev` | `next dev` | FAIL if 없음 |
| `build` | `next build` | FAIL if 없음 |
| `start` | `next start` | FAIL if 없음 |
| `lint` | `eslint` | WARN if 없음 |
| `lint:fix` | `eslint` + `--fix` | WARN if 없음 |
| `format` | `prettier --write` | WARN if 없음 |
| `format:check` | `prettier --check` | WARN if 없음 |
| `typecheck` | `tsc --noEmit` | WARN if 없음 |

**수정 동작**: 누락된 스크립트를 package.json에 추가

---

### 4. 폴더 구조 (VAC 패턴)

아래 디렉토리 존재 여부 확인:

| 경로 | 역할 | 판정 |
|:-----|:-----|:-----|
| `src/components/ui/` | shadcn/ui 컴포넌트 | FAIL if 없음 |
| `src/components/common/` | 공통 컴포넌트 | WARN if 없음 |
| `src/components/layout/` | 레이아웃 컴포넌트 | WARN if 없음 |
| `src/features/` | 기능별 모듈 (VAC) | WARN if 없음 |
| `src/hooks/` | 전역 훅 | WARN if 없음 |
| `src/lib/` | 유틸리티 | FAIL if 없음 |
| `src/providers/` | Provider | WARN if 없음 |
| `src/stores/` | Zustand 스토어 | WARN if 없음 |
| `src/types/` | 전역 타입 | WARN if 없음 |

**수정 동작**: 누락된 디렉토리를 `mkdir -p`로 생성

---

### 5. 핵심 파일 존재

| 파일 | 판정 |
|:-----|:-----|
| `src/app/layout.tsx` | FAIL if 없음 |
| `src/app/page.tsx` | FAIL if 없음 |
| `src/app/not-found.tsx` | FAIL if 없음 |
| `src/app/error.tsx` | WARN if 없음 |
| `src/app/loading.tsx` | WARN if 없음 |
| `src/app/globals.css` | FAIL if 없음 |
| `src/lib/utils.ts` | FAIL if 없음 — "shadcn cn() 유틸 없음" |
| `src/providers/query-provider.tsx` | WARN if 없음 — "@tanstack/react-query가 있지만 Provider 없음" |
| `components.json` | WARN if 없음 — "shadcn/ui 초기화 안 됨" |

**수정 동작**: FAIL 파일 중 `not-found.tsx`, `error.tsx`, `loading.tsx`는 기본 템플릿으로 생성. 나머지는 수동 대응 안내.

---

### 6. Global CSS 테마 구조

`src/app/globals.css`를 읽고 확인:

| 검사 | PASS | FAIL/WARN |
|:-----|:-----|:----------|
| `@import "tailwindcss"` | 존재 | FAIL — "Tailwind 미설정" |
| `:root` 블록 | 존재 + CSS 변수 정의 | FAIL — "테마 변수 없음" |
| `.dark` 블록 | 존재 | WARN — "다크 테마 미설정" |
| `--primary` 변수 | `:root`에 정의됨 | WARN |
| `--background` 변수 | `:root`에 정의됨 | WARN |
| `--foreground` 변수 | `:root`에 정의됨 | WARN |
| `--destructive` 변수 | `:root`에 정의됨 | WARN |
| 테마 주석 | `THEME COLORS` 주석 존재 | WARN — "테마 섹션 구분 주석 없음" |

**수정 동작**: 주석만 자동 추가. 변수 누락은 안내만 출력.

---

### 7. 폰트 설정

| 검사 | PASS | FAIL/WARN |
|:-----|:-----|:----------|
| `public/fonts/` 디렉토리 | 존재 | WARN |
| `.woff2` 파일 | `public/fonts/`에 1개 이상 | WARN — "로컬 폰트 없음" |
| `layout.tsx`에 폰트 로드 | `localFont` 또는 `next/font` import 존재 | WARN |
| `lang="ko"` | layout.tsx의 html 태그에 존재 | WARN — "한국어 lang 미설정" |

---

### 8. Provider 구조

| 검사 | PASS | WARN |
|:-----|:-----|:-----|
| QueryProvider | `src/providers/` 안에 `query` 포함 파일 존재 | WARN if @tanstack/react-query 있는데 Provider 없음 |
| layout.tsx에서 Provider 사용 | layout.tsx에 Provider import 존재 | WARN — "Provider가 layout에 연결되지 않음" |

---

### 9. 설정 파일

| 파일 | 판정 |
|:-----|:-----|
| `.prettierrc` 또는 `prettier.config.*` | WARN if 없음 |
| `.prettierignore` | WARN if 없음 |
| `.gitignore` | FAIL if 없음 |
| `.env.example` | WARN if 없음 |
| `.env.local` | WARN if 없음 (안내만, 생성하지 않음) |
| `eslint.config.*` | WARN if 없음 |
| `CLAUDE.md` | WARN if 없음 — "/setup:init으로 생성 권장" |

**수정 동작**: `.prettierrc`, `.prettierignore`, `.env.example`, `.gitignore` 누락 시 기본 템플릿으로 생성

---

### 10. 빌드 검증

```bash
pnpm build
```

| 결과 | 판정 |
|:-----|:-----|
| exit 0 | PASS |
| TypeScript 에러 | FAIL — 에러 메시지 표시 |
| 기타 에러 | FAIL — 에러 메시지 표시 |

**수정 동작**: 빌드 에러 분석 후 자동 수정 시도 (최대 3회). 수정 불가하면 에러 내용 출력.

---

## Output 형식

### Step 2: 검사 결과 (수정 여부 묻기 직전)

```
🔍 Next.js 프로젝트 검사 결과

프로젝트: [package.json name]
Next.js: [버전]

┌─────────────────────────────────┬────────┐
│ 검사 항목                        │ 결과   │
├─────────────────────────────────┼────────┤
│ 1. 프로젝트 기본 구조             │ PASS   │
│ 2. 의존성                        │ PASS   │
│ 3. 스크립트                      │ WARN   │
│ 4. 폴더 구조 (VAC)              │ PASS   │
│ 5. 핵심 파일                     │ FAIL   │
│ 6. Global CSS 테마              │ PASS   │
│ 7. 폰트 설정                     │ PASS   │
│ 8. Provider 구조                │ PASS   │
│ 9. 설정 파일                     │ WARN   │
│ 10. 빌드 검증                    │ PASS   │
└─────────────────────────────────┴────────┘

PASS: 8  WARN: 2  FAIL: 0

[WARN 상세]
  - 3. 스크립트: `format:check` 스크립트 없음
  - 9. 설정 파일: `.prettierignore` 없음

[FAIL 상세]
  - 5. 핵심 파일: src/app/not-found.tsx 없음
```

이 결과를 출력한 직후 `AskUserQuestion` 으로 수정 여부를 묻는다 (실행 흐름 Step 3 참고).

### Step 5: 최종 리포트 (수정 후)

```
✅ 수정 완료 (또는 "리포트 종료")

수정된 항목 (3):
  - 3. format:check 스크립트 추가
  - 9. .prettierignore 생성
  - 5. src/app/not-found.tsx 기본 템플릿 생성

수정 건너뜀 (0):
  (없음)

수동 대응 필요 (0):
  (없음)
```

수정을 건너뛴 항목이 있으면 그 사유(사용자가 No 선택, 자동 수정 불가 등)도 함께 표시.

---

## Rules

- 검사만 하고 **검사 외 코드 수정은 하지 않음** (수정 동의 시에도 설정 파일만 수정)
- 프로젝트의 비즈니스 코드는 절대 수정하지 않음
- PASS 항목은 상세 출력하지 않음 (간결하게)
- WARN/FAIL만 상세 사유 표시
- 수정 시 생성하는 파일은 `/setup:create-nextjs`와 동일한 템플릿 사용
- 빌드 검증에서 수정하는 것은 설정/타입 에러만 — 로직 에러는 안내만
- `package.json`이 없으면 즉시 중단
- 검사 결과 테이블은 반드시 출력
- **수정 전에는 반드시 AskUserQuestion 으로 사용자 동의를 받음** — 자동 수정 모드(플래그) 없음
