#!/usr/bin/env bash
set -euo pipefail
# Usage: scripts/quantize.sh /path/to/llama-quantize model-f16.gguf model-q4.gguf
"$1" "$2" "$3" Q4_K_M
