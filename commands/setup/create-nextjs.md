---
description: "Next.js 프로젝트 초기 세팅 (shadcn/ui, VAC 패턴, Zustand, TanStack Query)"
argument-hint: "<프로젝트명: 예) my-app>"
---

# Create Next.js Project

Next.js 최신 안정 버전 기반으로 프로덕션-레디 프로젝트를 세팅합니다.

**반드시 아래 순서를 따릅니다. 단계를 건너뛰지 마세요.**

---

## Step 0: 사전 확인

1. 인자로 받은 `$ARGUMENTS`를 프로젝트명으로 사용 (없으면 AskUserQuestion으로 질문)
2. WebSearch로 **Next.js 최신 안정 버전** 확인 (npmjs.com/package/next)
3. **생성 위치 결정** — AskUserQuestion으로 사용자에게 어디에 프로젝트를 만들지 묻는다. 기본 옵션:
   - **하위 디렉토리에 생성** (Recommended) — `./[프로젝트명]/` 으로 생성. 가장 흔한 패턴
   - **현재 디렉토리에 생성** — `.` 사용. 빈 또는 거의 빈 폴더에 직접 세팅할 때
   - **상위 디렉토리에 생성** — `../[프로젝트명]/`. 현재 위치가 `.claude` 같은 템플릿 폴더라 한 단계 위에 만들고 싶을 때
   - (Other) — 사용자가 절대/상대 경로를 직접 입력

   선택 결과를 `[프로젝트경로]` 변수로 보관하여 이후 Step 들에서 사용한다. 예:
   - 하위: `[프로젝트경로] = [프로젝트명]`
   - 현재: `[프로젝트경로] = .`
   - 상위: `[프로젝트경로] = ../[프로젝트명]`
   - 직접: `[프로젝트경로] = [사용자 입력 경로]`
4. 선택된 위치에 `package.json`이 이미 있으면 AskUserQuestion으로 덮어쓸지 확인

---

## Step 1: Next.js 프로젝트 생성

```bash
npx create-next-app@latest [프로젝트경로] \
  --typescript --tailwind --eslint --app --src-dir \
  --import-alias "@/*" --use-pnpm --turbopack
```

- `[프로젝트경로]` 는 Step 0-3 에서 결정된 값 (`.`, `[프로젝트명]`, `../[프로젝트명]`, 또는 사용자 입력 경로)
- 기존 파일과 충돌하면 임시 디렉토리 생성 후 파일 이동

---

## Step 2: shadcn/ui 초기화

```bash
cd [프로젝트경로] && pnpm dlx shadcn@latest init -d
```

- 기본 설정(base-nova 스타일, cssVariables: true)으로 초기화
- Button 컴포넌트가 자동 생성됨을 확인

---

## Step 3: 추가 의존성 설치

```bash
pnpm add zustand @tanstack/react-query
pnpm add -D prettier
```

---

## Step 4: package.json 스크립트 보강

`scripts`에 아래 항목이 없으면 추가:

```json
{
  "dev": "next dev --turbopack",
  "build": "next build",
  "start": "next start",
  "lint": "eslint .",
  "lint:fix": "eslint . --fix",
  "format": "prettier --write .",
  "format:check": "prettier --check .",
  "typecheck": "tsc --noEmit"
}
```

- `name` 필드를 프로젝트명으로 수정
- `prettier`는 devDependencies로 이동 (dependencies에 있다면)

---

## Step 5: VAC 패턴 폴더 구조 생성

```
src/
├── components/
│   ├── ui/          # (shadcn/ui 자동 생성됨)
│   ├── common/      # 프로젝트 공통 컴포넌트
│   └── layout/      # Header, Footer, Sidebar 등
├── features/        # 기능별 모듈 (VAC 패턴)
├── hooks/           # 전역 커스텀 훅
├── lib/             # (shadcn/ui 자동 생성됨 — utils.ts)
├── providers/       # React Context Provider
├── stores/          # Zustand 스토어
└── types/           # 전역 타입 정의
```

각 폴더를 `mkdir -p`로 생성.

---

## Step 6: Global CSS 정리

`src/app/globals.css`를 수정:

1. shadcn/ui가 생성한 기존 내용 유지
2. `--font-sans`를 `var(--font-pretendard)`로 변경
3. `:root` 섹션 상단에 주석 추가:
   ```css
   /* ============================================
      THEME COLORS - 이 섹션의 값을 변경하면 전체 프로젝트에 반영됩니다
      ============================================ */
   ```
4. `.dark` 섹션 상단에도 동일 패턴의 주석 추가
5. 각 변수 그룹별 한줄 주석 (Primary, Secondary, Background, Muted, Accent, Destructive, Border)

**목표**: globals.css의 CSS 변수만 바꾸면 전체 테마가 변경되도록 구조화

---

## Step 7: Pretendard 폰트 설치

1. `public/fonts/` 디렉토리 생성
2. GitHub에서 Pretendard Variable woff2 다운로드:
   ```bash
   curl -sL "https://github.com/orioncactus/pretendard/releases/download/v1.3.9/Pretendard-1.3.9.zip" -o pretendard.zip
   unzip -o pretendard.zip "web/variable/woff2/PretendardVariable.woff2" -d .
   mv web/variable/woff2/PretendardVariable.woff2 .
   rm -rf web pretendard.zip
   ```
3. `src/app/layout.tsx`에서 `next/font/local`로 Pretendard 로드:
   ```tsx
   const pretendard = localFont({
     src: "../../public/fonts/PretendardVariable.woff2",
     variable: "--font-pretendard",
     display: "swap",
     weight: "45 920",
   });
   ```
4. `html` 태그에 `lang="ko"` 설정

---

## Step 8: Layout + Provider 설정

### QueryProvider (`src/providers/query-provider.tsx`)
```tsx
"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () => new QueryClient({
      defaultOptions: {
        queries: { staleTime: 60 * 1000, refetchOnWindowFocus: false },
      },
    })
  );
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
```

### Root Layout (`src/app/layout.tsx`)
- `<QueryProvider>`로 children 감싸기
- Metadata에 title template 패턴 적용:
  ```tsx
  title: { default: "[프로젝트명]", template: "%s | [프로젝트명]" }
  ```

---

## Step 9: 페이지 생성

### 홈 (`src/app/page.tsx`)
- 프로젝트명 표시 + shadcn Button 2개 (primary, outline)
- 간결한 랜딩 페이지

### 404 (`src/app/not-found.tsx`)
- "404" 큰 숫자 + "페이지를 찾을 수 없습니다" + 홈 이동 버튼
- **주의**: shadcn/ui v4에서는 `asChild` 대신 `render` prop 사용
  ```tsx
  <Button render={<Link href="/" />}>홈으로 돌아가기</Button>
  ```

### Error (`src/app/error.tsx`)
- "use client" 필수
- error + reset props 받아서 "다시 시도" 버튼 제공
- `useEffect`로 console.error 출력

### Loading (`src/app/loading.tsx`)
- Tailwind CSS 스피너 (animate-spin)

---

## Step 10: 설정 파일 생성

### `.prettierrc`
```json
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 80,
  "bracketSpacing": true,
  "endOfLine": "lf"
}
```

### `.prettierignore`
```
node_modules
.next
out
public
pnpm-lock.yaml
```

### `.env.example`
```
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### `.env.local`
- `.env.example` 복사 + 주석으로 안내

### `.gitignore`
- Next.js 기본 + `.env.local`, `/output/` 추가

---

## Step 11: 예제 파일 생성

### Zustand Store (`src/stores/example-store.ts`)
- count + increment/decrement/reset 패턴의 간단한 예제

### 공통 타입 (`src/types/index.ts`)
- `ApiResponse<T>`, `PaginatedResponse<T>` 타입 정의

---

## Step 12: CLAUDE.md 생성

프로젝트 루트에 CLAUDE.md 생성. 아래 섹션 포함:

1. **Tech Stack** — 감지된 모든 기술 스택 나열
2. **Project Structure** — 1~3 depth 트리 + 각 폴더 역할
3. **Patterns & Conventions** — VAC 패턴 설명, Naming 테이블, State Management 전략
4. **Style Guide** — globals.css 토큰 위치, Colors 테이블 (oklch 값), Typography
5. **Key Dependencies** — 핵심 라이브러리 테이블
6. **Dev Commands** — 모든 스크립트 명령어 테이블
7. **Notes** — shadcn 컴포넌트 추가 방법, 테마 변경 방법

기존 `@AGENTS.md` 참조가 있으면 CLAUDE.md 최상단에 유지.

---

## Step 13: 빌드 확인

```bash
pnpm build
```

- 빌드 실패 시 에러를 분석하고 수정 후 재시도
- 빌드 성공할 때까지 반복 (최대 3회)

---

## Step 14: 정리

1. 임시 파일/폴더 삭제 (temp 디렉토리 등)
2. Next.js 자동 생성 파일 중 불필요한 것 삭제 (README.md, AGENTS.md 등)

---

## Output

```
✅ Next.js 프로젝트 세팅 완료

프로젝트: [프로젝트명]
생성 위치: [프로젝트경로]
Next.js: [버전]
shadcn/ui: ✓ (base-nova)
상태관리: Zustand + TanStack Query
폰트: Pretendard Variable
패턴: VAC (View-Action-Container)

생성된 파일:
  - CLAUDE.md
  - src/app/ (page, not-found, error, loading)
  - src/providers/query-provider.tsx
  - src/stores/example-store.ts
  - src/types/index.ts
  - .prettierrc, .env.example, .env.local

명령어:
  pnpm dev        → 개발 서버
  pnpm build      → 프로덕션 빌드
  pnpm format     → 코드 포맷팅
  pnpm typecheck  → 타입 체크
```

---

## Rules

- 모든 외부 버전은 WebSearch로 확인 후 최신 안정 버전 사용
- 감지되지 않는 항목은 추측하지 말 것
- 코드 예시에서 `asChild` 사용 금지 — shadcn/ui v4는 `render` prop 사용
- globals.css의 색상 체계는 oklch 유지 (shadcn 기본값)
- 빌드 성공 확인 없이 완료 처리 금지
- 프로젝트명이 주어지지 않으면 반드시 AskUserQuestion으로 질문
