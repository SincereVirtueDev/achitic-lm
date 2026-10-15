#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  LLAMA_CPP_DIR=/path/to/llama.cpp scripts/quantize.sh model-f16.gguf model-quant.gguf Q4_K_M [options]
  LLAMA_CPP_DIR=/path/to/llama.cpp scripts/quantize.sh /path/to/llama-quantize model-f16.gguf model-quant.gguf [Q4_K_M] [options]

Options:
  --checkpoint PATH              PyTorch/Achitic checkpoint for parity verification.
  --tokenizer PATH               SentencePiece tokenizer for verification.
  --max-delta FLOAT              Maximum allowed normal max_abs_delta. Default: 0.25.
  --top1-min FLOAT               Minimum allowed top-1 match. Default: 0.90.
  --generate-tokens N            Greedy load-and-generate token count. Default: 8.
  --prompt TEXT                  Verification prompt. Default: Xin chao.
  --context N                    llama.cpp context for verification. Default: 128.
  --allow-experimental           Keep artifact even if fallback or verification fails; output is not release-ready.

Environment:
  LLAMA_CPP_DIR                  Required pinned llama.cpp checkout/build.
  LLAMA_QUANTIZE                 Optional path to llama-quantize. Defaults to LLAMA_CPP_DIR/build/bin/llama-quantize.
  ACHITIC_VERIFY_GGUF            Optional verifier script path. Defaults to scripts/verify_gguf.py.
  PYTHON                         Optional Python command. Defaults to python3.
USAGE
}

die() {
  echo "error: $*" >&2
  exit 2
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python3}"
POLICY="$ROOT/scripts/quantize_policy.py"
VERIFIER="${ACHITIC_VERIFY_GGUF:-$ROOT/scripts/verify_gguf.py}"

CHECKPOINT="${CHECKPOINT:-releases/nano/nano.pt}"
TOKENIZER="${TOKENIZER:-releases/nano/tokenizer.model}"
MAX_DELTA="${QUANT_MAX_DELTA:-0.25}"
TOP1_MIN="${QUANT_TOP1_MIN:-0.90}"
GENERATE_TOKENS="${QUANT_GENERATE_TOKENS:-8}"
PROMPT="${QUANT_PROMPT:-Xin chao}"
CONTEXT="${QUANT_CONTEXT:-128}"
ALLOW_EXPERIMENTAL=0

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 3 ]]; then
  usage
  exit 2
fi

if [[ -x "$1" && $# -ge 3 ]]; then
  LLAMA_QUANTIZE="${LLAMA_QUANTIZE:-$1}"
  IN_GGUF="$2"
  OUT_GGUF="$3"
  if [[ $# -ge 4 && "$4" != --* ]]; then
    QTYPE="$4"
    shift 4
  else
    QTYPE="Q4_K_M"
    shift 3
  fi
else
  IN_GGUF="$1"
  OUT_GGUF="$2"
  QTYPE="$3"
  shift 3
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --checkpoint)
      CHECKPOINT="$2"; shift 2 ;;
    --tokenizer)
      TOKENIZER="$2"; shift 2 ;;
    --max-delta)
      MAX_DELTA="$2"; shift 2 ;;
    --top1-min)
      TOP1_MIN="$2"; shift 2 ;;
    --generate-tokens)
      GENERATE_TOKENS="$2"; shift 2 ;;
    --prompt)
      PROMPT="$2"; shift 2 ;;
    --context)
      CONTEXT="$2"; shift 2 ;;
    --allow-experimental)
      ALLOW_EXPERIMENTAL=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      die "unknown argument: $1" ;;
  esac
done

LLAMA_DIR="${LLAMA_CPP_DIR:-}"
[[ -n "$LLAMA_DIR" ]] || die "LLAMA_CPP_DIR is required"
[[ -e "$IN_GGUF" ]] || die "input GGUF not found: $IN_GGUF"
[[ -e "$CHECKPOINT" ]] || die "checkpoint not found: $CHECKPOINT"
[[ -e "$TOKENIZER" ]] || die "tokenizer not found: $TOKENIZER"

QUANTIZE_BIN="${LLAMA_QUANTIZE:-}"
if [[ -z "$QUANTIZE_BIN" ]]; then
  if [[ -x "$LLAMA_DIR/build/bin/llama-quantize" ]]; then
    QUANTIZE_BIN="$LLAMA_DIR/build/bin/llama-quantize"
  elif [[ -x "$LLAMA_DIR/llama-quantize" ]]; then
    QUANTIZE_BIN="$LLAMA_DIR/llama-quantize"
  else
    die "llama-quantize not found; set LLAMA_QUANTIZE or build llama.cpp"
  fi
fi
[[ -x "$QUANTIZE_BIN" ]] || die "llama-quantize is not executable: $QUANTIZE_BIN"

LOG="${QUANT_LOG:-$OUT_GGUF.quantize.log}"
FALLBACK_SUMMARY="${QUANT_FALLBACK_SUMMARY:-$OUT_GGUF.fallbacks.json}"
VERIFY_OUT="${QUANT_VERIFY_OUT:-$OUT_GGUF.verify.json}"

mkdir -p "$(dirname "$OUT_GGUF")"

echo "quantize_command: $QUANTIZE_BIN $IN_GGUF $OUT_GGUF $QTYPE"
if ! "$QUANTIZE_BIN" "$IN_GGUF" "$OUT_GGUF" "$QTYPE" >"$LOG" 2>&1; then
  cat "$LOG" >&2
  die "llama-quantize failed"
fi
cat "$LOG"

"$PYTHON_BIN" "$POLICY" check-fallback --log "$LOG" --summary "$FALLBACK_SUMMARY" --allow-experimental

set +e
"$PYTHON_BIN" "$VERIFIER" \
  --checkpoint "$CHECKPOINT" \
  --tokenizer "$TOKENIZER" \
  --gguf "$OUT_GGUF" \
  --llama-cpp-dir "$LLAMA_DIR" \
  --prompt "$PROMPT" \
  --context "$CONTEXT" \
  --generate-tokens "$GENERATE_TOKENS" \
  --normal-max-delta "$MAX_DELTA" \
  --normal-top1-min "$TOP1_MIN" \
  --skip-stress \
  --out "$VERIFY_OUT"
VERIFY_STATUS=$?
set -e

REPORT_STATUS=0
if [[ -s "$VERIFY_OUT" ]]; then
  "$PYTHON_BIN" "$POLICY" check-report --report "$VERIFY_OUT" --max-delta "$MAX_DELTA" --top1-min "$TOP1_MIN" || REPORT_STATUS=$?
else
  REPORT_STATUS=3
fi

FALLBACK_STATUS=0
"$PYTHON_BIN" "$POLICY" check-fallback --log "$LOG" || FALLBACK_STATUS=$?

if [[ "$VERIFY_STATUS" -ne 0 || "$REPORT_STATUS" -ne 0 || "$FALLBACK_STATUS" -ne 0 ]]; then
  if [[ "$ALLOW_EXPERIMENTAL" -eq 1 ]]; then
    echo "warning: quantized artifact kept as experimental only; do not publish as verified evidence" >&2
    exit 0
  fi
  echo "error: quantized artifact failed policy; see $LOG, $FALLBACK_SUMMARY and $VERIFY_OUT" >&2
  exit 1
fi

echo "quantized artifact passed fallback and exact-artifact llama.cpp verification policy"
