# Attribution

`aeon-radio-drama` orchestrates four upstream audio systems. Full credit to:

## Models

### Qwen3-TTS (dialogue + narration)
- Voice synthesis with rich expressive control + per-character "voice design" instructs.
- The `FB_Qwen3TTSVoiceDesign`, `FB_Qwen3TTSRoleBank`, and `FB_Qwen3TTSDialogueInference` nodes are part of the Qwen3-TTS ComfyUI integration.
- Authors: Alibaba Qwen team.

### ACE Step 1.5 (music score + long ambient SFX fallback)
- **Authors:** StepFun AI
- **Repository:** https://github.com/ace-step/ACE-Step
- **HuggingFace:** https://huggingface.co/ace-step/ACE-Step-v1-3.5B
- The APG sampling chain originated in [NerdyRodent's v35 reference workflow](https://github.com/nerdyrodent/AVeryComfyNerd).

### MMAudio Large 44k v2 (primary SFX engine, ≤10 s)
- **Paper:** "MMAudio: Taming Multimodal Joint Training for High-Quality Video-to-Audio Synthesis" (Cheng et al., 2024)
- **ComfyUI integration:** https://github.com/kijai/ComfyUI-MMAudio (by Kijai)
- **Models:** mmaudio_large_44k_v2 + bigvgan_v2 vocoder (NVIDIA)
- The bigvgan vocoder is from NVIDIA's [BigVGAN](https://github.com/NVIDIA/BigVGAN) project.

### Stable Audio Open 1.0 (SFX fallback, 10–47 s)
- **Authors:** Stability AI
- **HuggingFace:** https://huggingface.co/stabilityai/stable-audio-open-1.0
- T5 text encoder shipped separately as `stable-audio-open-t5.safetensors`.

## Python libraries

| Library | Use here | Author |
|---|---|---|
| [pedalboard](https://github.com/spotify/pedalboard) | Mastering chain | Spotify |
| [librosa](https://github.com/librosa/librosa) | LUFS / DR / RMS analysis | Brian McFee et al. |
| [soundfile](https://github.com/bastibe/python-soundfile) | WAV/FLAC IO | Bastian Bechtold |
| [numpy](https://numpy.org/) / [scipy](https://scipy.org/) | numerical foundation | NumPy / SciPy teams |

## ffmpeg

The mix bus, sidechain ducking, sample-rate canonicalization, and final loudnorm all run on [FFmpeg](https://www.ffmpeg.org/). The pipeline depends on the `sidechaincompress`, `loudnorm`, `aresample=async=1`, `aformat`, `alimiter`, and `ebur128` filters specifically.

## ComfyUI

The orchestration target. https://github.com/comfyanonymous/ComfyUI

## Pipeline-specific design notes

- **Three-Lock voice persistence** (voice_instruct + seed + emotion_overrides per character) is described in `references/voice-casting.md`. The pattern is original to this project.
- **Sample-rate canonicalization at every stage boundary** to fix the historical mix distortion bug (mismatched rates feeding sidechaincompress) — described in `PRODUCTION.md` § 6.
- **Duration-routed SFX engine selection** (≤10 s → MMAudio, 10–47 s → SAO, 47+ s → ACE) — empirically validated A/B testing across foley / mechanical / biological / transient categories.
- **Dynamics-preserving mastering chain** (no compressor in default flow, no LRA constraint, brick-wall Clipping vs upward-makeup Limiter) — described in `SKILL.md` § Music mastering and `scripts/music_mastering.py`.

## License notes

This repo is MIT-licensed. The models retain their own licenses — refer to each upstream for terms.
