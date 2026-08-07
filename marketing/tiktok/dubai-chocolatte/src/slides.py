"""Photo Mode carousel - same look as the film, hand-picked compositions."""
from pathlib import Path
import render as R

OUT = Path("slides"); OUT.mkdir(exist_ok=True)
for f in OUT.glob("*.jpg"): f.unlink()

src = R.load_sources()
L = R.build_text_layers()

# (timestamp in the film, slide name) - one idea per slide, 5 total
PICKS = [
    (1.00, "1-hook"),        # macro feather + "but you drink it"
    (3.60, "2-reveal"),      # the clean money shot, no type
    (5.00, "3-detail"),      # drizzle + sensory line
    (7.30, "4-zero"),        # 0% ALCOHOL
    (9.60, "5-visit"),       # end card
]
for t, name in PICKS:
    R.compose(t, src, L).save(OUT / f"slide-{name}.jpg", quality=93, subsampling=0)
    print("  ", name)
print("slides written")
