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
  <a href="tel:{TEL}">{PHONE}</a>
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
      <li><a href="/breakfast-gulfport.html">Breakfast in Gulfport</a></li>
      <li><a href="/things-to-do-in-gulfport.html">Things to do in Gulfport</a></li>
      <li><a href="{FACTS["shop"]}">Shop</a></li>
      <li><a href="/sunday-jazz-brunch.html">Sunday jazz</a></li>
      <li><a href="/private-events.html">Private events</a></li>
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


def visit_card(show_phone=True):
    hours = "<br>".join(e(h["label"]) for h in FACTS["hours"])
    phone = f'<a href="tel:{TEL}">{PHONE}</a> · ' if show_phone else ""
    return f'''<div class="card" id="visit-card">
    <h2>Visit</h2>
    <p>{e(A["street"])}<br>{e(A["city"])}, {e(A["region"])} {e(A["postal"])}</p>
    <p>{hours}</p>
    <p>{phone}<a href="{FACTS["maps"]}">Directions</a></p>
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
      <img src="/images/v3/hero-night-2400.webp" width="2400" height="1500" alt="The Beach Boulevard porch at Sober Bar at night, string lights and guests outside" fetchpriority="high" decoding="async">
    </picture>
    <div class="hero-scrim"></div>
    <div class="hero-copy">
      <span class="eyebrow">Gulfport, FL</span>
      <h1>A bar for staying out, minus the hangover.</h1>
      <p class="lead">Espresso at 7. A proper cocktail after dark.</p>
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
      <p class="room-copy">Velvet booths, one chandelier, and a porch when you want the air.</p>
      <div class="room-grid">
        <figure class="wipe"><img src="/images/v3/hero-m-768.webp" width="768" height="960" alt="Curved velvet booths under the chandelier"><figcaption class="cap">Under the chandelier</figcaption></figure>
        <figure class="wipe"><img src="/images/v3/bar-sq-768.webp" width="768" height="768" alt="Pendant lights over the bar at night"><figcaption class="cap">The bar</figcaption></figure>
        <figure class="wipe"><img src="/images/v3/patio-754.webp" width="754" height="1006" alt="The porch at night, string lights over outdoor seats"><figcaption class="cap">The patio</figcaption></figure>
      </div>
    </div>
  </section>

  <section class="bleed" aria-label="Behind the bar">
    <img src="/images/v3/behind-1200.webp" width="1200" height="675" alt="Bartenders working the rail at Sober Bar" loading="lazy" decoding="async">
    <div class="scrim"></div>
    <p class="pull">We didn’t want a juice bar. <em>We wanted a bar.</em></p>
  </section>

  <section>
    <div class="wrap">
      <span class="eyebrow">From the bar</span>
      <h2>Three to start.</h2>
      <div class="drinks" style="margin-top:22px">{''.join(drinks)}</div>
      <p style="margin-top:22px"><a class="text-link" href="/menu.html#cocktails">Full menu →</a></p>
    </div>
  </section>

  <section class="cream" id="menu-teaser">
    <div class="wrap">
      <span class="eyebrow" style="color:#6b5a32">Morning to late</span>
      <h2>Breakfast doesn’t clock out.</h2>
      <p class="room-copy muted">The kitchen stays with the bar. Same plates at 8am and 8pm.</p>
      <div class="food-row">
        <img src="/images/v3/morning-melt-800.webp" width="800" height="600" alt="The Classic Morning Melt breakfast sandwich" loading="lazy">
        <img src="/images/v3/muffuletta-800.webp" width="800" height="600" alt="The Muffuletta on toasted focaccia" loading="lazy">
      </div>
      <p style="margin-top:18px"><a href="/menu.html#breakfast">Breakfast</a> · <a href="/menu.html#kitchen">Kitchen</a></p>
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
        {faq_html(FACTS["faq"][:1])}
      </div>
      <a class="map-link" href="{FACTS["maps"]}"><img src="/images/v3/map.svg" width="800" height="360" alt="Map pin for 3062 Beach Blvd S, Gulfport"></a>
    </div>
  </section>

  <section class="close">
    <img src="/images/v3/bar-wide-1200.webp" width="1400" height="788" alt="The bar at night, pendant lights over the stools" loading="lazy">
    <div class="scrim"></div>
    <div class="wrap">
      <h2>Pull up a stool.</h2>
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
{faq_schema(FACTS["faq"][:1])}
'''
    write("index.html", shell(
        "Sober Bar & Kitchen — Gulfport",
        "Espresso at 7, zero-proof cocktails after dark, on Beach Boulevard in Gulfport.",
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
    <p class="lead" style="color:#3c342c">From the first coffee to the last cocktail. Ask us what it costs today.</p>
    {room("/images/v3/bar-wide-1200.webp", 1400, 788, "The bar at Sober Bar at night")}
    <nav class="chips" aria-label="Menu categories">{chips}</nav>
    {''.join(sections)}
    <p>{e(ALC)} Tell us about allergies before you order.</p>
    <p>{reserve("menu", "Reserve dinner")} <a class="text-link" href="/reservations.html" style="margin-left:16px">Reservations →</a></p>
    <p style="color:#3c342c">{e(BOOKING)}</p>
  </div>
</main>'''
    write("menu.html", shell(
        "Menu — Sober Bar & Kitchen",
        "Cocktails, coffee, breakfast, and the kitchen in Gulfport. Prices at the table.",
        "/menu.html",
        main,
        "menu",
    ))


def build_reservations():
    main = f'''<main id="main" class="page">
  <div class="wrap book">
    <h1>Reserve a table</h1>
    <p class="lead">Dinner, 4 to 9:30. Sunday brunch, 10 to 1. Every other hour, walk in and we’ll seat you.</p>
    <div class="hero-actions">
      <span data-hero-cta>{reserve("res", "Reserve dinner")}</span>
      <a class="text-link" data-placement="res-brunch" href="{e(BRUNCH)}">Reserve Sunday brunch</a>
    </div>
    {party_note()}
    {visit_card(show_phone=False)}
  </div>
</main>'''
    write("reservations.html", shell(
        "Reserve a table — Sober Bar",
        "Dinner books from 4 to 9:30. Sunday brunch, 10 to 1. Parties of 1–6. Daytime is walk-in.",
        "/reservations.html",
        main,
        "res",
    ))


def article(title, desc, path, h1, lead, body, placement, kind="dinner", book=True, label="Reserve a table", show_phone=True):
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
    {visit_card(show_phone)}
  </div>
</main>'''
    write(path.lstrip("/"), shell(title, desc, path, main, placement, kind=kind))


def build_rest():
    article(
        "Breakfast and coffee in Gulfport — Sober Bar",
        "Espresso, cold brew, and a New Orleans-inspired breakfast from 7am in Gulfport. Daytime is walk-in.",
        "/breakfast-gulfport.html",
        "Breakfast and coffee in Gulfport",
        "Espresso, cold brew, and breakfast with a New Orleans accent. Doors at 7.",
        "<p>The rest of the menu stays up until close.</p>" + menu_list(["coffee", "breakfast"]),
        "breakfast",
        book=False,
    )
    article(
        "Sunday jazz brunch in Gulfport — Sober Bar",
        "Live jazz every Sunday brunch at Sober Bar in Gulfport. Call for this Sunday’s set.",
        "/sunday-jazz-brunch.html",
        "Sunday jazz brunch in Gulfport",
        "Coffee’s on at 7. The set is why you stay.",
        f'''<p>Call <a href="tel:{TEL}">{PHONE}</a> for this Sunday’s set. We don’t publish the band or the start time.</p>
        <p>The full menu is on, including <strong>The White Rabbit</strong> and the plant-based <strong>Garden District Muffuletta</strong>. Stay late enough and order a <strong>Call Me an Ube</strong>.</p>''',
        "jazz",
        kind="brunch",
        label="Reserve Sunday brunch",
        show_phone=False,
    )
    article(
        "Mocktails — Sober Bar",
        "Zero-proof cocktails in Gulfport, a few minutes from St. Pete.",
        "/mocktails-st-petersburg.html",
        "A proper cocktail. Zero proof.",
        "Poured in Gulfport, a few minutes from St. Pete.",
        f"<p>Start with a Call Me an Ube.</p>{menu_list(['cocktails'])}",
        "mocktails",
    )
    gulf = '''
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
    '''
    article(
        "Things to do in Gulfport — Sober Bar",
        "Williams Pier, the beach, the markets, and a porch on Beach Boulevard.",
        "/things-to-do-in-gulfport.html",
        "Things to do in Gulfport",
        "The pier, the beach, the night market — and our porch when you’re walked out.",
        gulf,
        "gulfport",
    )
    story = '''
    <p>I kept asking a simple question: why does going out have to come with alcohol?</p>
    <p>Gulfport already had the art walk, the night market, and good food. Skip the drink and your choices were a coffee shop or a sad soda at someone else’s bar.</p>
    <h2>So I built the bar I wanted to walk into.</h2>
    <p>The kitchen is New Orleans-inspired. The drinks are built like the cocktails you already order. The room does the rest of the convincing.</p>
    <p>People walk in skeptical. Then they taste a Call Me an Ube and stay for the room.</p>
    <h2>Who it’s for</h2>
    <p>Designated drivers. Pregnant friends. People in recovery. People who simply don’t feel like it tonight. They still want the night out.</p>
    <p>The hard part wasn’t the recipes. It was proving a sober bar could still feel like a bar.</p>
    '''
    article(
        "Why I opened a sober bar — Sober Bar",
        "Sean Hawthorne on opening a cocktail bar and coffee house in Gulfport.",
        "/why-i-opened-a-sober-bar.html",
        "Why I opened a sober bar",
        "Gulfport had plenty of nights out. None of them were for people skipping the drink.",
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
        "FOX 13, I Love the Burg, St. Pete Rising, and The Gabber on Sober Bar in Gulfport.",
        "/as-seen-in.html",
        "As seen in",
        "Four stories worth reading. Room photos, ask Sean.",
        press + f"<p>Email <a href=\"mailto:{EMAIL}\">{EMAIL}</a> for photos.</p>",
        "press",
    )


def build_private():
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
    <p>No mail app? Email <a href="mailto:{EMAIL}">{EMAIL}</a> or <a href="tel:{TEL}">call the bar</a>.</p>
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
    body = f'''<p>Showers, birthdays, office gatherings, recovery milestones. Same room, same patio. Menus and pricing come back in the quote.</p>
    <p>The orders people request first: Call Me an Ube and Jinn &amp; Juniper.</p>
    <p><a href="/sunday-jazz-brunch.html">Sunday jazz</a> is this room, not a second venue.</p>
    {form}'''
    main = f'''<main id="main" class="page">
  <div class="wrap">
    <h1>Private events in Gulfport</h1>
    <p class="lead">Give us a date and a headcount. We’ll tell you if the room can throw it.</p>
    {room("/images/v3/hero-d-1200.webp", 1400, 875, "The lounge, where private gatherings sit")}
    <p><a class="reserve" href="#inquire">Plan your gathering</a></p>
    {body}
    <p style="margin-top:22px">{reserve("private-events")}</p>
    {visit_card(show_phone=False)}
  </div>
</main>'''
    write("private-events.html", shell(
        "Private events in Gulfport — Sober Bar",
        "Showers, birthdays, and gatherings in the Gulfport room. Tell us the date.",
        "/private-events.html",
        main,
        "private-events",
    ))


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
    <p class="lead">Tell us the event. We’ll tell you what we can actually bring.</p>
    {room("/images/v3/bar-wide-1200.webp", 1400, 788, "The bar at Sober Bar")}
    {form}
  </div>
</main>'''
    write("event-sponsorship.html", shell(
        "Event sponsorship — Sober Bar",
        "Custom event sponsorship with Sober Bar in Gulfport.",
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
        f"- Mocktails: {FACTS['domain']}/mocktails-st-petersburg.html",
        f"- Breakfast: {FACTS['domain']}/breakfast-gulfport.html",
        f"- Gulfport guide: {FACTS['domain']}/things-to-do-in-gulfport.html",
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
        "/sunday-jazz-brunch.html", "/private-events.html", "/mocktails-st-petersburg.html",
        "/things-to-do-in-gulfport.html", "/why-i-opened-a-sober-bar.html",
        "/as-seen-in.html",
    ]
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        pri = "1.0" if u == "/" else "0.7"
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
        "100% alcohol-free", "yes — 100", "50 seats", "30 indoor", "20 outdoor",
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
    if "morning-melt" not in home or "muffuletta-" not in home:
        raise SystemExit("homepage food row missing")
    if "productId=101287" not in home or "productId=101285" in home:
        raise SystemExit("homepage seat link drifted")
    mock = (PUBLIC / "mocktails-st-petersburg.html").read_text()
    if "productId=101287" not in mock or "In the Tampa Bay area" in mock:
        raise SystemExit("mocktails page drifted")
    breakfast_main = (PUBLIC / "breakfast-gulfport.html").read_text().split("<main", 1)[-1].split("</main", 1)[0]
    if "productId=" in breakfast_main:
        raise SystemExit("breakfast body has a seat link")
    jazz = (PUBLIC / "sunday-jazz-brunch.html").read_text()
    if "productId=101285" not in jazz:
        raise SystemExit("jazz should book brunch")
    skip_counts = {
        "concierge-card.html", "passport-card.html", "review-tent.html",
        "press-kit.html", "vote.html",
    }
    for path in PUBLIC.glob("*.html"):
        if path.name in skip_counts:
            continue
        visible = re.sub(r"<script[\s\S]*?</script>", " ", path.read_text(), flags=re.I)
        visible = re.sub(r"<head[\s\S]*?</head>", " ", visible, flags=re.I)
        visible = re.sub(r"\s(?:href|src|srcset|content)=\"[^\"]*\"", " ", visible)
        visible = re.sub(r"<[^>]+>", " ", visible)
        visible = html.unescape(visible)
        phones = visible.count(PHONE)
        streets = visible.count("3062")
        if phones > 3 or streets > 3:
            raise SystemExit(f"{path.name} mentions phone {phones}, address {streets}")
        low = visible.lower()
        for b in ("geckofest", "speakeasy", "free drink", "10% off", "kratom"):
            if b in low:
                raise SystemExit(f"{b} in {path.name}")
    if "kratom" in (PUBLIC / "review-tent.html").read_text().lower():
        raise SystemExit("review tent still lists kratom")
    print("facts check ok")


if __name__ == "__main__":
    build_home()
    build_menu()
    build_reservations()
    build_rest()
    build_private()
    build_sponsor()
    build_legal()
    build_llms_and_sitemap()
    check()
