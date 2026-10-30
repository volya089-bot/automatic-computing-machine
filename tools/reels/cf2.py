"""CloseFast promo, batch 2: the social autoposting section, and an honest early-access angle.
CloseFast is a new product with no users or reviews yet, so nothing here implies social proof."""

URL = "cf.warrify.io"
SAY_URL = "cf dot warrify dot io"


def angle_autopost(theme, cid, min_len=None):
    c = {"id": cid, "theme": theme, "header": "CLOSEFAST - SOCIAL AUTOPOSTING", "scenes": [
        {"type": "big", "big": "1 listing", "sub": "= posts for 4 platforms", "size": 170,
         "say": ["You made a product. Now it needs a Reel, a TikTok, a pin and a post. Every single time."]},
        {"type": "ladder", "label": "FROM ONE PRODUCT, CLOSEFAST DRAFTS", "cap_y": 1500, "rows": [
            ["Instagram Reels", "script"], ["TikTok", "script"], ["Pinterest pins", "with product link"], ["X threads", "text"]],
         "say": ["CloseFast has a social autoposting section. From one product or link it drafts Instagram Reels, TikTok scripts, Pinterest pins and X threads."]},
        {"type": "big", "big": "on a schedule", "sub": "through your own connected accounts", "size": 130,
         "say": ["Connect your accounts once, and it publishes on a schedule you control, from the same dashboard as your Etsy shop."]},
        {"type": "big", "big": "your keys", "sub": "you choose the AI model and the cost", "size": 150,
         "say": ["It runs on your own AI keys, so you choose the model and see the cost in your own provider dashboard."]},
        {"type": "cta", "big": URL, "sub": "free plan, no card", "follow": "Brand new: tell us what to build next",
         "say": [f"Try it free at {SAY_URL}."]},
    ]}
    if min_len:
        c["min_len"] = min_len
    return c


def angle_new(theme, cid, min_len=None):
    c = {"id": cid, "theme": theme, "header": "CLOSEFAST - EARLY ACCESS", "scenes": [
        {"type": "big", "big": "0 reviews", "sub": "because it just launched", "size": 170,
         "say": ["CloseFast has zero reviews. Not because it is bad. Because it just launched."]},
        {"type": "big", "big": "built solo", "sub": "for Etsy & print-on-demand sellers", "size": 150,
         "say": ["It is a new tool, built by a solo founder, for Etsy and print-on-demand sellers."]},
        {"type": "ladder", "label": "WHAT IS INSIDE TODAY", "cap_y": 1500, "rows": [
            ["AI titles & 13 tags", "listings"], ["Competitor watch", "pricing"], ["Social autoposting", "IG, TikTok, Pins"],
            ["Etsy + Printify + Shopify", "1 dashboard"]],
         "say": ["Inside today: AI titles and tags, competitor watch, social autoposting, and Etsy, Printify and Shopify in one dashboard."]},
        {"type": "big", "big": "early users", "sub": "shape what gets built next", "col": "pos", "size": 140,
         "say": ["The first users decide what gets built next. Found a bug? Tell us, and it gets fixed."]},
        {"type": "cta", "big": URL, "sub": "free plan, no card", "follow": "Be one of the first",
         "say": [f"Be one of the first. The free plan needs no card. {SAY_URL}."]},
    ]}
    if min_len:
        c["min_len"] = min_len
    return c


CLIPS = []
for fn, key in [(angle_autopost, "autopost"), (angle_new, "new")]:
    CLIPS.append(fn("light", f"cf_{key}_ig"))
    CLIPS.append(fn("dark", f"cf_{key}_tt", min_len=61))
    CLIPS.append(fn("navy", f"cf_{key}_yt"))

PINS = [
    {"id": "pin_closefast_4", "kicker": "ONE ETSY LISTING, FOUR PLATFORMS", "title": "Autoposting",
     "stats": [["Reels", "Instagram scripts"], ["TikTok", "video scripts"], ["Pins", "with your product link"], ["Scheduled", "from one dashboard"]],
     "source": "", "footer": "CloseFast  |  start free at cf.warrify.io"},
    {"id": "pin_closefast_5", "kicker": "NEW TOOL FOR ETSY SELLERS", "title": "Early Access", "theme": "dark",
     "stats": [["AI listings", "titles + 13 tags"], ["Competitor watch", "and price suggestions"], ["Autoposting", "IG, TikTok, Pinterest"], ["$0", "free plan, no card"]],
     "source": "", "footer": "CloseFast  |  be one of the first: cf.warrify.io"},
]
