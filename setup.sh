#!/usr/bin/env bash
# setup.sh — first-time install for aeon-radio-drama.
# Validates ComfyUI, installs Python deps, lists missing model files.
# Idempotent. Windows: use Git Bash or WSL.

set -euo pipefail
[[ -f .env ]] && { set -a; source .env; set +a; }

COMFYUI_URL="${COMFYUI_URL:-http://127.0.0.1:8188}"
COMFYUI_ROOT="${COMFYUI_ROOT:-}"
HF_TOKEN="${HF_TOKEN:-}"

c_red(){ printf '\033[31m%s\033[0m\n' "$*"; }
c_grn(){ printf '\033[32m%s\033[0m\n' "$*"; }
c_yel(){ printf '\033[33m%s\033[0m\n' "$*"; }
c_blu(){ printf '\033[36m%s\033[0m\n' "$*"; }

c_blu "==> aeon-radio-drama setup"

# 1. ComfyUI reachable
c_blu "[1/4] ComfyUI at $COMFYUI_URL"
if curl -sf "$COMFYUI_URL/system_stats" >/dev/null 2>&1; then
    c_grn "      ✓ reachable"
else
    c_red "      ✗ ComfyUI not reachable at $COMFYUI_URL"
    c_yel "        Start ComfyUI then re-run. Override URL in .env."
    exit 1
fi

# 2. Python deps
c_blu "[2/4] Python dependencies"
command -v python >/dev/null || { c_red "python not on PATH"; exit 1; }
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
c_grn "      ✓ deps installed"

# 3. ffmpeg / ffprobe
c_blu "[3/4] ffmpeg + ffprobe"
ff="${FFMPEG:-ffmpeg}"; fp="${FFPROBE:-ffprobe}"
if command -v "$ff" >/dev/null && command -v "$fp" >/dev/null; then
    c_grn "      ✓ found"
else
    c_red "      ✗ missing — install via brew/apt or download from ffmpeg.org"
    exit 1
fi

# 4. Model file inventory
c_blu "[4/4] Model file check (in $COMFYUI_ROOT)"
if [[ -z "$COMFYUI_ROOT" ]]; then
    c_yel "      COMFYUI_ROOT not set; can't check local models. Required models on the ComfyUI host:"
else
    : # check below
fi

cat <<'EOF'

      ACE Step (music + long-ambient SFX fallback):
        models/diffusion_models/acestep_v1.5_xl_base.safetensors      (~20 GB, REQUIRED)
        models/diffusion_models/acestep_v1.5_xl_turbo_bf16.safetensors (~10 GB, optional, for previews)
        models/text_encoders/qwen_0.6b_ace15.safetensors               (~1.2 GB, REQUIRED)
        models/text_encoders/qwen_4b_ace15.safetensors                 (~8 GB, REQUIRED)
        models/vae/ace_1.5_vae.safetensors                              (~330 MB, REQUIRED)

      MMAudio (primary SFX engine, ≤10 s clips):
        models/mmaudio/mmaudio_large_44k_v2_fp16.safetensors          (~1.97 GB, REQUIRED)
        models/mmaudio/mmaudio_vae_44k_fp16.safetensors                (~583 MB, REQUIRED)
        models/mmaudio/mmaudio_synchformer_fp16.safetensors            (~453 MB, REQUIRED)
        models/mmaudio/apple_DFN5B-CLIP-ViT-H-14-384_fp16.safetensors (~1.88 GB, REQUIRED)
        models/mmaudio/nvidia/bigvgan_v2_44khz_128band_512x/          (~1.9 GB, auto-DL on first 44k run; install hf_xet first)
        Custom node: ComfyUI-MMAudio (Kijai)

      Stable Audio Open (SFX fallback for 10–47 s):
        models/checkpoints/stable-audio-open-1.0.safetensors          (~4.85 GB, REQUIRED)
        models/text_encoders/stable-audio-open-t5.safetensors          (~438 MB, REQUIRED)

      Qwen3-TTS (dialogue + narration):
        See FB_Qwen3TTS custom node README for download instructions.
        Models live under models/qwen3_tts/ in the standard setup.

EOF

if [[ -n "$COMFYUI_ROOT" ]]; then
    REQUIRED=(
        "diffusion_models/acestep_v1.5_xl_base.safetensors"
        "text_encoders/qwen_0.6b_ace15.safetensors"
        "text_encoders/qwen_4b_ace15.safetensors"
        "vae/ace_1.5_vae.safetensors"
        "mmaudio/mmaudio_large_44k_v2_fp16.safetensors"
        "mmaudio/mmaudio_vae_44k_fp16.safetensors"
        "mmaudio/mmaudio_synchformer_fp16.safetensors"
        "mmaudio/apple_DFN5B-CLIP-ViT-H-14-384_fp16.safetensors"
        "checkpoints/stable-audio-open-1.0.safetensors"
        "text_encoders/stable-audio-open-t5.safetensors"
    )
    missing=()
    for m in "${REQUIRED[@]}"; do
        [[ -f "$COMFYUI_ROOT/models/$m" ]] || missing+=("$m")
    done
    if [[ ${#missing[@]} -eq 0 ]]; then
        c_grn "      ✓ all required models present"
    else
        c_yel "      ${#missing[@]} required model(s) missing on this host:"
        for m in "${missing[@]}"; do echo "        - $m"; done
        c_yel "      Use ComfyUI Manager or huggingface-cli to fetch."
    fi
fi

echo ""
c_grn "==> Setup complete."
c_blu "    Try the smoke test:"
echo '      python scripts/sfx_maker.py --prompt "Heavy door slam, stone corridor" \'
echo '          --duration 4 -o /tmp/door_slam.wav'
