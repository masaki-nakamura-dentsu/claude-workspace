---
name: feedback_ai_tips_content_curation_criteria
description: "Masaki's Good/Bad criteria for which AI-news items belong in the weekly AI Tips digest ([[ai_teams_weekly_digest]]) — filters for GBC (advertising agency) staff-usable tips on work efficiency/marketing/client work, rejects product-news, off-industry, vendor-selection, and safety/governance content"
metadata:
  type: feedback
  originSessionId: 86655793-9c0c-4cdd-867b-e20342b361f7
  modified: 2026-09-29T02:01:26.123Z
---

Stated explicitly 2026-08-19 after reviewing a test digest generated from ITmedia AI＋/AINOW RSS items: "技術的な更新は局員の業務内容(業務効率、マーケティング使用、クライアント案件)に対してのTipsになっていない" (purely technical/news updates aren't tips for staff's actual work — efficiency, marketing use, client work). He rated 13 real topics Good/Bad and said he'll keep giving this feedback going forward, expecting it to be learned and applied — this should shape the automated prompt itself, not just be a one-off note, since [[ai_teams_weekly_digest]]'s weekly job runs headlessly with no human review step before posting.

## The 13 rated examples (verbatim topic titles)
**Good:**
- 原始人風プロンプト検証 (a concrete prompt-engineering technique: terse/blunt phrasing to cut token usage — directly usable, testable technique)
- AIペルソナでマーケ課題解消 (AI persona used to solve a real marketing problem — direct marketing use case)
- AIエージェント失敗事例4選 (concrete failure case studies — practical lessons, not abstract)
- AIエージェントのマーケ活用10選 (a list of concrete marketing use cases)
- 総務業務でのAIエージェント活用 (a concrete use case in a business-operations function GBC staff can relate to)

**Bad:**
- Google公式AIエージェント教材 (official teaching material/curriculum announcement — not a usable tip)
- AI利用料コストを一元管理 (a cost-management tool/product launch — vendor news, not a usage tip)
- AIエージェントでCAD/CAM連携 (manufacturing-industry-specific — irrelevant to an advertising agency)
- 業務効率化の鍵は生成AI以外 (a contrarian opinion piece about efficiency, not actually about how to use AI)
- AIエージェントの安全対策事例 (AI safety/governance case study — policy-oriented, not a usage tip)
- AIエージェント製造業活用7工程 (manufacturing-industry-specific again — off-industry)
- 生成AIチャットボット選定軸 (vendor/tool selection criteria — procurement-oriented, not "how to use it")
- AIエージェントの選定基準 (same pattern — selection/comparison criteria, not a usage tip)

## Additional Good example, 2026-08-19 (refines the rule below)
Masaki flagged this article as interesting even though it wasn't in the original 13-topic test batch: [味の素「ほんだし」ラベル崩れ事例](https://www.itmedia.co.jp/aiplus/article/2608/17/2000000564/) — Ajinomoto posted an official X (Twitter) product photo where AI image editing (brightness/background changes) garbled the product label text, drew public criticism, and required a public apology. His stated reasons: **it involves a real, recognizable client brand (味の素)**, and **SNS posting/creative execution is literally advertising-agency work** (i.e. GBC/dentsu staff do this exact kind of task for their own clients).

This shows "Good" isn't limited to explicit how-to techniques — a **real-world case study (even a failure/cautionary one) involving a recognizable brand and an agency-relevant task (SNS content, creative execution, client-facing output)** counts as Good too, for the same reason "AIエージェント失敗事例4選" was rated Good in the original batch: concrete, real-stakes lessons are valuable even without a reusable prompt attached. **How to apply**: when the extraction prompt encounters an article about a named real brand/company doing something with AI in a marketing/creative/SNS context — success or failure — lean toward keeping it, not just pure "here's a prompt technique" content.

## Confirmation, 2026-08-19 (all 4 topics rated Good)
After [[continuous_data_capture_setup]]'s teams_daemon.py community-channel bug fix started surfacing real content from the newly-added channels, a fresh test digest with 4 topics was rated **all Good** by Masaki: the 3 already-validated web topics (caveman prompt, Ajinomoto AI-persona marketing, AI-agent marketing use cases) plus a new one — **「過去動画アーカイブをAIで解析」** (a colleague building an automated pipeline to scene-split video archives and analyze them with LLMs/OpenCV for cut-sheet generation) sourced from the newly-fixed 生成AI活用・業務効率化Tips channel. This confirms the "業務効率化" (work-efficiency) category of the rule extends to fairly technical internal tool-building content, not just marketing/client-facing tips — the deciding factor is still "would this help a GBC staff member's actual work," not the topic's technical depth. No new exclusions to add from this round; the filter is holding up well across both web-sourced and Teams-sourced content.

## Major refinement, 2026-08-24: "concrete transferable technique" is the real deciding factor, not just topic category
Masaki rated a 12-topic digest (2026-08-24 週, sourced entirely from ITmedia AI＋/AINOW since Teams channels had little new content that week). 7 Good, 5 不要 (not needed):

**Good**: 動画アーカイブをAIで解析(具体的なツール構成: シーン認識→LLM/OpenCV解析→JSON出力)、簡潔な指示でトークン65%減(Cavemanという具体的なプロンプト技法)、AIペルソナで壁を突破(NEC BestMoveというツール名+AIペルソナ生成という具体的手法)、AIで広告マーケ施策10選(具体的な10ユースケースのリスト)、AIに業務知識を教える工夫(熟練者の知識をAIに移管し誤情報を克服する具体的な工夫)、社内用語をAIに橋渡し(社内用語の壁を越えるための具体的アプローチ)、AIで生成AIの品質判定(LLM as a Judgeという手法+その3要素)

**不要**: Gemini活用でAI定着(首都高速道路、「工夫により10倍に」と書いてあるだけで具体的な工夫の中身が書かれていない)、AIでnote記事を量産(エイベックス松浦氏の個人的な体験談、業務に転用できる技法が無い)、口コミ作文をAI支援(カインズの機能リリースニュース、使い方ではなく製品発表)、対話型AI研修で定着(愛知県西尾市の研修プログラム紹介、AI活用技法そのものではなく人材育成施策の話)、AI推薦は事前に決定(ChatGPTの推薦の仕組み解説、面白い豆知識だが「どう使うか」という実践的technique が無い)

**新しい判断軸**: これまでの「業務効率化/マーケ/クライアント業務に関連するか」という大枠に加えて、**「具体的で真似できる技法・手法・プロセスが書かれているか」が決定的に重要**。実在企業の事例紹介という体裁であっても、結論が「〇〇という工夫で成功した」で終わり、その工夫の中身(具体的に何をしたか)が書かれていなければ不要判定になる。逆に、事例の形を取っていても、使ったツール名・具体的なプロンプト/プロセス・克服した課題への対処法など「読者が明日から真似できる要素」が含まれていればGoodになる。単なる製品リリースニュースや、人材育成プログラムの紹介、AIの仕組み解説(使い方の提案を伴わないもの)、個人の体験談は、たとえAI関連であっても「技法」が無ければ不要。

## Major feature addition, 2026-08-24: "how_to_try" — don't just summarize, tell the reader how to replicate it themselves
After rating the 12-topic digest, Masaki added a further requirement: ITmedia-style articles describe "company X did Y with AI" but staff actually want to know **how to replicate it themselves with their own ChatGPT/Copilot right now**. His concrete example: the "LLM as a Judge" (AIで生成AIの品質判定) topic was interesting, but the real question is "what prompt would I actually type into ChatGPT to try this myself?"

**Implementation**: added a `how_to_try` field to the digest JSON schema (`weekly_ai_digest.py`'s `build_structured_prompt()`), instructing claude to write a concrete, copy-pasteable example prompt/instruction for each topic — not just repeat the summary, but bridge from "here's what they did" to "here's what you'd type." Rendered in the digest with a green "▶ 試してみる:" line under each topic's summary. If a topic's underlying technique can't reasonably be turned into a concrete prompt (e.g., it's pure news/product-announcement content with nothing to replicate), the rule instructs not adopting that topic at all — this reinforces the "concrete transferable technique" rule above rather than being a separate concern.

**How to apply going forward**: every future digest topic should read as "what happened + what you'd literally type to try it" — a summary alone, however well-written, is not sufficient on its own. Verify each digest still includes a `how_to_try` line per topic when checking output quality.

## Second major refinement, 2026-08-24 (same day): switched to 10-point scoring, revealed two more dimensions
Masaki rated a 5-topic supplementary digest (sourced from newly-added Akiyama Yuta/KEITO/Web担当者Forum) on a 10-point scale instead of Good/不要:
- AI検索での発見力向上術(GEO/AIO手法) → 7点
- AIで1ヶ月分のSNS投稿作成(Genspark活用) → **5点「目新しさがない」**
- PDFをAIで要約・分析 → **5点「目新しさがない」**
- AIでレシート精算・資料作成 → **3点「我々の部署では使わない需要」**
- AI感を消すデザイン術(ブランドのデザインシステムをAIに移植する技法) → **9点**(最高評価)

**New dimension 1 — Novelty (目新しさ) matters, not just topical relevance/concreteness.** "SNSの投稿をAIで1ヶ月分作る" and "PDFをAIで要約する" are both legitimate, on-topic, concrete-technique topics (would have passed the earlier "Good" bar) — but scored only 5/10 specifically because they describe generic capabilities most people already know ChatGPT/Copilot can do. The 9-point topic (AI感を消すデザイン術) won because it taught a **specific, non-obvious technique** (feeding an AI a brand's existing design system/reference images to strip the "generic AI look" from generated creative) — something a reader would NOT already assume was possible or know how to do. **Going forward: prefer topics that teach something surprising/non-obvious over topics that just demonstrate an already-famous AI capability, even when both are concrete and on-topic.**

**New dimension 2 — Department-specific relevance, not just "is this AI+business."** The 3-point item (AI-powered receipt/expense processing) is a legitimate, concrete, novel-ish technique, but scored low because expense/receipt admin work is **not something GBC's marketing/client-facing team actually does** — it's generic back-office/accounting work outside their scope. This sharpens the earlier "業務効率化" category: it must be efficiency **for the kind of work this specific team does** (marketing execution, client account work, creative production), not just any office task an AI happens to be good at.

**How to apply**: when curating, ask two extra questions beyond "is it concrete and on-topic": (a) would a reasonably AI-literate GBC staff member already assume this is possible, or does it teach something they'd be surprised by? (b) is this specifically the kind of task GBC's marketing/advertising/client-facing staff do, not generic office administration that could apply to literally any department? Weight both against the existing "concrete transferable technique" bar (see the refinement above) — all three together now form the real filter.

## Third refinement, 2026-09-01: tool/feature accessibility within GBC's actual work environment matters
Masaki rated a 4-topic digest on a 100-point scale:
- AIモデルでSNS動画量産(Filmora使用) → **60点「Filmoraは会社で使えないので実践的ではない」**
- ChatGPT Workで代理操作 → **70点「面白くて目新しい話だが、ChatGPT Workはうちの社員全員が使えるわけではない」**
- GA4でAI経由流入を計測(新チャネル「AI Assistant」) → **80点「管理画面を見てもまだ追加されていなかったが、今後活用できそうなTipsなので点数が高い」**
- 生成AIで動画を記事化(YouTube→記事) → **70点「今のところYouTubeから記事を作るという需要はない。今後可能性はある」**

**New dimension 3 — actual tool/access availability to GBC staff, distinct from topical relevance or technique concreteness.** A technique can be concrete, novel, and on-topic and still lose points if the specific tool it depends on isn't usable in practice:
- Filmora is blocked/unusable at the company entirely → biggest penalty (60点), even though the 3-step how_to_try was concrete and well-formed.
- ChatGPT Work is interesting/novel but only some staff have access → moderate penalty (70点), scored higher than Filmora because novelty partially offsets the access gap.
- GA4 is a tool GBC staff already use daily for client reporting, and the new "AI Assistant" channel — even though not yet visible in Masaki's own admin panel — will land inside that same familiar tool and feeds directly into existing client-reporting work → scored high (80点) despite not being immediately usable today. Being "coming soon to a tool we already use for this exact task" outweighs "not usable yet."

**New dimension 4 — current vs. future demand, called out explicitly.** The video→article topic scored 70 with the explicit reasoning "no demand for this right now, but possible in future" — distinguish this from dimension 3's access-blocked case: here the technique/tool is usable, but there's simply no current business need for this specific use case within GBC's work. Both "blocked tool" and "no current need" reduce score below topics with immediate applicability, but neither drops a topic to reject-tier if the underlying idea has future potential — it becomes a mid-range score (60-70) rather than a rejection.

**How to apply**: beyond concreteness/novelty/department-relevance (dimensions above), now also weigh: (a) is the required tool/feature actually accessible to GBC staff today (fully available > partially available to some staff > blocked/unavailable), and (b) is there a tool already in GBC's existing toolkit (e.g., GA4, Office/Copilot) that this rides on, which raises the score even if the specific feature hasn't rolled out yet — vs. requiring adoption of an entirely new, currently-inaccessible tool. Also separately note when demand is "not yet needed but plausible later" as a moderating (not disqualifying) factor.

## The underlying rule (inferred, to be refined as more feedback arrives)
Keep only items that give GBC (dentsu advertising-agency) staff something **directly actionable in their own work** — a technique, prompt, or concrete use case for **work efficiency, marketing execution, or client account work**.

Reject:
1. **Product/vendor news** — a company launching a tool or service, even AI-related, is not a "tip" (e.g. cost-management SaaS launches, editor feature announcements).
2. **Off-industry content** — use cases specific to manufacturing, CAD/CAM, or other industries GBC staff don't work in.
3. **Selection/comparison/procurement content** — "how to choose a chatbot," "agent selection criteria" — these help someone buying a tool, not someone using AI to do their job.
4. **Safety/governance/policy content** — AI safety measures, risk mitigation case studies — not usage tips.
5. **Meta/abstract educational material** — official curricula, high-level "learn AI agents" guides without a concrete applicable technique.

Keep:
- Concrete prompt/technique demonstrations (even quirky ones like the "caveman prompt" token-savings trick)
- Marketing-specific AI use cases (persona generation, campaign ideation, etc.)
- Failure-case studies with a lesson attached (what went wrong and why — still actionable)
- Use cases in business-support functions relatable to GBC staff (general affairs, back-office, client-facing work)
- Real-brand/real-client case studies (success or failure) in marketing/creative/SNS execution — e.g. a named company's AI-generated social post going wrong — even without a reusable technique, because the client-relevance and agency-relevant task (SNS/creative output) themselves make it valuable

## Fourth refinement, 2026-09-07: cross-week repetition penalty, and influencer-content is out of scope entirely
Masaki rated the 2026-09-07 digest (6 topics, ChatGPT for PowerPoint add-in tips + web/Teams sourced) on a 100-point scale:
- 選択範囲に直接AI編集(ChatGPT for PowerPoint、選択中のテキストボックスに直接書き込み) → **95点**
- 内容そのまま配色だけ統一(ChatGPT for PowerPointでデザインテーマだけ統一) → **85点「実際にやってみたところまずまずの出来だった」**
- デッキの論理構成をAIに点検(ChatGPT for PowerPointでストーリー展開をレビュー) → **95点**
- AIに反論させる壁打ち術(Claude/ChatGPTに辛口批評させる) → **90点**
- AI検索での自社ブランド確認法(Ahrefs Brand RadarでChatGPT/Gemini/Perplexity比較) → **75点「前回も似たような例があった」**
- AIインフルエンサー制作術(Flovaでキャラクター企画→画像→動画生成) → **60点「我々はインフルエンサー制作をしない」**

**New dimension 5 — week-over-week repetition penalizes even a genuinely good topic.** The Brand Radar/AI検索順位トピック is concrete, on-topic, and would pass every existing filter, but scored only 75 because a similar "AI検索での見え方をモニタリングする"系の話題already appeared in an earlier round (2026-08-24 test digest, dimension-1 example: 「AI検索での発見力向上術(GEO/AIO手法)」→7点当時). This is distinct from the existing intra-digest `dedupe_topics()` mechanism (which only catches duplicates *within the same run*) — this is duplication *across separate weekly runs*, which nothing was checking for before. **Fix applied same day**: added `load_recent_topic_titles()` to `weekly_ai_digest.py`, which reads the `## ` headings out of the last 4 archived digest `.md` files in `OUTPUT_DIR` and injects them into the extraction prompt as a "already covered — treat same-angle content as a repeat even from a different source article, downgrade or exclude unless there's a genuinely new data point/development" instruction. (Hit a Dropbox-sync Unicode-normalization gotcha while implementing: the hardcoded Japanese filename-prefix pattern in a `Path.glob()` call silently matched zero files because the literal's NFC form didn't match the on-disk NFD-normalized filename — fixed by globbing all `*.md` in that dedicated output folder instead of pattern-matching the Japanese substring.)

**New dimension 6 — a topic can be concrete, novel, AND properly "AI activity" and still be excluded solely because GBC doesn't perform that function.** AIインフルエンサー制作 is a legitimate, detailed, replicable AI workflow (character sheet → image gen → video gen), but scored only 60 for one reason: GBC doesn't produce influencers as a service. This is the same underlying principle as the existing 経費精算/back-office exclusion (dimension 2), but the earlier framing ("is this GBC's marketing/client-facing work vs. generic office admin") didn't obviously cover influencer content, since influencer marketing sounds adjacent to advertising work — it required this explicit correction to realize GBC specifically does not do influencer *production* (only categories that sound advertising-adjacent get a pass by default; must check the specific department's actual service scope, not just "is this marketing-flavored"). **Fix applied same day**: added an explicit exclusion rule to `build_structured_prompt()` for AI-influencer/AI-character content creation topics.

**Secondary confirmation**: the 85-point topic's reasoning ("実際にやってみたところまずまずの出来だった") is the first case of Masaki actually testing a suggested `how_to_try` technique himself and reporting back the real-world result — validates that the `how_to_try` field (added 2026-08-24) is achieving its intended purpose of genuine reproducibility, not just reading well.

## Fifth refinement, 2026-09-07(同日続き): 製品特化トピックへの偏りはNG、汎用ChatGPT/Copilot技法と同程度欲しい
2026-09-07のダイジェスト(6トピック中3件がChatGPT for PowerPointアドイン関連)を見た直後、ユーザーから「Office製品だけの情報はNGです。通常のChatGPTやCopilotの使い方も同じぐらいTipsが欲しい」との明示的フィードバック。

**New dimension 7 — digest-level composition balance, distinct from per-topic quality.** これまでの基準(具体性/目新しさ/部署関連性/ツールアクセス可能性/週またぎ重複)はすべて個々のトピックの採否を判定する軸だったが、今回のフィードバックは**ダイジェスト全体の構成比**に関するもの——個々のトピックの質が高くても(実際、Office添加関連の3件は85-95点と好評価だった)、特定の1製品(PowerPoint add-in)に偏りすぎると全体としては不満が出る。「Office製品限定の技法」と「ChatGPT/Copilotを素で使う汎用プロンプト技法(特定Office製品に依存しない)」を同程度の比率で入れてほしい、という要望。

**Fix applied same day**: `build_structured_prompt()`に構成バランスのルールを追加——Office特化トピックが全体の半分を超えないよう、汎用プロンプト技法を優先的に採用するよう指示。ただしこのルールはLLM抽出パス(`build_structured_prompt()`)にのみ効き、[[ai_teams_weekly_digest]]の「手動発掘Tips差し込み」機構(`manual_staged_topics.json`)経由で追加されるトピックはこのプロンプトを通らずコード側で直接マージされるため対象外——**今回の偏りの直接原因は、2026-09-02にユーザー依頼で仕込んだChatGPT Office Add-in Tips3件が今週の枠にそのまま乗ったこと**。今後、手動でTipsを発掘・stagingする際(WebSearchで探して`manual_staged_topics.json`に追記する作業)は、Claude自身が構成バランスを意識し、特定の1製品/1機能に偏った候補を3件以上まとめて仕込まない、汎用的なプロンプト技法も混ぜる、といった判断を人手で行う必要がある(コード側の機械的なチェックは無い)。

## Sixth refinement, 2026-09-14: Gemini/Google Workspace is NOT a company-standard tool; upper-tier/special-model techniques don't reliably transfer to ChatGPT Enterprise
Masaki rated the 2026-09-14 digest (3 topics, all web-sourced) on a 100-point scale — all three scored in the mediocre 60-65 range, the first week where every single topic hit the same underlying problem:
- 3Dシミュレーターを対話だけで自作(ChatGPT Pro「Astra」系の特殊モデルで3D空間を再現) → **65点「Astro(Astra)は会社契約では使えない。通常のChatGPT Enterpriseをやっても、正しいものが出力されなかった」** — Masaki actually tried the digest's own `how_to_try` translation on real ChatGPT Enterprise and it produced wrong/broken output.
- Deep Researchの意外な3活用法(Google Geminiの「Deep Research」機能) → **60点「会社標準のChatGPTやCopilotの話でないのが良くない。そうでなかったとしてもChatGPTやCopilotでのやり方を伝えるべき」**
- チャットだけで校正ツールを自作(Google Geminiの「Canvas」機能) → **60点、同じ理由**

**New dimension 8 — Gemini/Google Workspace is explicitly NOT a company-standard tool, contradicting the prior prompt text.** The existing `build_structured_prompt()` rule (added 2026-09-01, dimension 3) listed "会社で使える一般的なツール(ChatGPT/Copilot/Gemini/GA4等)" — grouping Gemini together with ChatGPT/Copilot as if equally standard. This week's feedback directly falsifies that: GBC's actual standard AI tools are **ChatGPT Enterprise and Microsoft 365 Copilot only** (aligned with [[feedback_gbc_ai_material_authoring_rules]]'s "電通で使えるツールのみ紹介"). The digest's own `how_to_try` for topics 2 and 3 gave Gemini-specific instructions ("Geminiで『Deep Research』を選び…", "Geminiで『Canvas』を開き…") instead of translating to ChatGPT/Copilot — this directly violates the 2026-08-24 `how_to_try` rule's original intent ("read as what you'd literally type into *your own* ChatGPT/Copilot") but the prompt text never explicitly forbade defaulting to the source article's own tool when that tool is Gemini.

**New dimension 9 — a technique depending on a premium/special model tier doesn't reliably transfer just because "ChatGPT" is a company-standard tool.** Topic 1 already had a properly-formatted ChatGPT/Copilot-translated `how_to_try` (satisfying the *format* of the existing rule), but the underlying capability (ChatGPT Pro's advanced "Astra"/3D-rendering model + an OpenAI API key for photorealistic rendering) is not available under the company's ChatGPT Enterprise contract — so the translation was well-formed but factually unreproducible, and Masaki found this out by actually testing it. This is a sharper version of dimension 3 (tool access availability, e.g. the Filmora case): it's not enough to check "is the tool name (ChatGPT) company-standard" — must also consider whether the *specific model/feature tier* the source technique relies on is plausibly within the Enterprise plan's feature set. When in doubt, the `how_to_try` should flag the uncertainty explicitly rather than presenting a confident reproduction claim.

**Fix applied same day**: rewrote the relevant `build_structured_prompt()` rules in `weekly_ai_digest.py`: (1) removed Gemini from the "generally usable tool" list, added an explicit rule that Gemini/Google Workspace features must either be translated to a genuinely-existing ChatGPT/Copilot equivalent or the topic must be rejected outright — never leave Gemini-specific instructions in `how_to_try`; (2) added a rule that upper-tier/special-model-dependent techniques (ChatGPT Pro-only models, API-key integrations, etc.) must either carry an explicit reproducibility caveat in `how_to_try` or be downgraded to the same low-priority tier as company-blocked tools (Filmora-style, dimension 3). py_compile passed; not yet verified against a live run with real new content (next opportunity: next Monday's digest, or whenever new relevant source material appears).

**How to apply going forward**: whenever curating this digest — automated or manual staging — treat "ChatGPT Enterprise" and "Microsoft 365 Copilot" as the only default-safe tools; anything else (Gemini, Claude web apps not in [[claude_playwright_setup]]'s own admin use, third-party AI apps) requires either a verified equivalent in one of the two standard tools or explicit exclusion. Don't trust a superficially well-formatted `how_to_try` as proof of reproducibility — the underlying capability itself must plausibly exist in the company's actual plan tier.

## Seventh refinement, 2026-09-27: consumer-facing AI feature topics are out even when marketing-adjacent; a policy-blocked feature is still worth reporting if the block itself is news
Masaki rated the 2026-09-27 digest (8 topics) on a 100-point scale:
- AI買い物代理人を模擬質問で検証 → **65点「我々の実務では使わなさそう」**
- Copilotが仕事の新OSに刷新 → **80点「今はまだ会社のCopilotには導入されていないようなので事前情報としては有用だが、今は使えないので80点」**
- ChatGPT内でDeepL直接翻訳 → **75点「確かにMCPは対応したが、電通はこの接続を認めていない。しかし、その確認ができたので75点」**
- AI使用否定が発覚し炎上 → **80点「事例として有用」**
- 店頭AIポップが内部資料流出 → **85点「注意喚起事例として有用」**
- 聞き返すAIで顧客対応改善 → **65点「実務で利用しない内容」**
- バズ投稿の型をAIで解剖 → **65点「実務で利用しない内容」**
- 念のため一言は逆に非効率 → **90点「実務的」**(今回最高評価)

**New dimension 10 — a topic about a consumer-facing AI feature/product, even in a marketing-sounding wrapper, doesn't count as "usable" unless it's a technique GBC staff themselves would apply.** Three of eight topics scored 65 with the identical reason "実務で利用しない内容": an AI shopping-agent test, a conversational customer-support AI, and an AI analysis of what makes social posts go viral. All three *describe* an AI capability in a plausibly marketing-relevant space, but none hands the reader something to do in their own work — they're closer to "here's an AI feature end-consumers/other companies use" than "here's a technique you can run." This sharpens dimension 6 (GBC's actual service scope) further: being about marketing/CX/social topically is not sufficient — the topic must be something a GBC staffer would personally operate (a prompt, a workflow, a tool they'd use for a client or internal task), not an analysis/review of a product feature aimed at end users.

**New dimension 11 — a policy-blocked integration is still worth including specifically because confirming the block has informational value, distinct from a tool that's simply inaccessible.** The ChatGPT×DeepL MCP topic scored 75 (higher than earlier Filmora-style blocked-tool cases like 60-65) precisely because dentsu staff might otherwise assume this integration is usable and try it — reporting "this now exists technically, but dentsu does not permit this connection" answers a real question readers would have and prevents wasted attempts or policy violations. This differs from the existing dimension-3 "会社で使えないので優先度を下げる" rule (Filmora/Astra), which was about techniques that simply can't be reproduced — here the topic's value is centered on the access-restriction fact itself, not on the (unusable) how-to. **How to apply**: when a topic's core content is "a new AI integration/connector now exists between two tools" and one of those tools has a known company usage restriction, don't just downgrade it as a blocked-tool case — check whether reporting the restriction itself (so staff know not to attempt it) is the useful part, and frame the topic around that rather than around a how_to_try that can't actually be followed.

**Confirms existing rules without change**: Copilot rollout preview (80点) matches the GA4 precedent (dimension 3 — future feature in an already-standard tool still scores well even if not yet live); the two case-study topics (AI是認拒否炎上 80点, 店頭AIポップ内部資料流出 85点) confirm the real-brand/cautionary-case-study rule; the top scorer (念のため一言は逆に非効率, 90点「実務的」) is a plain concrete/practical technique matching the core bar.

**Fix applied same day**: added dimension 10 (consumer-facing AI feature ≠ usable technique) and dimension 11 (policy-blocked integration still valuable as a restriction-confirmation) to `build_structured_prompt()` in `~/TeamsExport/scripts/weekly_ai_digest.py`.

## Eighth refinement, 2026-10-05: how_to_try must be low-effort; GEO-type learning topics stay in for Masaki himself
2026-10-04号の評価: 「AI検索の出典を疑う」90点(誰もが陥る話で有用)/「指示文をAIに採点させる」75点(よくある定型プロンプト改善で、手間が多く局員が実際に使わなさそう。もっと簡単な「試してみる」に)/「AIが引用する第三者サイト特定」60点(AI学習者としては90点だが局員はGEO対応が少ない。ただし本人が学びたいので今後もピックアップしてほしい)。

**New dimension 12 — how_to_tryの手軽さ**: 再現可能でも、表作成→再検索→再検証のような多段手順は局員が実行しない。コピペ1回(最大2ステップ)で効果が分かる形にする。定型的なプロンプト改善術ほど手順の軽さで差がつく。
**New dimension 13 — 読者は局員だけでなく編集者本人(中村さん)でもある**: GEO/LLMO等のAI学習者向け先端トピックは、局員向けスコアが低くても1配信1件程度は継続採用する(除外ルールで落とさない)。
**Fix applied same day**: 両ルールを`build_structured_prompt()`に追加(py_compile OK)。

## Ninth refinement, 2026-10-14: ライセンス保有率・対象者の広さ・すぐ試せる新機能
2026-10-12号の評価: 会議・チャット自動ナレッジ化60点(ネタは今後も欲しいが局員全員がM365 Copilot契約ではない)/現場に書かせず一次情報記事化70点(Global Qチームには95点だが数名にしか効かない)/GA4×AI 65点(局員があまりやらない)/AI検索は第三者サイト勝負80点(過去の類似Tipsで減点)/回答を操作できる画面に(GPT-6 Intelligent UI)100点(実際に試して既に使えた。他のプロンプト例も欲しい)/ChatGPTに音声を直接投入80点(本当に今までできなかったか裏取りしたい)/AIの出力ブレを仕組みで防ぐ80点(実際にできるか確認したい)。

**New dimension 14**: M365 Copilot(会議Copilot等)はGBC全員が持っていない。how_to_tryはChatGPT Enterprise手順を主にする。
**New dimension 15**: 一部チーム/一部作業向け(記事執筆、GA4分析)は減点。採用時は対象者を明記。
**New dimension 16**: すぐ試せるChatGPT新機能は最高評価。プロンプト例を2〜3個並べる。
**New dimension 17**: 「これまでできなかった」系の記述は裏取り/出典の主張と明示(音声アップロードは2026-10-06リリースノート。以前は記録モード等で一部可能だった)。how_to_tryで使う機能は画面上の場所も添えて実行可能性を示す。
重複減点(dimension: cross-week repetition)はGEO枠でも適用されることを確認。
**Fix applied same day**: 上記をbuild_structured_prompt()に追加(py_compile OK)。

**追加プロンプト例(Intelligent UI、ユーザー承認2026-10-14、月次Tips資料などで再利用可)**: (a)A/B/C案比較表で評価軸の重みスライダー→総合点・順位が入れ替わる (b)出張準備チェックリスト、出発日入力で「〇日前までにやること」が並び替わる (c)提案内容の理解度クイズ5問、選択肢を押すと正解と解説。全文は`Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/Project_AI業務活用PJ/weekly_ai_digest/追加プロンプト例_IntelligentUI_20261014.md`。
**音声投入の裏取り結果**: 添付は2026-10-06のリリースノートからの新機能(以前は2025-06からの記録モードのみ)→ユーザー「であれば有用」。裏取りで評価が保たれた例。
**出力ブレ対策**: やりたい人がいたため、同僚向けの手順書`Work/GBC_戦略企画部/GBCインテリジェンス／知見機能/01_AI活用/Project_AI業務活用PJ/weekly_ai_digest/ChatGPTプロジェクトで出力ブレを防ぐ手順_20261014.md`を作成。


## How to apply
When [[ai_teams_weekly_digest]]'s `weekly_ai_digest.py` builds its structured-extraction prompt (`build_structured_prompt()` in `~/TeamsExport/scripts/weekly_ai_digest.py`), the filtering instructions should encode this Good/Bad pattern directly so the headless claude call self-filters before Masaki ever sees the output — he should not need to manually reject bad topics from every digest. As of 2026-08-19 this criteria was added to that prompt's rules section; as of 2026-09-07 it also includes a cross-week "already covered" topic list (`load_recent_topic_titles()`) and an explicit influencer-content exclusion; as of 2026-09-14 it also excludes Gemini/Google-Workspace-native instructions from `how_to_try` and flags upper-tier/special-model reproducibility risk; as of 2026-09-27 it also excludes consumer-facing-feature analysis topics and reframes policy-blocked integrations around the restriction-confirmation value rather than treating them as generically low-priority. **When Masaki gives new Good/Bad ratings in future sessions, update both this memory file (add the new examples so the pattern stays sharp) and the actual prompt text in `weekly_ai_digest.py`** — this is a living, refinable filter, not a one-time fix. When checking "is this dimension already covered," don't assume a category (e.g. "marketing-adjacent") passes by default — verify against GBC's actual service scope.

## Tenth refinement (2026-10-19, 10/18号の評価)
4形式出力100 / RFP壁打ち75 / AIペルソナ85 / アクセシビリティ=AI可読性90 / 指示文登録で自作エージェント70。
- 高評価: まだ局員が知らない使い方(HTMLで出力させる等)、今までに無い視点。
- 減点: 既出の定番(RFP壁打ち、指示文登録エージェント)。電通社内でも実施済みの手法(ペルソナ)は手法として新しくないが、他社事例ならニュースとして価値あり。
- 反映: build_structured_prompt()に上記ルール追加。既出見出しの参照を直近4→12ファイルに広げ、"Teams"を含むファイルだけに限定(手順書の見出しが混ざっていた)。
