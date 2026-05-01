# Audio Assembly & Mixing Guide

Complete ffmpeg pipeline for assembling radio drama productions from individual audio assets.

## Step 1: Normalize All Clips

Before mixing, normalize everything to the same format:

```bash
# Normalize to 48kHz 16-bit mono (for dialogue)
ffmpeg -i input.wav -ar 48000 -ac 1 -sample_fmt s16 normalized.wav

# Normalize to 48kHz stereo (for music and SFX)
ffmpeg -i input.wav -ar 48000 -ac 2 -sample_fmt s16 normalized.wav
```

## Step 2: Build the Dialogue Timeline

Concatenate dialogue clips in scene order with pauses between them:

```bash
# Create silence clips for pauses
ffmpeg -f lavfi -i anullsrc=r=48000:cl=mono -t 2.0 pause_2s.wav

# Concatenate dialogue + pauses in order
ffmpeg -i line_001.wav -i pause_1s.wav -i line_002.wav -i pause_0.5s.wav -i line_003.wav \
  -filter_complex "[0:a][1:a][2:a][3:a][4:a]concat=n=5:v=0:a=1[out]" \
  -map "[out]" scene_dialogue.wav
```

For many clips, use a concat file:
```bash
# concat_list.txt
file 'line_001.wav'
file 'pause_1s.wav'
file 'line_002.wav'
file 'pause_0.5s.wav'
file 'line_003.wav'

ffmpeg -f concat -safe 0 -i concat_list.txt -c copy scene_dialogue.wav
```

## Step 3: Apply Fades to Music Cues

```bash
# Fade in 3s, fade out 5s on a 30s music clip
ffmpeg -i music_raw.wav \
  -af "afade=t=in:st=0:d=3,afade=t=out:st=25:d=5" \
  music_faded.wav
```

## Step 4: Sidechain Ducking (Music Under Dialogue)

The most important mixing technique for radio drama — music automatically drops when someone speaks.

### Simple Volume Approach

```bash
# Mix dialogue (full volume) with music (at 30% volume)
ffmpeg -i dialogue.wav -i music.wav \
  -filter_complex "[1:a]volume=0.3[music];[0:a][music]amix=inputs=2:duration=longest[out]" \
  -map "[out]" mixed.wav
```

### Dynamic Sidechain Compression (Recommended)

Music dynamically ducks when dialogue is present, then smoothly returns:

```bash
ffmpeg -i dialogue.wav -i music.wav \
  -filter_complex "
    [0:a]asplit=2[dialogue][sc];
    [1:a]volume=0.5[music_vol];
    [sc]aformat=sample_fmts=fltp[sc_fmt];
    [music_vol][sc_fmt]sidechaincompress=
      threshold=0.02:
      ratio=8:
      attack=50:
      release=300:
      level_sc=1.0:
      level_in=1.0
    [ducked_music];
    [dialogue][ducked_music]amix=inputs=2:duration=longest[out]
  " -map "[out]" scene_mixed.wav
```

**Parameter guide:**

| Parameter | Value | Effect |
|-----------|-------|--------|
| threshold | 0.01-0.05 | Lower = more aggressive ducking. 0.02 is a good default |
| ratio | 4-12 | Higher = deeper duck. 8 is natural for radio drama |
| attack | 20-100ms | How fast music drops. 50ms is transparent |
| release | 200-500ms | How fast music returns. 300ms avoids pumping |
| volume (pre) | 0.3-0.6 | Base music level before ducking. 0.5 for prominent score, 0.3 for background bed |

## Step 5: Layer SFX

SFX are typically layered at specific timestamps using the adelay filter:

```bash
# Place SFX at specific time offsets
ffmpeg -i scene_dialogue_music.wav -i sfx_door.wav -i sfx_thunder.wav \
  -filter_complex "
    [1:a]adelay=5000|5000,volume=0.7[sfx1];
    [2:a]adelay=23000|23000,volume=0.8[sfx2];
    [0:a][sfx1]amix=inputs=2:duration=first[mix1];
    [mix1][sfx2]amix=inputs=2:duration=first[out]
  " -map "[out]" scene_full.wav
```

The adelay value is in milliseconds. Calculate from the dialogue timeline.

## Step 6: Scene-to-Scene Crossfades

```bash
# 3-second crossfade between scenes
ffmpeg -i scene1.wav -i scene2.wav \
  -filter_complex "acrossfade=d=3:c1=tri:c2=tri" \
  transition.wav
```

Curve options: `tri` (linear), `exp` (exponential — more dramatic), `log` (logarithmic — gentler).

For full productions, chain crossfades:
```bash
ffmpeg -i scene1.wav -i scene2.wav -i scene3.wav \
  -filter_complex "
    [0:a][1:a]acrossfade=d=3:c1=tri:c2=tri[s12];
    [s12][2:a]acrossfade=d=3:c1=tri:c2=tri[out]
  " -map "[out]" full_production.wav
```

## Step 7: Mastering Chain

Apply to the final assembled mix:

```bash
ffmpeg -i full_production.wav \
  -af "
    loudnorm=I=-16:TP=-1.5:LRA=11,
    acompressor=threshold=-20dB:ratio=3:attack=5:release=50,
    alimiter=limit=-1dB:level=disabled
  " master.wav
```

| Stage | What it does |
|-------|-------------|
| loudnorm I=-16 | Targets -16 LUFS (podcast/audiobook standard) |
| TP=-1.5 | True peak ceiling at -1.5dB (prevents clipping on any device) |
| LRA=11 | Loudness range — keeps quiet and loud parts within 11 LU |
| acompressor | Gently tames dynamic spikes |
| alimiter | Hard ceiling — nothing goes above -1dB |

## Step 8: Export

```bash
# Production master (WAV)
# (already done from Step 7)

# Distribution MP3
ffmpeg -i master.wav -b:a 320k -id3v2_version 3 \
  -metadata title="The Last Lighthouse" \
  -metadata artist="AI Radio Drama" \
  -metadata album="Radio Drama Productions" \
  final.mp3

# Distribution AAC (for Apple platforms)
ffmpeg -i master.wav -c:a aac -b:a 256k final.m4a
```

## Complete Single-Scene Assembly (All-in-One)

For quick assembly of a single scene with dialogue, ducked music, and SFX:

```bash
ffmpeg \
  -i scene_dialogue.wav \
  -i scene_music.wav \
  -i scene_sfx_rain.wav \
  -i scene_sfx_door.wav \
  -filter_complex "
    [0:a]asplit=2[dialogue][sc];
    [1:a]volume=0.4,afade=t=in:d=3,afade=t=out:st=40:d=5[music];
    [sc]aformat=sample_fmts=fltp[sc_fmt];
    [music][sc_fmt]sidechaincompress=threshold=0.02:ratio=8:attack=50:release=300[ducked];
    [2:a]volume=0.6[rain];
    [3:a]adelay=8000|8000,volume=0.7[door];
    [dialogue][ducked]amix=inputs=2:duration=longest[dm];
    [dm][rain]amix=inputs=2:duration=longest[dmr];
    [dmr][door]amix=inputs=2:duration=first[mixed];
    [mixed]loudnorm=I=-16:TP=-1.5:LRA=11[out]
  " -map "[out]" scene_final.wav
```
