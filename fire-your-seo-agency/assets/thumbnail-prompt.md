# GitHub 소셜 프리뷰(1280×640) 생성 가이드

원칙: **글자는 이미지 모델에 맡기지 않는다** (오탈자·깨진 한글). 배경만 생성하고
타이포는 코드/피그마로 얹는 2단 방식이 정본. 급하면 B안(원샷)도 가능.

기준은 커밋된 `assets/social-preview.png`다. 아래 표는 **그 파일에서 실측한 값**이므로
재생성할 때는 이 수치를 그대로 재현한다. 재생성했다면 다시 실측해 이 표를 갱신한다.

## 실측 오버레이 스펙 (커밋된 1280×640 PNG)

| # | 문구 | 잉크 박스 (y) | 캡 높이 | 좌측 x | 색 |
|---|---|---|---|---|---|
| 1 | `fire-your-seo-agency` | 198–262 | 65px | 75 | `#F6F7F9` |
| 2 | `SEO 대행 · GEO 대행 · "AI 검색 최적화" 업체까지` | 289–316 | 28px | 73 | `#F7941E` |
| 3 | `월 150만 원짜리 일, AI 에이전트가 대체합니다` | 339–364 | 26px | 73 | `#F6F7F9` |
| 4 | `SEO · AEO · GEO · LLMO · NEO(네이버)` | 397–417 | 21px | 73 | `#AEB8C7` |
| 5 | `github.com/leopard627/fire-your-seo-agency` | 544–563 | 20px | 73 | `#6B7A90` |

- 폰트 크기 ≈ 캡 높이 ÷ 0.72 → 1행 ≈90px, 2행 ≈39px, 3행 ≈36px, 4행 ≈29px, 5행 ≈28px
- 좌측 73px 좌정렬. 배경 아트(불타는 문서·돋보기)는 우측에 두고 타이포와 겹치지 않게 한다
- 3행의 가격대는 README 두 문서와 함께 움직인다 — 한쪽만 바꾸면 표기가 갈린다

## 배경 프롬프트 (Midjourney/DALL-E/Stable Image 공용)

```
A dramatic dark navy tech background (deep #0D2137 to near-black gradient),
a single burning orange-red flame emerging from a paper invoice document
that is dissolving into small glowing data particles and search-bar icons,
subtle grid of faint chart lines in the far background, cinematic rim light,
high contrast, minimal composition with empty space on the left 60% for text,
no letters, no words, no typography, 16:9
```

## 재생성 후 (필수)

```bash
python3 tools/optimize_assets.py            # 무손실 재압축 (픽셀이 바뀌면 거부)
python3 tools/validate.py                   # 1280×640·용량 예산·README 임베드 검사
```

- 합성 결과는 **원본 크기로 확대해 글자를 검수**한다 — 한글 오탈자·자모 깨짐은 축소
  이미지에서 보이지 않는다
- 저장은 PNG 1280×640, 커밋 전에 위 두 명령을 통과시킨다 (CI도 같은 검사를 돈다)

## B안 — 원샷 (영문 타이포까지 모델에 맡기는 빠른 버전)

```
Minimal GitHub social preview banner, 1280x640, dark navy background,
huge bold white monospace text "fire-your-seo-agency" centered-left,
a small orange flame icon replacing the hyphen dot, subtitle line in amber
"SEO · AEO · GEO · LLMO · NEO", clean flat vector style, subtle noise texture,
professional developer-tool aesthetic
```

⚠️ B안은 영문도 철자가 깨질 수 있음 — 생성 후 반드시 글자 검수. 한글은 절대 넣지 말 것.

## 로고(정사각 아바타)용

```
Flat vector logo icon, a stylized flame formed by a magnifying glass handle,
orange-red gradient flame (#ED1C24 to #F7941E) on deep navy circle background,
minimal, bold silhouette, no text, app-icon style, centered
```

