---
description: "onepager-template.html 기반 프로젝트 파악용 원페이저 생성"
argument-hint: "<주제 또는 프로젝트명>"
---

# One-Pager 생성

**프로젝트를 30초 안에 파악할 수 있는 원페이저(6섹션)를 생성합니다.**

결과물: `output/onepager.html`

---

## 섹션 구조 (고정)

1. **Overview** — Problem + Solution + Core Value (한눈에)
2. **Target User** — 핵심 페르소나 1~3
3. **Core Features** — 3~6개 핵심 기능 표
4. **How It Works** — 단일 User Flow (4~6 단계)
5. **Tech & Stack** — Stack + Architecture Notes
6. **At a Glance** — Business / Status / Roadmap 한 줄 요약

> 사업계획서가 아닌 "파악용". Wireframe, IA, Risks, 상세 Roadmap 등은 의도적으로 제외.

---

## 실행 절차

### Step 1: 사전 준비
1. `.claude/templates/onepager-template.html` Read
2. 루트 `CLAUDE.md` Read (프로젝트 컨텍스트 파악)
3. `output/` 폴더 존재 확인

### Step 2: Q&A
AskUserQuestion으로 핵심 정보만 확인:
1. 한 줄 요약(Core Value Statement) — "{누구}에게 {무엇}을 {어떻게} 제공"
2. Problem 3가지와 그에 대응하는 Solution 3가지
3. 핵심 타겟 유저 (1~3 페르소나)
4. 핵심 기능 (3~6개)
5. 핵심 User Flow 단계 (4~6단계)

> 가정 금지. CLAUDE.md에서 답을 찾을 수 있으면 굳이 묻지 않는다.

### Step 3: 정리 확인
이해한 내용을 짧게 요약하고 AskUserQuestion으로 승인.

### Step 4: 생성
1. 템플릿의 모든 `{{PLACEHOLDER}}`를 실제 내용으로 교체
2. 프로젝트 실제 색상/브랜드/기술 스택 사용
3. 한국어로 작성
4. `output/onepager.html`로 저장 (기존 파일 있으면 덮어쓰기 전 확인)

### Step 5: 완료 안내
```
원페이저 생성 완료 → output/onepager.html
브라우저에서 확인해 주세요.
```

---

## 규칙
- 코드 수정 금지 — `output/onepager.html`만 생성
- 6섹션 구조 유지 (임의로 섹션 추가/제거 금지)
- 모호한 점은 가정하지 말고 질문
- 한국어
- CLAUDE.md 스타일 가이드에 맞춤
