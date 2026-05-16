import feedparser
import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

FEEDS = [
    # --- SEA Esports ---
    ("EsportsAsia SEA",       "https://esportsasia.com/rss/category/southeast-asia"),
    ("EsportsAsia News",      "https://esportsasia.com/rss/category/gaming-news"),
    ("ONE Esports",           "https://www.oneesports.gg/feed/"),
    ("ONE Esports MLBB",      "https://www.oneesports.gg/mobile-legends/feed/"),
    ("ONE Esports DOTA2",     "https://www.oneesports.gg/dota2/feed/"),
    ("ONE Esports Valorant",  "https://www.oneesports.gg/valorant/feed/"),
    ("AFK Gaming",            "https://afkgaming.com/rssfeed"),

    # --- Global Esports ---
    ("Dot Esports",           "https://dotesports.com/feed"),
    ("Dot Esports Valorant",  "https://dotesports.com/valorant/feed"),
    ("Dot Esports DOTA2",     "https://dotesports.com/dota-2/feed"),
    ("Dot Esports CS2",       "https://dotesports.com/counter-strike/feed"),
    ("Esports Insider",       "https://esportsinsider.com/feed"),
    ("Dexerto Esports",       "https://www.dexerto.com/esports/feed/"),
    ("Inven Global",          "https://www.invenglobal.com/feed"),
    ("HLTV",                  "https://www.hltv.org/rss/news"),

# Google News RSS 
("Google News — SEA Esports",      "https://news.google.com/rss/search?q=esports+southeast+asia&hl=en-US&gl=US&ceid=US:en"),
("Google News — MPL",              "https://news.google.com/rss/search?q=MPL+esports&hl=en-US&gl=US&ceid=US:en"),
("Google News — VCT Pacific",      "https://news.google.com/rss/search?q=VCT+Pacific+valorant&hl=en-US&gl=US&ceid=US:en"),
("Google News — MLBB Tournament",  "https://news.google.com/rss/search?q=mobile+legends+tournament&hl=en-US&gl=US&ceid=US:en"),
("Google News — DOTA2 SEA",        "https://news.google.com/rss/search?q=dota+2+sea+tournament&hl=en-US&gl=US&ceid=US:en"),
("Google News — Esports Events",   "https://news.google.com/rss/search?q=esports+tournament+2026&hl=en-US&gl=US&ceid=US:en"),
],

SEA_KEYWORDS = [
    "sea", "southeast asia", "malaysia", "indonesia", "philippines",
    "singapore", "thailand", "vietnam", "myanmar", "mpl", "mpl ph",
    "mpl id", "mpl my", "mpl sg", "m-series", "m5", "m6", "m7",
    "vct pacific", "pacific", "one esports", "afk gaming",
    "evos", "rrq", "onic", "fnatic sea", "team secret", "navi sea",
    "team liquid sea", "blacklist", "echo", "aurora", "alter ego",
    "talon esports", "paper rex", "valorant sea", "dota sea",
    "mdl", "pgl sea", "blast sea", "sea games esports",
]

ESPORTS_KEYWORDS = [
    "esports", "e-sports", "tournament", "championship", "league",
    "qualifier", "grand finals", "semifinals", "playoffs",
    "lan event", "major", "minor", "invitational", "cup",
    "valorant", "dota 2", "dota2", "cs2", "counter-strike",
    "mobile legends", "mlbb", "pubg mobile", "free fire",
    "wild rift", "honor of kings", "apex legends", "overwatch",
    "league of legends", "lol", "fortnite", "rocket league",
    "team", "roster", "player", "pro player", "coach",
    "prize pool", "bracket", "group stage", "bo3", "bo5",
]

ALL_KEYWORDS = SEA_KEYWORDS + ESPORTS_KEYWORDS

def is_relevant(entry):
    text = (
        entry.get("title", "") + " " +
        entry.get("summary", "") + " " +
        " ".join(t.get("term", "") for t in entry.get("tags", []))
    ).lower()
    return any(kw in text for kw in ALL_KEYWORDS)

def parse_date(entry):
    for field in ("published_parsed", "updated_parsed"):
        t = entry.get(field)
        if t:
            try:
                return datetime.datetime(*t[:6])
            except Exception:
                pass
    return datetime.datetime.min

items = []
seen_urls = set()

for source_name, url in FEEDS:
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            link = entry.get("link", "")
            if not link or link in seen_urls:
                continue
            if not is_relevant(entry):
                continue
            seen_urls.add(link)
            items.append({
                "title":   entry.get("title", "No title"),
                "link":    link,
                "summary": entry.get("summary", ""),
                "date":    parse_date(entry),
                "source":  source_name,
            })
    except Exception as e:
        print(f"Failed {source_name}: {e}")

items.sort(key=lambda x: x["date"], reverse=True)
items = items[:100]

# Build RSS XML
rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")
SubElement(channel, "title").text = "Jay Respawns — Esports Weekly Feed"
SubElement(channel, "link").text = "https://jayrespawns.com"
SubElement(channel, "description").text = "Aggregated esports news: SEA and global"
SubElement(channel, "lastBuildDate").text = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

for item in items:
    entry_el = SubElement(channel, "item")
    SubElement(entry_el, "title").text = item["title"]
    SubElement(entry_el, "link").text = item["link"]
    SubElement(entry_el, "description").text = item["summary"]
    SubElement(entry_el, "pubDate").text = item["date"].strftime("%a, %d %b %Y %H:%M:%S +0000")
    SubElement(entry_el, "source").text = item["source"]

xml_str = minidom.parseString(tostring(rss)).toprettyxml(indent="  ")
with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(xml_str)

print(f"Done. {len(items)} items written to feed.xml.")
