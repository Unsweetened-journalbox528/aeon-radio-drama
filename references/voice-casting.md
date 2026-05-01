# Voice Casting Guide

## The Three-Lock System

Every character needs three locks for voice consistency:

### Lock 1: Voice Instruct

**Formula:** `[pitch & register] + [texture & quality] + [accent/origin] + [pace & rhythm] + [emotional baseline]`

**Tier examples by character archetype:**

| Archetype | Voice Instruct |
|-----------|---------------|
| Grizzled detective | "Gruff middle-aged man, Brooklyn accent, speaks in clipped sentences, gravel in the throat from decades of whiskey and late nights" |
| Young scientist | "Bright, quick feminine voice with precision and enthusiasm, words tumbling over each other when excited, Midwest American neutral" |
| Ancient being | "Deep, resonant voice with cosmic authority, speaking slowly as if each word spans centuries, neither fully masculine nor feminine" |
| Nervous witness | "Thin, reedy voice that rises in pitch under pressure, speaking in halting fragments, clearing throat frequently" |
| Warm narrator | "Rich, warm baritone with BBC-documentary clarity, unhurried pacing that lets ideas breathe, the voice of a trusted storyteller" |
| Child | "Young, clear voice with unfiltered honesty, slightly higher pitch, the natural musicality of someone discovering language" |
| Villain | "Silk-smooth tenor with unsettling calm, each word precisely placed, the warmth in the voice somehow making it more threatening" |
| Military leader | "Crisp, commanding alto, every syllable a bullet point, no wasted words, the accent of someone raised in institutions" |

### Lock 2: Voice Seed

- Any integer. Pick memorable numbers (42, 101, 200, etc.)
- Document in characters.json immediately upon assignment
- NEVER change a seed mid-production
- Different characters MUST have different seeds

### Lock 3: Emotion Overrides

Append to the base instruct. The seed stays the same.

**Standard set:**

```json
{
  "neutral": "",
  "tender": ", speaking with gentle tenderness and quiet intimacy",
  "broken": ", voice cracking with grief, barely holding together",
  "commanding": ", projecting with full authority, each word a decree",
  "fearful": ", voice tight with fear, words tumbling out faster",
  "intimate": ", barely above a whisper, close and confiding",
  "furious": ", voice shaking with barely contained rage",
  "joyful": ", bright and warm with genuine delight",
  "sorrowful": ", heavy with sadness, each word weighted with loss",
  "contemplative": ", thoughtful and measured, as if thinking aloud",
  "cautious": ", speaking more quietly, carefully measuring each word",
  "defiant": ", finding unexpected steel, each word planted firmly",
  "desperate": ", raw urgency stripping away all composure",
  "amused": ", a smile audible in the voice, warmth and wit",
  "exhausted": ", words coming slow and heavy, energy nearly spent"
}
```

Custom overrides for specific characters are even better — they capture the unique way that character expresses each emotion.

## Ensemble Design

### Contrast Checklist

Before finalizing a cast, verify contrast across:

- [ ] **Pitch spread** — at least one high, one mid, one low voice
- [ ] **Pace variety** — not everyone speaks at the same speed
- [ ] **Texture range** — mix smooth, rough, breathy, crisp
- [ ] **Energy levels** — contrast reserved with animated
- [ ] **Accent diversity** — helps instant recognition

### Common Pitfalls

- Two characters with similar pitch AND pace — listeners will confuse them
- All male or all female cast without enough texture variety
- Narrator voice too similar to a main character
- Over-describing voices (3+ sentences) — the model loses focus

## Characters.json Template

```json
{
  "production": "The Last Lighthouse",
  "characters": {
    "NARRATOR": {
      "voice_instruct": "Rich, warm baritone with BBC-documentary clarity, unhurried pacing",
      "seed": 200,
      "emotion_overrides": {
        "tense": ", pace tightening slightly, an undercurrent of urgency",
        "reflective": ", softer and more contemplative, almost speaking to oneself",
        "ominous": ", dropping lower, each word carrying weight and warning"
      }
    },
    "INSPECTOR": {
      "voice_instruct": "Sharp, precise feminine voice with authority, clipped professional cadence",
      "seed": 310,
      "emotion_overrides": {
        "cautious": ", speaking more quietly, carefully measuring each word",
        "commanding": ", projecting with full authority",
        "sympathetic": ", softening, genuine concern breaking through the professional shell"
      }
    },
    "KEEPER": {
      "voice_instruct": "Weathered elderly man, hoarse from years of sea air, speaking in halting fragments",
      "seed": 445,
      "emotion_overrides": {
        "fearful": ", voice dropping to a whisper, words tumbling over each other",
        "defiant": ", finding unexpected steel, each word planted firmly",
        "broken": ", the last reserves of strength crumbling, raw and exposed"
      }
    }
  }
}
```
