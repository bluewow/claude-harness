---
description: "Next.js 프로젝트 초기 세팅 + 실무 기반 구조 (shadcn/ui, VAC, Zustand, TanStack Query, API 계층, env, Storage 추상화·이미지 업로드, 공통 컴포넌트, Vitest, design.md)"
argument-hint: "<프로젝트명: 예) my-app> [--base-only]"
---

# Create Next.js Project

Next.js 최신 안정 버전 기반으로 **프로덕션-레디 프로젝트 기반 구조**를 세팅합니다.
목표는 스캐폴드가 아니라, 기능을 계속 추가해도 **중복 코드와 디자인 불일치가 생기지 않는 실무형 기반**입니다.

**반드시 아래 순서를 따릅니다. 단계를 건너뛰지 마세요.**

두 가지 모드가 있습니다.

| 모드 | 조건 | 수행 범위 |
| --- | --- | --- |
| **신규 생성** | 대상 위치에 `package.json` 이 없음 | Step 0 → 1 → 2 … → 16 전체 |
| **기존 보강** | 대상 위치에 `next` 의존성이 있는 `package.json` 이 있음 | Step 0 → 0-A(분석) → Step 5 이후를 **부족한 항목만** 수행 |

`--base-only` 가 주어지면 신규 생성에서도 Step 8~13(기반 계층·업로드·테스트)을 생략하고 스캐폴드(Step 1~7, 12, 14~16)만 만든다.

---

## Step 0: 사전 확인

1. 인자로 받은 `$ARGUMENTS`를 프로젝트명으로 사용 (없으면 AskUserQuestion으로 질문)
2. WebSearch 또는 `npm view next version` 으로 **Next.js 최신 안정 버전** 확인. `npm view shadcn version` 도 함께 확인
3. **생성 위치 결정** — AskUserQuestion으로 사용자에게 어디에 프로젝트를 만들지 묻는다. 기본 옵션:
   - **하위 디렉토리에 생성** (Recommended) — `./[프로젝트명]/` 으로 생성. 가장 흔한 패턴
   - **현재 디렉토리에 생성** — `.` 사용. 빈 또는 거의 빈 폴더(예: `.claude`, `docs` 만 있음)에 직접 세팅할 때
   - **상위 디렉토리에 생성** — `../[프로젝트명]/`. 현재 위치가 `.claude` 같은 템플릿 폴더라 한 단계 위에 만들고 싶을 때
   - (Other) — 사용자가 절대/상대 경로를 직접 입력

   선택 결과를 `[프로젝트경로]` 변수로 보관하여 이후 Step 들에서 사용한다. 예:
   - 하위: `[프로젝트경로] = [프로젝트명]`
   - 현재: `[프로젝트경로] = .`
   - 상위: `[프로젝트경로] = ../[프로젝트명]`
   - 직접: `[프로젝트경로] = [사용자 입력 경로]`
4. 선택된 위치에 `package.json` 이 이미 있으면:
   - `next` 의존성이 있으면 **기존 보강 모드**로 전환한다고 알리고 Step 0-A 로
   - 아니면 AskUserQuestion으로 덮어쓸지 확인
5. 대상 위치에 `.claude/` 가 있고 그 안에 자체 `.git` 이 있으면(하네스 clone) 기억해 둔다 → Step 12 에서 Prettier·ESLint·git 대상에서 제외한다. **`.claude` 안의 파일은 이 커맨드가 절대 수정·포맷·되돌리기 하지 않는다.**
6. `docs/` 에 기존 정책 문서가 있으면 읽어 둔다. 공통 컴포넌트 선택(Step 10)과 CLAUDE.md 의 프로젝트 소개에 반영한다.

---

## Step 0-A: 기존 프로젝트 분석 (기존 보강 모드에서만)

코드를 수정하기 전에 아래 항목을 **먼저 확인하고 표로 정리**한다. 기존 구조를 무시하고 새 구조를 덮어씌우지 않는다.

| 항목 | 확인할 것 |
| --- | --- |
| 버전·설정 | Next.js / React / TypeScript 버전, `tsconfig` strict, ESLint·Prettier 설정 |
| App Router | `src/app` 구조, 라우트 그룹, `loading/error/not-found/global-error` 유무 |
| 폴더·모듈 | `components/features/lib/hooks/stores/providers/types` 존재 여부와 실제 쓰임 |
| 공통 컴포넌트 | `components/ui`(shadcn), `components/common`, 중복 구현된 버튼·모달·리스트 |
| 레이아웃 | 헤더·푸터·컨테이너가 공통인지, 페이지마다 임의 폭·패딩인지 |
| 스타일 | 토큰 소스(`globals.css`), 하드코딩 색상·간격, 다크 모드 |
| API 호출 | `fetch` 직접 호출 위치, 응답 봉투, 에러 처리 방식 |
| 상태 관리 | 서버 상태/클라이언트 상태 도구, 중복 fetch |
| 환경변수 | `process.env` 직접 참조 위치, `.env.example` 유무 |
| Loading/Empty/Error | 세 상태의 표현이 통일돼 있는지 |
| 이미지·파일 | 업로드 방식(서버 경유 vs presigned), 저장 위치, `next/image` 설정 |
| 중복 | 두 곳 이상에서 반복되는 UI·로직 |

분석 결과에서 **부족한 항목만** Step 5 이후의 해당 단계로 보강한다. 이미 있는 구현은 재사용하고, 기존 API 계약·동작을 깨지 않는다.

---

## Step 1: Next.js 프로젝트 생성 (신규 생성 모드)

```bash
npx create-next-app@latest [프로젝트경로] \
  --typescript --tailwind --eslint --app --src-dir \
  --import-alias "@/*" --use-pnpm --turbopack
```

- `[프로젝트경로]` 는 Step 0-3 에서 결정된 값
- 현재 디렉토리(`.`)에 `.claude`, `docs` 만 있는 경우 create-next-app 이 그대로 진행된다. 다른 파일과 충돌하면 임시 디렉토리 생성 후 파일 이동
- 생성 후 `CLAUDE.md` 가 `@AGENTS.md` 한 줄로 만들어지고 `AGENTS.md` 는 `next dev` 가 재생성하는 파일이다 — **둘 다 유지**

---

## Step 2: shadcn/ui 초기화 + 프리미티브 추가

```bash
cd [프로젝트경로] && pnpm dlx shadcn@latest init -d
pnpm dlx shadcn@latest add input textarea select checkbox radio-group label field \
  dialog alert-dialog sonner card badge skeleton pagination separator spinner empty table -y -o
```

- 기본 설정(base-nova 스타일, neutral, cssVariables: true)으로 초기화. Button 이 자동 생성됨
- 위 프리미티브가 기본 세트다. 프로젝트 정책 문서(Step 0-6)에서 필요한 것이 더 있으면 추가하고, 없는 것을 미리 넣지 않는다
- `sonner` 가 `next-themes` 를 함께 설치한다. ThemeProvider 는 다크 모드 토글이 필요할 때만 추가
- **`src/components/ui/*` 는 손으로 수정하지 않는다** (재생성 시 덮어씀)

---

## Step 3: 추가 의존성 설치

```bash
pnpm add zustand @tanstack/react-query
pnpm add -D prettier vitest
```

- Node 22 이상이면 `pnpm add -D @types/node@^<Node 메이저>` 로 맞춘다 (vitest peer 경고 방지)
- 그 밖의 의존성(zod, react-hook-form, AWS SDK 등)은 **넣지 않는다**. 필요해지는 시점에 사용자와 결정

---

## Step 4: package.json 스크립트 보강

`scripts` 에 아래 항목이 없으면 추가:

```json
{
  "dev": "next dev --turbopack",
  "build": "next build",
  "start": "next start",
  "lint": "eslint .",
  "lint:fix": "eslint . --fix",
  "format": "prettier --write .",
  "format:check": "prettier --check .",
  "typecheck": "tsc --noEmit",
  "test": "vitest run",
  "test:watch": "vitest"
}
```

- `name` 필드를 프로젝트명(kebab-case)으로 수정
- `prettier` 는 devDependencies 로 이동 (dependencies 에 있다면)

---

## Step 5: 폴더 구조 생성

```
src/
├── app/
│   └── api/uploads/{presign,complete,local/[...key]}/   # Step 9
├── components/
│   ├── ui/            # shadcn/ui 자동 생성 — 수정 금지
│   ├── common/        # 합성 컴포넌트 (Step 10)
│   └── layout/        # SiteHeader, SiteFooter, Sidebar 등
├── features/          # 기능별 모듈 (VAC 패턴)
├── hooks/             # 전역 커스텀 훅
├── lib/
│   ├── api/           # errors · response · client
│   ├── storage/       # types · keys · local · s3 · sigv4 · index
│   ├── upload/        # shared · client
│   ├── env.ts · constants.ts · utils.ts(shadcn 생성)
├── providers/         # React Context Provider
├── stores/            # Zustand 스토어
└── types/             # 전역 타입
docs/
├── design.md          # 디자인 사용 규칙 (Step 14)
└── uploads/           # local 업로드 저장 위치 (git 제외, 런타임 생성)
public/fonts/
```

각 폴더를 `mkdir -p` 로 생성. `docs/uploads` 는 만들지 않는다(드라이버가 생성).

---

## Step 6: Global CSS 정리

`src/app/globals.css` 를 수정:

1. shadcn/ui 가 생성한 기존 내용 유지
2. `@theme inline` 의 `--font-sans` 를 `var(--font-pretendard)` 로 변경
3. `:root` 섹션 상단에 주석 추가:
   ```css
   /* ============================================
      THEME COLORS - 이 섹션의 값을 변경하면 전체 프로젝트에 반영됩니다
      ============================================ */
   ```
4. `.dark` 섹션 상단에도 동일 패턴의 주석 추가 (`THEME COLORS (DARK)`)
5. 각 변수 그룹별 한줄 주석 (Background/Foreground, Primary, Secondary, Muted, Accent, Destructive, Border/Input/Ring, Chart, Radius, Sidebar)

**목표**: globals.css 의 CSS 변수만 바꾸면 전체 테마가 변경되도록 구조화. 색상 체계는 oklch 유지.

---

## Step 7: Pretendard 폰트 설치

1. `public/fonts/` 디렉토리 생성
2. GitHub 에서 Pretendard Variable woff2 다운로드 (**스크래치패드에서** 받아 압축 해제 후 복사 — 프로젝트에 zip 을 남기지 않는다):
   ```bash
   curl -sL "https://github.com/orioncactus/pretendard/releases/download/v1.3.9/Pretendard-1.3.9.zip" -o pretendard.zip
   unzip -o -q pretendard.zip "web/variable/woff2/PretendardVariable.woff2" -d .
   cp web/variable/woff2/PretendardVariable.woff2 [프로젝트경로]/public/fonts/
   ```
   - `unzip` 이 없으면 PowerShell `Expand-Archive` 사용
3. `src/app/layout.tsx` 에서 `next/font/local` 로 Pretendard 로드:
   ```tsx
   const pretendard = localFont({
     src: "../../public/fonts/PretendardVariable.woff2",
     variable: "--font-pretendard",
     display: "swap",
     weight: "45 920",
   });
   ```
4. `html` 태그에 `lang="ko"` 설정. Geist Mono 는 `--font-geist-mono` 로 유지(코드용)

---

## Step 8: 기반 계층 (lib)

각 파일 상단에 한국어 주석으로 용도 2~3줄. `any` 금지. 아래 계약은 **이름까지 그대로** 따른다 — 이후 커맨드(check-nextjs)와 CLAUDE.md 가 이 이름을 참조한다.

### 8-1. 타입 · 상수

- `src/types/index.ts`
  ```ts
  export interface ApiSuccess<T> { success: true; data: T }
  export interface ApiFailure { success: false; error: { code: string; message: string; details?: unknown } }
  export type ApiResponse<T> = ApiSuccess<T> | ApiFailure;
  export interface PaginatedResponse<T> { items: T[]; total: number; page: number; pageSize: number; hasNext: boolean }
  export interface PaginationParams { page: number; pageSize: number }
  ```
- `src/lib/constants.ts` — `SITE { name, description }`, `NAV_ITEMS`, `PAGINATION { defaultPageSize, maxPageSize }`. 도메인 상수는 `features/<기능>/constants.ts` 에

### 8-2. 환경변수 단일 진입점 — `src/lib/env.ts`

- `publicEnv` — `NEXT_PUBLIC_*` 만 (예: `appUrl`)
- `getServerEnv(): ServerEnv` — 캐시, 브라우저에서 호출하면 throw, 필수값 누락 시 `환경변수 X 가 설정되지 않았습니다. .env.local 을 확인하세요 (.env.example 참고).` 메시지로 throw
- `ServerEnv`: `nodeEnv`, `storageDriver: "local" | "s3"` (기본 local), `localUploadDir` (기본 `docs/uploads`), `s3: S3Env | null` (driver 가 s3 일 때만 `S3_BUCKET/S3_REGION/S3_ACCESS_KEY_ID/S3_SECRET_ACCESS_KEY` 필수, `S3_ENDPOINT/S3_PUBLIC_BASE_URL/S3_FORCE_PATH_STYLE` 선택)
- `resetServerEnvCache()` — 테스트용
- 규칙: 코드 곳곳에서 `process.env.X` 를 직접 읽지 않는다

### 8-3. API 계층 — `src/lib/api/`

- `errors.ts` — `ApiErrorCode = BAD_REQUEST | UNAUTHORIZED | FORBIDDEN | NOT_FOUND | CONFLICT | PAYLOAD_TOO_LARGE | UNSUPPORTED_MEDIA_TYPE | INTERNAL` (status 매핑 400/401/403/404/409/413/415/500). `class ApiError extends Error { code; status; details? }` + 정적 생성자 `badRequest/notFound/payloadTooLarge/unsupportedMediaType/internal`, `isApiError`, `getErrorMessage(error, fallback)`
- `response.ts` (서버 전용) — `ok(data, init?)`, `fail(apiError)`, `toApiError(unknown)` (SyntaxError → 400, 그 외 → 500), `handleRoute(handler)` (try/catch → `fail`, 5xx 는 `console.error`), `readJsonBody(request)` (객체가 아니면 400). `Response.json` 사용(테스트에서 Next 의존 없이 실행되도록)
  ```ts
  export const POST = handleRoute(async (request) => { const body = await readJsonBody(request); …; return ok(data); });
  ```
- `client.ts` (클라이언트) — `apiFetch<T>(input, init?)`: 봉투를 풀어 `data` 반환, 실패는 `ApiError` throw(네트워크 오류는 status 0). `apiPost<T>(input, body, init?)`. **컴포넌트에서 `fetch` 직접 호출 금지**

### 8-4. 업로드 규칙 · 클라이언트 흐름 — `src/lib/upload/`

- `shared.ts` (클라이언트·서버 공용) — `IMAGE_UPLOAD { maxSizeBytes: 10MB, maxCount: 10, allowedTypes: [jpeg,png,webp,heic] }`, `EXTENSION_BY_TYPE`, `TYPE_BY_EXTENSION`, `isAllowedImageType`, `formatBytes`, `validateImageFile({type,size}) → {ok:true}|{ok:false,message}`, 타입 `PresignRequest { fileName, contentType, size }`, `PresignResponse = UploadTarget`, `CompleteUploadRequest { key }`, `UploadedImage { key, url, size, contentType }`
- `client.ts` — `uploadImage(file, { onProgress?, signal? }): Promise<UploadedImage>`: ① `validateImageFile` ② `apiPost("/api/uploads/presign")` ③ 반환된 `url/method/headers` 로 **XHR PUT** (진행률 제공) ④ `apiPost("/api/uploads/complete", { key })`. **환경 분기 없음** — 드라이버 차이는 서버가 흡수

### 8-5. Storage 추상화 — `src/lib/storage/`

- `types.ts` — 이 인터페이스가 계약이다:
  ```ts
  export type StorageDriverName = "local" | "s3";
  export interface CreateUploadTargetInput { key: string; contentType: string; size: number }
  export interface UploadTarget { key: string; method: "PUT"; url: string; headers: Record<string, string>; expiresAt: string }
  export interface ObjectMetadata { size: number; contentType: string }
  export interface StorageDriver {
    readonly name: StorageDriverName;
    createUploadTarget(input: CreateUploadTargetInput): Promise<UploadTarget>;
    head(key: string): Promise<ObjectMetadata | null>;
    delete(key: string): Promise<void>;
    getPublicUrl(key: string): string;
  }
  ```
- `keys.ts` — `generateObjectKey({ contentType, now?, uuid? })` → `uploads/YYYY/MM/<uuid>.<ext>`, `isSafeObjectKey(key)` (정규식으로 형식 고정 — **local 드라이버 경로 탈출 방지의 근거**), `getKeyExtension`
- `local.ts` — `createLocalStorage({ rootDir, routePrefix = "/api/uploads/local", presignExpiresInSeconds = 300 }): LocalStorageDriver`. 인터페이스 외에 `write(key, bytes)`, `read(key) → { stream, metadata } | null`, `rootDir` 추가. 키의 `uploads/` 접두는 벗기고 `rootDir/YYYY/MM/<uuid>.<ext>` 에 저장(이중 `uploads/uploads` 방지). `path.resolve` 결과가 `rootDir` 밖이면 throw. contentType 은 확장자로 유도
- `sigv4.ts` — 외부 SDK 없이 `node:crypto` 만으로 AWS Signature V4. `presignUrl({ method, url, region, service, accessKeyId, secretAccessKey, expiresInSeconds, now, signedHeaders?, sessionToken? })`, `signRequestHeaders(...)`. `now` 는 항상 인자(테스트 가능). AWS 공식 벡터(`AKIAIOSFODNN7EXAMPLE`, `20130524T000000Z`, examplebucket `GET /test.txt` → 서명 `aeeed9bb…f604d404`)를 테스트로 고정
- `s3.ts` — `createS3Storage({ bucket, region, accessKeyId, secretAccessKey, endpoint?, forcePathStyle?, publicBaseUrl?, presignExpiresInSeconds?, sessionToken?, fetchImpl?, now? })`. presigned PUT 에 `Content-Type` 을 SignedHeaders 로 포함, `head` 는 서명된 HEAD(200 → 메타, 404 → null), `delete` 는 200/204/404 성공. S3·R2·MinIO 호환(endpoint 있으면 path-style 기본)
- `index.ts` — `getStorage()` 싱글턴(env 의 driver 로 선택), `getLocalStorage()` (local 아니면 null), `resetStorageInstance()`. `process.cwd()` 기반 경로 계산에는 `path.resolve(/* turbopackIgnore: true */ process.cwd(), dir)` 주석을 붙인다(Turbopack 이 프로젝트 전체를 trace 하는 빌드 경고 방지)

이 계층은 **의존성 추가 없이** 구현한다. 규모가 크면 `s3.ts + sigv4.ts + 테스트` 를 서브에이전트에 위임하되, `types.ts` 를 먼저 확정하고 계약을 지시문에 넣는다.

---

## Step 9: 업로드 API 라우트

```
POST /api/uploads/presign   {contentType,size} → validateImageFile → generateObjectKey → storage.createUploadTarget → ok(UploadTarget)
POST /api/uploads/complete  {key} → isSafeObjectKey → storage.head(key) (없으면 404) → validateImageFile 재검증(실패 시 delete + 400) → ok(UploadedImage)
PUT  /api/uploads/local/[...key]   local 드라이버 전용(아니면 404). Content-Type 이 키 확장자와 다르면 415, content-length/실제 크기 > max 면 413, 0바이트면 400 → storage.write
GET  /api/uploads/local/[...key]   storage.read → 파일 스트림 응답(Content-Type, Content-Length, Cache-Control: private)
```

- 모든 핸들러는 `handleRoute` 로 감싼다. `params` 는 **Promise** 다: `const { key } = await context.params`
- 도메인 엔티티(요청서 사진 등)와의 연결·삭제 권한은 여기서 하지 않는다. `complete` 가 돌려준 `UploadedImage` 를 도메인 API 가 저장하는 구조로 둔다

---

## Step 10: 공통 컴포넌트 · 레이아웃

### 원칙 (CLAUDE.md 와 design.md 에도 그대로 적는다)

1. 새로운 UI 를 구현하기 전에 기존 공통 컴포넌트를 먼저 확인한다 (`common/` → `ui/` 순)
2. 기존 컴포넌트로 구현 가능하면 반드시 재사용한다
3. 기존 컴포넌트의 확장(props/variant)으로 해결 가능하면 새로 만들지 않는다
4. 두 곳 이상에서 같은 합성이 반복될 때만 `common/` 에 추가한다
5. 특정 페이지에서만 쓰는 UI 는 `features/<기능>/` 안에 둔다 — 과도한 공통화 금지

### `src/components/common/` (기본 세트)

| 파일 | 컴포넌트 | 책임 |
| --- | --- | --- |
| `page-container.tsx` | `PageContainer` (size: narrow/default/wide), `PageHeader` (title, description, actions), `Section` (title, description, actions) | 페이지 폭·패딩·섹션 간격을 한 곳에서 결정. 페이지에서 `max-w-*`/`mx-auto` 직접 금지 |
| `loading-state.tsx` | `LoadingState` (size: page/section/inline, label) | ui/spinner 사용. 라우트 `loading.tsx` 는 `size="page"` |
| `empty-state.tsx` | `EmptyState` (icon, title, description, action) | ui/empty 합성 |
| `error-state.tsx` | `ErrorState` (title, description, onRetry, retryLabel, action) | ui/empty + destructive 아이콘, `role="alert"` |
| `confirm-dialog.tsx` | `ConfirmDialog` (open/onOpenChange 또는 trigger, title, description, confirmLabel, cancelLabel, variant: default/destructive, loading, onConfirm) | ui/alert-dialog 래퍼. `window.confirm` 대체 |
| `image-upload.tsx` | `ImageUpload` (value: UploadedImage[], onChange, maxCount, disabled, label) | 제어형. 진행률·실패 재시도·삭제·최대 장수. 흐름은 `lib/upload/client` 에 두고 UI 만 담당. ref 는 렌더 중 갱신하지 말고 effect 에서(`react-hooks/refs`) |

### `src/components/layout/`

- `site-header.tsx` — sticky 헤더, 브랜드 링크(`SITE.name`), 내비는 `NAV_ITEMS` 로만
- `site-footer.tsx` — 연도 + `SITE.description`

### shadcn/ui v4 주의

- `asChild` 없음 → `render` prop. 링크 버튼은 `<Button render={<Link href="/" />} nativeButton={false}>`
- 아이콘 + 텍스트 버튼은 아이콘에 `data-icon="inline-start" | "inline-end"`
- 토스트는 `import { toast } from "sonner"`, 루트 레이아웃에 `<Toaster position="top-center" richColors />`

---

## Step 11: app 파일 · VAC 예제

### Provider (`src/providers/query-provider.tsx`)
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
- `<QueryProvider>` 안에 `<SiteHeader />` + `<div className="flex flex-1 flex-col">{children}</div>` + `<SiteFooter />` + `<Toaster />`
- Metadata: `title: { default: SITE.name, template: \`%s | ${SITE.name}\` }`, `description: SITE.description`

### 라우트 상태 파일
- `loading.tsx` → `<LoadingState size="page" />`
- `error.tsx` ("use client") → `PageContainer size="narrow"` 안에 `<ErrorState onRetry={reset} />`, `useEffect` 로 `console.error`
- `global-error.tsx` ("use client") → 공통 컴포넌트·CSS 를 신뢰할 수 없으므로 **인라인 스타일만**으로 최소 UI
- `not-found.tsx` → `EmptyState` + 홈 링크 버튼(`render={<Link/>} nativeButton={false}`)

### 홈 (`src/app/page.tsx`)
- `PageContainer > PageHeader + Section`. 기반 확인용으로 VAC 예제 feature 를 렌더링
- 실제 화면이 생기면 예제는 제거 대상임을 CLAUDE.md 에 적는다

### VAC 예제 (`src/features/photo-upload-demo/`)
- `use-photo-upload-demo.ts` (Action: `useState<UploadedImage[]>`, `clear`) · `photo-upload-demo.view.tsx` (View: Card + Badge + `ImageUpload`, props 만) · `photo-upload-demo.tsx` (Container: 훅 → View)

### Zustand 예제 (`src/stores/example-store.ts`)
- `useCounterStore` — count + increment/decrement/reset

---

## Step 12: 설정 파일

### `.prettierrc`
```json
{ "semi": true, "singleQuote": false, "tabWidth": 2, "trailingComma": "all", "printWidth": 80, "bracketSpacing": true, "endOfLine": "lf" }
```

### `.prettierignore`
```
node_modules
.next
out
public
pnpm-lock.yaml
.claude
docs
```
- **`.claude` 와 `docs` 는 반드시 제외**. 빠뜨리면 첫 `pnpm format` 이 하네스 md/json/html 수십 개를 재포맷한다

### `eslint.config.mjs`
- `globalIgnores` 에 `".claude/**"` 추가 (훅 스크립트의 `require()` 가 lint 에러를 낸다)

### `.env.example`
```
NEXT_PUBLIC_APP_URL=http://localhost:3000

# 이미지 저장소: local (기본, docs/uploads) | s3 (S3/R2 presigned URL)
STORAGE_DRIVER=local
LOCAL_UPLOAD_DIR=docs/uploads

# STORAGE_DRIVER=s3 일 때 필수
S3_BUCKET=
S3_REGION=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
# 선택: R2/MinIO 엔드포인트, 공개 CDN 도메인, path-style 강제
S3_ENDPOINT=
S3_PUBLIC_BASE_URL=
S3_FORCE_PATH_STYLE=
```

### `.env.local`
- `.env.example` 의 local 값 복사 + 주석("새 변수를 추가하면 .env.example 에도 키를 추가")
- 하네스 `settings.json` 이 `.env*` 쓰기를 막고 있으면 **Bash heredoc 으로 한 번에** 작성한다 (Edit/sed 는 거부됨)

### `.gitignore`
- Next.js 기본 + 아래 추가:
  ```
  .env.local
  !.env.example
  /.output/
  /docs/uploads/
  /.claude/          # .claude 가 자체 git 저장소일 때만
  ```
- `.env*` 규칙이 `.env.example` 까지 막으므로 `!.env.example` 필수
- 업로드 디렉터리만 정확히 제외한다. `docs/` 전체나 소스는 제외하지 않는다

### `.gitattributes`
```
* text=auto eol=lf
*.woff2 binary
*.ico binary
*.png binary
```

### `vitest.config.mts` (`.ts` 로 만들면 ESM 경고)
```ts
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";
export default defineConfig({
  test: { environment: "node", include: ["src/**/*.test.ts"] },
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
});
```

---

## Step 13: 단위 테스트

대상 파일 옆에 `*.test.ts` 로 둔다. 최소 세트:

| 파일 | 검증 |
| --- | --- |
| `lib/storage/sigv4.test.ts` | AWS 공식 벡터 서명 일치, 쿼리 정렬, 경로 인코딩(공백·한글·`+`) |
| `lib/storage/s3.test.ts` | mock fetch 로 head 200/404/500, delete, presigned URL 의 `X-Amz-*`·SignedHeaders 에 content-type, path-style vs virtual-hosted, publicBaseUrl |
| `lib/storage/local.test.ts` | tmp 디렉터리에서 write→head→read→delete, 경로 탈출 거부, 저장 경로가 `rootDir/YYYY/MM/` |
| `lib/storage/keys.test.ts` | 키 형식, 허용/거부 케이스(`..`, 대문자 uuid, 잘못된 월) |
| `lib/api/response.test.ts` | ok/fail 봉투, toApiError 매핑, handleRoute 의 500 로그, readJsonBody |
| `lib/upload/shared.test.ts` | validateImageFile 경계값, formatBytes |

`pnpm test` 가 전부 통과해야 한다.

---

## Step 14: 문서

### `docs/design.md` (디자인 사용 규칙)
- design-system 스킬의 `references/design.md` **포맷 A** 를 따른다: 값(hex/oklch/px) 금지, 토큰명·유틸명만. 충돌 시 코드가 승리
- 섹션: 0 한 줄 방향성 / 1 색상 사용 규칙 / 2 타이포 / 3 간격·레이아웃(PageContainer 크기, gap 단계, radius, 그리드, 모바일 우선) / 4 컴포넌트·유틸 사용 규칙
- 4 에는 **표준 합성 공식 표**를 반드시 넣는다: 페이지 골격 · 로딩 · 빈 상태 · 오류 · 확인 다이얼로그 · 토스트 · 폼 필드(Field 계열) · 카드 · 상태 배지 · 이미지 업로드 · 페이지네이션 · 표. 각 행에 "사용" 과 "하지 않는 것"
- 버튼(크기·variant·render prop), 폼(높이 덮어쓰기 금지, FieldError), 접근성(아이콘 버튼 aria-label) 규칙, Do/Don't

### `CLAUDE.md`
프로젝트 루트. 기존 `@AGENTS.md` 참조는 최상단에 유지. 섹션:

1. **소개** — 한 줄 + `docs/policy`, `docs/design.md` 포인터
2. **Tech Stack** — 감지된 스택 (Storage 추상화, Vitest 포함)
3. **Project Structure** — 1~3 depth 트리 + 각 폴더 역할
4. **Patterns & Conventions** — **새 UI 를 만들기 전 필수 순서(5원칙)**, VAC 표, 서버/클라이언트 컴포넌트 구분, API 계층 사용법, 상태 관리, 환경변수, Loading/Empty/Error, Naming 표
5. **이미지 업로드 구조** — 3단계 흐름, 드라이버 선택, 키 형식, `UploadedImage` 를 도메인이 저장
6. **Style Guide** — 토큰 위치, Colors 표(oklch), Typography, "값은 코드에만·규칙은 design.md 에만"
7. **Key Dependencies**, **Dev Commands**(test 포함) + 검증 순서
8. **프로젝트별 함정** — `.claude` lint/format 제외, `docs/uploads` git 제외, `AGENTS.md` 는 재생성 파일, `params` 는 Promise, `nativeButton={false}`, `.env*` 편집 거부 시 heredoc
9. **Notes** — shadcn 추가 방법, 테마 변경, S3/R2 전환(env 만 바꾸면 됨 + 버킷 CORS 에 PUT/Content-Type), Next.js 최신 API 는 `node_modules/next/dist/docs/` 확인

---

## Step 15: 검증

순서대로, 전부 통과할 때까지(최대 3회 수정 반복):

1. `pnpm exec prettier --write src <변경 파일>` — **`.claude` 가 대상에 들어가지 않는지 먼저 확인**
2. `pnpm typecheck`
3. `pnpm lint`
4. `pnpm test`
5. `pnpm build` — 경고도 확인한다. "filesystem access causes the whole project to be traced" 가 나오면 Step 8-5 의 `turbopackIgnore` 주석 누락
6. **API 스모크 1회** — 스크래치패드에 Node 스크립트(`fetch`)로 dev 서버에 대해: presign 200 → PUT 200 → complete 200(size/contentType 일치) → GET 이 같은 바이트를 돌려줌 → pdf 거부 400 → 깨진 JSON 400 → 없는 키 404 → 경로 탈출 404 → Content-Type 불일치 415 → 파일이 `docs/uploads/YYYY/MM/` 에 존재 → **스크립트가 만든 `docs/uploads` 삭제**
7. **브라우저 스모크 1회 + 스크린샷 1장** (Playwright 가 가능할 때) — 홈 렌더, 파일 업로드 후 배지·타일·목록, 삭제, 404 페이지. 로케이터 문제로 실패하면 고쳐서 재실행하지 않고 보고만 한다. 404 페이지의 홈 버튼은 `<a role="button">` 이므로 `link` 역할로 찾지 않는다
8. dev 서버는 스모크가 끝나면 반드시 종료

보고에는 어느 층까지 검증했고 무엇을 하지 않았는지를 한 줄로 적는다.

---

## Step 16: 정리

1. 스크래치패드의 임시 파일(폰트 zip, 스모크 스크립트, Playwright 설치본) 정리. 삭제가 권한상 거부되면 보고만
2. Next.js 자동 생성 파일 중 `README.md` 와 `public/*.svg` 샘플 삭제. **`AGENTS.md` 는 삭제하지 않는다** (`next dev` 가 재생성하고 CLAUDE.md 가 참조)
3. `docs/uploads` 가 남아 있지 않은지 확인
4. 커밋은 사용자가 요청할 때만. `.claude` 가 자체 저장소면 프로젝트 저장소의 인덱스에 gitlink 로 들어가지 않았는지(`git ls-files -s .claude`) 확인하고, 들어갔다면 `git rm --cached .claude`

---

## Output

### 신규 생성 모드

```
✅ Next.js 프로젝트 세팅 완료

프로젝트: [프로젝트명]
생성 위치: [프로젝트경로]
Next.js: [버전] / shadcn: [버전]
shadcn/ui: ✓ (base-nova, 프리미티브 N개)
상태관리: Zustand + TanStack Query
Storage: local(docs/uploads) / s3(presigned, SDK 없음)
폰트: Pretendard Variable
패턴: VAC (View-Action-Container)
테스트: Vitest N개 통과

생성된 파일:
  - CLAUDE.md, docs/design.md
  - src/app/ (layout, page, loading, error, global-error, not-found, api/uploads/*)
  - src/components/common/ (page-container, loading-state, empty-state, error-state, confirm-dialog, image-upload)
  - src/components/layout/ (site-header, site-footer)
  - src/lib/ (env, constants, api/*, storage/*, upload/*)
  - src/features/photo-upload-demo/, src/providers/, src/stores/, src/types/
  - .prettierrc, .prettierignore, .gitattributes, vitest.config.mts, .env.example, .env.local

검증: typecheck ✓ lint ✓ test ✓ build ✓ API 스모크 ✓ 브라우저 스모크 [✓/생략]

명령어:
  pnpm dev / build / test / typecheck / lint / format
```

### 기존 보강 모드 (아래 7개 제목으로 보고)

```
### 현재 프로젝트에서 발견한 문제
### 이번에 변경한 구조
### 새로 추가하거나 수정한 공통 컴포넌트
### 이미지 업로드 구조
### 로컬/운영 환경 차이
### 추가로 개선하면 좋은 항목
### 실행한 검증 및 결과
```
+ "지시와 다르게 판단한 것 · 미해결" 을 마지막에 한 문단.

---

## Rules

- 모든 외부 버전은 WebSearch 또는 `npm view` 로 확인 후 최신 안정 버전 사용. 감지되지 않는 항목은 추측하지 말 것
- **기존 코드 우선**: 코드를 수정하기 전에 기존 프로젝트를 충분히 확인한다. 새 구조를 만들기 전에 기존 공통 컴포넌트와 기존 구현을 먼저 탐색한다. "새로 만드는 것"보다 "기존 것을 재사용하고 정리하는 것"을 우선한다
- **기존 기능 보호**: 기존 기능·API 계약 유지, 불필요한 dependency 추가 금지, 불필요한 파일 이동 최소화, 과도한 abstraction 금지. 필요한 경우 점진적으로 개선
- "좋아 보이는 구조"가 아니라 현재 프로젝트 규모와 실제 개발 생산성을 기준으로 판단한다
- 코드 예시에서 `asChild` 사용 금지 — shadcn/ui v4 는 `render` prop 사용
- globals.css 의 색상 체계는 oklch 유지 (shadcn 기본값). 디자인 값은 코드에만, 규칙은 design.md 에만
- Storage 는 인터페이스로 추상화하고 특정 서비스에 결합하지 않는다. 호출 측은 환경 분기를 갖지 않는다
- `.claude/` 안의 파일은 읽기만 한다. 포맷·수정·`git checkout` 금지
- 빌드·테스트·스모크 통과 확인 없이 완료 처리 금지
- 프로젝트명이 주어지지 않으면 반드시 AskUserQuestion 으로 질문
