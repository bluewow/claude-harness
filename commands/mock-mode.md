---
description: "env 단일 노브 mock 모드 패턴 설치·점검 (Next.js) — init: 신규 설치/기존 retrofit, check: 규약 drift 점검"
argument-hint: "init | check"
---

# Mock Mode

외부 의존(DB·결제·인증기관·알림 등) 없이 앱 전체 플로우를 목데이터로 완성해 두고,
env 스위치만으로 실연동에 단계 전환하는 패턴을 설치(init)하거나 점검(check)합니다.

**반드시 아래 순서를 따릅니다. 단계를 건너뛰지 마세요.**

---

## 패턴 개요 — 3층 구조

| 층 | 스위치 | 역할 |
| --- | --- | --- |
| ① 앱 모드 (단일 노브) | `NEXT_PUBLIC_APP_ENV=mock\|local\|dev\|prod` | mock 이면 앱 전체가 목데이터로 동작 (외부 무접근). **미설정 = mock (fail-safe)** |
| ② 외부 능력 어댑터 | 능력별 `<CAPABILITY>_PROVIDER=mock` | real 모드 안에서도 능력별 단계적 실연동 (예: DB 는 붙였지만 결제·알림은 아직 mock) |
| ③ 라우트 가드 | — | 외부 능력을 쓰는 API 라우트는 mock 모드에서 `503 unconfigured` 반환 |

핵심 규약:

1. **모드 판정은 한 곳** — `src/lib/app-env.ts` 의 `isRealMode()` 만 사용. `process.env.NEXT_PUBLIC_APP_ENV` 를 다른 파일에서 직접 읽지 않는다.
2. **외부 능력은 반드시 provider 인터페이스를 거친다** — 서버 코드에서 외부 API 직접 fetch 금지. 인터페이스 + mock 어댑터 + `get<X>Provider()` env 스위치.
3. **목데이터는 `src/lib/mock-data.ts` 한 파일에 중앙화** — 파일 헤더에 "백엔드 연결 시 제거" 주석. 서버 코드(`src/server/`)에서 import 금지 (클라이언트 Container 전용).
4. **Container 분기 규약** — `realMode ? 쿼리데이터 : MOCK_*`. View 는 모드를 모른다 (props 만 받음).
5. **실패 플로우 매직 값** — mock 어댑터는 QA 용 실패 트리거를 갖는다: 입력 끝 4자리 `0000` = 항상 실패. 어댑터 주석에 명시.
6. **`.env.example` 싱크** — 노브·provider env 는 반드시 `.env.example` 에 주석("mock(기본). 실기관 선정 후 어댑터 추가")과 함께 등재.

---

## Step 0: 사전 확인

1. `$ARGUMENTS` 가 `init` / `check` 인지 확인. 없으면 AskUserQuestion 으로 선택받는다.
2. Next.js 프로젝트인지 확인 (`package.json` 에 `next`). 아니면 중단하고 보고.
3. 소스 루트 확인 (`src/` 유무). 이하 경로는 `src/` 기준 — 없으면 프로젝트 구조에 맞게 치환.
4. 이미 패턴이 설치돼 있는지 스캔: `src/lib/app-env.ts` 존재 여부, `_PROVIDER` env 사용 여부.
   - init 인데 이미 설치됨 → 사용자에게 알리고 check 로 전환할지 AskUserQuestion.

---

## Step 1 (init): 설치 범위 결정

AskUserQuestion 으로 두 가지를 받는다:

1. **설치 층** — ① 앱 모드 노브만 / ①+② provider 포함 (Recommended) / 기존 코드 retrofit
2. **외부 능력 목록** (② 선택 시) — 예: 결제, 본인인증, 알림톡, 메일. 능력마다 provider 파일 하나.

기존 프로젝트 retrofit 이면: 서버 코드에서 외부 API 를 직접 호출하는 지점을 Grep 으로 찾아
(`fetch(`, SDK import) 능력 단위로 묶어 보여주고, 어떤 것을 provider 로 추출할지 확인받는다.

---

## Step 2 (init): 파일 생성

### 2-1. `src/lib/app-env.ts` — 단일 노브

```ts
/**
 * 데이터 모드 단일 노브 — NEXT_PUBLIC_APP_ENV: mock | local | dev | prod
 * mock = 목데이터(외부 무접근). 미설정 = mock (fail-safe).
 * NEXT_PUBLIC_ 은 빌드 시 인라인되므로 서버·클라이언트 공용, 전환 시 재빌드 필요.
 * 비밀 값은 절대 이 노브에 싣지 않는다 (클라이언트에 노출됨).
 */
export type AppEnv = "mock" | "local" | "dev" | "prod";

export function getAppEnv(): AppEnv {
  const v = process.env.NEXT_PUBLIC_APP_ENV;
  return v === "local" || v === "dev" || v === "prod" ? v : "mock";
}

/** real 모드 여부 — 모드 판정은 반드시 이 함수만 사용 */
export function isRealMode(): boolean {
  return getAppEnv() !== "mock";
}
```

### 2-2. `src/server/providers/<capability>.ts` — 능력별 어댑터 (능력마다 1파일)

아래는 "결제" 예시. 능력 이름·입출력 타입은 프로젝트에 맞게 치환한다.

```ts
/**
 * 결제 어댑터 — 실 PG 선정 전. mock 어댑터로 전체 플로우를 먼저 완성한다.
 * 실기관 연동 시: 1) 이 파일에 어댑터 추가 2) PAYMENT_PROVIDER env 로 전환.
 * mock 규칙: 즉시 승인. 카드번호 끝 4자리 "0000" 은 항상 실패(실패 플로우 QA 용).
 */
export type PaymentProviderName = "mock"; // 실 어댑터 추가 시 유니온 확장

export type ChargeResult =
  | { ok: true; txId: string }
  | { ok: false; error: string };

export interface PaymentProvider {
  readonly name: PaymentProviderName;
  charge(input: { cardNo: string; amount: number }): Promise<ChargeResult>;
}

const mockPaymentProvider: PaymentProvider = {
  name: "mock",
  async charge(input) {
    if (input.cardNo.endsWith("0000")) {
      return { ok: false, error: "승인이 거절됐어요(모의)." };
    }
    return { ok: true, txId: `mock_tx_${input.cardNo.slice(-4)}` };
  },
};

export function getPaymentProvider(): PaymentProvider {
  const name = process.env.PAYMENT_PROVIDER ?? "mock";
  if (name !== "mock") {
    throw new Error(
      `PAYMENT_PROVIDER=${name} 어댑터가 없습니다 — 실기관 선정 후 이 파일에 추가하세요.`,
    );
  }
  return mockPaymentProvider;
}
```

### 2-3. `src/lib/mock-data.ts` — 중앙 목데이터 골격

```ts
/**
 * 목 모드(NEXT_PUBLIC_APP_ENV=mock) 표시용 중앙 목데이터.
 * - 클라이언트 Container 전용 — src/server/ 에서 import 금지.
 * - 백엔드(API) 연결 시 TanStack Query 로 대체하고 이 파일은 제거한다.
 * - 데이터는 데모 시나리오가 자연스럽게 이어지도록 작성한다.
 */
export const MOCK_EXAMPLE = {
  // 프로젝트 도메인에 맞게 채운다
};
```

### 2-4. API 라우트 가드 (외부 능력을 쓰는 라우트에)

```ts
import { NextResponse } from "next/server";
import { isRealMode } from "@/lib/app-env";

export async function POST(request: Request) {
  if (!isRealMode()) {
    return NextResponse.json(
      { ok: false, error: "unconfigured" },
      { status: 503 },
    );
  }
  // ... getPaymentProvider().charge(...) 등
}
```

(mock 모드의 화면은 Container 분기가 담당하므로 라우트는 503 이면 충분하다.)

### 2-5. Container 분기 (사용 예 — 생성 파일 아님, 규약 안내용)

```tsx
const realMode = isRealMode();
const q = useQuery({ queryKey: ["rows"], queryFn: fetchRows, enabled: realMode });
const rows = realMode ? (q.data?.rows ?? []) : MOCK_ROWS;
```

---

## Step 3 (init): env·문서 되먹임

1. `.env.example` 에 블록 추가 (없으면 파일 생성, `.env.local` 은 건드리지 않는다):

```bash
# 데이터 모드 단일 노브: mock | local | dev | prod
# mock=목데이터(외부 무접근) — 미설정 시 mock (fail-safe)
NEXT_PUBLIC_APP_ENV=

# 결제 어댑터 — mock(기본, 즉시 승인·끝 4자리 0000 은 실패 모의). 실 PG 선정 후 어댑터 추가
PAYMENT_PROVIDER=mock
```

2. 프로젝트 `CLAUDE.md` 에 아래 단락을 추가(이미 유사 단락이 있으면 갱신):

```markdown
## Mock Mode

데이터 모드는 `NEXT_PUBLIC_APP_ENV` 단일 노브(mock|local|dev|prod, 미설정=mock).
모드 판정은 `src/lib/app-env.ts` 의 `isRealMode()` 만 사용한다. 외부 능력(결제 등)은
`src/server/providers/` 의 provider 인터페이스를 거친다(직접 fetch 금지). 목데이터는
`src/lib/mock-data.ts` 중앙화 — Container 에서 `realMode ? 쿼리 : MOCK_*` 분기, 서버 import 금지.
```

---

## Step 4 (init): 검증·보고

1. `pnpm typecheck`(없으면 `npx tsc --noEmit`) 통과 확인.
2. 보고: 생성 파일 목록, 설치한 층, 능력 목록, retrofit 했다면 추출한 호출 지점, 남은 일(목데이터 채우기 등).

---

## check: 규약 drift 점검

init 없이 `check` 로 호출되면 아래를 점검하고 표로 보고한다 (수정은 사용자 확인 후):

| # | 점검 | 방법 |
| --- | --- | --- |
| 1 | 모드 판정 단일화 | `NEXT_PUBLIC_APP_ENV` 를 `app-env.ts` 밖에서 직접 읽는 곳 Grep |
| 2 | provider 우회 | `src/server/` 에서 providers/ 를 거치지 않는 외부 `fetch(`·SDK 호출 |
| 3 | env 싱크 | 코드의 `*_PROVIDER` env 키 ↔ `.env.example` 등재 대조 (양방향) |
| 4 | 목데이터 서버 누수 | `src/server/` 가 `mock-data` 를 import 하는지 |
| 5 | 라우트 가드 누락 | provider 를 쓰는 라우트 중 `isRealMode()` 가드 없는 곳 |
| 6 | fail-safe | 노브 미설정 시 기본이 mock 인지 (`getAppEnv` 폴백 확인) |
| 7 | 매직 값 규약 | mock 어댑터에 실패 트리거(`0000`)와 주석이 있는지 |

보고 형식: 항목별 ✅/⚠️ + 위반 파일 목록 + 권장 조치. ⚠️ 항목은 수정 여부를 AskUserQuestion 으로 확인받고 진행한다.
