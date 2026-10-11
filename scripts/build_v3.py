#!/usr/bin/env python3
"""Render static pages from public/facts.json."""
import html
import json
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


def seat(placement):
    return f'{FACTS["seatOn"]}?channel=site&placement={e(placement)}'


def reserve(placement, label="Reserve a table", extra=""):
    return (
        f'<a class="reserve" data-placement="{e(placement)}" href="{seat(placement)}"{extra}>'
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


def header():
    return '''<header class="site-header" id="nav">
  <a class="mark" href="/">Sober Bar</a>
  <nav class="nav-links" aria-label="Primary">
    <a href="/menu.html">Menu</a>
    <a href="/#the-room">The Room</a>
    <a href="/#visit">Visit</a>
    ''' + reserve("nav") + '''
  </nav>
  <button class="burger" id="burger" type="button" aria-expanded="false" aria-controls="drawer">Menu</button>
</header>
<nav class="drawer" id="drawer" aria-label="Mobile">
  <a href="/menu.html">Menu</a>
  <a href="/#the-room">The Room</a>
  <a href="/#visit">Visit</a>
  ''' + reserve("nav") + '''
  <a href="tel:''' + TEL + '''">''' + PHONE + '''</a>
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


def sticky(placement):
    return f'''<nav class="sticky" aria-label="Call, reserve, or directions">
  <a href="tel:{TEL}">Call</a>
  {reserve("sticky", "Reserve")}
  <a href="{FACTS["maps"]}">Directions</a>
</nav>
<script src="/site.js" defer></script>
</body>
</html>
'''


def shell(title, desc, path, main, placement, preload="", body_class="pad"):
    return head(title, desc, path, preload, body_class) + header() + main + footer() + sticky(placement)


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
      <p class="lead">Zero-proof cocktails after dark. Coffee and New Orleans-inspired plates from 7am.</p>
      <div class="hero-actions">
        <span data-hero-cta>{reserve("hero")}</span>
        <a class="text-link" href="/menu.html">View menu →</a>
      </div>
    </div>
  </section>

  <section id="the-room">
    <div class="wrap">
      <span class="eyebrow">The Room</span>
      <h2>Chandeliers, then the patio.</h2>
      <p class="room-copy">We wanted a bar, not a juice bar. Coffee at open. The room turns after dark.</p>
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
      <h2>Plates from 7am.</h2>
      <p class="room-copy muted">The kitchen stays open with the bar. Same list, open to close.</p>
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
        <p class="fine">{e(ALC)}</p>
        <details>
          <summary>{e(FACTS["faq"][0]["q"])}</summary>
          <p>{e(FACTS["faq"][0]["a"])}</p>
        </details>
      </div>
      <a class="map-link" href="{FACTS["maps"]}"><img src="/images/v3/map.svg" width="800" height="360" alt="Map pin for 3062 Beach Blvd S, Gulfport"></a>
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
  "url": "{FACTS["domain"]}/",
  "telephone": "{TEL}",
  "email": "{EMAIL}",
  "servesCuisine": "New Orleans-inspired",
  "acceptsReservations": "{FACTS["seatOn"]}",
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
  "sameAs": ["{FACTS["instagram"]}", "{LISTING}"]
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{{
    "@type": "Question",
    "name": {json.dumps(FACTS["faq"][0]["q"])},
    "acceptedAnswer": {{ "@type": "Answer", "text": {json.dumps(FACTS["faq"][0]["a"])} }}
  }}]
}}
</script>
'''
    write("index.html", shell(
        "Sober Bar & Kitchen — Gulfport",
        "A bar for staying out, minus the hangover. Zero-proof cocktails, coffee, and New Orleans-inspired plates on Beach Boulevard.",
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
    <p>{reserve("menu")} <a class="text-link" href="/reservations.html" style="margin-left:16px">Reservations →</a></p>
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
    <p class="lead">Booking opens on SeatOn.</p>
    <span data-hero-cta>{reserve("res")}</span>
    {party_note()}
    <p class="fine">Walk-ins are welcome.</p>
    {visit_card()}
  </div>
</main>'''
    write("reservations.html", shell(
        "Reserve a table — Sober Bar",
        "Book a table at Sober Bar in Gulfport. Walk-ins welcome. Online booking opens on SeatOn.",
        "/reservations.html",
        main,
        "res",
    ))


def article(title, desc, path, h1, lead, body, placement):
    main = f'''<main id="main" class="page">
  <div class="wrap">
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
    {room("/images/v3/hero-d-1200.webp", 1400, 875, "The lounge at Sober Bar under the chandelier")}
    {body}
    <p style="margin-top:22px"><span data-hero-cta>{reserve(placement)}</span> <a class="text-link" href="/menu.html" style="margin-left:16px">View menu →</a></p>
    {visit_card()}
  </div>
</main>'''
    write(path.lstrip("/"), shell(title, desc, path, main, placement))


def build_rest():
    article(
        "Breakfast and coffee in Gulfport — Sober Bar",
        "Espresso, cold brew, chai, and a New Orleans-inspired breakfast from 7am at Sober Bar in Gulfport.",
        "/breakfast-gulfport.html",
        "Breakfast and coffee in Gulfport",
        "Espresso, cold brew, and a New Orleans-inspired breakfast from 7am. Walk-ins are welcome.",
        "<p>The espresso bar is open with the doors. The full menu runs open to close.</p>" + menu_list(["coffee", "breakfast"]) + f"<p>{e(ALC)}</p>",
        "breakfast",
    )
    article(
        "Sunday jazz brunch in Gulfport — Sober Bar",
        "Live jazz every Sunday brunch at Sober Bar in Gulfport. Call (813) 586-1660 for this Sunday's jazz time.",
        "/sunday-jazz-brunch.html",
        "Sunday jazz brunch in Gulfport",
        "Live jazz in the room every Sunday brunch. Reserve a table if you want it held.",
        f'''<p>The doors are already open at 7am if you want coffee first. Walk-ins are welcome. Call <a href="tel:{TEL}">{PHONE}</a> for this Sunday’s jazz time. No band or start time is published.</p>
        <p>The full menu runs on Sunday, including <strong>The White Rabbit</strong> and the plant-based <strong>Garden District Muffuletta</strong>. Later, the bar pours <strong>Call Me an Ube</strong>.</p>
        <p>{e(ALC)}</p>''',
        "jazz",
    )
    article(
        "Mocktails near St. Pete — Sober Bar",
        "Zero-proof cocktails at Sober Bar in Gulfport, on Beach Boulevard near St. Petersburg.",
        "/mocktails-st-petersburg.html",
        "Zero-proof cocktails near St. Pete",
        "Sober Bar pours zero-proof cocktails in Gulfport, on Beach Boulevard.",
        f"<p>No drive time is published. Come for the room, then the list.</p>{menu_list(['cocktails'])}<p>{e(ALC)}</p>",
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
    <h2>GeckoFest</h2>
    <p><a href="https://visitgulfportflorida.com/event/gecko-fest/">GeckoFest</a> is Gulfport’s annual street festival. The chamber lists the 2026 festival for Saturday, September 5, 10 a.m.–8 p.m.</p>
    '''
    article(
        "Things to do in Gulfport — Sober Bar",
        "A local guide to Gulfport's pier, beach, markets, and Sober Bar on Beach Boulevard.",
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
    <p>Sober Bar at {e(A["street"])} is a coffee house by day and a cocktail bar by night. The kitchen is New Orleans-inspired. The drinks are built like craft cocktails. {e(ALC)}</p>
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
    body = f'''<p>Showers, birthdays, office gatherings, and recovery milestones use the same room and patio. Tell us the date and headcount and we’ll confirm what fits. Menus and pricing are in the quote.</p>
    <p>{e(ALC)} Popular builds include Call Me an Ube and Jinn &amp; Juniper.</p>
    <p><a href="/sunday-jazz-brunch.html">Sunday jazz brunch</a> is the same room, not a separate venue.</p>
    {form}'''
    main = f'''<main id="main" class="page">
  <div class="wrap">
    <h1>Private events in Gulfport</h1>
    <p class="lead">Tell us the date and headcount. We’ll confirm what fits.</p>
    {room("/images/v3/hero-d-1200.webp", 1400, 875, "The lounge, where private gatherings sit")}
    <p><a class="reserve" href="#inquire">Plan your gathering</a></p>
    {body}
    <p style="margin-top:22px">{reserve("private-events")}</p>
    {visit_card()}
  </div>
</main>'''
    write("private-events.html", shell(
        "Private events in Gulfport — Sober Bar",
        "Showers, birthdays, office gatherings, and recovery milestones at Sober Bar in Gulfport.",
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
        f"- {FACTS['partyLimit']} Walk-ins are welcome.",
        f"- {FACTS['jazz']}",
        f"- Reserve: {FACTS['seatOn']}",
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
    ]
    party_ok = set()
    for path in PUBLIC.glob("*.html"):
        text = path.read_text().lower()
        for b in banned:
            if b in text:
                raise SystemExit(f"banned {b} in {path.name}")
        if "party of 7" in text and path.name not in party_ok:
            raise SystemExit(f"party of 7 on {path.name}")
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
