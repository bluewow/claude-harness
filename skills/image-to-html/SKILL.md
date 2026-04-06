---
name: image-to-html
description: 사용자가 "/image-to-html" slash command를 입력했을 때만 활성화. 디자인 이미지를 영역별로 크롭하여 HTML/CSS로 구현한다. 이미지 붙여넣기, 디버깅 요청, UI 수정 요청 등 일반적인 이미지 관련 작업에서는 트리거하지 않는다.
---

# Image to HTML

전체 페이지 디자인 이미지를 영역별로 크롭 → 개별 분석 → HTML/CSS 구현.

## 사용법

```
/image-to-html <이미지_경로>
```

---

## 프로세스

### Phase 1: 이미지 분석 & 크롭

1. **전체 이미지 로드** - Read로 원본 이미지를 열어 전체 구조 파악
2. **자동 경계 감지** - 크롭 스크립트 실행:
   ```
   python .claude/skills/image-to-html/crop_sections.py <이미지경로> <출력폴더> [min_height]
   ```
3. **크롭 검증** - 모든 크롭 이미지를 Read로 한장씩 열어 확인:
   - 2개 영역이 합쳐졌는지?
   - 상단/하단이 잘렸는지?
   - 너무 작은 조각이 분리되었는지?
4. **경계 보정** - 문제가 있으면 수동 경계로 재크롭:
   ```python
   from PIL import Image
   img = Image.open(img_path)
   boundaries = [0, 92, 752, ...]  # AI가 보정한 경계
   for i, (s, e) in enumerate(zip(boundaries, boundaries[1:])):
       img.crop((0, s, img.width, e)).save(f"sections/{i+1:02d}_section.png")
   ```
5. **섹션 목록 출력** - 사용자에게 보여주고 확인

### Phase 2: 스타일 가이드 추출

크롭 이미지들에서 공통 스타일 요소 추출:
- 색상 팔레트, 타이포그래피, 간격 체계, 컴포넌트 패턴

`css/style.css` 상단에 주석으로 기록.

### Phase 3: 섹션별 구현

각 크롭 이미지에 대해 순차적으로:
1. **크롭 이미지 Read** - 세밀하게 분석
2. **HTML 작성** - 시맨틱 태그, BEM 네이밍
3. **CSS 작성** - Phase 2 스타일 가이드 기반
4. **사용자 확인** - 브라우저 확인 요청 후 다음 섹션

---

## 모델 선택 가이드

| Phase | 작업 | 권장 모델 | 이유 |
|-------|------|-----------|------|
| Phase 1 | 이미지 분석 & 크롭 | **opus** | 이미지 해석 정확도 |
| Phase 2 | 스타일 가이드 추출 | **opus** | 디자인 언어 이해 |
| Phase 3 | HTML/CSS 구현 | **sonnet** | 코드 생성 속도 + 비용 효율 |

Agent 사용 시 `model` 파라미터로 전환:
```
Agent(model="sonnet", prompt="크롭 이미지 기반으로 hero 섹션 HTML/CSS 구현...")
```

---

## 출력 구조

```
project/
├── index.html
├── css/
│   └── style.css
└── images/sections/    ← 크롭된 섹션 이미지
```

---

## 핵심 원칙

1. **크롭 먼저, 구현은 나중** - 전체 이미지를 한번에 분석하지 않는다
2. **크롭 검증 필수** - 모든 크롭 결과를 Read로 열어 확인한다
3. **섹션 단위 진행** - 한 섹션 완료 → 사용자 확인 → 다음 섹션
4. **추측 금지** - 크롭 이미지에서 보이지 않는 요소는 만들지 않는다
