---
name: design-system
description: 새 컴포넌트·화면·페이지를 생성하거나, 스타일·테마·디자인 토큰을 수정할 때 활성화. 프로젝트의 기존 디자인 토큰(globals.css, tailwind.config, theme 등)을 플랫폼별로 탐지해 단일 진실 소스로 사용하고, references/design.md 는 값이 아닌 사용 규칙·의도만 보충합니다. 단순 텍스트 수정·로직 버그·백엔드 작업에는 활성화하지 않습니다.
---

# Design System

**원칙: 코드의 디자인 토큰이 값의 단일 진실 소스, design.md 는 값을 적지 않고 사용 규칙만 보충.**

## 3대 원칙

1. **값은 코드에만** — 색상·간격·폰트 값은 `globals.css`/`tailwind.config`/theme 파일이 정의
2. **규칙은 design.md 에만** — "언제·어디에·왜 쓰는지", do/don't, 컴포넌트 합성 패턴
3. **충돌 시 코드가 승리** — design.md 가 값을 적었더라도 코드 값이 우선. 충돌 발견 시 design.md 측의 값을 제거하도록 사용자에게 알림

---

## 워크플로우

### Step 1: 플랫폼 감지

`CLAUDE.md` 에 명시적 플랫폼 기재가 있으면 그 값을 우선. 없으면 다음 마커를 순서대로 탐색:

| 마커 | 플랫폼 |
|---|---|
| `package.json` → `dependencies.next` | Next.js |
| `package.json` → `dependencies.nuxt` | Nuxt |
| `package.json` → `vite` + `react` | Vite + React |
| `package.json` → `react-native` 또는 `expo` | React Native / Expo |
| `package.json` → `svelte`/`@sveltejs/kit` | Svelte / SvelteKit |
| `package.json` → `vue` (Nuxt 아님) | Vue (Vite 등) |
| `pubspec.yaml` | Flutter |
| `*.xcodeproj`, `Package.swift` | iOS Swift |
| `build.gradle*`, `AndroidManifest.xml` | Android |
| 위 어느 것도 없고 `.html` 파일만 존재 | Plain HTML/CSS |

복수 플랫폼(모노레포 등) 감지 시 사용자에게 어느 영역을 다룰지 질문.

### Step 2: 토큰 소스 탐색 (플랫폼별)

플랫폼별로 아래 파일들을 `Glob` 으로 검색 후 발견된 것만 `Read`. **위에서 아래로 우선순위 순**.

**Next.js / React / Vite-React**
1. `tailwind.config.{js,ts,mjs,cjs}` — Tailwind theme 확장
2. `**/globals.css`, `**/global.css` — `:root { --... }` 변수
3. `components.json` — shadcn/ui 설정 (있으면 shadcn 컨벤션 추정)
4. `**/theme.{ts,tsx,js,jsx}`, `**/themes/**/*.{ts,js}` — JS 테마 객체
5. `**/tokens.{json,ts,js}` — 토큰 전용 파일
6. `src/styles/**/*.css` — 추가 변수

**Nuxt / Vue**
1. `tailwind.config.*`
2. `assets/css/main.css`, `assets/styles/**/*.css`
3. `nuxt.config.{js,ts}` → `css`/`app.head` 항목
4. `**/composables/useTheme.*`

**React Native / Expo**
1. `tamagui.config.{ts,js}`
2. `**/theme.{ts,js}`, `**/colors.{ts,js}`, `**/tokens.{ts,js}`
3. `app.json`/`app.config.{ts,js}` → `expo.splash`/`expo.icon` 색상
4. NativeWind: `tailwind.config.*`

**Svelte / SvelteKit**
1. `tailwind.config.*`
2. `src/app.css`, `src/app.html`
3. `src/lib/styles/**/*.css`

**Flutter**
1. `lib/theme/**/*.dart`, `lib/themes/**/*.dart`
2. `lib/**/theme.dart`, `lib/**/colors.dart`
3. `lib/main.dart` → `ThemeData(...)`

**iOS (Swift)**
1. `**/Assets.xcassets/**/Colors/**`
2. `**/Theme.swift`, `**/Color+*.swift`, `**/DesignSystem/**`
3. SwiftUI: `**/ui/theme/**/*.swift`

**Android (Kotlin)**
1. `app/src/main/res/values/colors.xml`
2. `app/src/main/res/values/themes.xml`, `styles.xml`
3. Compose: `**/ui/theme/**/*.kt`

**Plain HTML/CSS**
1. `styles.css`, `style.css`, `main.css` (루트 `--` 변수)
2. HTML 내 `<style>` 블록의 `:root`

**탐색 결과 메모:**
```
[토큰 소스 탐지]
- 플랫폼: Next.js (App Router)
- 발견:
  - src/app/globals.css (--color-primary, --color-bg, ...)
  - tailwind.config.ts (colors, spacing, fontFamily)
- 미발견: theme 객체, tokens 파일
```

### Step 3: design.md 로드

`.claude/skills/design-system/references/design.md` 가 존재하면 `Read`. 없으면 빈 상태로 진행.

### Step 4: 분기 처리

| 토큰 소스 | design.md | 동작 |
|---|---|---|
| ✅ 있음 | ✅ 있음 | **표준**: 코드 토큰을 값 소스, design.md 를 규칙 소스로 결합 |
| ✅ 있음 | ❌ 없음 | **규칙 슬롯 생성 제안**: "토큰은 발견했습니다. 사용 규칙(do/don't)을 design.md 로 정리할까요?" 동의 시 [규칙 전용 포맷]으로 생성 |
| ❌ 없음 | ✅ 있음 | design.md 의 값+규칙을 사용. 코드 작성 시 발견 값을 토큰 파일(globals.css 등)로 승격할지 사용자에게 제안 |
| ❌ 없음 | ❌ 없음 | **빈 프로젝트**: 사용자에게 방향 질문 (업종, 톤, 참고) → [전체 포맷]으로 design.md 작성 → 첫 컴포넌트 작성 시 globals.css 등으로 승격 |

### Step 5: 적용 및 설명

작업 수행 후 어떤 소스가 어떤 결정에 영향을 줬는지 1~2줄로 명시:
> "코드 토큰의 `--color-primary` 를 CTA에 사용. design.md 규칙에 따라 한 화면에 1회만 배치."

---

## design.md 표준 포맷

### 규칙 전용 포맷 (토큰 소스가 있을 때 — 권장)

값을 적지 않고 토큰명만 참조합니다.

```markdown
# 디자인 규칙: {프로젝트명}

> 토큰 소스: {예: src/app/globals.css, tailwind.config.ts}
> 마지막 업데이트: {YYYY-MM-DD}

## 색상 사용 규칙
- `--color-primary` — 주요 CTA에만, 페이지당 1~2회
- `--color-secondary` — 보조 액션, 카드 내 강조
- `--color-error` — 에러 메시지·필수 검증 표시
- 그라데이션 — hero·랜딩 CTA 한정, 본문 카드 금지

## 타이포 사용 규칙
- `font-display` — hero·랜딩 헤드라인만, 본문 금지
- 라벨 — 항상 uppercase + `tracking-wide`
- 본문은 `text-base` 이하 사용 금지 (가독성)

## 간격 사용 규칙
- 섹션 간 — `space-y-16` 이상
- 카드 내부 — `p-6` (모바일), `p-8` (데스크탑)

## 컴포넌트 사용 규칙
- 카드 배경 — 항상 `bg-surface-container-lowest`
- Primary 버튼 — 한 화면 최대 1개
- 폼 인풋 — `Input` 컴포넌트만, 직접 `<input>` 금지

## Do / Don't
- ✅ 새 컴포넌트는 기존 토큰만 사용
- ✅ 새 토큰 추가 필요 시 사용자 승인 후 코드 토큰 파일에 추가
- ❌ 인라인 hex 값 금지 — 반드시 토큰 경유
- ❌ design.md 에 토큰 값(hex/px) 적지 말 것 — 토큰명만
```

### 전체 포맷 (토큰 소스가 없을 때만)

```markdown
# 디자인 시스템: {프로젝트명}

> 토큰 소스: 없음 (이 문서가 값+규칙 모두 정의 — 첫 코드 작성 시 globals.css 등으로 승격 예정)
> 마지막 업데이트: {YYYY-MM-DD}

## 방향성
{한 줄 크리에이티브 요약}

## 색상
| 토큰 | 값 | 용도 |
|---|---|---|
| primary | #5300b7 | 주요 CTA |
| secondary | #6d28d9 | 보조 |
| bg | #f7f9fb | 페이지 배경 |
| surface | #ffffff | 카드 |

## 타이포
| 용도 | 폰트 | 크기 | 굵기 |
|---|---|---|---|
| Display | Manrope | 3.5rem | 800 |
| Body | Pretendard | 1rem | 400 |

## 간격
| 토큰 | 값 |
|---|---|
| xs | 0.25rem |
| sm | 0.5rem |
| md | 1rem |
| lg | 2rem |

## 사용 규칙
(규칙 전용 포맷과 동일)
```

---

## 충돌 해결 우선순위

1. **코드 토큰 파일** (globals.css, tailwind.config, theme.ts 등) — 값의 최고 권위
2. **design.md** — 규칙의 최고 권위, 값은 코드에 양보
3. **CLAUDE.md 의 스타일 가이드** — 위 둘에 없는 일반 규약

**design.md 의 값과 코드 토큰이 다를 경우**: 코드를 따르고, design.md 측의 값을 제거하라고 사용자에게 알립니다.

---

## design.md 갱신 시점

다음 상황에서만 갱신:
- 사용자가 "디자인 규칙 추가"·"design.md 업데이트" 등 명시적 요청
- 새 컴포넌트 패턴이 반복 등장해 규칙화가 필요할 때 (사용자 확인 후)
- 코드 토큰이 추가/제거되어 design.md 의 토큰 참조가 깨질 때

전체 재작성 금지. 변경이 필요한 섹션만 수정.
