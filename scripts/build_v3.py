#!/usr/bin/env python3
"""Render static pages from public/facts.json."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
FACTS = json.loads((PUBLIC / "facts.json").read_text())

A = FACTS["address"]
ADDR = f'{A["street"]}, {A["city"]}, {A["region"]} {A["postal"]}'
PHONE = FACTS["phoneDisplay"]
TEL = FACTS["phoneTel"]
EMAIL = FACTS["email"]
ALC = FACTS["alcohol"]
HOURS = " · ".join(h["label"] for h in FACTS["hours"])
LISTING = FACTS["listing"]


def e(text):
    return html.escape(text, quote=True)


DINNER = FACTS["seatOnDinner"]
BRUNCH = FACTS["seatOnBrunch"]
BOOKING = FACTS["booking"]


def seat(kind="dinner"):
    return BRUNCH if kind == "brunch" else DINNER


def reserve(placement, label="Reserve a table", kind="dinner", extra_class=""):
    cls = "reserve" if not extra_class else f"reserve {extra_class}"
    return (
        f'<a class="{cls}" data-placement="{e(placement)}" href="{e(seat(kind))}">'
        f'{label}</a>'
    )


def head(title, desc, path, preload="", body_class="pad"):
    canon = FACTS["domain"] + path
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{canon}">
  <link rel="icon" href="/favicon.svg">
  <meta name="theme-color" content="#0E0C0A">
  {preload}
  <link rel="stylesheet" href="/v3.css">
  <script src="/analytics.js" defer></script>
</head>
<body class="{body_class}">
<a class="skip" href="#main">Skip to content</a>
'''


def header(kind="dinner"):
    return f'''<header class="site-header" id="nav">
  <a class="mark" href="/">Sober Bar</a>
  <div class="header-end">
    {reserve("nav", "Reserve", kind, "header-reserve")}
    <nav class="nav-links" aria-label="Primary">
      <a href="/menu.html">Menu</a>
      <a href="/#the-room">The Room</a>
      <a href="/#visit">Visit</a>
      {reserve("nav", kind=kind)}
    </nav>
    <button class="burger" id="burger" type="button" aria-expanded="false" aria-controls="drawer">Menu</button>
  </div>
</header>
<nav class="drawer" id="drawer" aria-label="Mobile">
  <a href="/menu.html">Menu</a>
  <a href="/#the-room">The Room</a>
  <a href="/#visit">Visit</a>
  {reserve("nav", kind=kind)}
</nav>
'''


def footer():
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="foot-mark"><img src="/images/logo-sunburst-400.webp" alt="" width="128" height="80" loading="lazy"><span>Sober Bar</span></div>
    <ul class="foot-links">
      <li><a href="/why-i-opened-a-sober-bar.html">Our story</a></li>
      <li><a href="/as-seen-in.html">As seen in</a></li>
      <li><a href="/mocktails-st-petersburg.html">Mocktails in St. Pete</a></li>
      <li><a href="/brunch-gulfport.html">Brunch in Gulfport</a></li>
      <li><a href="/private-events.html">Private events</a></li>
      <li><a href="/breakfast-gulfport.html">Breakfast in Gulfport</a></li>
      <li><a href="/things-to-do-in-gulfport.html">Things to do in Gulfport</a></li>
      <li><a href="{FACTS["shop"]}">Shop</a></li>
      <li><a href="/sunday-jazz-brunch.html">Sunday jazz</a></li>
    </ul>
    <p class="fine"><a href="{FACTS["instagram"]}">Instagram</a> · <a href="{FACTS["facebook"]}">Facebook</a></p>
    <p class="fine">{e(ALC)}</p>
    <p class="fine">{e(ADDR)} · <a href="tel:{TEL}">{PHONE}</a> · {e(HOURS)}</p>
    <p class="fine"><a href="/privacy.html">Privacy</a> · <a href="/terms.html">Terms</a></p>
  </div>
</footer>
'''


def sticky(kind="dinner"):
    return f'''<nav class="sticky" aria-label="Call, reserve, or directions">
  <a href="tel:{TEL}">Call</a>
  {reserve("sticky", "Reserve", kind)}
  <a href="{FACTS["maps"]}">Directions</a>
</nav>
<script src="/site.js" defer></script>
</body>
</html>
'''


def shell(title, desc, path, main, placement, preload="", body_class="pad", kind="dinner"):
    return head(title, desc, path, preload, body_class) + header(kind) + main + footer() + sticky(kind)


def thumb(stem, alt):
    if not stem:
        return ""
    return (
        f'<img src="/images/v3/{stem}-160.webp" '
        f'srcset="/images/v3/{stem}-160.webp 160w, /images/v3/{stem}-320.webp 320w" '
        f'sizes="96px" width="96" height="96" alt="{e(alt)}" loading="lazy" decoding="async">'
    )


def room(src, w, h, alt, cap=None):
    fig = f'<figure class="room-top wipe"><img src="{src}" width="{w}" height="{h}" alt="{e(alt)}" loading="lazy" decoding="async">'
    if cap:
        fig += f'<figcaption class="cap">{e(cap)}</figcaption>'
    return fig + "</figure>"


def party_note():
    return (
        f'<p class="fine">Online booking is for parties of 1–6. For 7 or more, call '
        f'<a href="tel:{TEL}">{PHONE}</a>.</p>'
    )


def call_btn():
    return f'<a class="call" href="tel:{TEL}" aria-label="Call {PHONE}">Call</a>'


def hero_cta(placement, label, kind="dinner", extra=""):
    more = f"{extra}" if extra else ""
    return (
        f'<div class="hero-actions">{call_btn()}'
        f'<span data-hero-cta>{reserve(placement, label, kind)}</span>{more}</div>'
    )


def faq_html(items):
    return "".join(
        f'<details><summary>{e(item["q"])}</summary><p>{e(item["a"])}</p></details>'
        for item in items
    )


def faq_schema(items):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
            }
            for item in items
        ],
    }
    return f'<script type="application/ld+json">\n{json.dumps(data, indent=2)}\n</script>'


def visit_card():
    hours = "<br>".join(e(h["label"]) for h in FACTS["hours"])
    return f'''<div class="card" id="visit-card">
    <h2>Visit</h2>
    <p>{e(A["street"])}<br>{e(A["city"])}, {e(A["region"])} {e(A["postal"])}</p>
    <p>{hours}</p>
    <p><a href="tel:{TEL}">{PHONE}</a> · <a href="{FACTS["maps"]}">Directions</a></p>
  </div>'''


def menu_list(ids):
    chunks = []
    for cat in FACTS["menu"]:
        if cat["id"] not in ids:
            continue
        items = "".join(
            f'<li><strong>{e(it["name"])}</strong> — {e(it["desc"])}</li>' for it in cat["items"]
        )
        chunks.append(f'<h2>{e(cat["name"])}</h2><ul class="list">{items}</ul>')
    return "\n".join(chunks)


def menu_cards(ids):
    chunks = []
    for cat in FACTS["menu"]:
        if cat["id"] not in ids:
            continue
        items = []
        for it in cat["items"]:
            photo = thumb(it.get("image"), it["name"])
            cls = "mi" if photo else "mi no-photo"
            items.append(
                f'<li class="{cls}">{photo}<div><h3>{e(it["name"])}</h3><p>{e(it["desc"])}</p></div></li>'
            )
        chunks.append(f'<h2>{e(cat["name"])}</h2><ul class="menu-list">{"".join(items)}</ul>')
    return "\n".join(chunks)


def json_ld(data):
    return f'<script type="application/ld+json">\n{json.dumps(data, indent=2)}\n</script>'


def opening_hours():
    return [
        {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": h["days"],
            "opens": h["opens"],
            "closes": h["closes"],
        }
        for h in FACTS["hours"]
    ]


def place_schema(path, description, image):
    data = {
        "@context": "https://schema.org",
        "@type": ["BarOrPub", "Restaurant"],
        "name": "Sober Bar & Kitchen",
        "url": FACTS["domain"] + path,
        "telephone": TEL,
        "email": EMAIL,
        "servesCuisine": "New Orleans-inspired",
        "areaServed": ["Gulfport, FL", "St. Petersburg, FL", "Tampa Bay"],
        "hasMenu": FACTS["domain"] + "/menu.html",
        "image": FACTS["domain"] + image,
        "description": description,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": A["street"],
            "addressLocality": A["city"],
            "addressRegion": A["region"],
            "postalCode": A["postal"],
            "addressCountry": "US",
        },
        "openingHoursSpecification": opening_hours(),
        "sameAs": [FACTS["instagram"], FACTS["facebook"], LISTING],
    }
    return json_ld(data)


def breadcrumb(path, name):
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Sober Bar",
                "item": FACTS["domain"] + "/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": name,
                "item": FACTS["domain"] + path,
            },
        ],
    }
    return json_ld(data)


def landing(title, desc, path, preload, hero, eyebrow, h1, lead, actions, middle, menu_inner, faqs, kind, image):
    faq_block = ""
    if faqs:
        faq_block = faq_html(faqs) + faq_schema(faqs)
    main = f'''<main id="main">
  <section class="page-hero" id="top">
    {hero}
    <div class="hero-scrim"></div>
    <div class="hero-copy">
      <span class="eyebrow">{eyebrow}</span>
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
      {actions}
    </div>
  </section>
  <section>
    <div class="wrap prose">
      {middle}
    </div>
  </section>
  <section class="cream" id="menu">
    <div class="wrap">
      {menu_inner}
    </div>
  </section>
  <section id="visit">
    <div class="wrap">
      {visit_card()}
      {faq_block}
    </div>
  </section>
</main>
{place_schema(path, desc, image)}
{breadcrumb(path, h1)}
'''
    write(path.lstrip("/"), shell(title, desc, path, main, path, preload, "home pad", kind))


LOUNGE_HERO = '''<picture>
      <source type="image/avif" media="(max-width: 767px)" srcset="/images/v3/hero-d-480.avif 480w, /images/v3/hero-d-768.avif 768w" sizes="100vw">
      <source type="image/webp" media="(max-width: 767px)" srcset="/images/v3/hero-d-480.webp 480w, /images/v3/hero-d-768.webp 768w" sizes="100vw">
      <source type="image/webp" srcset="/images/v3/hero-d-768.webp 768w, /images/v3/hero-d-1200.webp 1200w, /images/v3/hero-d-1400.webp 1400w" sizes="100vw">
      <img src="/images/v3/hero-d-1400.webp" width="1400" height="875" alt="Curved velvet booths under the chandelier at Sober Bar" fetchpriority="high">
    </picture>'''

LOUNGE_PRELOAD = '''<link rel="preload" as="image" href="/images/v3/hero-d-768.avif" type="image/avif" media="(max-width: 767px)" fetchpriority="high">
  <link rel="preload" as="image" href="/images/v3/hero-d-1200.webp" type="image/webp" media="(min-width: 768px)" fetchpriority="high">'''

BAR_HERO = '''<picture>
      <source type="image/webp" srcset="/images/v3/bar-wide-480.webp 480w, /images/v3/bar-wide-768.webp 768w, /images/v3/bar-wide-1200.webp 1200w, /images/v3/bar-wide-1400.webp 1400w" sizes="100vw">
      <img src="/images/v3/bar-wide-1400.webp" width="1400" height="788" alt="Pendant lights over the bar at Sober Bar at night" fetchpriority="high">
    </picture>'''

BAR_PRELOAD = '''<link rel="preload" as="image" href="/images/v3/bar-wide-768.webp" type="image/webp" media="(max-width: 767px)" fetchpriority="high">
  <link rel="preload" as="image" href="/images/v3/bar-wide-1200.webp" type="image/webp" media="(min-width: 768px)" fetchpriority="high">'''

PORCH_HERO = '''<picture>
      <source media="(max-width: 767px)" type="image/avif" srcset="/images/v3/hero-night-m-480.avif 480w, /images/v3/hero-night-m-768.avif 768w" sizes="100vw">
      <source media="(max-width: 767px)" type="image/webp" srcset="/images/v3/hero-night-m-480.webp 480w, /images/v3/hero-night-m-768.webp 768w, /images/v3/hero-night-m-1200.webp 1200w" sizes="100vw">
      <source type="image/webp" srcset="/images/v3/hero-night-768.webp 768w, /images/v3/hero-night-1200.webp 1200w, /images/v3/hero-night-1800.webp 1800w, /images/v3/hero-night-2400.webp 2400w" sizes="100vw">
      <img src="/images/v3/hero-night-2400.webp" width="2400" height="1500" alt="The Beach Boulevard porch at Sober Bar at night, string lights and guests outside" fetchpriority="high">
    </picture>'''

PORCH_PRELOAD = '''<link rel="preload" as="image" href="/images/v3/hero-night-m-768.avif" type="image/avif" media="(max-width: 767px)" fetchpriority="high">
  <link rel="preload" as="image" href="/images/v3/hero-night-1800.webp" type="image/webp" media="(min-width: 768px)" fetchpriority="high">'''


def write(name, text):
    path = PUBLIC / name
    path.write_text(text)
    print(name, len(text.encode()))


def build_home():
    drinks = []
    wanted = ["Call Me an Ube", "Bee's Bouquet", "Hot Mami"]
    by_name = {it["name"]: it for cat in FACTS["menu"] for it in cat["items"]}
    for name in wanted:
        it = by_name[name]
        stem = it.get("image")
        if stem and (PUBLIC / "images" / "v3" / f"{stem}-800.webp").exists():
            img = (
                f'<img src="/images/v3/{stem}-800.webp" '
                f'srcset="/images/v3/{stem}-480.webp 480w, /images/v3/{stem}-800.webp 800w" '
                f'sizes="(max-width:767px) 96px, 30vw" width="480" height="600" alt="{e(name)}" loading="lazy" decoding="async">'
            )
        else:
            img = thumb(stem, name) if stem else ""
        drinks.append(f'<article class="drink">{img}<div><h3>{e(name)}</h3><p>{e(it["desc"])}</p></div></article>')
    schema_hours = ",".join(
        '{ "@type": "OpeningHoursSpecification", "dayOfWeek": [%s], "opens": "%s", "closes": "%s" }'
        % (",".join(f'"{d}"' for d in h["days"]), h["opens"], h["closes"])
        for h in FACTS["hours"]
    )
    preload = '''<link rel="preload" as="image" href="/images/v3/hero-night-m-768.avif" type="image/avif" media="(max-width: 767px)" fetchpriority="high">
  <link rel="preload" as="image" href="/images/v3/hero-night-1800.webp" type="image/webp" media="(min-width: 768px)" fetchpriority="high">'''
    main = f'''<main id="main">
  <section class="hero" id="top">
    <picture>
      <source media="(max-width: 767px)" type="image/avif" srcset="/images/v3/hero-night-m-480.avif 480w, /images/v3/hero-night-m-768.avif 768w" sizes="100vw">
      <source media="(max-width: 767px)" type="image/webp" srcset="/images/v3/hero-night-m-480.webp 480w, /images/v3/hero-night-m-768.webp 768w, /images/v3/hero-night-m-1200.webp 1200w" sizes="100vw">
      <source type="image/webp" srcset="/images/v3/hero-night-768.webp 768w, /images/v3/hero-night-1200.webp 1200w, /images/v3/hero-night-1800.webp 1800w, /images/v3/hero-night-2400.webp 2400w" sizes="100vw">
      <img src="/images/v3/hero-night-2400.webp" width="2400" height="1500" alt="The Beach Boulevard porch at Sober Bar at night, string lights and guests outside" fetchpriority="high">
    </picture>
    <div class="hero-scrim"></div>
    <div class="hero-copy">
      <span class="eyebrow">Gulfport, FL</span>
      <h1>A bar for staying out, minus the hangover.</h1>
      <p class="lead">Zero-proof cocktails after dark. Coffee and New Orleans-inspired plates from 7am.</p>
      <div class="hero-actions">
        <span data-hero-cta>{reserve("hero")}</span>
        <a class="text-link" href="/menu.html">View menu →</a>
      </div>
      <p class="fine">{e(BOOKING)}</p>
    </div>
  </section>

  <section id="the-room">
    <div class="wrap">
      <span class="eyebrow">The Room</span>
      <h2>Chandeliers, then the patio.</h2>
      <p class="room-copy">We wanted a bar, not a juice bar. Coffee at open. The room turns after dark.</p>
      <div class="room-grid">
        <figure class="wipe"><img src="/images/v3/hero-m-768.webp" width="768" height="960" alt="Curved velvet booths under the chandelier" loading="lazy" decoding="async"><figcaption class="cap">Under the chandelier</figcaption></figure>
        <figure class="wipe"><img src="/images/v3/bar-sq-768.webp" width="768" height="768" alt="Pendant lights over the bar at night" loading="lazy" decoding="async"><figcaption class="cap">The bar</figcaption></figure>
        <figure class="wipe"><img src="/images/v3/patio-754.webp" width="754" height="1006" alt="The porch at night, string lights over outdoor seats" loading="lazy" decoding="async"><figcaption class="cap">The patio</figcaption></figure>
      </div>
    </div>
  </section>

  <section class="bleed" aria-label="Behind the bar">
    <img src="/images/v3/behind-1200.webp" width="1200" height="675" alt="Bartenders working the rail at Sober Bar" loading="lazy" decoding="async">
    <div class="scrim"></div>
    <p class="pull">We didn’t want a juice bar. <em>We wanted a bar.</em></p>
  </section>

  <section class="cream" id="menu-teaser">
    <div class="wrap">
      <span class="eyebrow" style="color:#6b5a32">From the bar</span>
      <h2>Three to start.</h2>
      <div class="drinks" style="margin-top:22px">{''.join(drinks)}</div>
      <p style="margin-top:22px"><a href="/menu.html#cocktails">Full cocktail list</a></p>
      <h2 style="margin-top:36px">Plates from 7am.</h2>
      <p class="room-copy muted">The kitchen stays open with the bar. Same list, open to close. Daytime is walk-in.</p>
      <p>Sunday is <a href="/brunch-gulfport.html">brunch in Gulfport</a>, with live jazz in the room.</p>
      <p><a href="/breakfast-gulfport.html">Breakfast in Gulfport</a> starts at 7am.</p>
      <p>See the <a href="/menu.html#kitchen">kitchen menu</a>.</p>
    </div>
  </section>

  <section id="visit">
    <div class="wrap visit-grid">
      <div>
        <span class="eyebrow">Visit</span>
        <h2>Beach Boulevard.</h2>
        <p>{e(ADDR)}</p>
        <p>{e(HOURS)}</p>
        <p><a href="tel:{TEL}">Call {PHONE}</a></p>
        <p><a href="{FACTS["maps"]}">Directions</a></p>
        <p class="fine">{e(BOOKING)}</p>
        <p class="fine">{e(ALC)}</p>
        <p>Out from St. Pete for the night? <a href="/things-to-do-in-gulfport.html">The pier and the beach</a> are a short walk from here.</p>
        <p>The evening list is <a href="/mocktails-st-petersburg.html">mocktails in St. Pete and Gulfport</a>.</p>
        <p>A shower, a birthday, or a larger table is <a href="/private-events.html">private events and group dining</a>.</p>
        {faq_html(FACTS["faq"])}
      </div>
      <a class="map-link" href="{FACTS["maps"]}"><img src="/images/v3/map.svg" width="800" height="360" alt="Map of Sober Bar on Beach Boulevard in Gulfport"></a>
    </div>
  </section>

  <section class="close">
    <img src="/images/v3/bar-wide-1200.webp" width="1400" height="788" alt="The bar at night, pendant lights over the stools" loading="lazy">
    <div class="scrim"></div>
    <div class="wrap">
      <h2>Your table’s waiting.</h2>
      <div class="hero-actions">{reserve("close")}</div>
    </div>
  </section>
</main>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": ["BarOrPub", "Restaurant"],
  "name": "Sober Bar & Kitchen",
  "alternateName": "Sober Bar",
  "url": "{FACTS["domain"]}/",
  "telephone": "{TEL}",
  "email": "{EMAIL}",
  "servesCuisine": "New Orleans-inspired",
  "areaServed": ["Gulfport, FL", "St. Petersburg, FL", "Tampa Bay"],
  "acceptsReservations": "{DINNER}",
  "hasMenu": "{FACTS["domain"]}/menu.html",
  "image": "{FACTS["domain"]}/images/v3/hero-night-2400.webp",
  "description": {json.dumps(ALC)},
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "{A["street"]}",
    "addressLocality": "{A["city"]}",
    "addressRegion": "{A["region"]}",
    "postalCode": "{A["postal"]}",
    "addressCountry": "US"
  }},
  "openingHoursSpecification": [{schema_hours}],
  "sameAs": ["{FACTS["instagram"]}", "{FACTS["facebook"]}", "{LISTING}"]
}}
</script>
{faq_schema(FACTS["faq"])}
'''
    write("index.html", shell(
        "Sober Bar & Kitchen — Gulfport",
        "A bar for staying out, minus the hangover. Zero-proof cocktails and coffee in Gulfport.",
        "/",
        main,
        "home",
        preload,
        "home pad",
    ))


def build_menu():
    chips = "".join(f'<a href="#{c["id"]}">{e(c["name"])}</a>' for c in FACTS["menu"])
    sections = []
    for cat in FACTS["menu"]:
        wide = ""
        if cat.get("wide"):
            wide = (
                f'<figure class="wide-food"><img src="/images/v3/{cat["wide"]}-800.webp" width="800" height="600" alt="{e(cat["name"])} at Sober Bar" loading="lazy"></figure>'
            )
        items = []
        for it in cat["items"]:
            photo = thumb(it.get("image"), it["name"])
            cls = "mi" if photo else "mi no-photo"
            items.append(f'<li class="{cls}">{photo}<div><h3>{e(it["name"])}</h3><p>{e(it["desc"])}</p></div></li>')
        sections.append(
            f'<section class="menu-sec" id="{cat["id"]}"><h2>{e(cat["name"])}</h2>{wide}<ul style="list-style:none;padding:0;margin:0">{"".join(items)}</ul></section>'
        )
    main = f'''<main id="main" class="page cream">
  <div class="wrap">
    <h1>Menu</h1>
    <p class="lead" style="color:#3c342c">Served from open to close, every day. No prices on this page.</p>
    {room("/images/v3/bar-wide-1200.webp", 1400, 788, "The bar at Sober Bar at night")}
    <nav class="chips" aria-label="Menu categories">{chips}</nav>
    {''.join(sections)}
    <p>{e(ALC)} Ask for today’s prices. Tell us about allergies before you order.</p>
    <p>Same list from the first coffee to the last cocktail. <a href="/mocktails-st-petersburg.html">Coming from St. Pete</a>, start with a drink.</p>
    <p>{reserve("menu", "Reserve dinner")} <a class="text-link" href="/reservations.html" style="margin-left:16px">Reservations →</a></p>
    <p style="color:#3c342c">{e(BOOKING)}</p>
  </div>
</main>'''
    write("menu.html", shell(
        "Menu — Sober Bar & Kitchen",
        "Cocktails, NA beer, coffee, breakfast, and the kitchen at Sober Bar in Gulfport. No prices published.",
        "/menu.html",
        main,
        "menu",
    ))


def build_reservations():
    main = f'''<main id="main" class="page">
  <div class="wrap book">
    <h1>Reserve a table</h1>
    <p class="lead">Dinner online is 4–9:30pm. Sunday brunch online is 10am–1pm. Daytime is walk-in.</p>
    <div class="hero-actions">
      <span data-hero-cta>{reserve("res", "Reserve dinner")}</span>
      <a class="text-link" data-placement="res-brunch" href="{e(BRUNCH)}">Reserve Sunday brunch</a>
    </div>
    {party_note()}
    {visit_card()}
  </div>
</main>'''
    write("reservations.html", shell(
        "Reserve a table — Sober Bar",
        "Book dinner online from 4–9:30pm, or Sunday brunch from 10am–1pm. Daytime is walk-in. Parties of 1–6.",
        "/reservations.html",
        main,
        "res",
    ))


def article(title, desc, path, h1, lead, body, placement, kind="dinner", book=True, label="Reserve a table"):
    if book:
        actions = (
            f'<p style="margin-top:22px"><span data-hero-cta>{reserve(placement, label, kind)}</span> '
            f'<a class="text-link" href="/menu.html" style="margin-left:16px">View menu →</a></p>'
            f'<p class="fine">{e(BOOKING)}</p>'
        )
    else:
        actions = (
            f'<p style="margin-top:22px">{e(BOOKING)}</p>'
            f'<p><a class="text-link" href="/menu.html">View menu →</a></p>'
        )
    main = f'''<main id="main" class="page">
  <div class="wrap">
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
    {room("/images/v3/hero-d-1200.webp", 1400, 875, "The lounge at Sober Bar under the chandelier")}
    {body}
    {actions}
    {visit_card()}
  </div>
</main>'''
    write(path.lstrip("/"), shell(title, desc, path, main, placement, kind=kind))


def build_rest():
    article(
        "Breakfast and coffee in Gulfport — Sober Bar",
        "Breakfast and coffee from 7am at Sober Bar & Kitchen, 3062 Beach Blvd S, Gulfport, FL 33707. Daytime is walk-in. Call (813) 586-1660.",
        "/breakfast-gulfport.html",
        "Breakfast and coffee in Gulfport",
        "Espresso, cold brew, and a New Orleans-inspired breakfast from 7am at Sober Bar & Kitchen, 3062 Beach Blvd S. Daytime is walk-in.",
        f"<p>The espresso bar is open with the doors at {e(ADDR)}. Call <a href=\"tel:{TEL}\">{PHONE}</a>. The full menu runs open to close. Daytime tables are walk-in. After dark, the <a href=\"/mocktails-st-petersburg.html\">non-alcoholic cocktails</a> are the reason to stay.</p>"
        f"<p>Sunday midday is <a href=\"/brunch-gulfport.html\">brunch in Gulfport</a>, with live jazz. Online brunch booking is 10am–1pm.</p>"
        + menu_list(["coffee", "breakfast"]) + f"<p>{e(ALC)}</p>",
        "breakfast",
        book=False,
    )
    article(
        "Sunday jazz brunch in Gulfport — Sober Bar",
        "Live jazz every Sunday brunch at Sober Bar in Gulfport. Call (813) 586-1660 for this Sunday's jazz time.",
        "/sunday-jazz-brunch.html",
        "Sunday jazz brunch in Gulfport",
        "Live jazz in the room every Sunday brunch. Online brunch booking is 10am–1pm. Call (813) 586-1660 for this Sunday's jazz time.",
        f'''<p>The doors are already open at 7am if you want coffee first. Daytime is walk-in. Call <a href="tel:{TEL}">{PHONE}</a> for this Sunday’s jazz time. No band or start time is published. Online brunch booking is 10am–1pm.</p>
        <p>The room is the lounge on Beach Boulevard: booths under the chandelier, the bar beside them, and the porch just outside. Jazz is in that room.</p>
        <p>The meal is <a href="/brunch-gulfport.html">brunch in Gulfport</a>. This page is the music.</p>
        <p>The full menu runs on Sunday, including <strong>The White Rabbit</strong> and the plant-based <strong>Garden District Muffuletta</strong>. Later, the bar pours <strong>Call Me an Ube</strong>.</p>
        <p>{e(ALC)}</p>''',
        "jazz",
        kind="brunch",
        label="Reserve Sunday brunch",
    )
    gulf = f'''
    <h2>Waterfront</h2>
    <ul class="list">
      <li><a href="https://mygulfport.us/waterfront-redevelopment-district/">Williams Pier</a> — The Walter and Bert Williams Fishing Pier, at 54th Street South and Shore Boulevard. Free admission, with fishing access, benches, and lighting.</li>
      <li><a href="https://mygulfport.us/recreation/parks/beachfront-water-complex/">Gulfport Beach</a> — City beach on Shore Boulevard between 54th and 58th Streets, open 4 a.m. to midnight.</li>
    </ul>
    <h2>Eat</h2>
    <ul class="list"><li><a href="https://www.omaddys.com/">O'Maddy's Bar &amp; Grille</a> — Waterfront dining at 5405 Shore Blvd S. Open daily 11 a.m. to midnight, with live bands.</li></ul>
    <h2>Shop</h2>
    <ul class="list">
      <li><a href="https://visitgulfportflorida.com/event/gulfport-night-market/">Gulfport Night Market</a> — First Friday and third Saturday, 5–9 p.m., along Beach Boulevard.</li>
      <li><a href="https://visitgulfportflorida.com/event/gulfport-fresh-market/">Gulfport Tuesday Fresh Market</a> — A year-round Tuesday market on Beach Boulevard, 9 a.m.–2 p.m.</li>
      <li><a href="https://www.gulfportbeachbazaar.com/">Gulfport Beach Bazaar</a> — Coastal gifts and souvenirs on Beach Boulevard.</li>
    </ul>
    <h2>On Beach Boulevard</h2>
    <p>When the walk is done, the bar is on Beach Boulevard. <a href="/mocktails-st-petersburg.html">Cocktails</a> come out after dark, and coffee starts at 7am.</p>
    <p>Sunday midday is <a href="/brunch-gulfport.html">brunch in Gulfport</a>.</p>
    '''
    article(
        "Things to do in Gulfport — Sober Bar",
        "Gulfport's pier, beach, and markets, plus Sober Bar & Kitchen at 3062 Beach Blvd S. Call (813) 586-1660.",
        "/things-to-do-in-gulfport.html",
        "Things to do in Gulfport",
        "The pier, the beach, and a table on Beach Boulevard.",
        gulf,
        "gulfport",
    )
    story = f'''
    <p>The idea started with a simple question: why does going out have to come with alcohol?</p>
    <p>Gulfport already had art walks, night markets, and good food. If you were not drinking, the options were a coffee shop or a soda at a regular bar.</p>
    <h2>We didn’t want a juice bar. We wanted a bar.</h2>
    <p>Sober Bar at {e(A["street"])} is a coffee house by day and a cocktail bar by night. The kitchen is New Orleans-inspired. The drinks are built like craft cocktails. {e(ALC)} <a href="/mocktails-st-petersburg.html">The cocktail list</a> is where most people start.</p>
    <p>People walk in skeptical. Then they see the room, taste a Call Me an Ube, and stay.</p>
    <h2>Who comes in</h2>
    <p>Designated drivers. Pregnant guests. People in recovery. People who just do not feel like drinking tonight. The common thread is choice.</p>
    <p>The hardest part was not the drinks. It was convincing people a sober bar could still feel like a bar.</p>
    '''
    article(
        "Why I opened a sober bar — Sober Bar",
        "Sean Hawthorne on opening Sober Bar, a cocktail bar and coffee house in Gulfport, Florida.",
        "/why-i-opened-a-sober-bar.html",
        "Why I opened a sober bar",
        "A Gulfport bar for the night out, without the hangover.",
        story,
        "story",
    )
    press = '''
    <article class="press"><h2>FOX 13</h2><p>Florida Tonight with Haley Hinds.</p><p><a href="https://www.fox13news.com/video/fmc-tcdaujvlcx10y2dc">Watch the segment →</a></p></article>
    <article class="press"><h2>I Love the Burg</h2><p>Opening story on the cocktail lounge and café.</p><p><a href="https://ilovetheburg.com/sober-bar-cocktails-coffee-gulfport/">Read the article →</a></p></article>
    <article class="press"><h2>St. Pete Rising</h2><p>Opening story for the Gulfport lounge and café.</p><p><a href="https://stpeterising.com/home/sober-bar-opening-next-month-in-downtown-gulfport-with-zero-proof-cocktails-and-kava">Read the article →</a></p></article>
    <article class="press"><h2>The Gabber</h2><p>April 2026 and June 2026 South Pinellas business roundups.</p><p><a href="https://thegabber.com/south-pinellas-business-news-roundup-for-june-2026/">June 2026 →</a> · <a href="https://thegabber.com/south-pinellas-business-news-roundup-for-april-2026/">April 2026 →</a></p></article>
    '''
    article(
        "As seen in — Sober Bar",
        "Press for Sober Bar in Gulfport: FOX 13, I Love the Burg, St. Pete Rising, and The Gabber.",
        "/as-seen-in.html",
        "As seen in",
        "Four outlets, linked. Email Sean for room photos.",
        press + f"<p>Email <a href=\"mailto:{EMAIL}\">{EMAIL}</a> or call <a href=\"tel:{TEL}\">{PHONE}</a>.</p>",
        "press",
    )


def build_intent_pages():
    brunch_faqs = [
        {
            "q": "Where is brunch in Gulfport?",
            "a": f"Sunday brunch is at Sober Bar & Kitchen, {ADDR}. Online booking is 10am–1pm. Call {PHONE}.",
        },
        {
            "q": "Is there live music at brunch?",
            "a": FACTS["jazz"],
        },
        {
            "q": "Can I book brunch for a group?",
            "a": "Online booking is for parties of 1–6, Sunday 10am–1pm. For 7 or more, call the bar.",
        },
    ]
    brunch_middle = f'''
    <p>Sunday brunch at Sober Bar &amp; Kitchen is the midday table on Beach Boulevard. You sit in the lounge: curved booths under a chandelier, the bar in the same room, and the porch just outside when you want air. Doors open at 7am, so coffee can come before the brunch window. Daytime outside that window is walk-in.</p>
    <p>The brunch you can reserve is Sunday, 10am–1pm. Live jazz plays every Sunday brunch. Call <a href="tel:{TEL}">{PHONE}</a> for this Sunday’s jazz time. No band or start time is published.</p>
    <p>If you came for the music, start with <a href="/sunday-jazz-brunch.html">Sunday jazz</a>.</p>
    <figure class="space-side wipe"><img src="/images/v3/patio-754.webp" width="754" height="1006" alt="The porch at night, string lights over outdoor seats" loading="lazy" decoding="async"><figcaption class="cap">The porch</figcaption></figure>
    <p>Gulfport borders St. Petersburg. The address is {e(ADDR)}. When the table is done, <a href="/things-to-do-in-gulfport.html">the pier and the beach</a> are a short walk.</p>
    <p>The kitchen is New Orleans-inspired. Brunch is not a separate card. The full menu runs open to close, including Sunday.</p>
    {party_note()}
    <p>A larger gathering is <a href="/private-events.html">private events and group dining</a>. Tell us the date and the headcount.</p>
    '''
    brunch_menu = f'''
    <p class="muted">Same plates from the first coffee to the last seating. Ask for today’s prices.</p>
    <figure class="wide-food"><img src="/images/v3/morning-melt-800.webp" width="800" height="600" alt="The Classic Morning Melt at Sober Bar" loading="lazy" decoding="async"></figure>
    {menu_cards(["breakfast", "kitchen"])}
    <p>{e(ALC)}</p>
    <p>Espresso and cold brew are on the <a href="/menu.html#coffee">coffee list</a>.</p>
    <p>The evening pours are on the <a href="/mocktails-st-petersburg.html">mocktails page</a>.</p>
    '''
    landing(
        "Brunch in Gulfport — Sober Bar & Kitchen",
        f"Sunday brunch in Gulfport at Sober Bar & Kitchen, {ADDR}. Live jazz. Book online 10am–1pm. Call {PHONE}.",
        "/brunch-gulfport.html",
        LOUNGE_PRELOAD,
        LOUNGE_HERO,
        "Gulfport, FL",
        "Brunch in Gulfport",
        "Sunday brunch under the chandelier, with live jazz in the room. Book online from 10am to 1pm.",
        hero_cta("brunch", "Reserve Sunday brunch", "brunch"),
        brunch_middle,
        brunch_menu,
        brunch_faqs,
        "brunch",
        "/images/v3/hero-d-1400.webp",
    )

    mock_faqs = [
        FACTS["nearFaq"],
        {
            "q": "Where can I get mocktails in Gulfport?",
            "a": f"At Sober Bar & Kitchen, {ADDR}. The cocktails are zero-proof. {ALC} Call {PHONE}.",
        },
        {
            "q": "Do the drinks contain alcohol?",
            "a": ALC,
        },
    ]
    mock_middle = f'''
    <h2>Non-alcoholic cocktails near St. Pete</h2>
    <p>If you searched for mocktails in St. Petersburg, the bar is in Gulfport, which borders St. Petersburg and sits in the Tampa Bay area. Beach Boulevard is the block. Coffee runs from 7am. The cocktails are the reason to stay once the room turns. Dinner books online from 4–9:30pm. Friday and Saturday the doors stay open until midnight. Daytime tables are walk-in.</p>
    <h2>The room</h2>
    <p>Pendant lights over the bar, bartenders on the rail, and chandeliers in the lounge behind the stools. This was built as a bar, not a juice bar. The drinks are built like bar cocktails. The cocktails are zero-proof. {e(ALC)}</p>
    {room("/images/v3/behind-1200.webp", 1200, 675, "Bartenders working the rail at Sober Bar", "The bar")}
    <h2>Mocktails in Gulfport</h2>
    <p>The Gulfport search lands in the same room. {e(ADDR)} is the storefront. Sunday midday is <a href="/brunch-gulfport.html">brunch in Gulfport</a>, with live jazz.</p>
    <p><a href="/breakfast-gulfport.html">Mornings</a> are coffee and breakfast, and those tables are walk-in.</p>
    <p>A group, a shower, or a birthday is <a href="/private-events.html">private events and group dining</a>.</p>
    '''
    mock_menu = f'''
    <p class="muted">The cocktails are zero-proof. Prices are at the bar.</p>
    {menu_cards(["cocktails", "beer"])}
    <p>{e(ALC)}</p>
    <p>The rest of the kitchen is on the <a href="/menu.html">full menu</a>.</p>
    '''
    landing(
        "Mocktails in St. Pete and Gulfport — Sober Bar & Kitchen",
        f"Mocktails in St. Pete and Gulfport at Sober Bar & Kitchen, {ADDR}. Non-alcoholic cocktails. {ALC}",
        "/mocktails-st-petersburg.html",
        BAR_PRELOAD,
        BAR_HERO,
        "St. Petersburg · Gulfport",
        "Mocktails in St. Pete and Gulfport",
        "Non-alcoholic cocktails in Gulfport, just across the line from St. Petersburg.",
        hero_cta("mocktails", "Reserve a table"),
        mock_middle,
        mock_menu,
        mock_faqs,
        "dinner",
        "/images/v3/bar-wide-1400.webp",
    )

    event_faqs = [
        {
            "q": "How does group dining work?",
            "a": f"Online booking is for parties of 1–6. Dinner is 4–9:30pm and Sunday brunch is 10am–1pm. Daytime is walk-in. For 7 or more, call {PHONE}. An online reservation holds a table. It does not hold the room.",
        },
        {
            "q": "How do I plan a private event?",
            "a": f"Email {EMAIL} or call {PHONE} with the date and headcount. Showers, birthdays, office gatherings, and recovery milestones use the same room and patio. An inquiry does not reserve the date. Menus and pricing are in the quote.",
        },
    ]
    form = f'''<div class="card" id="inquire">
    <h2>Plan your gathering</h2>
    <p>This form opens an email to {EMAIL}. It does not send by itself, and this page does not store what you type. An inquiry does not reserve the date.</p>
    <form class="form" id="inquireForm">
      <div><label for="inq-name">Name</label><input id="inq-name" name="name" autocomplete="name" required></div>
      <div><label for="inq-phone">Phone</label><input id="inq-phone" name="phone" type="tel" autocomplete="tel" required></div>
      <div><label for="inq-email">Email</label><input id="inq-email" name="email" type="email" autocomplete="email" required></div>
      <div><label for="inq-when">Preferred date and time</label><input id="inq-when" name="when" required></div>
      <div><label for="inq-guests">Guest count</label><input id="inq-guests" name="guests" inputmode="numeric" required></div>
      <div><label for="inq-occasion">Occasion</label><select id="inq-occasion" name="occasion"><option>Shower</option><option>Birthday</option><option>Office gathering</option><option>Recovery milestone</option><option>Book club</option><option>Other</option></select></div>
      <div><label for="inq-notes">Notes</label><textarea id="inq-notes" name="notes"></textarea></div>
      <button class="reserve" type="submit">Open email inquiry</button>
    </form>
    <p>No mail app? Email <a href="mailto:{EMAIL}">{EMAIL}</a> or call <a href="tel:{TEL}">{PHONE}</a>.</p>
    {party_note()}
  </div>
  <script>
    document.getElementById('inquireForm').addEventListener('submit', function (event) {{
      event.preventDefault();
      var form = event.currentTarget;
      function value(key) {{ return form.elements[key].value.trim(); }}
      var body = ['Hi Sober Bar,','','I would like to plan a gathering.','','Name: '+value('name'),'Phone: '+value('phone'),'Email: '+value('email'),'Preferred date and time: '+value('when'),'Guest count: '+value('guests'),'Occasion: '+value('occasion'),'Notes: '+value('notes')].join('\\n');
      window.location.href = 'mailto:{EMAIL}?subject=' + encodeURIComponent('Group Event Inquiry | Website') + '&body=' + encodeURIComponent(body);
    }});
  </script>'''
    events_middle = f'''
    <h2>Group dining</h2>
    <p>Come for dinner as a group, or for Sunday brunch. Online booking covers parties of 1–6: dinner from 4–9:30pm, and Sunday brunch from 10am–1pm. Daytime is walk-in. For 7 or more, call <a href="tel:{TEL}">{PHONE}</a>. The online link holds a table for that party size. It does not hold the room.</p>
    <p><a href="{e(BRUNCH)}">Reserve Sunday brunch</a> when the group is coming at midday.</p>
    <h2>Private events</h2>
    <p>Showers, birthdays, office gatherings, recovery milestones, and book clubs use the same lounge and the same porch. Tell us the date and headcount and we’ll confirm what fits. Menus and pricing are in the quote. An inquiry does not reserve the date.</p>
    <p><a href="/sunday-jazz-brunch.html">Sunday jazz brunch</a> is the same room, not a separate venue.</p>
    {room("/images/v3/hero-d-1200.webp", 1400, 875, "Curved velvet booths under the chandelier at Sober Bar", "Under the chandelier")}
    <p>{e(ALC)} Popular builds include Call Me an Ube and Jinn &amp; Juniper.</p>
    {form}
    '''
    events_menu = f'''
    <p class="muted">The group orders from the same list as the bar.</p>
    {menu_cards(["cocktails"])}
    <p>{e(ALC)}</p>
    <p>Plates are on the <a href="/menu.html#kitchen">kitchen menu</a>.</p>
    <p>Sunday’s table is <a href="/brunch-gulfport.html">brunch in Gulfport</a>.</p>
    '''
    landing(
        "Private events and group dining in Gulfport — Sober Bar",
        f"Private events and group dining at Sober Bar & Kitchen, {ADDR}. Parties of 1–6 book online. For 7 or more, call {PHONE}.",
        "/private-events.html",
        PORCH_PRELOAD,
        PORCH_HERO,
        "Gulfport, FL",
        "Private events and group dining in Gulfport",
        "A table for the group, or the room for a shower, a birthday, or a milestone.",
        hero_cta("events", "Reserve a table", "dinner", '<a class="text-link" href="#inquire">Plan your gathering</a>'),
        events_middle,
        events_menu,
        event_faqs,
        "dinner",
        "/images/v3/hero-night-2400.webp",
    )


def build_sponsor():
    form = f'''<div class="card" id="inquire">
    <h2>Discuss sponsorship</h2>
    <p>Every sponsorship is custom. This form opens an email to {EMAIL}. It does not send by itself.</p>
    <form class="form" id="sponsorForm">
      <div><label for="sp-name">Name</label><input id="sp-name" name="name" required></div>
      <div><label for="sp-email">Email</label><input id="sp-email" name="email" type="email" required></div>
      <div><label for="sp-event">Event</label><input id="sp-event" name="event" required></div>
      <div><label for="sp-notes">Notes</label><textarea id="sp-notes" name="notes"></textarea></div>
      <button class="reserve" type="submit">Open email inquiry</button>
    </form>
    <p>No mail app? Email <a href="mailto:{EMAIL}">{EMAIL}</a> or call <a href="tel:{TEL}">{PHONE}</a>.</p>
  </div>
  <script>
    document.getElementById('sponsorForm').addEventListener('submit', function (event) {{
      event.preventDefault();
      var form = event.currentTarget;
      function value(key) {{ return form.elements[key].value.trim(); }}
      var body = ['Name: '+value('name'),'Email: '+value('email'),'Event: '+value('event'),'Notes: '+value('notes')].join('\\n');
      window.location.href = 'mailto:{EMAIL}?subject=' + encodeURIComponent('Sponsorship inquiry') + '&body=' + encodeURIComponent(body);
    }});
  </script>'''
    main = f'''<main id="main" class="page">
  <div class="wrap">
    <h1>Event sponsorship</h1>
    <p class="lead">Tell us about the event. We’ll put together what fits.</p>
    {room("/images/v3/bar-wide-1200.webp", 1400, 788, "The bar at Sober Bar")}
    <p>{e(ALC)}</p>
    {form}
  </div>
</main>'''
    write("event-sponsorship.html", shell(
        "Event sponsorship — Sober Bar",
        "Custom event sponsorship with Sober Bar in Gulfport. Tell us about the event.",
        "/event-sponsorship.html",
        main,
        "sponsorship",
    ))


def build_legal():
    privacy = f'''<main id="main" class="page"><div class="wrap">
    <h1>Privacy</h1>
    <p class="lead">Last updated September 2026.</p>
    <h2>Information we collect</h2>
    <p>If you use the mailing-list form, you provide an email address. Google Analytics collects limited usage information: pages visited, approximate location, device and browser, traffic source, and clicks on reservation, directions, email, and social links.</p>
    <h2>How the form works</h2>
    <p>Submit opens a pre-filled email in your mail app. This website does not store the address or send it to a server.</p>
    <h2>How we use it</h2>
    <p>If you email us to join the list, we use the address for occasional updates. We do not sell or share it. Reply to any message to be removed, or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    <h2>Cookies</h2>
    <p>Google Analytics may use cookies. We do not send email addresses to Analytics. You can limit cookies in your browser.</p>
    <h2>Contact</h2>
    <p>Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    </div></main>'''
    terms = f'''<main id="main" class="page"><div class="wrap">
    <h1>Terms</h1>
    <p class="lead">Last updated July 2026.</p>
    <h2>Use of the site</h2>
    <p>This website is information about Sober Bar, a cocktail bar and coffee house in Gulfport, Florida. It is general information.</p>
    <h2>Intellectual property</h2>
    <p>The Sober Bar name, logo, photography, and site content belong to Sober Bar and need permission to reuse.</p>
    <h2>Accuracy</h2>
    <p>Menu items, hours, and offerings can change. Check with us before you visit if something looks off.</p>
    <h2>Contact</h2>
    <p>Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    </div></main>'''
    missing = '''<main id="main" class="page"><div class="wrap"><h1>That page is off the menu.</h1><p class="lead"><a href="/">Back to Sober Bar</a> · <a href="/menu.html">View the menu</a></p></div></main>'''
    write("privacy.html", shell("Privacy — Sober Bar", "How Sober Bar handles email and analytics.", "/privacy.html", privacy, "privacy"))
    write("terms.html", shell("Terms — Sober Bar", "Terms for using the Sober Bar website.", "/terms.html", terms, "terms"))
    write("404.html", shell("Page not found — Sober Bar", "That page is not on the Sober Bar site.", "/404.html", missing, "404"))


def build_llms_and_sitemap():
    lines = [
        f"# {FACTS['name']}",
        "",
        f"> {ALC}",
        "",
        f"- Address: {ADDR}",
        f"- Phone: {PHONE}",
        f"- Email: {EMAIL}",
        f"- Hours: {HOURS}",
        f"- {FACTS['booking']}",
        f"- {FACTS['partyLimit']}",
        f"- Friday and Saturday close at midnight.",
        f"- {FACTS['jazz']}",
        f"- Reserve dinner: {DINNER}",
        f"- Reserve Sunday brunch: {BRUNCH}",
        f"- Website: {FACTS['domain']}",
        f"- Sober Bar & Kitchen in Gulfport: {FACTS['domain']}/",
        f"- Mocktails in St. Pete and Gulfport: {FACTS['domain']}/mocktails-st-petersburg.html",
        f"- Brunch in Gulfport: {FACTS['domain']}/brunch-gulfport.html",
        f"- Private events and group dining: {FACTS['domain']}/private-events.html",
        f"- Sunday jazz brunch: {FACTS['domain']}/sunday-jazz-brunch.html",
        f"- Breakfast in Gulfport: {FACTS['domain']}/breakfast-gulfport.html",
        f"- Things to do in Gulfport: {FACTS['domain']}/things-to-do-in-gulfport.html",
        "",
        "## Menu",
    ]
    for cat in FACTS["menu"]:
        lines.append(f"### {cat['name']}")
        for it in cat["items"]:
            lines.append(f"- {it['name']}: {it['desc']}")
    (PUBLIC / "llms.txt").write_text("\n".join(lines) + "\n")
    urls = [
        "/", "/menu.html", "/reservations.html", "/breakfast-gulfport.html",
        "/brunch-gulfport.html", "/sunday-jazz-brunch.html", "/private-events.html",
        "/mocktails-st-petersburg.html",
        "/things-to-do-in-gulfport.html", "/why-i-opened-a-sober-bar.html",
        "/as-seen-in.html",
    ]
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        pri = "1.0" if u == "/" else "0.8" if u in {
            "/mocktails-st-petersburg.html",
            "/brunch-gulfport.html",
            "/private-events.html",
            "/breakfast-gulfport.html",
            "/things-to-do-in-gulfport.html",
        } else "0.7"
        body.append(f"  <url><loc>{FACTS['domain']}{u if u != '/' else '/'}</loc><lastmod>2026-10-11</lastmod><priority>{pri}</priority></url>")
    body.append("</urlset>\n")
    (PUBLIC / "sitemap.xml").write_text("\n".join(body))
    redir = PUBLIC / "_redirects"
    text = redir.read_text()
    extra = "/vote.html / 301\n/vote / 301\n"
    if "/vote.html" not in text:
        redir.write_text(text.rstrip() + "\n" + extra)


def check():
    banned = [
        "nothing contains alcohol", "nothing on the menu", "nothing on our menu",
        "100% alcohol-free", "alcohol-free", "yes — 100", "50 seats", "30 indoor", "20 outdoor",
        "sipsisoberbar", "closed monday", "2 hours before", "serves alcohol",
        "party of 7", "wi-fi", "wifi", "4.9", "google reviews",
        "up to 12", "12 guests",
        "inside or out", "indoor or outdoor",
    ]
    # "11 a.m." must not match a 1am close. Require the 1 not to follow a digit.
    late_close = re.compile(r"(?<!\d)1\s*a\.?\s*m\b|(?<!\d)01:00", re.I)
    party_ok = set()
    allowed = {DINNER, BRUNCH}
    files = list(PUBLIC.glob("*.html")) + [PUBLIC / "llms.txt", PUBLIC / "facts.json"]
    for path in files:
        raw = path.read_text()
        text = raw.lower()
        for b in banned:
            if b in text:
                raise SystemExit(f"banned {b} in {path.name}")
        if late_close.search(text):
            raise SystemExit(f"banned late close in {path.name}")
        for url in re.findall(r"https://getseat\.net[^\"<\s]*", raw):
            if html.unescape(url) not in allowed:
                raise SystemExit(f"unexpected seat link in {path.name}: {url}")
        if "party of 7" in text and path.name not in party_ok:
            raise SystemExit(f"party of 7 on {path.name}")
    home = (PUBLIC / "index.html").read_text()
    if "morning-melt" in home or "muffuletta-" in home:
        raise SystemExit("food photo on homepage")
    if "productId=101287" not in home or "productId=101285" in home:
        raise SystemExit("homepage seat link drifted")
    drink_stems = (
        "ube-pro", "ube-160", "hot-mami", "bouquet", "morning-melt", "muffuletta",
        "bagel-", "parfait", "bodega", "mad-hatter", "white-rabbit", "garden-mezze",
        "hot-honey", "fig-brie", "goat-salad", "mardi-salad", "pretzel", "naan-",
        "guinness", "heineken", "run-wild", "cappuccino", "latte-", "chai-",
    )

    def above(raw, marker, name):
        head, sep, _rest = raw.partition(marker)
        if not sep:
            raise SystemExit(f"missing {marker} in {name}")
        for stem in drink_stems:
            if stem in head:
                raise SystemExit(f"{stem} above the menu in {name}")
        return head

    above(home, 'id="menu-teaser"', "index.html")
    intent = {
        "brunch-gulfport.html": "101285",
        "mocktails-st-petersburg.html": "101287",
        "private-events.html": "101287",
    }
    for name, product in intent.items():
        raw = (PUBLIC / name).read_text()
        above(raw, 'id="menu"', name)
        if product not in raw or 'class="call"' not in raw or "3062 Beach Blvd S" not in raw:
            raise SystemExit(f"landing CTA or NAP missing in {name}")
        if ALC not in raw or f"tel:{TEL}" not in raw:
            raise SystemExit(f"alcohol line or phone missing in {name}")
    mock = (PUBLIC / "mocktails-st-petersburg.html").read_text()
    if "Non-alcoholic cocktails near St. Pete" not in mock or "Mocktails in Gulfport" not in mock:
        raise SystemExit("mocktails page drifted")
    brunch = (PUBLIC / "brunch-gulfport.html").read_text()
    if "Brunch in Gulfport" not in brunch:
        raise SystemExit("brunch page drifted")
    events = (PUBLIC / "private-events.html").read_text()
    if "group dining" not in events.lower():
        raise SystemExit("private events page drifted")
    if "kratom" in (PUBLIC / "review-tent.html").read_text().lower():
        raise SystemExit("review tent still lists kratom")
    print("facts check ok")


if __name__ == "__main__":
    build_home()
    build_menu()
    build_reservations()
    build_rest()
    build_intent_pages()
    build_sponsor()
    build_legal()
    build_llms_and_sitemap()
    check()
