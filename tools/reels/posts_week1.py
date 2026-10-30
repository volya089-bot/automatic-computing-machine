"""Build the Metricool post list for week 1 (31 Oct - 7 Nov 2026) as JSON.

Each reel gets a caption assembled from its own voiceover lines plus its source line,
so the caption never claims anything the video does not."""
import json
import sys

import week1

RAW = "https://raw.githubusercontent.com/volya089-bot/automatic-computing-machine/media"
YT = "https://www.youtube.com/@OwnersMath-q8d"
TZ = "Europe/Rome"

TAGS = {
    "cw": ["#carwash", "#businessideas", "#smallbusiness", "#entrepreneur", "#businessmath"],
    "lm": ["#laundromat", "#businessideas", "#passiveincome", "#smallbusiness", "#entrepreneur"],
    "vm": ["#vendingmachine", "#sidehustle", "#businessideas", "#smallbusiness", "#entrepreneur"],
    "st": ["#selfstorage", "#realestateinvesting", "#businessideas", "#passiveincome", "#investing"],
    "cf": ["#coffeeshop", "#smallbusiness", "#businessideas", "#cafeowner", "#entrepreneur"],
    "atm": ["#atmbusiness", "#sidehustle", "#passiveincome", "#businessideas", "#smallbusiness"],
    "gym": ["#planetfitness", "#franchise", "#gymowner", "#businessideas", "#entrepreneur"],
    "cmp": ["#businessideas", "#smallbusiness", "#entrepreneur", "#businessmath", "#investing"],
}
SRCKEY = {"cw": "carwash", "lm": "laundromat", "vm": "vending", "st": "storage", "cf": "coffee", "atm": "atm", "gym": "gym"}
CMP_SRC = "The Hustle, ATM Depot, Cents, Toast, RecNation, MMCG Invest, SharpSheets"

# (date, hour, clip id) per network, plus Pinterest pins.
DAYS = [("2026-10-31", None), ("2026-11-01", "lm"), ("2026-11-02", "vm"), ("2026-11-03", "st"),
        ("2026-11-04", "cf"), ("2026-11-05", "atm"), ("2026-11-06", "gym"), ("2026-11-07", "cmp")]
PIN_KEY = {"cw": "carwash", "lm": "laundromat", "vm": "vending", "st": "storage", "cf": "coffee", "atm": "atm",
           "gym": "gym", "cmp": "compare"}

CLIPS = {c["id"]: c for c in week1.CLIPS}
PINS = {p["id"]: p for p in week1.PINS}


def says(clip):
    return [s for sc in clip["scenes"] for s in sc["say"]]


def caption_ig(clip, key):
    lines = says(clip)
    hook, body, cta = lines[0], lines[1:-1], lines[-1]
    src = CMP_SRC if key == "cmp" else week1.SRC[SRCKEY[key]]
    return (f"{hook}\n\n{' '.join(body)}\n\n{cta}\n\n"
            f"Source: {src}. Lines marked \"my math\" are my own arithmetic on those figures. Not financial advice.\n\n"
            + " ".join(TAGS[key]))


def caption_tt(clip, key):
    return f"{says(clip)[0]} " + " ".join(TAGS[key][:4])


def title(clip):
    t = clip["header"].title().replace(" - ", ": ").replace("'S", "'s").replace("Atm", "ATM").replace("Noi", "NOI")
    return t[:90]


def schedule():
    posts = []
    for date, key in DAYS:
        if key is None:  # Saturday: evening car-wash extras only (10:00 already queued)
            slots = [("18:00", "cw3_ig", "cw4_tt", "cw")]
            pins = [("14:00", "pin_carwash_1"), ("21:00", "pin_carwash_2")]
        else:
            pre = key
            slots = [("10:00", f"{pre}_ig1", f"{pre}_tt1", key), ("18:00", f"{pre}_ig2", f"{pre}_tt2", key)]
            pins = [("14:00", f"pin_{PIN_KEY[key]}_1"), ("21:00", f"pin_{PIN_KEY[key]}_2")]
        for hhmm, igid, ttid, k in slots:
            posts.append({"network": "instagram", "date": f"{date}T{hhmm}:00", "clip": igid,
                          "media": f"{RAW}/reels/{igid}.mp4", "text": caption_ig(CLIPS[igid], k)})
            posts.append({"network": "tiktok", "date": f"{date}T{hhmm}:00", "clip": ttid,
                          "media": f"{RAW}/reels/{ttid}.mp4", "text": caption_tt(CLIPS[ttid], k), "title": title(CLIPS[ttid])})
        for hhmm, pid in pins:
            p = PINS[pid]
            stats = "; ".join(f"{b} {lab}" for b, lab in p["stats"])
            kicker = p.get("kicker", "THE ECONOMICS OF OWNING A").title()
            posts.append({"network": "pinterest", "date": f"{date}T{hhmm}:00", "clip": pid,
                          "media": f"{RAW}/pins/{pid}.png",
                          "pinTitle": f"{kicker} {p['title']}"[:100],
                          "text": f"{stats}. {p['source']}. Full breakdowns on the Owner's Math YouTube channel."[:500],
                          "alt": f"Infographic: {kicker.lower()} {p['title'].lower()}. {stats}."})
    return posts


if __name__ == "__main__":
    json.dump(schedule(), sys.stdout, indent=1, ensure_ascii=False)
