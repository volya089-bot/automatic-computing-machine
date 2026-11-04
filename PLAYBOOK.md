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
