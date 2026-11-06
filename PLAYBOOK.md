# Owner's Math — content playbook (v4, Nov 2026)

Why this exists: in the first week every long video and short used the same template as dozens of
copycat "The Economics of Owning a ___" channels (10–200 views each). These rules make Owner's Math
look and sound like nobody else. Follow them for every new video.

## 1. Titles — our own voice, not the niche template
- Never use the suffix `| The Economics of Owning a ___`. Dozens of channels use it.
- Lead with the viewer's own money or a number they can picture: "Your $100 Dinner…", "Your $40 Fill-Up…".
- Write from the **customer's side of the counter**, then reveal the owner's math.
- One number, one surprise, under ~60 characters. No clickbait the video doesn't pay off.
- Before publishing, search YouTube for the exact title. If 3+ near-identical titles exist, rewrite.

## 2. Long-video structure
- 0:00–0:30: scene → surprising number → second, stranger number → the question. Then straight to the title card.
- **No agenda paragraph** ("In the next twenty minutes, you are going to see…"). It tells viewers how long
  it will take and lists the answers. Removed from every scheduled video on 4 Nov 2026 (`tools/cut_agenda.py`).
- No "So, you want to own a ___". Open the body with the customer's first moment (the receipt, the door, the pump).
- Re-hook every ~2–3 min with a new open question or number.
- **Retention data (6 Nov 2026, YouTube Analytics):** long videos lose 50–70% of viewers in the first 10–30 s
  (gym: 86% → 33% by 0:24; ghost city: 100% → 31% by 0:28), then the curve goes flat. Second dip at ~2:40–4:00.
  Shorts hold 70–85%, with the steepest drop after ~45 s.
- So: the first 30 s are the whole game. Rules:
  1. The question or promise is spoken by 0:10, not 0:40. No atmospheric scene-setting before it.
  2. No empty set / B-roll and no stick figures in the cold open — only the hero, numbers, and the question
     (`_tail.py` uses COLD_END: only hero-face fillers before the title card).
  3. No `bars='scope'` on the first shot (letterbox cuts the top label).
  4. Every data panel shows something within 1 s of its shot start (anchor it on the word, not before).
  5. Open loop on screen 0:01 → title card: a bottom chip "STAY FOR #N · <payoff>" (`tools/fix_hook.sh`).
  6. At ~40% of runtime (the start of a middle chapter): chip "COMING UP · <later payoff>", 6 s.
- Shorts: 25–40 s (nothing past 45 s). Description line 1 = "▶ Full video: <link>" once the long video is live;
  also set YouTube Studio → Related video.
- Vary the back half: "Two owners" and "5 rules to survive" must not appear in every video. Rotate endings
  (a case study, a viewer-math challenge, a "what we would do with $X").
- Keep: real sources named on screen, "illustrative" labels, the hero character, Owner's Math receipts.

## 3. Shorts — written as shorts, never cut from the long intro
Tool: `razgon-2d-studio/tools/make_short3.py` (spec examples in `razgon-2d-studio/shorts_v4/b*.json`).
- Frame 0 = the hook. The first spoken line **is** the on-screen title. No cover image, no pre-roll.
- 25–40 seconds, 6–9 lines, one idea.
- The signature: money lines print onto the **Owner's Math receipt** as they are spoken; the last line is the
  red TOTAL. This is our recognisable format — keep it.
- End on the payoff or a line that loops back to the first line. Never "watch the full video to find out".
- Every number must come from the long video's sourced script.

## 3b. Our hero and our look (not the competitors')
- The hero is ours: black round head, **green hoodie, green visor, pencil behind the ear, calculator badge**
  (`/home/claude/brand/hero0-3.png`, sheet `youtube/hero_sheet.jpg`). Same hero in videos, shorts and thumbnails.
- He is cheerful and reacts: points at the hook → is shocked by the cost → grins with cash at the TOTAL.
- Bright, warm look: shorts sit on the warm yellow→orange→teal gradient; footage gets a midtone lift
  (`curves 0.25→0.33, 0.6→0.75`, saturation ×1.3–1.4). No dark, gloomy frames.
- New long videos: render in a brighter studio style (golden / storybook), not the dark "dusk" grade,
  and give the hero more screen time with happy/funny reactions.

## 4. Topics — the customer's world first
Prioritise businesses the viewer uses weekly (they already have an opinion and a receipt):
grocery stores, vending machines, movie theaters, gyms, phone carriers, pharmacies, dentists, vet clinics,
fast-casual chains, pizza delivery, parking apps, theme parks, airlines' seat fees, concerts/ticket fees,
car insurance, rental cars, wedding venues, funeral homes, daycare, barbershops, nail salons.
Lower priority: industries viewers never touch as customers (casinos, airports) unless the angle is personal
("why the walk to your gate is so long").

## 5. Descriptions
- Line 1–2 = the hook question + main keyword (this is what search shows). Ko-fi link goes **below** the chapters.
- Keep: chapters, sources, disclaimer ("educational, not financial advice"), AI disclosure, comment question.
- Shorts captions: one-line hook + "For education only, not financial advice. Made with AI."

## 3c. One post per network (since 4 Nov 2026)
Never schedule one Metricool post to several networks. Each network gets its own post.
- **YouTube Shorts**: the v5 short (25-40 s, receipt, hero), 13:00 / 16:00 / 19:00 Rome, SEO title + tags.
- **TikTok**: same v5 file, own post at the same time; caption = hook line + one comment question +
  "Educational, not financial advice. Made with AI." + 2 topic tags + #businesstok #learnontiktok #ownersmath.
- **Instagram Reels**: a separate IG cut (`tools/make_reel_ig.py`, specs `ig_v1/q*.json`): 1080x1920, 30 fps,
  15-19 s, 0-1.5 s = only the shock number on black, cut/zoom every ~1.5 s, big yellow (#FFD60A) numbers,
  white 2-3 word captions, last line "Save this, so you don't forget the numbers", own cover (yellow on black).
  ONE reel a day at 19:30 Rome (20:30 Kyiv). Caption: 2 lines + yes/no question + disclaimer + 5 niche tags
  (no #money #business). isAiGenerated = true. No YouTube elements ("watch till the end", "full video on the channel").
- Metricool is on Starter (paid): the free plan allows only 20 publications/month and counts each network separately.
