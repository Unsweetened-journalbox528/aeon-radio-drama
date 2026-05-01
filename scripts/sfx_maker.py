#!/usr/bin/env python3
"""SFX Maker — standalone CLI for single-shot sound effect generation.

Parallel to `music_tool/music_maker.py`. Wraps `radio_drama.py`'s SFX
backend chain so an agent can generate one SFX at a time without needing
a full radio-drama project structure.

Backend routing (auto, by duration):
  ≤10 s    MMAudio Large 44k v2     primary; sharp transients, foley, mechanical
  10–47 s  Stable Audio Open 1.0    fallback; ambient texture
  47+ s    ACE Step 1.5             last resort; long ambient beds only

Usage:
  python sfx_maker.py --prompt "Heavy wooden door slamming shut in stone corridor" \
      --duration 4 -o output/the_one_dreaming/sfx/door_slam.wav
  python sfx_maker.py --prompt "Distant thunder rolling across hills" \
      --duration 8 --seed 42 -o sfx/thunder.flac
  python sfx_maker.py --prompt "Steady rain on metal roof, muffled" \
      --duration 30 -o ambience/rain_30s.wav

Output formats: .wav (transcoded to pcm_s16le), .flac (lossless), .mp3 (libmp3lame -q 2).
The library file is also placed at input/sfx/<name> for radio_drama.py to find later.
"""
import argparse
import os
import shutil
import sys
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import radio_drama internals — same module that powers `--stage sfx`
import radio_drama as rd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    p = argparse.ArgumentParser(
        description="Standalone SFX generator. Auto-routes to MMAudio (≤10s), "
                    "Stable Audio Open (10–47s), or ACE Step (47+s).")
    p.add_argument("--prompt", "--description", required=True, dest="prompt",
                   help="Specific physical description: include material, action, "
                        "environment, perspective. e.g. 'heavy wooden door slamming "
                        "shut in stone corridor, deep resonant thud with echo'.")
    p.add_argument("--duration", type=float, required=True,
                   help="Length in seconds. <=10 routes to MMAudio, 10–47 to "
                        "Stable Audio Open, >47 to ACE Step.")
    p.add_argument("--output", "-o", required=True,
                   help="Output path (.wav / .flac / .mp3). Parent dirs auto-created.")
    p.add_argument("--seed", type=int, default=None,
                   help="Fixed seed for reproducibility (default: random).")
    p.add_argument("--negative", default="music, speech, vocals, singing",
                   help="Negative prompt (MMAudio + SAO). Default keeps engines "
                        "locked to SFX mode (no drifting musical).")
    p.add_argument("--name", default=None,
                   help="Library filename for input/sfx/ (default: derived from "
                        "--output basename). Lets radio_drama.py find this SFX "
                        "later by name.")
    p.add_argument("--no-library", action="store_true",
                   help="Don't also place a copy in input/sfx/. By default the "
                        "tool stores a library copy so future radio_drama runs "
                        "can reference this SFX by filename.")
    args = p.parse_args()

    # Validate output path early
    out_path = os.path.abspath(args.output)
    out_ext = os.path.splitext(out_path)[1].lower()
    if out_ext not in (".wav", ".flac", ".mp3"):
        print(f"ERROR: --output must be .wav, .flac, or .mp3 (got {out_ext})")
        sys.exit(2)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    seed = args.seed if args.seed is not None else random.randint(0, 2**31 - 1)
    library_name = args.name or os.path.basename(out_path)

    print("=== SFX Maker ===")
    print(f"  prompt:    {args.prompt[:80]}{'...' if len(args.prompt) > 80 else ''}")
    print(f"  duration:  {args.duration:.1f}s")
    print(f"  seed:      {seed}")
    print(f"  output:    {out_path}")
    print(f"  library:   {library_name}{' (skipped)' if args.no_library else ''}")
    # Backend availability check up-front so the user knows which engine will run
    mma_ok = bool(rd.find_mmaudio_models())
    sao_ok = bool(rd.find_stable_audio_checkpoint())
    if args.duration <= rd.MMAUDIO_MAX_DURATION:
        backend = "MMAudio Large 44k v2" if mma_ok else \
                  ("Stable Audio Open" if sao_ok else "ACE Step (fallback)")
    elif args.duration <= 47.0:
        backend = "Stable Audio Open 1.0" if sao_ok else "ACE Step (fallback)"
    else:
        backend = "ACE Step 1.5"
    print(f"  backend:   {backend}")
    print()

    # Build a minimal ctx dict — generate_sfx() and its backends need only
    # `project_name` (used in the ComfyUI filename_prefix). Everything else
    # is module-level state in radio_drama.
    ctx = {"project_name": "sfx_maker"}

    # Negative prompt for MMAudio/SAO is set per-call. We patch the module
    # default since generate_sfx() reads it at call time.
    original_neg = getattr(rd, "MMAUDIO_NEGATIVE_PROMPT", None)
    if hasattr(rd, "MMAUDIO_NEGATIVE_PROMPT"):
        rd.MMAUDIO_NEGATIVE_PROMPT = args.negative

    try:
        library_path = rd.generate_sfx(
            ctx=ctx,
            src=library_name,
            description=args.prompt,
            duration=float(args.duration),
            seed=seed,
        )
    except Exception as e:
        print(f"\nFAILED: {e}")
        sys.exit(1)
    finally:
        if original_neg is not None and hasattr(rd, "MMAUDIO_NEGATIVE_PROMPT"):
            rd.MMAUDIO_NEGATIVE_PROMPT = original_neg

    if not library_path or not os.path.exists(library_path):
        print(f"\nFAILED: backend completed but no output file at {library_path}")
        sys.exit(1)

    # Copy/transcode from library to user's --output. _import_to_library
    # already handles container transcoding (FLAC→WAV gets real PCM, etc.)
    rd._import_to_library(library_path, out_path)

    # Optionally remove the library copy if user said --no-library
    if args.no_library and library_path != out_path:
        try:
            os.remove(library_path)
        except Exception:
            pass

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"\nGenerated: {out_path}  ({size_mb:.2f} MB)")
    if not args.no_library:
        print(f"Library:   {library_path}  (so radio_drama.py can reference '{library_name}')")
    print(f"Seed:      {seed}  (reuse to regenerate exactly the same SFX)")


if __name__ == "__main__":
    main()
