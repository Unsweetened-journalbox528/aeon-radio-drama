---
name: radio-drama-producer
description: >
  Full-pipeline radio drama and audiobook production — from creative premise to finished mixed audio.
  USE THIS SKILL whenever the user mentions: radio drama, audio drama, audiobook, audio play, radio play,
  podcast drama, audio fiction, radio theatre, audio storytelling, dramatic audio, audio production,
  voice acting project, audio book production, sound design for story, audio narrative, spoken word
  production, dramatic podcast, audio series, radio show, audio episode, voice drama, or any request
  to produce a complete audio production with multiple voices, music, and sound effects. Also trigger
  when the user wants to turn a story idea into a full audio production, create a podcast episode with
  characters and music, or produce any multi-track audio narrative combining dialogue, score, and SFX.
  This skill orchestrates four ComfyUI audio systems (Qwen3-TTS for voice, ACE Step 1.5 XL for music,
  MMAudio Large 44k v2 for SFX, Stable Audio Open 1.0 as SFX fallback for >10s clips) into a
  unified production pipeline. See `radio-drama-production` for the SSH runbook that invokes this.
---

# Radio Drama Producer — Full Pipeline Skill

Produce complete radio dramas, audiobooks, and audio fiction from a creative premise. This skill orchestrates the full pipeline: script writing, voice casting, audio generation (dialogue + music + SFX), and final mixed output.

## The Four-Phase Pipeline

**Phase 1: Script** — Write a structured radio drama script from the user's creative input
**Phase 2: Voice Casting** — Design unique voices for every character using the Three-Lock system
**Phase 3: Audio Generation** — Render all dialogue, music, and SFX via ComfyUI workflows
**Phase 4: Assembly & Mix** — Stitch and master everything into a finished audio file

## Phase 1: Script Writing

Accept the user's creative input (premise, genre, characters, tone, target length) and write a complete radio drama script in structured JSON format.

The script JSON is the backbone of the entire pipeline — every downstream phase parses it. See `references/script-format.md` for the full schema.

### Script Structure

```json
{
  "title": "The Last Lighthouse",
  "genre": "mystery/thriller",
  "target_duration_minutes": 15,
  "characters": ["KEEPER", "INSPECTOR", "NARRATOR"],
  "acts": [
    {
      "act_number": 1,
      "title": "The Arrival",
      "scenes": [
        {
          "scene_id": "act1_scene1",
          "location": "Lighthouse exterior, stormy night",
          "elements": [
            {"type": "sfx_cue", "description": "Heavy rain and crashing waves against rocks", "duration_s": 5},
            {"type": "music_cue", "mood": "tense_ambient", "description": "Low drone with distant foghorn motif", "duration_s": 30, "fade_in_s": 3},
            {"type": "narration", "text": "The lighthouse had been dark for three days when Inspector Mara arrived.", "emotion": "neutral"},
            {"type": "sfx_cue", "description": "Car door slam, footsteps on wet gravel", "duration_s": 3},
            {"type": "dialogue", "character": "INSPECTOR", "text": "Hello? Anyone here?", "emotion": "cautious"},
            {"type": "pause", "duration_s": 2},
            {"type": "dialogue", "character": "KEEPER", "text": "You shouldn't have come.", "emotion": "fearful"}
          ]
        }
      ]
    }
  ]
}
```

### Element Types

| Type | Purpose | Key Fields |
|------|---------|------------|
| `narration` | Narrator voice-over | text, emotion |
| `dialogue` | Character speech | character, text, emotion, (optional) delivery_note |
| `music_cue` | Background score | mood, description, duration_s, fade_in_s, fade_out_s |
| `sfx_cue` | Sound effect | description, duration_s |
| `pause` | Silence/beat | duration_s |
| `direction` | Production note (not rendered) | note |

### Pacing Guidelines

- Open scenes with SFX/ambience to establish location (3-5s)
- Music cues should overlap dialogue, not compete — use low-energy backgrounds during speech
- Insert 1-2s pauses after emotional beats to let moments land
- Scene transitions: 2-3s crossfade with transitional SFX or music shift
- Target ~120-150 words per minute for dialogue pacing

## Phase 2: Voice Casting

Design voices for every character using the Three-Lock system from the tts-voice-designer skill.

For each character, define:
1. **voice_instruct** — natural language vocal description
2. **seed** — fixed integer for consistency
3. **emotion_overrides** — per-emotion instruct additions

### Casting Manifest

```json
{
  "characters": {
    "NARRATOR": {
      "voice_instruct": "Calm, measured feminine voice with BBC-documentary clarity, unhurried pacing",
      "seed": 200,
      "emotion_overrides": {
        "tense": ", pace tightening slightly, an undercurrent of urgency",
        "reflective": ", softer and more contemplative, almost speaking to herself"
      }
    },
    "INSPECTOR": {
      "voice_instruct": "Sharp, precise feminine voice with authority, clipped professional cadence",
      "seed": 310,
      "emotion_overrides": {
        "cautious": ", speaking more quietly, carefully measuring each word",
        "commanding": ", projecting with full authority"
      }
    },
    "KEEPER": {
      "voice_instruct": "Weathered elderly man, hoarse from years of sea air, speaking in halting fragments",
      "seed": 445,
      "emotion_overrides": {
        "fearful": ", voice dropping to a whisper, words tumbling over each other",
        "defiant": ", finding unexpected steel, each word planted firmly"
      }
    }
  }
}
```

Design for **contrast** — listeners distinguish characters by voice alone. Vary pitch, pace, texture, accent, and energy across the cast. See `references/voice-casting.md` for detailed guidance.

## Phase 3: Audio Generation

> ## ⛔ STOP — DO NOT BUILD COMFYUI WORKFLOWS BY HAND
>
> Every workflow shown below is **already built and tested** inside `scene_production_tool/radio_drama.py`. The JSON examples in this section are **reference material** — they document what the orchestrator constructs internally, not a runtime contract you should reimplement.
>
> **The correct way to generate audio:**
>
> ```bash
> # Full pipeline (dialogue + music + SFX + mix), one command:
> python ${COMFYUI_ROOT}\scene_production_tool\radio_drama.py <project_name> --stage all
>
> # Or per-stage (idempotent — already-rendered assets are skipped on re-run):
> python radio_drama.py <project_name> --stage tts
> python radio_drama.py <project_name> --stage music
> python radio_drama.py <project_name> --stage sfx
> python radio_drama.py <project_name> --stage mix
> ```
>
> The orchestrator handles: workflow construction, APG chain wiring (xl_base/xl_sft music), schema validation, ComfyUI submission, retry-on-transient-error, output collection, canonicalization to 48 kHz/stereo/pcm_s24le, and dynamics-preserving mastering.
>
> **Symptoms you're heading the wrong direction:**
> - "I'm checking the model loader for ACE Step…"
> - "Let me find the proper VAE node…"
> - "I need to figure out the negative conditioning structure…"
> - HTTP 400 on `/prompt` submission with cryptic node validation errors
> - "I don't have a compatible workflow template"
>
> All of these mean **stop and use `radio_drama.py`**. The workflow JSON in this section exists so you can understand what's happening, not so you can rebuild it. See `radio-drama-production` for the SSH runbook.
>
> **When to use `music_maker.py` instead:** if dialogue was generated outside the radio-drama project structure (or doesn't exist yet) and you only need music cues, call `music_tool/music_maker.py` directly — see "Standalone music generation" subsection at the end of this Phase.

The three systems below handle different tracks. The JSON shown is **what the orchestrator builds**, not what you should write by hand.

### Track 1: Dialogue & Narration (Qwen3-TTS)

For each `narration` and `dialogue` element in the script, the orchestrator constructs a workflow like this:

```json
{
  "1": {
    "class_type": "FB_Qwen3TTSVoiceDesign",
    "inputs": {
      "text": "<element text>",
      "voice_instruct": "<base_instruct + emotion_override>",
      "seed": "<character seed>"
    }
  },
  "2": {
    "class_type": "SaveAudio",
    "inputs": {
      "audio": ["1", 0],
      "filename_prefix": "<scene_id>_<element_index>_<character>"
    }
  }
}
```

For scenes with rapid dialogue, use DialogueInference for natural conversational flow:

```json
{
  "1": {
    "class_type": "FB_Qwen3TTSRoleBank",
    "inputs": {
      "roles": [<role definitions from casting manifest>]
    }
  },
  "2": {
    "class_type": "FB_Qwen3TTSDialogueInference",
    "inputs": {
      "script": "[character1] Line... [character2] Line...",
      "role_bank": ["1", 0],
      "pause_between_roles_ms": 400,
      "pause_between_sentences_ms": 200
    }
  },
  "3": {
    "class_type": "SaveAudio",
    "inputs": { "audio": ["2", 0], "filename_prefix": "<scene_id>_dialogue" }
  }
}
```

### Track 2: Music & Score (ACE Step 1.5 XL)

> **Reminder: do not assemble ACE Step workflows by hand.** `radio_drama.py --stage music` is the entry point. It imports `music_tool/music_maker.py` and dispatches to the right template (APG vs simple) based on the variant in your script. The JSON below is **reference for understanding what gets built**, not something to copy-paste into ComfyUI.

#### Default: xl_base with APG chain (12-node graph)

The current default is `xl_base` (50 steps, CFG 7.0, full fp32 base model, with the APG chain required for clean output from base models). This is the same chain `music_maker.py` uses for standalone tracks — both routes share `music_tool/templates/ace_step_music_apg_api.json`.

```json
{
  "1":  {"class_type": "UNETLoader",           "inputs": {"unet_name": "acestep_v1.5_xl_base.safetensors", "weight_dtype": "default"}},
  "2":  {"class_type": "CLIPLoader",           "inputs": {"clip_name": "umt5_base.safetensors", "type": "ace"}},
  "3":  {"class_type": "VAELoader",            "inputs": {"vae_name": "ace_step_audio_vae.safetensors"}},
  "4":  {"class_type": "TextEncodeAceStepAudio1.5", "inputs": {
            "tags": "<mood/style/instrument tags>", "lyrics": "[Instrumental]",
            "duration": "<duration_s>", "seed": "<seed>",
            "clip": ["2", 0]}},
  "5":  {"class_type": "EmptyAceStepLatentAudio", "inputs": {"seconds": "<duration_s>", "batch_size": 1}},
  "6":  {"class_type": "ModelSamplingAuraFlow", "inputs": {"shift": 3.0, "model": ["1", 0]}},
  "7":  {"class_type": "APG",                   "inputs": {"eta": 0.7, "norm_threshold": 2.5, "momentum": -0.75, "model": ["6", 0]}},
  "8":  {"class_type": "CFGGuider",             "inputs": {"cfg": 7.0, "model": ["7", 0], "positive": ["4", 0], "negative": ["4", 1]}},
  "9":  {"class_type": "KSamplerSelect",        "inputs": {"sampler_name": "gradient_estimation"}},
  "10": {"class_type": "BasicScheduler",        "inputs": {"scheduler": "simple", "steps": 50, "denoise": 1.0, "model": ["6", 0]}},
  "11": {"class_type": "RandomNoise",           "inputs": {"noise_seed": "<seed>"}},
  "12": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["11", 0], "guider": ["8", 0], "sampler": ["9", 0],
            "sigmas": ["10", 0], "latent_image": ["5", 0]}},
  "13": {"class_type": "VAEDecodeAudio",        "inputs": {"samples": ["12", 0], "vae": ["3", 0]}},
  "14": {"class_type": "SaveAudio",             "inputs": {"audio": ["13", 0], "filename_prefix": "<scene_id>_music"}}
}
```

The APG node + `gradient_estimation` sampler + `linear_quadratic`/`simple` scheduler are **required** for `xl_base` and `xl_sft` to render without artifacts. Without APG, those base models produce hollow/distorted audio. Distilled variants (`xl_turbo`, `base_turbo`, `xl_base_sft`) use a simpler 6-node KSampler graph instead. See `music_tool/templates/ace_step_music_simple_api.json` for that one.

#### Variants — choose per cue or per script

| Variant | Graph | Steps | CFG | Time @ 90 s | Notes |
|---|---|---|---|---|---|
| **`xl_base`** (default) | APG | 50 | 7.0 | ~21 s | Highest fidelity. Recommended unless iterating fast. |
| `xl_sft` | APG | 45 | 6.0 | ~18 s | Near-base quality, bf16 (~10 GB), ~20% faster. |
| `xl_base_sft` | simple KSampler | 35 | 3.0 | ~21 s | Merged base+SFT, no APG needed. |
| `xl_turbo` | simple KSampler | 10 | 1.0 | ~12 s | Distilled. Use for **preview iterations** while writing. |
| `base_turbo` | simple KSampler | 8 | 1.0 | ~8 s | Smallest (~4.8 GB), lowest quality. |

Set per-cue or script-wide:
```json
"music_cues": {
  "open":    {"tags": "...", "duration": 45, "variant": "xl_base"},
  "preview": {"tags": "...", "duration": 30, "variant": "xl_turbo"}
},
"ace_variant": "xl_base"   // script-wide default if cue doesn't specify
```

#### Music mastering (automatic, under-dialogue tuned)

Every music cue produced by `radio_drama.py --stage music` is automatically run through `scene_production_tool/music_mastering.py` between ACE output and canonicalization. The default is dialed for under-dialogue placement:

- **Preset:** `default` (EQ + light saturation, no compression)
- **Target LUFS:** `−18` (quieter than standalone music — the mix's sidechain ducking + final loudnorm bring it up)
- **Ceiling:** `−1 dBTP`

**Per-cue overrides in the script:**

```json
"music_cues": {
  "open":     {"tags": "...", "duration": 30, "master": "orchestral", "master_target_lufs": -20},
  "tension":  {"tags": "...", "duration": 30, "master": "default"},
  "hero":     {"tags": "...", "duration": 60, "master": "orchestral", "master_target_lufs": -14},
  "notes":    {"tags": "...", "duration": 20, "master": "off"}
}
```

`"master"` choices: `"default" | "edm" | "trap" | "chill" | "orchestral" | "jazz" | "auto" | "off"`. `"auto"` detects the preset from the cue's tags.

**Script-wide defaults:**

```json
{
  "music_master": "default",       // global preset for cues that don't set "master"
  "music_master_lufs": -18.0       // global LUFS target
}
```

**Prompting rules for under-dialogue beds:** avoid heavy dynamics (no `[drop]`, no `loud-quiet-loud`, no `sudden silence`) — they fight sidechain ducking. Prefer "sustained", "slow evolving", "consistent energy", "drone", "warm bed". Save the dynamics vocabulary for standalone music via `music_maker.py`.

**Hero moments:** when a cue takes center stage (opening titles, act breaks, silent-scene montage), override with `"master": "orchestral"` + `"master_target_lufs": -16` or `-14`, and raise its mix `volume` to `1.0`. Those moments deserve the full LRA of a proper master.

### Track 3: Sound Effects (MMAudio primary, SAO fallback)

> **Reminder: do not assemble SFX workflows by hand.** `radio_drama.py --stage sfx` runs `generate_sfx()` which automatically routes each event to the right engine based on duration. You don't pick the engine — the orchestrator does. JSON below is reference for what it builds.

SFX routing is **duration-aware**. After A/B testing on transients, foley, mechanical, ambient, and biological sounds, MMAudio beat both Stable Audio Open and ACE Step on quality — it's now the default. Engine per event:

| Requested duration | Engine | Why |
|---|---|---|
| 1–10 s | **MMAudio Large 44k v2** | Best quality for discrete SFX; 10 s coherence window |
| 10–47 s | **Stable Audio Open 1.0** | MMAudio drifts past 10 s; SAO handles up to 47 s cleanly |
| 47+ s | **ACE Step 1.5** | Only engine with unlimited duration (music-model; use for ambient only) |

This routing is already wired in `radio_drama.py`'s `generate_sfx()` priority chain — you don't set the engine per event; the tool picks based on duration.

#### Reference: MMAudio workflow (≤10 s) — 4-node graph the orchestrator builds:

```json
{
  "1": {"class_type": "MMAudioModelLoader", "inputs": {
    "mmaudio_model": "mmaudio_large_44k_v2_fp16.safetensors", "base_precision": "fp16"
  }},
  "2": {"class_type": "MMAudioFeatureUtilsLoader", "inputs": {
    "vae_model":         "mmaudio_vae_44k_fp16.safetensors",
    "synchformer_model": "mmaudio_synchformer_fp16.safetensors",
    "clip_model":        "apple_DFN5B-CLIP-ViT-H-14-384_fp16.safetensors",
    "mode": "44k", "precision": "fp16"
  }},
  "3": {"class_type": "MMAudioSampler", "inputs": {
    "mmaudio_model": ["1", 0], "feature_utils": ["2", 0],
    "duration": "<≤10.0>", "steps": 50, "cfg": 5.5, "seed": "<seed>",
    "prompt": "<specific physical description>",
    "negative_prompt": "music, speech, vocals, singing",
    "mask_away_clip": true, "force_offload": true
  }},
  "4": {"class_type": "SaveAudio", "inputs": {"audio": ["3", 0], "filename_prefix": "<scene_id>_sfx_<index>"}}
}
```

#### Reference: Stable Audio Open workflow (10–47 s, fallback) — orchestrator builds, uses ComfyUI native nodes:

```json
{
  "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "stable-audio-open-1.0.safetensors"}},
  "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "stable-audio-open-t5.safetensors", "type": "stable_audio"}},
  "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "<prompt>", "clip": ["2", 0]}},
  "4": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["2", 0]}},
  "5": {"class_type": "EmptyLatentAudio", "inputs": {"seconds": "<duration>", "batch_size": 1}},
  "6": {"class_type": "ConditioningStableAudio", "inputs": {
    "positive": ["3", 0], "negative": ["4", 0], "seconds_start": 0.0, "seconds_total": "<duration>"
  }},
  "7": {"class_type": "KSampler", "inputs": {
    "model": ["1", 0], "seed": "<seed>", "steps": 60, "cfg": 7.0,
    "sampler_name": "dpmpp_3m_sde_gpu", "scheduler": "exponential",
    "positive": ["6", 0], "negative": ["6", 1], "latent_image": ["5", 0], "denoise": 1.0
  }},
  "8": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
  "9": {"class_type": "SaveAudio", "inputs": {"audio": ["8", 0], "filename_prefix": "<prefix>"}}
}
```

**Critical**: SAO's `model.safetensors` does NOT embed the T5 text encoder — must be loaded separately via `CLIPLoader(type="stable_audio")`. Both files live in their respective folders (checkpoints/, text_encoders/).

**SFX prompt tips:** Be specific and physical. "Heavy wooden door slamming shut in a stone corridor, deep resonant thud with echo" beats "door sound." Include material, action, environment, perspective. For MMAudio specifically, time-series phrasing works well ("engine struggles, then catches, then rumbles"). See `references/sfx-prompts.md` for a category-organized prompt library — the vocabulary works across all three engines.

### Standalone music + SFX generation (when dialogue is already done)

If you have dialogue from somewhere else — a previous run, a different tool, a manual session — and the canonical radio-drama layout doesn't apply, you can generate music and SFX one-shot at a time without the full pipeline. Both tools are CLI wrappers around the same backend code `radio_drama.py` uses.

| Need | Tool | Command |
|---|---|---|
| One music cue | `music_tool/music_maker.py` | `python music_maker.py --prompt "..." --duration 45 --bpm 70 --key "A minor" --variant xl_base --master auto -o cue.flac` |
| One SFX clip | `scene_production_tool/sfx_maker.py` | `python sfx_maker.py --prompt "..." --duration 4 -o door_slam.wav` |

Neither tool requires the canonical project layout. Run from anywhere, output anywhere. **No node graphs to assemble by hand.**

#### Music — `music_maker.py`

Use `music_maker.py` directly:

```bash
mkdir -p ${COMFYUI_ROOT}\output\<project>\music

# Generate one cue per call. --master auto picks the right preset from prompt keywords:
python ${COMFYUI_ROOT}\music_tool\music_maker.py \
    --prompt "ambient cinematic, slow evolving pad, mysterious, breathing texture" \
    --duration 45 --bpm 70 --key "A minor" \
    --variant xl_base --master auto \
    -o ${COMFYUI_ROOT}\output\<project>\music\act1_open.flac

python music_maker.py --prompt "darker, descending, shadowed" --duration 30 --bpm 70 --key "D minor" \
    --variant xl_base --master auto -o output\<project>\music\act1_descent.flac

# ... etc. for each cue.
```

`music_maker.py` is a CLI wrapper around the same templates `radio_drama.py` uses — `music_tool/templates/ace_step_music_apg_api.json` for `xl_base`/`xl_sft`, the simple template for distilled variants. It handles workflow construction, ComfyUI submission, retry-on-transient-error, output collection, and dynamics-preserving mastering. **No node graphs to assemble by hand.** See the `music-producer` skill for the full prompt-engineering recipe (genre stack + instruments + dynamics vocabulary + structural section tags + mood).

For under-dialogue beds, override the LUFS target down to ‑18 to match the radio-drama mastering default:

```bash
python music_maker.py --prompt "..." --master default --target-lufs -18 -o ...
```

#### SFX — `sfx_maker.py`

Same pattern as `music_maker.py`, but for sound effects. Wraps `radio_drama.py`'s SFX backend chain (MMAudio → SAO → ACE) with auto-routing by duration:

```bash
mkdir -p ${COMFYUI_ROOT}\output\<project>\sfx

# Short transient (≤10s) → routes to MMAudio Large 44k v2:
python ${COMFYUI_ROOT}\scene_production_tool\sfx_maker.py \
    --prompt "Heavy wooden door slamming shut in stone corridor, deep resonant thud with echo" \
    --duration 4 \
    -o ${COMFYUI_ROOT}\output\<project>\sfx\door_slam.wav

# Medium ambient (10–47s) → routes to Stable Audio Open 1.0:
python sfx_maker.py --prompt "Steady rain on metal roof with distant thunder" \
    --duration 25 -o output\<project>\sfx\rain_ambient.wav

# Long ambient bed (47+s) → routes to ACE Step 1.5 (last resort):
python sfx_maker.py --prompt "Wind through pine forest, occasional bird calls, distant water" \
    --duration 90 -o output\<project>\sfx\forest_ambience.flac
```

The tool announces which backend will run **before** generating, so the agent sees `backend: MMAudio Large 44k v2` (or SAO/ACE) up front. It also places a library copy at `input/sfx/<name>` so future `radio_drama.py` runs can reference the SFX by filename if you ever migrate the project to the canonical layout.

Output formats: `.wav` (transcoded to `pcm_s16le`), `.flac` (lossless copy of ComfyUI output), `.mp3` (libmp3lame `-q 2`).

**SFX prompt style** — same as the inline guidance in `references/sfx-prompts.md`:
- ✅ "Heavy wooden door slamming shut in a stone corridor, deep resonant thud with echo"
- ❌ "door sound"

Include material, action, environment, and perspective. For MMAudio specifically, time-series phrasing works well: "engine struggles, then catches, then rumbles". Include kinetic verbs ("cranking", "shattering", "creaking") for percussive transients.

`--seed <n>` makes generation reproducible — same prompt + same seed = same SFX. Useful for swapping the prompt slightly while keeping the sonic character.

#### When to use which tool

| Situation | Tool |
|---|---|
| Agent has a script.json with the canonical schema, on the canonical Workstation layout | `radio_drama.py --stage all` (one command, full pipeline) |
| Agent only needs a music track, no radio drama context | `music_maker.py` (max-fidelity, mastering chain) |
| Agent has dialogue elsewhere and needs music cues | `music_maker.py` (per cue) |
| Agent has dialogue + music elsewhere and needs SFX | `sfx_maker.py` (per cue) |
| Agent built everything elsewhere, just needs to mix | `ffmpeg` per `references/mixing-guide.md` |

The orchestrator (`radio_drama.py`) is always preferable when the project layout permits, because it handles canonicalization, sidechain ducking, loudnorm mastering, and timeline re-timing for you. The standalone tools exist for the cases where retrofitting the canonical layout costs more than just generating the missing assets directly.

### Recovery: agent went off-path, dialogue exists outside the canonical layout

Symptom: agent generated dialogue files into `output/<project>/dialogue/` (or some other non-standard location) instead of `output/radio/<project>/audio/dialogue/`. Now `radio_drama.py --stage music` won't find them and the project structure is broken.

Two recovery paths:

**Path A — re-stage as a proper radio-drama project** (preferred if you want full pipeline including final mix):
```bash
mkdir -p ${COMFYUI_ROOT}\output\radio\<project>\audio\dialogue
move output\<project>\dialogue\*.flac  output\radio\<project>\audio\dialogue\
# Write script.json with music_cues + schedule + characters into output\radio\<project>\
# Then:
python radio_drama.py <project> --stage music
python radio_drama.py <project> --stage sfx
python radio_drama.py <project> --stage mix
```

**Path B — generate music + SFX in place, assemble manually** (simpler if you don't need the full radio_drama pipeline):
```bash
# Generate each music cue with music_maker.py (see "Standalone music generation" above)
python music_maker.py --prompt "..." --duration 45 --bpm 70 --key "A minor" \
    --variant xl_base --master default --target-lufs -18 -o output\<project>\music\<cue>.flac

# Generate each SFX with sfx_maker.py
python sfx_maker.py --prompt "..." --duration 4 -o output\<project>\sfx\<name>.wav

# Assemble manually with ffmpeg using the mixing-guide.md filter chain
```

### Submission Pattern (if you really must hand-build, which you shouldn't)

POST each workflow to ComfyUI:
```bash
curl -X POST http://localhost:8188/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": <workflow-json>}'
```

Reserved for cases where `radio_drama.py` and `music_maker.py` legitimately can't cover the use case (very rare). For 99% of agent workflows, those two tools are the answer.

Generate assets in batches — all dialogue for a scene, then music, then SFX. This lets you review dialogue timing before committing to music durations.

## Phase 4: Assembly & Mix

Stitch all rendered audio into a finished production using ffmpeg. See `references/mixing-guide.md` for the complete command reference.

### Assembly Order Per Scene

1. **Normalize** all clips to 48kHz mono/stereo
2. **Build the dialogue timeline** — lay out narration and dialogue clips in order with pauses
3. **Layer music** underneath dialogue with sidechain ducking (music drops ~12dB when speech is present)
4. **Layer SFX** at appropriate moments
5. **Add crossfades** between scenes (2-3s)
6. **Master** the final mix (loudnorm → compressor → limiter)

### Quick Assembly Command

```bash
ffmpeg -i dialogue_timeline.wav -i music_bed.wav -i sfx_layer.wav \
  -filter_complex "
    [1:a]volume=0.3[music];
    [2:a]volume=0.6[sfx];
    [0:a][music]amix=inputs=2:duration=longest[dialogue_music];
    [dialogue_music][sfx]amix=inputs=2:duration=longest[mixed];
    [mixed]loudnorm=I=-16:TP=-1.5:LRA=11[out]
  " -map "[out]" final_mix.wav
```

For proper sidechain ducking (music dynamically drops under dialogue), see the detailed ffmpeg sidechaincompress filter chain in `references/mixing-guide.md`.

### Output Formats

- **Production master:** WAV 48kHz 24-bit
- **Distribution:** MP3 320kbps or AAC 256kbps
- Convert: `ffmpeg -i final_mix.wav -b:a 320k final_mix.mp3`

## File Organization

```
production_name/
├── script.json              — the structured script
├── characters.json          — voice casting manifest
├── audio/
│   ├── dialogue/            — all TTS renders
│   ├── music/               — all ACE Step renders
│   ├── sfx/                 — all SFX renders (MMAudio or SAO, auto-routed by duration)
│   └── scenes/              — assembled per-scene mixes
└── output/
    ├── final_mix.wav        — mastered production
    └── final_mix.mp3        — distribution copy
```

## Production Workflow Summary

1. User provides creative input (premise, genre, characters, tone, length)
2. Write the full script as structured JSON → `script.json`
3. Design and cast all character voices → `characters.json`
4. Generate all audio assets via ComfyUI API (dialogue → music → SFX)
5. Assemble scene by scene with proper mixing and ducking
6. Master the final output
7. Deliver WAV + MP3

For detailed reference material:
- `references/script-format.md` — full JSON schema with annotated example
- `references/voice-casting.md` — Three-Lock system deep dive and ensemble design
- `references/mixing-guide.md` — complete ffmpeg pipeline for assembly and mastering
- `references/sfx-prompts.md` — SFX prompt library by category (works for MMAudio, SAO, and ACE)
