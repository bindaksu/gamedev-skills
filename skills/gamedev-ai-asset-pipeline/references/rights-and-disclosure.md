# Rights, Licences and Store Disclosure for Generated Assets (as of 2026-11; verify)

Read this before buying a vendor plan, before the first generated asset ships, before any store submission or store-page update, and before any voice work that involves a real performer. It is a working summary of public rules, not legal advice; route anything ambiguous to counsel.

Tags: **[O]** official page read on 2026-11-21 · **[S]** secondary (press, law-firm summary) · **[U]** unverified · **[inference]** a reading, not a quote. Where the research did not cover a question, this file says so and names the page to check; do not fill the gap from memory.

## 1. Who owns the output, per vendor and plan

Rights attach to the **plan tier at generation time** and to the **exact checkpoint**, not to the vendor name.

| Vendor / model | Output and licence terms | Tag |
|---|---|---|
| OpenAI image models | User owns output per ToS (terms page not read) | [U] |
| Google Gemini image | "Google won't claim ownership" of generated content; SynthID watermark on every output | [O] |
| Midjourney | Paid plans allow commercial use; companies over $1M gross revenue need Pro or Mega | [S] |
| Black Forest Labs | API outputs commercial. Self-hosting FLUX 3 Klein or FLUX.2 [dev] commercially needs a paid licence tier. FLUX.2 [klein] exists as an Apache 2.0 variant and a Non-Commercial variant | [O] |
| Recraft | Paid plans: you own outputs. Free plan: Recraft owns them and commercial use is not allowed | [S] |
| Ideogram 4.0 weights | Commercial licence | [O] |
| Adobe Firefly | Adobe's own models: licensed training data and IP indemnity on qualifying business plans. Partner models inside Firefly are not covered | [S] |
| Stability (SD 3.5, Stable Audio 3.0) | Community Licence free under $1M annual revenue; Enterprise licence above | [O] |
| Tencent Hunyuan3D open weights | Licence excludes the EU, UK and South Korea; products over 1M MAU need a Tencent licence | [O] |
| Microsoft TRELLIS.2 | MIT, but nvdiffrast/nvdiffrec dependencies are research-only | [S] |
| Hyper3D Rodin | Commercial licence on the Business plan | [O] |
| Tripo, Meshy | Not covered by research; read the current terms page before shipping | — |
| ElevenLabs music | Commercial use licensed on Starter and above | [O] |
| Suno | Commercial rights only for songs made on a paid plan; not retroactive | [O/S] |
| Udio | Downloads disabled since Oct 2025 after label settlements; licensed app unconfirmed. Do not ship | [S] |

Sources: https://ai.google.dev/gemini-api/docs/image-generation · https://bfl.ai/pricing · https://stability.ai/license · https://huggingface.co/tencent/Hunyuan3D-2.1/blob/main/LICENSE · https://github.com/microsoft/TRELLIS.2 · https://hyper3d.ai/pricing · https://elevenlabs.io/pricing/api · https://suno.com/pricing

### Licence check per exact checkpoint

1. Record the exact weights file or API model ID, its licence text URL and the date you read it in the Model Register.
2. Check every axis the licence uses: commercial vs non-commercial variant, revenue or MAU threshold, territory exclusions, plan tier, and whether outputs or only weights are licensed.
3. Check dependencies that run at inference (renderers, encoders, upscalers). A permissive model can depend on a research-only library.
4. Check models a vendor chains internally where its docs name them; a 3D vendor's pose-normalising step has been seen calling a third-party image-edit model [inference].
5. A checkpoint that fails any axis is blocked in the wrapper, not just noted. In production one team excluded a non-commercial variant of an otherwise usable model this way.

## 2. Copyright in generated output (US)

- **Copyright Office Part 2 (2025-01-29):** prompts alone do not make output protectable; human selection, arrangement and modification can be [O].
- **Part 3 (training)** is still a pre-publication draft (2025-05-09); the Office's AI page shows no 2026 update [O].
- **Thaler v. Perlmutter:** Supreme Court denied cert on 2026-03-02, so the human-authorship requirement stands. **Allen v. Perlmutter** is undecided [S].
- **Implication [inference]:** an unedited generated sprite may not be protectable, so a competitor could copy it. Record human contributions (repaint, composition, selection among attempts, arrangement into sheets) per asset in the manifest, so the claim can be made later for hero assets.
- Other jurisdictions are not covered by research.

Source: https://www.copyright.gov/ai/

## 3. Performers and voices

**SAG-AFTRA Interactive Media Agreement** [S: law-firm summary of the full text, 2026-01-29]:
- Ratified July 2025 (95.04%), runs to 2028-10-31.
- Covers voice and visual **digital replicas**. Replicas made from non-union material, or by prompting with a performer's name, also need consent and bargaining.
- Consent must be clear, separate and written, with a reasonably specific description of use, including real-time generation (chatbots) and sensitive content. Consent generally cannot be taken at hire for future games.
- Pay is per generated line (about 10 words). A usage report is due within 90 days of release. Performers can suspend consent during a strike.
- Excluded: "traditional AI" (animation, rigging) and audio processing such as pitch or noise work.

Pipeline rules that follow:
- Never prompt with a real performer's or celebrity's name; ban those strings in the prompt linter.
- Designed voices (voice design from a text description) avoid cloning a person; cloning needs the written consent above even for non-union talent [inference].
- Keep per-line provenance (line id, model, voice id, date) so a usage report can be produced from the ledger.
- Voice vendors can refuse prompts that describe a child's voice. Plan adult voices for child characters, and never upload a child's photo or voice as a reference.

## 4. Store rules

### Steam (Content Survey)
- The AI section covers content that ships and that players consume (art, sound, narrative, localization); efficiency tools are not the focus. Rewritten around 2026-01-16/17 [S].
- **Pre-Generated** content is reviewed like any other content [O].
- **Live-Generated** content must also describe guardrails against illegal output; players can report illegal live output through the overlay (since 2024-01-10) [O].
- No live-generated AI in Adult Only sexual content [O].
- Disclosures appear on the store page [S].
- Whether the survey reaches store-page capsules and trailers: not covered by research; verify at the URL below before answering.

Sources: https://partner.steamgames.com/doc/gettingstarted/contentsurvey · https://store.steampowered.com/news/group/4145017/view/3862463747997849618 (overlay reporting, 2024-01-10)

### Apple App Store (guidelines last updated 2026-10-16) [O]
- **2.3.4:** App Previews "may only use video screen captures of the app itself". Generated footage goes to trailers and ads, never to App Previews.
- **1.2:** "AI content creation apps" need filtering, reporting, blocking and protections against non-consensual intimate imagery. This applies when the game generates content at runtime; hand off to the live-generation owner.
- **5.1.2(i):** disclose, and get explicit permission, before sending personal data to a third-party AI (for example a player photo sent to an avatar generator).
- Apple has no AI-disclosure question for pre-generated assets in the research; verify in App Store Connect before submission.

Source: https://developer.apple.com/app-store/review/guidelines/

### Google Play
- The AI-Generated Content policy covers apps that generate content from text, voice or image prompts. They need in-app reporting or flagging, and the policy bans non-consensual deepfake sexual content and scam voice or video of real people [O].
- An Aug 2026 Android blog post asks for custom input and output moderation [S].
- Rules for pre-generated assets and for generated footage in store preview videos: not covered by research; verify at the policy page.

Source: https://support.google.com/googleplay/android-developer/answer/14094294

## 5. EU AI Act Article 50 (transparency)

- **Applies from 2026-08-02** [O]:
  - 50(1): tell users they are interacting with an AI unless obvious (LLM-driven NPCs; owned by the live-generation seat).
  - 50(2): **providers** of generative systems must mark output in a machine-readable way.
  - 50(4): **deployers** must label deepfakes. For evidently artistic, creative or fictional works, disclosure only has to avoid hampering "the display or enjoyment" of the work.
- **AI Omnibus (in force 2026-07-27)** [O]: for generative systems already on the market before 2026-08-02, the 50(2) marking duty is due by **2026-12-02**. Annex III high-risk rules move to 2027-12-02, Annex I to 2028-08-02.
- **Code of Practice** on transparency and marking published 2026-06-10, with EU label icons [O].
- Fines up to EUR 15M or 3% of turnover [S].
- **Conflicts flagged by research:** one law firm says Article 50 moved to 2027-12-02; earlier drafts proposed 2027-02-02 or 2026-11-02; a Nov 2025 proposal said Feb 2027. The Official Journal text says 2026-12-02, and that grace period covers marking only.
- **Implications for a studio using vendor generators [inference]:**
  - The studio is usually a deployer, not a provider. Marking is the vendor's duty, but keep vendor watermarks and metadata on marketing media rather than stripping them.
  - Some image tools embed C2PA provenance data in their outputs (seen in production on one vendor's built-in image tool). Record whether it is present in the manifest; engine import and lossy encoding usually drop it from in-game files, which is fine for stylised art but not for realistic marketing media.
  - A trailer showing realistic generated people, places or events that could pass as real needs a deepfake label; stylised in-game art falls under the artistic-work carve-out.
  - A studio that ships its own fine-tuned generator inside the game may become a provider; route that to counsel.

Sources: https://eur-lex.europa.eu/eli/reg/2024/1689/oj (Regulation (EU) 2024/1689, amended by Regulation (EU) 2026/1744) · https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act · https://cms.law/en/bel/legal-updates/eu-ai-act-developments-key-political-agreement-on-the-digital-omnibus-on-ai-implementation-timeline-and-transparency-consultation

## 6. Building the store answers from the ledger

The disclosure is a query over the provenance manifest and the review ledger, not a memory exercise. Teams in the research planned this but had not shipped it, and both lacked any AI-disclosure wording at submission time, so treat the procedure as [inference] and test it on the first submission.

1. Select every asset in the release build (match by the shipped file's hash against `derived_sha256` in the manifest).
2. Keep only rows with a generated origin, grouped by content class (2D art, 3D models, animation, SFX, music, voice, narrative text, localization, marketing).
3. For each class record: models used, share of shipped assets that are generated, human modification level, and whether any content is generated at runtime.
4. Map to each store's questions: Steam Pre-Generated description; Steam Live-Generated guardrails (if any runtime generation); App Store and Play answers where a question exists; third-party content and rights answers only after a human confirms the vendor terms rows.
5. Store the generated answer text with the release's git SHA and ledger hash. Re-run on every content update; a LiveOps drop with new generated art changes the answer.

```
STORE AI DISCLOSURE WORKSHEET        release: [version]   ledger hash: [sha256]   built: [date]
Class         Shipped assets  Generated  Models (exact IDs)        Human work               Runtime gen?
2D art        [n]             [n]        [ids]                     [repaint/composite/none]  no
3D models     [n]             [n]        [ids]                     [retopo/rig/none]         no
SFX           [n]             [n]        [ids]                     [edit/mix]                no
Music         [n]             [n]        [ids or none]             [arrangement]             no
Voice         [n]             [n]        [ids]                     [direction]               no
Marketing     [n]             [n]        [ids]                     [edit]                    n/a
Steam Pre-Generated text: [generated paragraph]
Steam Live-Generated: [none | guardrail description from the live-generation owner]
Vendor terms rows confirmed by: [human name or role]   date: [yyyy-mm-dd]
```
