"""CloseFast promo reels (Etsy / Printify sellers). Only product facts from the live page
(features, plans, prices) are used. The landing page's user counts, revenue-lift figures and
testimonials are deliberately left out because they could not be verified."""

URL = "cf.warrify.io"


def angle_listing(theme, cid, min_len=None):
    c = {"id": cid, "theme": theme, "header": "CLOSEFAST - AI FOR ETSY SELLERS", "scenes": [
        {"type": "big", "big": "13 tags", "sub": "and a title, for every listing", "size": 170,
         "say": ["Every Etsy listing needs a title and 13 tags. Writing them by hand, at midnight, is where the hours go."]},
        {"type": "ladder", "label": "WHAT CLOSEFAST DOES", "cap_y": 1500, "rows": [
            ["Writes SEO titles & tags", "in seconds"], ["Watches competitors", "24/7"], ["Suggests new prices", "auto"],
            ["Etsy + Printify + Shopify", "1 dashboard"]],
         "say": ["CloseFast writes SEO titles and tags in seconds, watches your competitors around the clock, and suggests new prices. Etsy, Printify and Shopify in one dashboard."]},
        {"type": "big", "big": "you approve", "sub": "nothing changes without your click", "size": 140,
         "say": ["It never changes a listing on its own. Every change waits in a queue for your one-click approval."]},
        {"type": "big", "big": "$0", "sub": "10 AI listings a month, no card", "col": "pos", "size": 220,
         "say": ["The Hobby plan is free forever. 10 AI listings a month, no credit card."]},
        {"type": "cta", "big": URL, "sub": "start free", "follow": "Free plan, no card needed",
         "say": [f"Try it free at {URL.replace('.', ' dot ')}."]},
    ]}
    if min_len:
        c["min_len"] = min_len
    return c


def angle_action(theme, cid, min_len=None):
    c = {"id": cid, "theme": theme, "header": "CLOSEFAST - DATA VS ACTION", "scenes": [
        {"type": "big", "big": "data ≠ done", "sub": "most Etsy SEO tools stop at a report", "size": 150,
         "say": ["Most Etsy SEO tools give you a report. Then you still write every listing yourself."]},
        {"type": "cols", "label": "WHO DOES THE WORK", "cols": [["research tool", 1, "you", "mute"], ["CloseFast", 3, "the agent", "acc"]],
         "say": ["CloseFast is built to act on the data. It drafts the listing, adjusts the price, and prepares social posts."]},
        {"type": "ladder", "label": "AGENTS THAT RUN FOR YOU", "cap_y": 1500, "rows": [
            ["Listing writer", "titles + tags"], ["Repricer", "vs competitors"], ["Arbitrage scout", "Etsy vs Shopify"],
            ["Social posts", "Pinterest, IG, TikTok"]],
         "say": ["There is a listing writer, a repricer, an arbitrage scout that compares Etsy and Shopify prices, and a social media module."]},
        {"type": "big", "big": "queue + approve", "sub": "or turn on Autopilot", "size": 130,
         "say": ["Decisions queue up for your approval. When you trust it, you can switch on Autopilot."]},
        {"type": "cta", "big": URL, "sub": "free plan, no card", "follow": "Free plan, no card needed",
         "say": [f"Start on the free plan at {URL.replace('.', ' dot ')}."]},
    ]}
    if min_len:
        c["min_len"] = min_len
    return c


def angle_plans(theme, cid, min_len=None):
    c = {"id": cid, "theme": theme, "header": "CLOSEFAST - PLANS & PRICES", "scenes": [
        {"type": "big", "big": "$0 to $499", "sub": "which CloseFast plan fits your shop?", "size": 140,
         "say": ["Which CloseFast plan actually fits your Etsy shop? Here is the whole price list."]},
        {"type": "ladder", "label": "PLANS", "cap_y": 1500, "rows": [
            ["Hobby", "$0 forever"], ["Starter", "$19 / mo"], ["Pro", "$49 / mo"], ["Lifetime", "$499 once"]],
         "say": ["Hobby is free. Starter is $19 a month. Pro is $49 a month. Lifetime is a one-time $499."]},
        {"type": "bars", "label": "WHAT YOU GET", "scale": 4, "rows": [
            ["Hobby: 10 AI listings / mo", 0, 1, "free", "mute"], ["Starter: 3 shops, unlimited", 0, 2, "$19", "acc"],
            ["Pro: + Autopilot 24/7", 0, 3, "$49", "acc"], ["Lifetime: all features", 0, 4, "$499", "pos"]],
         "say": ["Hobby gives you 10 AI listings a month. Starter covers 3 shops with unlimited listings and a 7-day free trial. Pro adds Autopilot around the clock."]},
        {"type": "eq", "lines": ["$499 / $49 a month"], "result": "about 10 months", "sub": "Lifetime vs Pro, my math",
         "say": ["Lifetime costs about the same as 10 months of Pro. My math."]},
        {"type": "cta", "big": URL, "sub": "start with the free plan", "follow": "Free plan, no card needed",
         "say": [f"Start free and upgrade only when you need it. {URL.replace('.', ' dot ')}."]},
    ]}
    if min_len:
        c["min_len"] = min_len
    return c


CLIPS = []
for fn, key in [(angle_listing, "listing"), (angle_action, "action"), (angle_plans, "plans")]:
    CLIPS.append(fn("light", f"cf_{key}_ig"))
    CLIPS.append(fn("dark", f"cf_{key}_tt", min_len=61))
    CLIPS.append(fn("navy", f"cf_{key}_yt"))

PINS = [
    {"id": "pin_closefast_1", "kicker": "AI FOR ETSY SELLERS", "title": "CloseFast", "theme": "dark",
     "stats": [["in seconds", "SEO titles & 13 tags"], ["24/7", "competitor watch"], ["you approve", "every change first"], ["$0", "10 AI listings/mo, no card"]],
     "source": "", "footer": "Start free at cf.warrify.io"},
    {"id": "pin_closefast_2", "kicker": "STOP WRITING ETSY LISTINGS BY HAND", "title": "CloseFast",
     "stats": [["Etsy", "+ Printify + Shopify"], ["1 dashboard", "for every shop"], ["Repricer", "vs your competitors"], ["Free", "Hobby plan, forever"]],
     "green": "Free", "source": "", "footer": "Start free at cf.warrify.io"},
    {"id": "pin_closefast_3", "kicker": "CLOSEFAST PLANS FOR", "title": "Etsy Sellers", "theme": "dark",
     "stats": [["$0", "Hobby, 10 AI listings/mo"], ["$19/mo", "Starter, 3 shops, 7-day trial"], ["$49/mo", "Pro, Autopilot 24/7"], ["$499", "Lifetime, one payment"]],
     "source": "", "footer": "Start free at cf.warrify.io"},
]
