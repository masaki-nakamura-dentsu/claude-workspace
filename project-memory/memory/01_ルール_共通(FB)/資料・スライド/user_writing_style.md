---
name: user_writing_style
description: "Masaki Nakamura's actual email/chat writing style, derived from 139 real sent emails (2026-01~07) — apply whenever asked to draft something 'in my style' / 私風に / 私っぽく"
metadata: 
  node_type: memory
  type: user
  originSessionId: b8fb3d93-93e1-4986-955c-081a6878f921
  modified: 2026-08-18T05:51:58.178Z
---

## When this applies
Whenever asked to write an email, chat message, or reply "in my style" (私風に / 私っぽく書いて / 私が書いたように), draft it using the patterns below instead of generic polite Japanese business writing. This applies in every chat/session, not just where it was first requested — it's a standing instruction, not one-off context.

Derived by filtering `~/OutlookExport/parsed_emails.jsonl` to messages where `from` actually contains `masaki.nakamura@dentsu.co.jp` (folder=SentItems alone is unreliable — many "sent" items are forwards where the visible text was authored by someone else). See [[local_work_data_export]] for the export location/regeneration method. Teams data (`~/TeamsExport/data/teams_messages.jsonl`) could NOT be used for this — the `author` field is null on every record (known bug in the scraper), so only email was analyzed.

## Opening line
First line is almost always just the recipient's name + honorific, on its own line, nothing else:
- `○○様` — standard, most common, works for both internal and external.
- `○○さま` — used interchangeably with 様, no strong pattern distinguishing them (roughly personal preference per thread, not formality level).
- `○○さん` — closer/more casual relationships.
- For groups/mailing lists: `GBC局員の皆様`, `ご担当者様`.

Second line (after a blank line) is a short self-ID/greeting, chosen by context:
- `お疲れ様です。中村(正)です。` — most common (22/139). Note the kanji 様 (never the hiragana さまです form), and the distinctive `中村(正)` self-reference — he uses this parenthetical to disambiguate from another Nakamura in the org. Use `(正)` when self-identifying in a way that could be ambiguous.
- `お疲れ様です。` alone — when already well known to the recipient, no self-ID needed.
- `お世話になっております。電通の中村です。` — for external/less-familiar contacts, states company name.
- `早速のご返信ありがとうございます。` / `早速のご確認ありがとうございました。` — when replying quickly to something just received.

## Body / tone
- **Short and to the point.** Median sent-email body is ~180 characters. Don't pad with throat-clearing — state the point in 1-3 short sentences/paragraphs.
- **Warm, not stiff keigo.** Polite business Japanese but not the most formal register: uses `了解致しました` (not かしこまりました), `申し訳ないです` (not 申し訳ございません), never uses 恐れ入ります. Friendliness over formality.
- **Liberal use of ！** for warmth even in business replies — e.g. `ご返信ありがとうございます！`, `先日はご一緒させていただきありがとうございました！`, `ご無理なさらず、ゆっくり休養ください！`. Roughly 1 exclamation mark per 1-2 short emails; more in casual/personal-relationship threads, fewer in formal external ones.
- **Double-period ellipsis (`。。`)** for a soft, slightly apologetic/hesitant tone — e.g. `お忙しい中申し訳ないです。。`, `失礼しました。。。`. This is a real habit, not a typo — reuse it when hedging.
- Bullet points (`*` / `・`) for structured/list info (steps, ingredients, folder contents), otherwise prose.

## Closing
- **Casual/internal**: sign-off is just the bare name `中村正樹` (no space between surname/given name, unlike the formal `中村 正樹` header format), often with no closing phrase at all for quick replies.
- **"Quick thanks" closer**: `取り急ぎ御礼まで。` / `取り急ぎご連絡まで。` — very common (22 occurrences) for brief acknowledgment replies.
- **Formal/external or first-contact**: closes with `何卒よろしくお願いいたします。` (or 致します — both used, ~46+72 combined occurrences, this is the single most common closing phrase) then the full signature block:
  ```
  Masaki Nakamura (Mr.)
  中村 正樹
  Global Business Center
  Dentsu Inc.
  masaki.nakamura@dentsu.co.jp
  ```

## English emails
Short and plain, same terseness as Japanese. Pattern: `Dear [First] san,` → 1-3 sentence body stating the ask/update directly → `Thank you.` No elaborate hedging or filler.

## Example (verbatim, for calibration)
Formal external delivery:
> 山本高之様
>
> お疲れ様です。中村(正)です。
> 先日は「GBCプロフィール写真撮影」にご参加いただきありがとうございました。
>
> 下記にて撮影した写真をお送りいたします。
> [link]
>
> 中には2つフォルダが有ります
> 「オリジナルサイズ」大きなサイズの写真で印刷時などに使用
> 「一般サイズ」長辺が2100pxで通常はこちらのサイズを使用
>
> 何卒よろしくお願いいたします。

Casual internal quick reply:
> 了解致しました。そうしましたら共有させて頂きます。
>
> 中村正樹

## Teams announcement / group-share style (議事録・お知らせ投稿)
Confirmed 2026-08-18 by comparing my draft of an AI活用PJ議事録 against what the user actually posted to the group. Distinct from the 1:1 email style above — this is for group updates/announcements shared to a whole team (Teams post, 議事録共有, etc.):
- **Extra blank lines between sections/paragraphs** — a full blank line (sometimes two) between every paragraph and before/after each `■` section, not just single line breaks. Visually airier than my default compact draft.
- **！ at the open and close specifically** — even though the body itself may stay plain: `ありがとうございました！` and `よろしくお願いいたします！` both got exclamation marks added where my draft had plain `。`. This matches the "liberal ！" pattern above but is even more consistent at these two bookend positions in group posts.
- **Section headers (`■`) are kept as short natural phrases, not meta-labels.** My draft used "■ 決定事項: Tips共有は「プッシュ型」で進めます" (labeling it as a decision-record); the user simplified to "■ 部員との共有は「プッシュ型」で" — drop the "決定事項:" framing, just state the topic.
- **Cuts internal-process details that don't matter to the external/group audience.** My draft included "Salesforceへの記録は必須にせず、無理のない範囲で進めます" (internal admin detail) — the user removed it entirely from the group-facing version. When drafting for a wider audience, prefer omitting internal tooling/process caveats that aren't the group's concern, even if they were discussed in the meeting.
- **Adds concrete detail where it helps the reader act, even if I hadn't included it.** The user added a parenthetical explaining *how* the Tips get produced ("社内のAI関連Teamsからの情報を自動収集したり、局員の業務内容と関連するTipsをAIと相談をしながら抽出") — don't over-trim useful mechanism detail in the name of brevity; cut process caveats that don't matter, but keep detail that clarifies what will actually happen.
- **Preserves nuance my summary flattened.** I wrote push-type as simply replacing the pull-type hearing approach. The user's version reframed it as push-as-a-hook-for-pull: "部員にTipsを紹介しつつ、それをきっかけに部員のAIお悩み相談や活用術の吸い上げを行う" — i.e. don't let a binary decision (A vs B) erase a "both, sequenced" nuance if that's what was actually decided.
- **States the sharing channel explicitly inline** even when it seems obvious from context (e.g. "共有の方法はTeamsで共有します。" as its own sentence).

**How to apply**: when drafting a group-facing summary/announcement (as opposed to a 1:1 email), default to this looser, warmer, detail-conscious style rather than the tighter email format above — more whitespace, bookend ！, headers as topics not labels, and re-check that internal-only asides have been cut while decision nuance has been kept.

## Refreshing this profile
If the user's style seems to have drifted or more data is needed, re-filter with:
```python
[d for d in jsonl_records if 'masaki.nakamura@dentsu.co.jp' in (d.get('from') or '').lower()]
```
on `~/OutlookExport/parsed_emails.jsonl` — do NOT trust `folder == 'SentItems'` alone.
