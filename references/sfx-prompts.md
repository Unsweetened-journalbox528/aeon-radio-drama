# Sound Effects Prompt Guide (MMAudio primary, SAO fallback)

The same prompt vocabulary works for all three SFX engines in the pipeline (MMAudio, Stable Audio Open, ACE Step). The auto-router in `radio_drama.py` picks the engine by duration — you write one prompt and the tool routes.

## Prompt Writing Principles

All three engines respond best to specific, physical descriptions. The more concrete the prompt, the better the result.

**Good prompt formula:** `[material] + [action] + [environment] + [perspective/distance]`

- "Heavy wooden door creaking open slowly in a stone room, close perspective" — specific, physical, vivid
- "Door sound" — too vague, unpredictable results

**Engine-specific tips:**
- **MMAudio** (your ≤10 s default) responds especially well to **time-series phrasing** for multi-stage sounds ("engine struggles, cranks twice, finally catches and rumbles"). Its negative prompt is defaulted to `"music, speech, vocals, singing"` to keep it locked on SFX rather than drifting musical.
- **Stable Audio Open** (10–47 s fallback) prefers describing the **full acoustic space** for ambient beds ("rain pelting stone surfaces, wind gusts, distant thunder"). Excels at atmosphere-over-time.
- **ACE Step** (47+ s last resort) needs **genre-like tags** because it's a music model — describe the texture as if it were music ("low drone, sparse piano hits, spectral shimmer"). Don't use for short events.

**Universal tips:**
- Describe the physics, not the emotion ("metal scraping on concrete" not "scary sound")
- Include the acoustic space ("in a large cathedral", "in a small bathroom", "outdoors on a hilltop")
- Specify distance ("close mic", "distant", "overhead")
- **Prefer ≤10 s events** to stay on MMAudio. Split a 15 s complex SFX into three separate cues: it's cleaner and each sub-event renders at the highest-quality engine.
- For ambient beds longer than 47 s, generate several clips and crossfade (covered in `mixing-guide.md`).

## Prompt Library by Category

### Environment / Weather

| Description | Prompt |
|------------|--------|
| Rain (light) | "Gentle rain falling on leaves and grass, soft patter, outdoor garden, peaceful" |
| Rain (heavy storm) | "Heavy downpour pelting stone surfaces, wind gusts, distant thunder rumbles, stormy night" |
| Thunder | "Single loud thunder crack, close, rattling windows, followed by rolling echo across sky" |
| Wind | "Strong wind howling across an open clifftop, whistling through gaps in rock, isolated location" |
| Ocean waves | "Ocean waves crashing against rocky shoreline, rhythmic, salt spray, seagulls distant" |
| Forest | "Quiet forest ambience, birdsong, leaves rustling in gentle breeze, insects buzzing, summer afternoon" |
| City street | "Busy city street ambience, passing cars, distant horns, pedestrian chatter, urban hum" |
| Night crickets | "Nighttime rural ambience, crickets chirping, occasional owl hoot, light breeze through tall grass" |

### Doors & Movement

| Description | Prompt |
|------------|--------|
| Wooden door open | "Heavy wooden door creaking open slowly on old hinges, stone room, medieval" |
| Door slam | "Wooden door slamming shut forcefully, the bang echoing in a hallway" |
| Metal gate | "Iron gate swinging open with a metallic screech, rusty hinges, outdoor" |
| Knock | "Three firm knocks on a heavy wooden door, deliberate spacing, indoor hallway" |
| Lock turning | "Old metal key turning in a heavy lock mechanism, click of tumblers, close mic" |

### Footsteps

| Description | Prompt |
|------------|--------|
| Gravel | "Deliberate footsteps crunching on loose gravel path, outdoor, steady walking pace" |
| Stone | "Leather shoes on stone floor, echoing in large empty room, steady walking pace" |
| Wooden floor | "Footsteps on old wooden floorboards, some boards creaking, indoor, quiet house" |
| Running | "Someone running on wet pavement, splashing through shallow puddles, urgent pace, night" |
| Stairs | "Footsteps ascending stone spiral staircase, echoing, slightly out of breath" |
| Snow | "Boots crunching through fresh snow, cold winter day, slow deliberate steps" |

### Technology / Mechanical

| Description | Prompt |
|------------|--------|
| Phone ring | "Old rotary telephone ringing, mechanical bell, indoor office, vintage" |
| Car engine | "Car engine starting up on a cold morning, initial crank, then idle purr" |
| Car door | "Car door opening and closing, metal thunk, outdoor, gravel parking area" |
| Typing | "Rapid typing on a mechanical keyboard, clickety-clack, office ambience, focused work" |
| Clock ticking | "Old grandfather clock ticking steadily, pendulum swing, quiet room, close mic" |
| Radio static | "Old radio tuning through static, fragments of distant voices between frequencies, vintage crackle" |

### Dramatic Punctuation

| Description | Prompt |
|------------|--------|
| Glass breaking | "Wine glass shattering on stone floor, sharp crystal fragments scattering, indoor, sudden" |
| Gunshot | "Single gunshot, handgun, outdoor, sharp crack with echo rolling across open landscape" |
| Explosion (distant) | "Distant explosion, low rumble building to a boom, shockwave rattling windows, then settling debris" |
| Scream | "A sudden scream of terror, feminine, cut short, echoing in a stairwell, distant" |
| Heartbeat | "Human heartbeat sound, steady then gradually accelerating, close and intimate, tense" |
| Silence after crash | "The ringing silence after a loud impact, tiny debris settling, dust falling, tinnitus tone fading" |

### Transitions

| Description | Prompt |
|------------|--------|
| Dream transition | "Ethereal shimmer, like wind chimes in reverse, swirling into soft white noise, dreamlike" |
| Time passing | "Clock ticking accelerating into fast-forward blur, then decelerating back to normal, time lapse" |
| Underwater | "Muffled underwater ambience, slow bubbles rising, distant whale-like tones, deep ocean" |
| Flashback | "Vinyl record scratch transitioning into muffled vintage room tone, old radio quality" |
| Tension riser | "Low rumbling crescendo building from silence, sub-bass vibration increasing, cinematic tension rise" |

### Foley / Everyday

| Description | Prompt |
|------------|--------|
| Paper | "Pages of a book turning slowly, paper rustling, quiet reading room" |
| Writing | "Pen scratching on paper, fountain pen, deliberate handwriting, close mic, quiet room" |
| Pouring drink | "Liquid pouring from a bottle into a glass, wine, gentle glug, close mic, evening" |
| Fire | "Crackling fireplace, logs shifting and popping, warm indoor room, cozy" |
| Chains | "Heavy metal chains dragging across stone floor, prison dungeon, echoing, slow" |
| Cloth | "Fabric rustling, heavy coat being put on, leather creaking, indoor" |

## Layering Strategy

For rich soundscapes, generate multiple SFX clips and layer them:

1. **Base ambience** (long clip, 30-47s) — the environmental bed (rain, forest, city)
2. **Spot effects** (short clips, 2-10s) — specific events (door, footstep, glass break)
3. **Texture** (medium clip, 10-20s) — subtle detail layers (distant bird, clock tick, wind gust)

Mix the base at ~60% volume, spot effects at 70-90%, and texture at 30-40%. This creates depth without muddiness.

## Troubleshooting

- **Clip sounds metallic or artificial** — add acoustic space to the prompt ("in a large room with stone walls")
- **Too many sounds at once** — simplify the prompt. One clear sound per generation, layer in post
- **Wrong duration** — Stable Audio sometimes generates shorter than requested. Generate at 1.5x needed length and trim
- **Music instead of SFX** — avoid musical terms in SFX prompts. Say "rhythmic" not "beat", "rising tone" not "melody"
