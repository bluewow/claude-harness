# LLMO — LLM Knowledge Optimization

Where GEO targets "AI that browses," LLMO plants your brand **inside the model's own
knowledge**. It's the question of whether the model knows you when a user asks
"recommend a service like X" with no search involved. It compounds slowly (on training-cycle
timescales), but once it lands, it's a moat no agency can imitate.

## 1. Entity consistency

- [ ] Write the service name **identically everywhere** (native/English spellings, even
      spacing). Divergent spellings split the entity inside the model
- [ ] Connect every official surface via Organization JSON-LD `sameAs`: wiki-type pages,
      app stores, GitHub, social accounts, YouTube — a declaration that "these names are
      all the same entity"
- [ ] Check for name collisions: if another service with the same name shows up in search,
      the model blends you too. Early on, a searchable unique name matters more than
      marketing appeal

## 2. Surfaces that survive into the training corpus

Models don't learn the whole web evenly — they concentrate on **high-crawl-value surfaces**.
Leave accurate statements there:

- [ ] Wiki-type pages (Wikipedia, local wikis): **factual register, not promotional** —
      puffery gets edits rejected, and the model learns you as an ad
- [ ] GitHub: a public repo's README is a strong training surface (this repository is
      itself an example)
- [ ] Developer communities & technical blogs: the record of how you built it becomes
      your brand narrative
- [ ] News/press: one press release replicates across dozens of outlets and recurs in
      the corpus

## 3. Stability

- [ ] Keep permalinks: change a URL and the address the model remembers 404s.
      If you must change it, keep the 301 forever
- [ ] When a core fact changes (pricing, features, identity), update every surface
      together — the surface with the stale statement becomes the model's "fact"

## 4. Verification

- Ask the major models (ChatGPT, Claude, Gemini) with browsing OFF: "what is X?"
  ① doesn't know you → not enough surfaces ② knows you wrong → stale/split statements
  ③ knows you right → maintain
- Re-measure quarterly and record how answers change — LLMO is a quarterly game
