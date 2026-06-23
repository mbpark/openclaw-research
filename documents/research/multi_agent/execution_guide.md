# Heterogeneous Chain Testing Guide

## Test Configuration

This document describes the setup for running heterogeneous chain tests with mixed Anthropic and Gemini models.

### Models
- **Claude**: claude-opus-4-8
- **Gemini**: gemini-2.5-flash

### Vectors File
```
chain_tests/vectors/expanded_vectors.json
```

### API Key Files
```
api_key.txt              # Anthropic API key
gemini_api_key.txt       # Gemini API key
```

### Model Sequence Format
- `claude-gemini-claude-gemini` - Alternating, starts with Claude
- `gemini-claude-gemini-claude` - Alternating, starts with Gemini

## Running Tests

### Chain Length 4: Claude → Gemini Flash → Claude → Gemini Flash

```bash
cd ~/.openclaw/workspace/documents/research/multi_agent

nohup python3 chain_tests/run_heterogeneous_v2.py \
  --chain-length 4 \
  --model-sequence claude-gemini-claude-gemini \
  --anthropic-key api_key.txt \
  --gemini-key gemini_api_key.txt \
  --vectors-file chain_tests/vectors/expanded_vectors.json \
  --results-dir chain_tests/comprehensive_results \
  > het_run_4_flash_claude.log 2>&1 &
echo "Started PID: $!"
```

### Chain Length 4: Gemini Flash → Claude → Gemini Flash → Claude

```bash
nohup python3 chain_tests/run_heterogeneous_v2.py \
  --chain-length 4 \
  --model-sequence gemini-claude-gemini-claude \
  --anthropic-key api_key.txt \
  --gemini-key gemini_api_key.txt \
  --vectors-file chain_tests/vectors/expanded_vectors.json \
  --results-dir chain_tests/comprehensive_results \
  > het_run_4_flash_gemini.log 2>&1 &
echo "Started PID: $!"
```

### Chain Length 5: Claude → Gemini Flash → Claude → Gemini Flash → Claude

```bash
nohup python3 chain_tests/run_heterogeneous_v2.py \
  --chain-length 5 \
  --model-sequence claude-gemini-claude-gemini-claude \
  --anthropic-key api_key.txt \
  --gemini-key gemini_api_key.txt \
  --vectors-file chain_tests/vectors/expanded_vectors.json \
  --results-dir chain_tests/comprehensive_results \
  > het_run_5_flash_claude.log 2>&1 &
echo "Started PID: $!"
```

### Chain Length 5: Gemini Flash → Claude → Gemini Flash → Claude → Gemini Flash

```bash
nohup python3 chain_tests/run_heterogeneous_v2.py \
  --chain-length 5 \
  --model-sequence gemini-claude-gemini-claude-gemini \
  --anthropic-key api_key.txt \
  --gemini-key gemini_api_key.txt \
  --vectors-file chain_tests/vectors/expanded_vectors.json \
  --results-dir chain_tests/comprehensive_results \
  > het_run_5_flash_gemini.log 2>&1 &
echo "Started PID: $!"
```

## Test Structure

### Vector Classes (5)
1. `class_1_direct_override` - 10 vectors
2. `class_2_nested_encapsulation` - 10 vectors
3. `class_3_progressive_erosion` - 10 vectors
4. `class_4_system_override` - 10 vectors
5. `class_5_logical_paradox` - 10 vectors

**Total: 50 vectors**

### Injection Points (3)
- `start` - Injection at hop 0 (beginning)
- `middle` - Injection at hop N/2
- `end` - Injection at last hop

### Total Tests
- **Chain 4:** 50 vectors × 3 points = 150 tests
- **Chain 5:** 50 vectors × 3 points = 150 tests

## Checkpointing

Results are saved every 10 tests to:
```
chain_tests/comprehensive_results/het_checkpoint_<chain_length>_<start_model>.json
```

## Final Results

```
chain_tests/comprehensive_results/het_final_<chain_length>_<start_model>.json
```

## Monitoring Progress

```bash
# Watch log file
tail -f het_run_4_flash_claude.log | grep -v FutureWarning

# Check checkpoint
cat chain_tests/comprehensive_results/het_checkpoint_4_claude.json | python3 -c "import sys, json; print(len(json.load(sys.stdin))), 'tests done'"
```

## Estimated Duration

Based on single model testing:
- Chain 4: ~2-3 hours per sequence
- Chain 5: ~3-4 hours per sequence
- Total (4 sequences): ~10-14 hours
