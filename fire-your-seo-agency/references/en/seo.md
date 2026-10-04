# SEO — Technical Foundation Checklist

Content a crawler can't read is content that doesn't exist. This lane has one goal:
**everything — content, meta, structured data — must be present in the HTML received
without JavaScript.**

## 1. Content exposure

- [ ] Do key pages open **without login?** Content behind a login wall is never indexed.
      If you can't open everything, expose at least a teaser (first paragraph, key numbers)
      via SSR and gate the rest.
- [ ] Is the body text present in `curl -sL <url>` output? If the site is SPA/CSR,
      adopting SSR/SSG/prerendering is priority #1 — everything below is meaningless without it.
- [ ] ⚠️ **CSR bailout trap**: even in SSR frameworks, certain hooks/APIs can silently drop
      a whole page to client rendering (e.g. Next.js `useSearchParams` without Suspense).
      Re-check representative pages with curl after every deploy — a sudden drop in body
      character count is an incident.

## 2. Sitemap

- [ ] sitemap.xml exists + referenced from robots.txt
- [ ] **Every** detail page (product, article, item) is included — a common mistake is
      listing only index pages
- [ ] If you're approaching 50K URLs / 50MB, **shard preemptively** (sitemap index + parts).
      The moment you exceed the limit, the whole file is silently ignored.
- [ ] Shipping a new content type includes adding it to the sitemap — a forgotten type
      stays out of the index for months (measured: 3 filter-page types missing for weeks)

## 3. Meta

- [ ] Title 50–60 chars: key term first, brand last
- [ ] Description 150–160 chars: a sentence that gives a reason to click (don't put
      disclaimers/warnings in the description — they only kill CTR)
- [ ] Unique per page — hundreds of pages sharing one templated description gets flagged
      as duplication
- [ ] OG image: the face of every share. Dynamic generation per page type is ideal

## 4. Structured data (JSON-LD)

- [ ] Schema matching the page type: Article, Product, FAQPage, BreadcrumbList, Organization
- [ ] **Must be 100% identical to visible text** — LD content not shown on screen risks
      a spam verdict
- [ ] `@id` convention: same entity = same `@id` site-wide. Declaring a fresh Organization
      on every page splits the entity — declare once globally, reference elsewhere
- [ ] Validate after deploy: Google Rich Results Test or the schema.org validator

## 5. URL & response hygiene

- [ ] canonical: parameter variants and duplicate paths point to one canonical URL
- [ ] Multilingual? hreflang must cross-reference (one-sided tags are void)
- [ ] Missing pages return 404, not 200 — soft 404s burn crawl budget
- [ ] ⚠️ **Baked-404 trap**: in ISR/CDN cache layers, a transient failure's 404 can get
      baked for hours. On data-fetch failure, throw (retry) instead of returning 404 —
      "doesn't exist" and "couldn't fetch" are different things
- [ ] Redirect chains: 1 hop max

## 6. Performance & assets

- [ ] Images in WebP/AVIF + explicit width/height (CLS)
- [ ] Preload LCP targets (hero image, fonts)
- [ ] Losslessly optimize logos/icons — a multi-hundred-KB logo shipped on every page
      is a common waste

## 7. Index acceleration

- [ ] IndexNow: ping new/updated pages at publish time (consumed by Bing, Naver, Yandex)
- [ ] Google doesn't support IndexNow — win with sitemap `lastmod` accuracy instead
- [ ] Publishing at volume? Build the ping into the publishing pipeline — manual pings
      always stop happening
