# Dubai Chocolatte — TikTok kit

Assets for the Dubai Chocolatte launch, built from the two product photos.

| File | What it is |
| --- | --- |
| `dubai-chocolatte-tiktok.mp4` | 1080×1920, 30fps, 10s, **silent by design** (see Sound) |
| `slides/` | 5-slide Photo Mode carousel, same story, same look |
| `src/` | The renderer, so the edit can be re-cut without starting over |

---

## The strategy in one paragraph

The Dubai chocolate trend is past its explosive phase and into its nostalgia
phase, so "we have Dubai chocolate" is no longer a hook on its own — plenty of
places have it. What almost nobody has is Dubai chocolate **you drink, in a bar
where nothing is alcoholic**. So the edit leads with food, not with sobriety:
the first six seconds are pure dessert, and the zero-proof reveal lands as the
twist at 6.4s. That ordering is deliberate — the venues doing best with
alcohol-free right now market the drink as a culinary object first and a
wellness choice second (or never).

## How the 10 seconds are built

| Time | Shot | On screen |
| --- | --- | --- |
| 0.0–1.7s | Macro push across the chocolate feather art | `DUBAI CHOCOLATE / BUT YOU DRINK IT` |
| 1.7–4.2s | Pull back off the foam to the whole glass | — (the reveal carries it) |
| 4.2–6.4s | Track down the chocolate inside the glass | `pistachio on top. chocolate all the way down.` |
| 6.4–8.2s | Cut to top-down, plate knocked down | `and it is completely` → **`0% ALCOHOL`** |
| 8.2–10.0s | Settle on the hero, end card | `SOBER BAR / GULFPORT · FLORIDA` |

Two things are doing the retention work. The opening frame is the **feather
latte art**, not the crumble — it's the most graphic, highest-contrast image in
either photo, so it survives being seen at thumbnail size in a fast scroll. And
`and it is completely` deliberately ends *before* a hard cut, so the sentence
finishes on the other side of it. Viewers hold through cuts to close an open
sentence.

## Sound — read this before you post

**The MP4 has a silent audio track on purpose.** Baked-in music competes with
whatever you add in-app, and TikTok's own audio library is where the
distribution advantage lives. Add the sound in the TikTok editor after upload.

One caveat that will bite you: **if @sipsoberbar is a Business account, you
cannot use trending sounds** — Business accounts are restricted to the
Commercial Music Library, because the licences covering personal use don't
extend to promotional use. A track that looks popular in your picker is popular
*within that library*, not on TikTok generally.

Your options, best first:

1. **Record your own audio.** Anything you record is unrestricted on any account
   type. Real ASMR over these visuals is the highest-value thing you could add:
   the crunch of pistachio being spooned on, the pour, ice settling in the glass.
   Ten seconds on a phone in a quiet room. This is what I'd do.
2. Use the Commercial Music Library — it's over a million tracks now, so it's no
   longer the graveyard it used to be.
3. Switch to a Creator account for trending audio, accepting that you lose some
   business features.

## Caption

Pick one. C is the one I'd run first — it asks for a comment you can answer in
two words, and comment volume is a stronger signal than likes.

**A — comment bait (recommended)**
> We turned the Dubai chocolate bar into a drink. Tell us what we should turn
> into a drink next 👇

**B — contrarian**
> A bar where you can't order a drink. Well — you can order this one. Dubai
> Chocolatte, now on at Sober Bar in Gulfport.

**C — straight**
> The Dubai Chocolatte just landed. Pistachio, dark chocolate, zero proof —
> because everything on our menu is. Gulfport, come get it.

## Hashtags

Broad for reach, niche for relevance, local for the people who can actually walk in.

```
#dubaichocolate #dubaichocolatebar #mocktail #mocktails #sobercurious
#zeroproof #nonalcoholic #soberbar #drinktok #foodtok
#gulfportfl #stpete #tampabay
```

Drop `#dubaichocolate` after the first two posts if reach is flat — that tag is
crowded and past peak. The alcohol-free tags are the durable ones:
`#sobercurious` and `#mocktails` carry enormous, year-round volume that isn't
tied to a trend cycle or to January.

## Also post the carousel

Photo Mode is currently out-reaching video for the same accounts, because swipes
count as session time and carousels get saved at a higher rate. `slides/` is the
same story in 5 slides. **Post it as a separate upload 2–3 days after the
video**, not the same day — mixed-format posting is itself rewarded, and you get
two shots at the same asset.

## Notes

- **Check the copy against the actual recipe.** `pistachio on top. chocolate all
  the way down.` describes what's visible in the photo. If the build has kataifi,
  say kataifi — that word is a search term people actively look for.
- **Cover frame:** pick around **3.5s** (the clean full glass) in TikTok's cover
  picker, not the default first frame — the macro is a great *hook* but a poor
  *thumbnail* on your profile grid, where it reads as an abstract texture.
- The address on the end card is 3062 Beach Blvd S. Verify before posting.

## Re-cutting it

`src/render.py` renders the frames; `src/slides.py` exports the carousel. Copy
changes live in `build_text_layers()`, timing in `SHOTS` and `BEATS`, camera
moves in `camera()`. The original photos are in `source/` and the two brand
faces (Josefin Sans, Cormorant Garamond — both SIL Open Font License) are
vendored in `src/fonts/`, so the whole kit re-cuts from a clean checkout with
nothing but Pillow, numpy, and ffmpeg.

```
python3 render.py && python3 slides.py
ffmpeg -y -framerate 30 -i frames/f%05d.png \
  -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 \
  -filter_complex "[0:v]unsharp=5:5:0.48:5:5:0.0,noise=alls=3:allf=t+u,format=yuv420p[v]" \
  -map "[v]" -map 1:a -shortest -c:v libx264 -preset slow -crf 18 \
  -profile:v high -level 4.1 -c:a aac -b:a 128k -movflags +faststart \
  dubai-chocolatte-tiktok.mp4
```
