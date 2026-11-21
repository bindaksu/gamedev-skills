# Policy and Ratings for In-Game LLM Features

As of 2026-11; verify. Store rules, rating questionnaires and laws below change often and several dates fall within months of this snapshot. This is an engineering checklist, not legal advice: take the feature-to-obligation map to counsel before launch [inference].

Read this file at the design review of any runtime-generated text or voice feature, again before every store submission or rating questionnaire, and whenever a feature adds free-text or voice input, romance, a kids audience, or a performer's voice.

Tags: [official] official page read 2026-11-21; [official-snip] official URL seen only in a search snippet; [secondary] press or law firm; [unverified] weak or no source; [inference] this pack's reading. Numbers in brackets point to the source list at the end.

## 1. Feature-to-obligation map [inference, from the rules in sections 2 and 3]

| Feature trait | What it triggers | Build this |
| --- | --- | --- |
| Any text or voice generated at runtime | Steam Live-Generated disclosure with a description of guardrails; Google Play AI-generated content policy; EU AI Act Art. 50(1) notice; Apple 4.7 responsibility for chatbots not embedded in the binary | First-interaction notice; written guardrail description; in-game report button on every generated line |
| Players type or speak to the model | Play in-app reporting that works without leaving the app; Apple 1.2 filtering, reporting, blocking and published contact details if the app counts as an AI content creation app; Apple 5.1.2(i) if personal data goes to a third-party AI | Input moderation; consent prompt before the first cloud call; a choices-only path for players who decline |
| Player-to-player sharing of generated content | ESRB "Users Interact" and PEGI unrestricted-communication criteria cover user-to-user communication | Blocking and reporting; without them, PEGI 18 from June 2026 [secondary 49] |
| Romantic or sexual companion | Apple "Dating and Relationships" descriptor, minimum 18+, "whether scripted or generated"; Steam bans live-generated Adult Only sexual content; California SB 243 companion-chatbot duties | Hard-block sexual content in generated output or design the feature out; age gate |
| Mental health, self-harm, off-topic chat | California SB 243 exemption for game bots is lost if the bot can discuss these or hold off-topic conversations [secondary 54] | Keep replies on the game; block these topics and route to a scripted, non-generated response |
| Players under 13 | COPPA (amended rule, compliance date Apr 22 2026); Apple 1.3 Kids category bars personal or device information to third parties and third-party analytics | No third-party model on children's input [inference from 1.3]; choices or a closed on-device path; no free text |
| A performer's voice or likeness | SAG-AFTRA Interactive Media Agreement digital-replica terms, including real-time generation | Separate written consent naming the use; per-line pay and usage reports; a way to switch the voice off |
| Voice or video resembling real people | EU AI Act Art. 50(4) deepfake labelling; Google Play bans scam voice or video of real people | No real-person voices without rights; label any synthetic likeness |

## 2. Platform rules (as of 2026-11; verify)

| Body | Rule | Source |
| --- | --- | --- |
| Steam | The Content Survey splits AI content into Pre-Generated and Live-Generated. Live-Generated games must describe their guardrails against illegal content. The disclosure appears on the store page, and players can report illegal live output through the in-game overlay (since Jan 10 2024). Live-generated Adult Only sexual content is not allowed. The Jan 2026 rewrite says disclosure covers what players consume, not development efficiency tools | [official 27, 38]; [secondary 39] |
| Steam, cost | Steam's FAQ suggests building per-call costs into the price, or selling microtransactions, a subscription or an unlock DLC | [official 27] |
| Apple 1.2 | Covers "AI content creation apps": filtering, a report mechanism with timely responses, user blocking and published contact details. Random or anonymous chat apps may be removed. Wording on NCII is disputed (conflict 1) | [official 40, 41] |
| Apple 4.7 | Chatbots not embedded in the binary are still the developer's responsibility | [official 40] |
| Apple 5.1.2(i) | Disclose personal data sent to third-party AI and get explicit permission first | [official 40] |
| Apple 1.3 Kids | No personal or device information to third parties; no third-party analytics | [official 40] |
| Apple age ratings | New descriptors arrive in App Store Connect on Nov 16 2026 and must be answered by Jan 12 2027. "Dating and Relationships" covers a companion in romantic or sexual exchanges "whether scripted or generated", minimum 18+. AI assistants and chatbots count toward how often sensitive content appears | [official 41, 42]; [official-snip 43] |
| Apple DPLA | Section 3.3.8(I) sets requirements for using the Foundation Models framework | [official 41] |
| Google Play | AI-generated content policy: in-app reporting or flagging without leaving the app; prevent restricted content; scope names text-to-text chatbots that are "central" to the app. Bans non-consensual deepfake sexual content and scam voice or video of real people | [official 44, 45] |
| Google Play, Aug 2026 | Reinforced rules on non-consensual intimate imagery and adversarial testing; asks for custom input and output moderation | [official-snip 46] |
| ESRB | "Users Interact": "possible exposure to unfiltered/uncensored user-generated content, including user-to-user communications". The ratings guide has no AI-specific element | [official 47] |
| IARC | The globalratings.com homepage and two searches turned up nothing AI-specific | [unverified] |
| PEGI | Descriptors include Unrestricted communication, Safe Online Gameplay, Pressure to play, Time-limited offers, Paid random items and Cryptocurrency. From June 2026, fully unrestricted player communication (no blocking or reporting) means PEGI 18, and paid random items default to PEGI 16. AI chat is not addressed | [official 48]; [secondary 49]; AI chat [unverified] |
| Fortnite islands (platform precedent) | Rule 1.22 bans medical or mental-health personas, romantic companions and attempts to bypass safety systems for the Conversations feature | [secondary 32] |

How ratings treat an AI NPC is unsettled. Answer questionnaires for the worst output the guardrails allow through, not the intended script, and keep the eval evidence that bounds it [inference].

## 3. Law (as of 2026-11; verify)

### EU AI Act Article 50

- Applies from Aug 2 2026 [official 50].
- 50(1): systems that talk directly with people (chatbots, agents, avatars) must tell users from the start of the first interaction, unless that is obvious to a reasonably well-informed person [official 50]. The FAQ and guidelines landing page give no game or NPC example [unverified]. Default to disclosing [inference].
- 50(2): providers must mark output in a machine-readable way. For generative systems already on the market before Aug 2 2026, the deadline is Dec 2 2026 under the AI Omnibus (in force Jul 27 2026) [official EUR-Lex; secondary 51]; dates disputed (conflict 2).
- 50(4): deployers must label deepfakes; for clearly artistic or fictional works the disclosure only has to avoid hampering "the display or enjoyment" of the work [official EUR-Lex].
- A final transparency and marking Code of Practice came out Jun 10 2026, with EU label icons [official 55].
- Fines up to EUR 15M or 3% of turnover [secondary 51].
- Who is the "provider" when a studio wraps a vendor model is a question for counsel; the marking duty may sit with the model vendor, the studio, or both [inference].

### United States

- **COPPA:** amended rule, compliance date Apr 22 2026 [official-snip 52].
- **FTC:** 6(b) study of companion chatbots launched Sep 2025; no report found [official-snip 53].
- **California SB 243** (from Jan 1 2026): duties for companion chatbots and private lawsuits at $1,000 per violation. Game bots are exempt only if their replies stay on the game and they cannot discuss mental health, self-harm or sexual content or hold off-topic conversations [secondary 54]. Design to stay inside the exemption: on-topic output filter, topic blocks, eval category [inference].
- **Copyright:** the US Copyright Office says prompts alone do not make output protectable; human selection, arrangement and modification can. The Supreme Court denied cert in Thaler v. Perlmutter on Mar 2 2026, so the human-authorship rule stands [official 56; secondary for the cert denial]. Generated quest text may not be protectable; keep human-written spines [inference].

### Performer voices

SAG-AFTRA Interactive Media Agreement (ratified July 2025, runs to Oct 31 2028) [secondary: fkks.com law-firm summary dated 2026-01-29]:
- Covers voice and visual digital replicas, including replicas made from non-union material or by prompting with a performer's name.
- Needs clear, separate written consent with a reasonably specific description of use, including real-time generation (chatbots) and sensitive content. Consent generally cannot be taken at hire for future games.
- Pay is per generated line (about 10 words); a usage report is due within 90 days of release; performers can suspend consent during a strike.
- Excludes "traditional AI" (animation, rigging) and audio processing such as pitch or noise work.
- Hand casting, consent paperwork and voice direction to `gamedev-audio-designer`; usage reports need per-line counts from the turn trace [inference].

## 4. Templates

### First-interaction notice (shown before the first generated reply, in every language)

```
[Character] replies are written [and voiced] live by AI. They may be wrong or odd and do not
change your rewards. Tap [Report] on any reply that is offensive or broken.
[Talk] [Use dialogue choices instead]
```

### Third-party AI consent (Apple 5.1.2(i); show before the first cloud call)

```
To talk with [Character], what you type [or say] is sent to [provider] to create replies.
[Provider] [does / does not] keep it. Details: [privacy link].
[Allow] [Not now]   (Not now = dialogue choices; ask again only from settings)
```

### Steam Live-Generated guardrail description

```
Live-generated content: NPC dialogue [and voice] generated at runtime by [model class] through
our servers. The model cannot change game state: it proposes from a fixed list of actions that
game rules check. Player input and every generated sentence pass moderation for [categories]
before display or speech. Characters refuse unsafe requests in character. Per-player rate limits
and a server switch can disable the feature at once. Players can report any reply in game and
through the Steam overlay; reports are reviewed within [SLA].
```

### Report payload (what a report must capture)

```
report_id, player_id (pseudonymous), npc_id, feature, turn_id, timestamp, client_version,
pinned model ID, prompt slots hash, player input (as moderated), generated line, intent,
moderation scores, reason chosen by player, free-text note (optional, moderated)
```

Keep report data only as long as the review SLA and legal holds need; route abuse patterns to `gamedev-anti-cheat-security` and report metrics to `gamedev-analytics-engineer`.

## 5. Age-banded design [inference]

| Audience | Input | Model placement | Output |
| --- | --- | --- | --- |
| Under 13 (or unknown in a kids-directed game) | Pre-written choices only | On-device or none; no third-party model | Generated text from closed templates, or scripted lines |
| 13-17 | Choices plus filtered free text | Cloud with consent, or on-device | No romance, no sexual content, topic blocks per SB 243 exemption |
| Adults, age-verified | Free text and voice | Any, with consent | Romance only with the 18+ descriptor; still no live-generated Adult Only sexual content on Steam |

## 6. Pre-submission checklist

- [ ] Steam Content Survey: Live-Generated answered; guardrail description matches the shipped pipeline
- [ ] Apple: 5.1.2(i) consent before the first third-party call; 1.2 filtering, report, block and contact details where it applies; new age-rating questions answered before Jan 12 2027
- [ ] Google Play: in-app report or flag without leaving the app; adversarial test evidence on file
- [ ] Rating questionnaires (IARC, ESRB, PEGI) answered for the worst output the guardrails allow
- [ ] EU: first-interaction notice in every EU language; machine-readable marking plan agreed with the model vendor
- [ ] Kids: no third-party model on under-13 input; no free text for under-13
- [ ] SB 243: on-topic filter and mental-health, self-harm and sexual-content blocks in place and in the eval set
- [ ] Performer consent covers real-time generation; per-line counts available for usage reports
- [ ] Privacy policy names every AI provider and what each keeps

## 7. Conflicts to keep flagged

1. Apple 1.2 wording: the Oct 16 2026 news post says apps must "proactively prevent and remove" NCII [41]; the live guideline text has no "proactively" [40].
2. EU marking grace period: Dec 2 2026 (final Omnibus per CMS [51], and the Official Journal text per the research) versus Feb 2027 (a Nov 2025 proposal); one law firm (Goodwin) says Article 50 moved to Dec 2 2027. The Dec 2 2026 grace period covers marking only, not the 50(1) notice.
3. SAG-AFTRA charge over the Fortnite voice NPC: one gaming site reported it withdrawn; never confirmed [unverified].
4. Ratings bodies (ESRB, IARC, PEGI) have no AI-specific criteria found; answers rest on existing user-interaction descriptors [unverified].

## 8. Sources

- 27 https://partner.steamgames.com/doc/gettingstarted/contentsurvey
- 32 https://wccftech.com/fortnite-uefn-ai-npc-conversations-gemini-elevenlabs/ ; https://tweaktown.com/news/111153/
- 38 https://store.steampowered.com/news/group/4145017/view/3862463747997849618 (Jan 10 2024)
- 39 https://gamingonlinux.com/2026/01/valve-tweak-steam-ai-disclosure-form-for-developers-to-clarify-its-for-content-consumed-by-players
- 40 https://developer.apple.com/app-store/review/guidelines/
- 41 https://developer.apple.com/news/ (Nov 2 and Oct 16 2026 items)
- 42 https://developer.apple.com/help/app-store-connect/reference/app-information/age-ratings-values-and-definitions
- 43 https://developer.apple.com/news/?id=ks775ehf (Jul 2025)
- 44 https://support.google.com/googleplay/android-developer/answer/13985936
- 45 https://support.google.com/googleplay/android-developer/answer/14094294
- 46 https://android-developers.googleblog.com/2026/08/ensuring-safety-genai-preventing-non-consensual-intimate-content.html
- 47 https://esrb.org/ratings-guide/
- 48 https://pegi.info/page/pegi-age-ratings
- 49 https://rpclegal.com/snapshots/consumer/summer-2026/pegi-updates-age-ratings-and-interactive-risk-criteria-for-video-games/
- 50 https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act
- 51 https://cms.law/en/bel/legal-updates/eu-ai-act-developments-key-political-agreement-on-the-digital-omnibus-on-ai-implementation-timeline-and-transparency-consultation
- 52 https://federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule
- 53 https://ftc.gov/news-events/news/press-releases/2025/09/ftc-launches-inquiry-ai-chatbots-acting-companions
- 54 https://skadden.com/insights/publications/2025/10/new-california-companion-chatbot-law
- 55 https://digital-strategy.ec.europa.eu (Code of Practice on transparency and marking, Jun 10 2026)
- 56 https://copyright.gov/ai
- EUR-Lex: Regulation (EU) 2024/1689 (CELEX 32024R1689) and the AI Omnibus, Regulation (EU) 2026/1744
- SAG-AFTRA agreement summary: fkks.com law-firm summary, 2026-01-29 (secondary; no deep link captured)
