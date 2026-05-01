# Radio Drama Script Format — JSON Schema

## Top-Level Structure

```json
{
  "title": "string — production title",
  "genre": "string — e.g. mystery/thriller, sci-fi, comedy, horror, drama",
  "target_duration_minutes": "number — estimated total runtime",
  "characters": ["array of character ID strings used in the script"],
  "acts": ["array of Act objects"]
}
```

## Act Object

```json
{
  "act_number": 1,
  "title": "string — act title",
  "scenes": ["array of Scene objects"]
}
```

## Scene Object

```json
{
  "scene_id": "string — unique ID, e.g. act1_scene1",
  "location": "string — setting description for context",
  "elements": ["array of Element objects, in playback order"]
}
```

## Element Types

### narration
Narrator voice-over. Rendered via FB_Qwen3TTSVoiceDesign with the NARRATOR voice config.

```json
{
  "type": "narration",
  "text": "The lighthouse had been dark for three days when Inspector Mara arrived.",
  "emotion": "neutral"
}
```

Fields: `text` (required), `emotion` (optional, defaults to "neutral").

### dialogue
Character speech. Rendered via FB_Qwen3TTSVoiceDesign with the character's voice config + emotion override.

```json
{
  "type": "dialogue",
  "character": "INSPECTOR",
  "text": "Hello? Anyone here?",
  "emotion": "cautious",
  "delivery_note": "calling out, voice echoing in the stone stairwell"
}
```

Fields: `character` (required — must match a key in characters.json), `text` (required), `emotion` (optional), `delivery_note` (optional — context for voice instruct refinement, not directly rendered).

### music_cue
Background score or transitional music. Rendered via ACE Step 1.5 XL.

```json
{
  "type": "music_cue",
  "mood": "tense_ambient",
  "description": "Low drone with distant foghorn motif, building unease",
  "duration_s": 30,
  "fade_in_s": 3,
  "fade_out_s": 5,
  "preset": "dark_tribunal"
}
```

Fields: `mood` (required — guides ACE preset/parameter selection), `description` (required — becomes the ACE prompt tags), `duration_s` (required), `fade_in_s` (optional), `fade_out_s` (optional), `preset` (optional — one of the 6 ACE presets).

Mood vocabulary: tense_ambient, warm_intimate, dark_foreboding, triumphant, melancholic, mysterious, action_urgent, pastoral_calm, sacred_ethereal, comedic_light.

### sfx_cue
Sound effect. Auto-routed by duration: **MMAudio Large 44k v2** for ≤10 s (primary, best quality), **Stable Audio Open 1.0** for 10–47 s, **ACE Step** as last resort for longer ambient beds.

```json
{
  "type": "sfx_cue",
  "description": "Heavy rain and crashing waves against rocks",
  "duration_s": 5,
  "volume": 0.8
}
```

Fields: `description` (required — specific and physical; material + action + environment + perspective), `duration_s` (required; prefer ≤10 s to stay on the best engine, max 47 s before falling back to ACE), `volume` (optional, 0.0-1.0, default 1.0 — relative mix level).

**Tip:** Split long SFX into multiple consecutive events rather than one long cue — a 15 s "door slam + footsteps + fumble for keys + latch" is three 3-5 s MMAudio events, not one 15 s SAO event. Cleaner result.

### pause
Silence or beat. Critical for pacing and dramatic effect.

```json
{
  "type": "pause",
  "duration_s": 2
}
```

Fields: `duration_s` (required). Use 0.5-1s for conversational beats, 2-3s for dramatic beats, 3-5s for scene transitions.

### direction
Production note that is NOT rendered as audio. Provides context for the AI during generation.

```json
{
  "type": "direction",
  "note": "The keeper emerges from shadow — we should hear his footsteps before his voice"
}
```

Fields: `note` (required). Use to guide SFX placement, emotional arcs, or timing decisions.

## Complete Example: Opening Scene

```json
{
  "title": "The Last Lighthouse",
  "genre": "mystery/thriller",
  "target_duration_minutes": 15,
  "characters": ["NARRATOR", "INSPECTOR", "KEEPER"],
  "acts": [
    {
      "act_number": 1,
      "title": "The Arrival",
      "scenes": [
        {
          "scene_id": "act1_scene1",
          "location": "Lighthouse exterior, stormy night",
          "elements": [
            {"type": "sfx_cue", "description": "Heavy storm — rain pelting stone, wind howling across open clifftop, distant crashing waves", "duration_s": 6, "volume": 0.7},
            {"type": "music_cue", "mood": "tense_ambient", "description": "low dark drone, sparse piano notes, foghorn-like bass swells, unsettling", "duration_s": 45, "fade_in_s": 3, "preset": "dark_tribunal"},
            {"type": "narration", "text": "The lighthouse had been dark for three days when Inspector Mara arrived. The coast guard found that curious. The inspector found it suspicious.", "emotion": "neutral"},
            {"type": "sfx_cue", "description": "Car door slam on wet gravel, then deliberate footsteps crunching on rain-soaked gravel path", "duration_s": 4},
            {"type": "direction", "note": "Inspector approaches the lighthouse door — her footsteps transition from gravel to stone steps"},
            {"type": "sfx_cue", "description": "Footsteps ascending worn stone steps, rain now muffled, heavy wooden door handle turning", "duration_s": 3},
            {"type": "dialogue", "character": "INSPECTOR", "text": "Hello? Anyone here?", "emotion": "cautious", "delivery_note": "calling out, voice echoing slightly"},
            {"type": "pause", "duration_s": 2.5},
            {"type": "sfx_cue", "description": "Slow, shuffling footsteps on stone floor, approaching from darkness", "duration_s": 3, "volume": 0.5},
            {"type": "dialogue", "character": "KEEPER", "text": "You shouldn't have come.", "emotion": "fearful"},
            {"type": "pause", "duration_s": 1},
            {"type": "dialogue", "character": "INSPECTOR", "text": "Mr. Harwell? I'm Inspector Mara. The coast guard reported your light went out Tuesday night.", "emotion": "neutral"},
            {"type": "dialogue", "character": "KEEPER", "text": "The light didn't go out. I turned it off.", "emotion": "defiant", "delivery_note": "a sudden shift from fear to conviction"},
            {"type": "sfx_cue", "description": "Thunder crack, close, rattling windowpanes", "duration_s": 2},
            {"type": "music_cue", "mood": "dark_foreboding", "description": "music intensifies, lower register, pulsing bass, tension building", "duration_s": 20, "fade_in_s": 1},
            {"type": "dialogue", "character": "INSPECTOR", "text": "You turned it off. Ships depend on that light, Mr. Harwell. People could have died.", "emotion": "commanding"},
            {"type": "dialogue", "character": "KEEPER", "text": "People already did. That's why I turned it off.", "emotion": "broken", "delivery_note": "the defiance crumbles, replaced by deep grief"},
            {"type": "pause", "duration_s": 3},
            {"type": "narration", "text": "The wind screamed against the lighthouse walls. And in that pause, Inspector Mara understood: she hadn't come to investigate a malfunction. She'd stumbled into something far worse.", "emotion": "tense"}
          ]
        }
      ]
    }
  ]
}
```

## Script Writing Guidelines

When generating a script from creative input:

1. **Open with atmosphere** — start every scene with SFX and music to establish the world before anyone speaks
2. **Alternate element types** — avoid long runs of dialogue without SFX or music changes; the audio landscape should be alive
3. **Use pauses deliberately** — silence is the most powerful dramatic tool in audio
4. **Write for the ear** — dialogue should be speakable. Read it aloud mentally. Avoid complex sentence structures that sound fine on paper but stumble in speech
5. **Music cue moods should evolve** — don't set one mood per scene. Let the score track the emotional arc
6. **SFX ground the listener** — specific physical sounds (footsteps, doors, rain) create the visual picture that audio drama lacks
7. **Direction elements are free** — use them liberally to guide audio generation without adding to runtime
8. **Target duration math** — dialogue reads at ~120-150 words per minute. A 15-minute drama needs ~1800-2250 words of spoken text, plus time for SFX, music, and pauses
