---
name: radio-drama-production
description: >
  Operational runbook for producing a radio drama on the operator's Workstation workstation (ComfyUI + RTX 5090)
  over SSH. Orchestrates the craft skills (radio-drama-producer, tts-voice-designer) by shipping
  their script.json to the box, driving the scene_production_tool/radio_drama.py pipeline, and pulling
  the finished master. Use when an agent needs to ACTUALLY produce a radio drama (not just design one).
  Complements radio-drama-producer/ (which covers script writing, voice casting, and craft) and
  tts-voice-designer/ (which covers the Three-Lock voice preservation system). This skill covers
  everything after "how do I actually run it?" — SSH, command reference, troubleshooting, delivery.
---

# Radio Drama Production — Operational Runbook

> **Related skills (read first):**
> - `radio-drama-producer/` — pipeline phases, script JSON schema, element types, craft guidelines
> - `tts-voice-designer/` — Three-Lock voice preservation, FB_Qwen3TTS node contracts, ensemble design
>
> This skill picks up where those leave off: **the agent has a script.json — now how do we produce it?**

## 1. Target host

- **Host:** `${SSH_USER}@127.0.0.1` (Workstation — RTX 5090, 64 GB RAM, Win 11 + OpenSSH)
- **ComfyUI endpoint on Workstation:** `http://127.0.0.1:8188` (must be running; `--disable-mmap` flag required on Windows with many large models)
- **Tool path:** `${COMFYUI_ROOT}\scene_production_tool\radio_drama.py`
- **Fallback IP:** `127.0.0.1` — same box via another interface; try if 155 fails

### SSH sanity

```bash
ssh -o ConnectTimeout=5 ${SSH_USER}@127.0.0.1 'hostname && curl -s http://127.0.0.1:8188/system_stats | findstr vram_free'
```

Windows OpenSSH runs `cmd.exe`; use `powershell -Command` for anything chain-heavy. Commands below assume cmd. For multi-line ops, pipe a here-doc over stdin.

## 2. Script format

The pipeline accepts **either** schema:

**Schema A — flat timeline** (when the agent knows absolute offsets already):
```json
{
  "title": "...",
  "characters": { "NARRATOR": {"voice": "...", "instruct": "..."} },
  "music_cues":  { "open":   {"tags": "...", "duration": 30, "bpm": 72, "key": "A minor"} },
  "timeline":    [
    {"t": 0,  "type": "music", "cue": "open", "fade_in": 2.0, "volume": 0.9},
    {"t": 5,  "type": "line",  "character": "NARRATOR", "text": "..."},
    {"t": 12, "type": "sfx",   "source": "door_slam.wav", "volume": 0.7}
  ]
}
```

**Schema B — acts/scenes/elements** (what `radio-drama-producer` generates):
```json
{
  "title": "...",
  "characters": ["NARRATOR", "INSPECTOR"],
  "voice_casting": {
    "NARRATOR":  {"voice_instruct": "...", "seed": 200,
                  "emotion_overrides": {"tense": ", pace tightening"}}
  },
  "acts": [{"act_number": 1, "scenes": [{"scene_id": "s1", "elements": [
    {"type": "sfx_cue",   "description": "...", "duration_s": 6},
    {"type": "music_cue", "description": "...", "duration_s": 45, "fade_in_s": 3},
    {"type": "narration", "text": "...", "emotion": "neutral"},
    {"type": "dialogue",  "character": "INSPECTOR", "text": "...", "emotion": "cautious"},
    {"type": "pause",     "duration_s": 2},
    {"type": "direction", "note": "(ignored at render time)"}
  ]}]}]
}
```

`radio_drama.py` auto-detects Schema B and flattens it. **Emotion labels** route through the per-character `emotion_overrides` table first, then fall back to the global table defined in `tts-voice-designer` (tender, broken, commanding, fearful, intimate, furious, joyful, sorrowful, contemplative, tense, cautious, defiant, reflective, angry, anguished, neutral).

Duration estimation for Schema B: narration/dialogue durations are first **estimated** from word count (150 wpm) for the initial layout, then the mix stage **re-times** using probed durations from the actual TTS renders. So if a voice came out 2 s slower than estimated, music cues and scene boundaries shift accordingly — the output stays aligned.

## 3. The four stages

```bash
# All at once
ssh ${SSH_USER}@127.0.0.1 'cd ${COMFYUI_ROOT} && python scene_production_tool\radio_drama.py MYPROJECT --stage all'

# Or one at a time (idempotent — rerun is safe, already-done work is skipped)
#   tts    — one WAV per narration/dialogue element, canonicalized to 48k stereo pcm_s24le
#   music  — one WAV per named music cue via ACE Step 1.5 XL turbo
#   sfx    — resolve/canonicalize manual library entries; generate ambient ones if generate:true
#   mix    — final 48k mix with sidechain ducking + loudnorm -16 LUFS → WAV + MP3
```

Resource footprint (per typical 10-min drama on RTX 5090):
- TTS: ~10 s / line
- Music: ~20 s / 30-s cue (turbo, 8 steps)
- Mix: ~10 s total (CPU-bound ffmpeg)
- Peak VRAM: ~12 GB

Total wall time: **15–45 min** depending on dialogue count. Run under `start /B` with a log file for anything >5 min so a dropped SSH doesn't kill the driver:

```bash
ssh ${SSH_USER}@127.0.0.1 'start /B python ${COMFYUI_ROOT}\scene_production_tool\radio_drama.py MYPROJECT --stage all > ${COMFYUI_ROOT}\output\radio\MYPROJECT\run.log 2>&1'

# Follow the log
ssh ${SSH_USER}@127.0.0.1 'powershell -Command "Get-Content ${COMFYUI_ROOT}\output\radio\MYPROJECT\run.log -Wait -Tail 20"'
```

## 4. End-to-end runbook

```bash
# 1. Make the project dir on Workstation
ssh ${SSH_USER}@127.0.0.1 'mkdir ${COMFYUI_ROOT}\output\radio\lighthouse'

# 2. Ship script.json (either schema). If you have SFX library WAVs, ship those too.
scp script.json ${SSH_USER}@127.0.0.1:${COMFYUI_ROOT}/output/radio/lighthouse/script.json
scp sfx/*.wav   ${SSH_USER}@127.0.0.1:${COMFYUI_ROOT}/input/sfx/

# 3. Produce (~20 min)
ssh ${SSH_USER}@127.0.0.1 'cd ${COMFYUI_ROOT} && python scene_production_tool\radio_drama.py lighthouse --stage all'

# 4. Pull master
scp ${SSH_USER}@127.0.0.1:${COMFYUI_ROOT}/output/radio/lighthouse/lighthouse_radio.mp3 .
scp ${SSH_USER}@127.0.0.1:${COMFYUI_ROOT}/output/radio/lighthouse/lighthouse_radio.wav .
```

## 5. Deliverables layout on Workstation

```
output/radio/MYPROJECT/
  script.json                     # agent-authored
  audio/
    _normalized_script.json       # debug — flat timeline after normalization + re-timing
    dialogue/line_NNN.wav         # canonical per-line TTS (48k/stereo/pcm_s24le)
    dialogue_map.json
    dialogue_raw/                 # raw TTS pre-canonicalization (kept for debugging)
    music/<cue>.wav               # canonical music beds
    music/music_map.json
    sfx/<name>.wav                # canonical SFX (library WAVs re-encoded on first use)
  MYPROJECT_radio.wav             # FINAL master, 48k stereo s24le, −16 LUFS
  MYPROJECT_radio.mp3             # FINAL master, VBR ~190 kbps
```

## 6. The sample-rate distortion fix

Previous pipelines produced audible distortion because of unannounced sample-rate crossings feeding into `sidechaincompress` and `amix`:

| Source | Native rate | Prior treatment |
|---|---|---|
| Chatterbox TTS | 24 000 Hz | fed raw into mix |
| Qwen3-TTS | ~24 000 Hz | same |
| ACE Step music | 44 100 Hz (MP3 export) | implicit resample at filter time |
| Manual SFX | varies | never normalized |

When `sidechaincompress` saw mismatched rates, ffmpeg's auto-inserted resamplers ran with inconsistent settings per filter, causing phase drift, level imbalance, and compressor pumping that looked like clipping.

`radio_drama.py` fixes this by forcing **one canonical format** (48 kHz / stereo / pcm_s24le) via `canonicalize()` at each of `stage_tts`, `stage_music`, `stage_sfx`. Then every filter chain in `stage_mix` starts with `aresample=async=1,aformat=sample_rates=48000:sample_fmts=fltp:channel_layouts=stereo` as a belt-and-braces guarantee.

Final mix chain: `alimiter` on speech bus → `sidechaincompress` on music against speech key → `amix weights=1.0 0.8` → `loudnorm I=-16:TP=-1.5:LRA=11`.

See `radio-drama-producer/references/mixing-guide.md` for the filter-chain reference.

## 6a. Music variants (ACE Step)

Music generation supports multiple ACE Step variants via a `variant` field on each music cue. The default is **`xl_base`** (full fp32 base model, APG chain, lossless quality). The radio-drama tool now shares its music workflow builders with `music_tool/music_maker.py` — both routes use the same APG chain for base models and the simple KSampler for distilled variants.

| Variant | UNet file | Chain | Steps | CFG | Time @ 90 s | Notes |
|---|---|---|---|---|---|---|
| **`xl_base`** (default) | acestep_v1.5_xl_base.safetensors (19.95 GB fp32) | APG | 50 | 7.0 | **~21 s** | Highest fidelity; unified with music-producer skill |
| `xl_sft` | acestep_v1.5_xl_sft_bf16.safetensors | APG | 45 | 6.0 | ~18 s | Near-base quality, bf16, faster |
| `xl_base_sft` | acestep_v1.5_xl_merge_base_sft_ta_0.5.safetensors (9.97 GB bf16) | simple | 35 | 3.0 | ~21 s | Merged model; works without APG |
| `xl_turbo` | acestep_v1.5_xl_turbo_bf16.safetensors (9.97 GB bf16) | simple | 10 | 1.0 | ~12 s | Distilled; fastest preview quality |
| `base_turbo` | acestep_v1.5_turbo.safetensors (4.8 GB bf16) | simple | 8 | 1.0 | ~8 s | Legacy default, smallest model |

**APG chain** (for `xl_base` / `xl_sft`):
`UNETLoader → ModelSamplingAuraFlow(shift=3) → APG(eta=0.7, norm=2.5, mom=-0.75) → CFGGuider → SamplerCustomAdvanced` with `gradient_estimation` sampler and `BasicScheduler(simple, steps, denoise=1.0)`.

**Simple chain** (for distilled/merged variants): plain `KSampler` with `euler` / `simple`.

Templates live at `music_tool/templates/`:
- `ace_step_music_apg_api.json`
- `ace_step_music_simple_api.json`

`build_ace_workflow()` in `radio_drama.py` imports `music_maker.py` and dispatches to the right builder by variant — same source of truth as standalone music generation.

Choose per-cue in the script:
```json
"music_cues": {
  "open":    {"tags": "...", "duration": 45, "variant": "xl_base"},
  "tension": {"tags": "...", "duration": 30},
  "bed":     {"tags": "...", "duration": 120, "variant": "xl_turbo"}
}
```

Script-wide default with `"ace_variant": "xl_turbo"` at the top level — useful when iterating on dialogue and you want fast music for preview. Default is `xl_base` otherwise.

Per-cue `steps` and `cfg` also override: `{"variant": "xl_base", "steps": 70, "cfg": 8.0}` for extra adherence.

## 6b. Music mastering (post-gen, dynamics-preserving, UNDER-DIALOGUE tuned)

Every music cue is run through `scene_production_tool/music_mastering.py` after ACE generation and before canonicalization. This is the same chain used by `music_maker.py` (HPF → EQ → optional compressor (default off) → light saturation → LUFS gain-match → brick-wall Clipping ceiling), but with a radio-drama-specific default.

### Defaults suited to under-dialogue placement

- **Preset:** `default` (balanced EQ + 2.5 dB saturation, no compression)
- **Target LUFS:** **−18 LUFS** (quieter than dialogue by design; the mix's sidechain ducking + final loudnorm do the rest)
- **Ceiling:** −1.0 dBTP

Why quieter than the stand-alone music tool? In radio drama, music lives beneath speech, gets ducked another ~12 dB when dialogue is present, then the final mix is loudness-normalized to −16 LUFS. If the music cue is pre-mastered to −12 LUFS (as standalone music would be), the mixdown has to compress more aggressively to make room. Landing cues at −18 LUFS gives the mix headroom without the cue sounding weak.

### Schema — per-cue mastering overrides

```json
"music_cues": {
  "open":     {"tags": "ambient, cinematic, contemplative", "duration": 30,
               "master": "orchestral", "master_target_lufs": -20},
  "tension":  {"tags": "dark pulse, bass drones", "duration": 30,
               "master": "default"},
  "montage":  {"tags": "upbeat jazz", "duration": 60,
               "master": "jazz", "master_target_lufs": -16},
  "silence":  {"tags": "ambient pad, very quiet", "duration": 20,
               "master": "off"}    // skip mastering entirely
}
```

Per-cue `master` values: `"default"` | `"edm"` | `"trap"` | `"chill"` | `"orchestral"` | `"jazz"` | `"auto"` (detect from tags) | `"off"` (skip mastering). Per-cue `master_target_lufs` overrides the default −18.

### Schema — script-wide defaults

```json
{
  "project": "my_drama",
  "music_master": "default",          // applied to any cue without its own "master"
  "music_master_lufs": -18.0,         // applied to any cue without its own "master_target_lufs"
  "music_cues": { ... }
}
```

Or `"music_master": "off"` at the script level to globally disable mastering (e.g., when you're feeding in pre-mastered tracks from somewhere else).

### Prompting rules for under-dialogue music

Heavy dynamics (big drops, sudden silences, long crescendos) fight against sidechain ducking and can produce weird pumping. For radio drama music beds, prefer:

- ✅ **Do**: "steady mood", "consistent energy", "breathing pad", "slow evolving", "minimal transients", "sustained", "drone", "ambient texture", "warm bed", "long reverb tail"
- ❌ **Avoid**: "[drop]", "[build]", "sudden silence", "loud-quiet-loud", "sidechain pump" (the mix adds its own), "stabs", "punchy transients"

Save the dynamics vocabulary for standalone music via `music_maker.py`; for drama beds you want the cue to sit still and let the dialogue breathe.

### When to override with `"master": "orchestral"`

For hero scoring moments (opening credits, act breaks, emotional climaxes) where you want the music to take the spotlight briefly. These cues are usually placed during silent scenes (no dialogue), so the under-dialogue argument doesn't apply. Use `"orchestral"` preset + `master_target_lufs: -16` to let the cue breathe, and raise its `volume` in the mix schedule:

```json
{"t": 45, "type": "music", "cue": "act_break", "fade_in": 3, "volume": 1.0}
```

### Verifying the mastering pass fired

Each cue prints a mastering line in the `[MUSIC]` stage log:

```
[open] gen 30.0s @ 72bpm D minor [xl_base]: ambient, cinematic, con...
   done in 23s
   mastering [default @ -18.0 LUFS]...
   raw: 48000Hz → canonicalizing
```

If you don't see the `mastering [...]` line, the preset was `off` or the module import failed — check for a `master FAILED` warning.

## 7. SFX priority chain (all installed)

After A/B testing all three engines on the same prompts + seeds (door_slam / gravel_steps / distant_thunder / car_start / wolf_howl), **MMAudio is the clear winner** for discrete SFX events. Priority is now:

1. **MMAudio Large 44k v2** (PRIMARY) — INSTALLED ✅. Best for transients, foley, mechanical, biological/tonal. Output 44.1 kHz stereo FLAC. **Coherence window ~10 s** — longer requests fall back. Once model is resident, ~6 s per 3-5 s clip on 5090.
2. **Stable Audio Open 1.0** (FALLBACK for >10 s) — INSTALLED ✅. Used when MMAudio's window is exceeded or MMAudio is unavailable. Max 47 s per gen, ~9 s wall time for a 5 s clip.
3. **ACE Step 1.5** (LAST RESORT for very long ambient beds) — INSTALLED ✅. Music model — weaker on discrete SFX events. Only activates when duration > 47 s.
4. **Manual library** at `input/sfx/<source>` — always preferred if a file is pre-placed; auto-canonicalized to 48 k on first use. Build a ~30-clip staple library once for things you re-use.
5. **ElevenLabs SoundEffects API** — not wired; set `ELEVENLABS_API_KEY` + add a branch in `generate_sfx` for paid-premium hero SFX (up to 22 s).

The SFX priority is **per-event**: `generate_sfx()` logs which backend activated (`[gen/mma]` = MMAudio, `[gen/sao]` = Stable Audio, `[gen/ace]` = ACE Step). Order is deterministic, so you always know which engine produced a given clip.

### Files on disk (Workstation)

```
models/mmaudio/
  mmaudio_large_44k_v2_fp16.safetensors          (1.97 GB, primary generator)
  mmaudio_vae_44k_fp16.safetensors               (583 MB, 44.1 kHz VAE)
  mmaudio_synchformer_fp16.safetensors           (453 MB, sync encoder)
  apple_DFN5B-CLIP-ViT-H-14-384_fp16.safetensors (1.88 GB, CLIP text/image encoder)
  nvidia/bigvgan_v2_44khz_128band_512x/          (1.9 GB, auto-downloaded vocoder + support files)
  # legacy, kept for 16k mode:
  mmaudio_vae_16k_fp32.safetensors
  mmaudio_vocoder_bigvgan_best_netG_fp32.safetensors

models/checkpoints/stable-audio-open-1.0.safetensors   (4.85 GB fp32, UNet + VAE)
models/text_encoders/stable-audio-open-t5.safetensors  (438 MB, T5 encoder)
```

Most are hard-linked from the HuggingFace cache blob, so re-downloads don't duplicate disk use.

### Prompt tips

All three engines respond best to **specific, physical prompts**: `"heavy wooden door slamming shut in a stone corridor, deep resonant thud with echo"` beats `"door sound"`. Include material, action, environment, perspective.

**MMAudio-specific tips** (its unique strengths):
- Include physical/kinetic verbs ("cranking", "shattering", "creaking")
- Use time-series phrasing for sequential sounds ("engine struggles, then catches, then rumbles")
- The `negative_prompt` defaults to `"music, speech, vocals, singing"` — keeps MMAudio locked on SFX rather than drifting musical

**MMAudio install notes** (if you ever need to reinstall):
- Install `hf_xet` package first (prevents HTTP download hangs)
- Place all 4 fp16 models in `models/mmaudio/`
- The NVIDIA bigvgan vocoder auto-downloads on first 44 k run (~21 s via hf_xet; will hang forever without it)
- Custom node: `ComfyUI-MMAudio` by Kijai

`radio-drama-producer/references/sfx-prompts.md` has a category-organized prompt library that works across all three engines.

## 8. Voice casting pass-through

Both schemas feed into the same voice resolution. For Schema B `voice_casting` (Three-Lock from `tts-voice-designer`):

- `voice_instruct` → Qwen3-TTS `voice_description`
- `seed` → Qwen3-TTS `seed` (document per character, never change mid-production)
- `emotion_overrides[emotion]` → appended to `voice_instruct` for that specific line

Per-line `delivery_note` (from Schema B) overrides the character's instruct entirely for that one line — use sparingly, only for beats that don't fit any emotion label.

## 9. Failure modes + recovery

| Symptom | Cause | Fix |
|---|---|---|
| `Submit failed: {...}` on first call | ComfyUI not running | `ssh ... 'curl http://127.0.0.1:8188/system_stats'` — restart if 404 |
| `[Errno 22]` on model load | Windows mmap bug | Verify `comfy/utils.py` line 41 is `DISABLE_MMAP = True` on Workstation |
| TTS stage hangs on one line | Non-ASCII glyph the tokenizer chokes on | Strip emoji/rare Unicode from that line |
| Music cue clipped | `volume > 1.0` | Clamp to ≤ 0.9 in the cue |
| SFX at wrong pitch | File dropped at 44.1 k, not canonicalized | `rm audio/sfx/<name>.wav && python radio_drama.py MYPROJECT --stage sfx` |
| Final WAV truncated | `tail_silence` too small | Raise `tail_silence` to ≥ 3.0 (Schema A) or append a terminal `pause` element (Schema B) |
| MMAudio fails on first run | `hf_xet` missing, bigvgan autodownload hangs | `pip install hf_xet` in ComfyUI venv, restart ComfyUI, retry |
| All engines fail | Models missing or ComfyUI down | Verify with `find_mmaudio_models()` / `find_stable_audio_checkpoint()` + `curl /system_stats` |
| Schema B timing off by >2 s | TTS estimate diverged | `mix` stage re-times from probed durations; rerun `--stage mix` |

## 10. Quick-start

```bash
# Minimal Schema-A script
cat > script.json <<'EOF'
{
  "title": "test",
  "characters": {"NARRATOR": {"voice": "warm male, 40s, storyteller"}},
  "music_cues": {"bed": {"tags": "ambient, cinematic, slow", "duration": 40, "bpm": 70, "key": "A minor"}},
  "timeline": [
    {"t": 0, "type": "music", "cue": "bed", "fade_in": 2, "volume": 0.85},
    {"t": 3, "type": "line",  "character": "NARRATOR", "text": "This is a test of the broadcast."}
  ]
}
EOF

ssh ${SSH_USER}@127.0.0.1 'mkdir ${COMFYUI_ROOT}\output\radio\test'
scp script.json ${SSH_USER}@127.0.0.1:${COMFYUI_ROOT}/output/radio/test/script.json
ssh ${SSH_USER}@127.0.0.1 'cd ${COMFYUI_ROOT} && python scene_production_tool\radio_drama.py test --stage all'
scp ${SSH_USER}@127.0.0.1:${COMFYUI_ROOT}/output/radio/test/test_radio.mp3 .
```

Working example at `output/radio/_example/script.json` on Workstation (Schema A, "The Last Broadcast").

## 11. Do NOT

- **Don't build ACE/MMAudio/SAO/Qwen3-TTS workflows by hand.** `radio_drama.py` is the abstraction over ComfyUI node graphs. If you find yourself looking up node schemas, hunting for the right VAE loader, or trying to figure out how to wire the negative conditioning, **stop** — that's an hour of debugging schema drift you don't need. Symptoms: HTTP 400 from `/prompt`, "I don't have a compatible workflow template", "let me check the model loader for ACE Step…". The fix is always `python radio_drama.py <project> --stage <stage>`.
- **If dialogue is already done elsewhere and you only need music or SFX**, don't try to retrofit the radio_drama project layout. Use the standalone CLIs:
  - `music_tool/music_maker.py` — wraps the same ACE Step templates `radio_drama.py --stage music` uses, with `--master auto` for dynamics-preserving mastering
  - `scene_production_tool/sfx_maker.py` — wraps `radio_drama.py`'s SFX backend chain (MMAudio → SAO → ACE), auto-routes by duration, places a library copy at `input/sfx/`
  
  Both tools work from any directory and require no project structure. See `radio-drama-producer/SKILL.md` → "Standalone music + SFX generation".
- Don't edit files under `custom_nodes/` on Workstation — the ComfyUI ecosystem updates them.
- Don't submit ComfyUI workflows while another script is running — the tool serializes for you; parallel runs fight.
- Don't `kill` ComfyUI mid-render — lost diffusion state; use `--stage` flags to skip finished work.
- Don't set music volume > 1.0 — limiter + loudnorm absorb ~2 dB; beyond that you clip.
- Don't bypass `canonicalize()` — dropping a raw 44.1 k SFX into `audio/sfx/` is how the old distortion bug comes back.

## 12. Recovery patterns

### Dialogue exists outside the canonical layout

Common when an agent went off-path and put files in `output/<project>/dialogue/` instead of `output/radio/<project>/audio/dialogue/`. Two paths:

**Path A — re-stage** (best if you want the full radio_drama pipeline to take over):
```bash
ssh ${SSH_USER}@127.0.0.1 'mkdir ${COMFYUI_ROOT}\output\radio\<project>\audio\dialogue'
ssh ${SSH_USER}@127.0.0.1 'move ${COMFYUI_ROOT}\output\<project>\dialogue\*.flac ${COMFYUI_ROOT}\output\radio\<project>\audio\dialogue\'
# Write script.json with music_cues + schedule + characters into output/radio/<project>/
ssh ${SSH_USER}@127.0.0.1 'cd ${COMFYUI_ROOT} && python scene_production_tool\radio_drama.py <project> --stage music --stage sfx --stage mix'
```

**Path B — music + SFX via standalone CLIs**, assemble manually:
```bash
# Music cues:
ssh ${SSH_USER}@127.0.0.1 'mkdir ${COMFYUI_ROOT}\output\<project>\music'
ssh ${SSH_USER}@127.0.0.1 'python ${COMFYUI_ROOT}\music_tool\music_maker.py --prompt "..." --duration 45 --bpm 70 --key "A minor" --variant xl_base --master default --target-lufs -18 -o ${COMFYUI_ROOT}\output\<project>\music\act1_open.flac'

# SFX clips (auto-routes MMAudio ≤10s, SAO 10-47s, ACE 47+s):
ssh ${SSH_USER}@127.0.0.1 'mkdir ${COMFYUI_ROOT}\output\<project>\sfx'
ssh ${SSH_USER}@127.0.0.1 'python ${COMFYUI_ROOT}\scene_production_tool\sfx_maker.py --prompt "Heavy door slam, stone corridor, deep echo" --duration 4 -o ${COMFYUI_ROOT}\output\<project>\sfx\door_slam.wav'

# Repeat for each cue/clip, then assemble with ffmpeg per references/mixing-guide.md
```

### Music cue clips, sounds wrong, or missed mastering

```bash
# Delete the canonical file and rerun music stage — it regenerates from the source cue
ssh ${SSH_USER}@127.0.0.1 'del ${COMFYUI_ROOT}\output\radio\<project>\audio\music\<cue>.wav'
ssh ${SSH_USER}@127.0.0.1 'python radio_drama.py <project> --stage music'
```

The stage is idempotent — already-good cues are skipped (file exists check), only the deleted one regenerates. Same trick works for dialogue lines and SFX.
