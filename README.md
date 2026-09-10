# synctoon — open-source AI 2D lip-sync animation from text (Python)

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://python.org)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Automate-Animation/synctoon.svg)](https://github.com/Automate-Animation/synctoon/stargazers)

synctoon turns a text script into a lip-synced 2D cut-out animation video. An LLM picks head angle, eyes, gesture, background and zoom per word. It works with Claude, Gemini, or a local Ollama model. ElevenLabs voices the script with word timestamps, or you bring your own audio. Every frame's asset choice is plain data you can edit before rendering.

Examples made with synctoon: [Daily YG Stories on YouTube](https://www.youtube.com/@DailyYGStories).

## Why synctoon

- **Frame-level control.** The whole video is one CSV, one row per frame. Change a cell, re-render, done.
- **Any LLM.** Anthropic, Gemini, or any OpenAI-compatible endpoint, including local Ollama, LM Studio and vLLM.
- **No forced-alignment server needed.** ElevenLabs returns word timestamps with the audio, so the default path has no Docker.
- **Re-render without re-asking the LLM.** `--skip-core` rebuilds frames from the edited CSV; already-rendered frames come from cache.
- **Free and GPL-3.0.** No SaaS, no watermark, no per-minute fee beyond the APIs you choose to call.

## How it works

```
script.txt ──┬─> ElevenLabs TTS (with-timestamps) ──> voice.mp3 + word times ─┐
             │      or                                                       │
             └─> your audio.mp3 + Gentle (Docker) ──> word times ────────────┤
                                                                             v
script text ──> LLM (8 prompts) ──> per-word head / eyes / emotion / gesture / zoom / background
                                                                             │
                                                                             v
                    g2p phonemes ──> mouth viseme per frame ──> video_frames_info.csv  (edit here)
                                                                             │
                                                                             v
                    frame_generator.py (PIL, cut-out layers) ──> video_frames/*.png
                                                                             │
                                                                             v
                    frame_to_video.py (OpenCV, 24 fps, silent) ──> videos/<name>.mp4 ──> ffmpeg mux audio
```

## Quick Start

Prerequisites: Python 3.10+, `ffmpeg` on PATH, an ElevenLabs key, and one LLM key (or a running Ollama).

```bash
git clone https://github.com/Automate-Animation/synctoon.git
cd synctoon
pip install -r requirements.txt
cp .env.example .env        # fill in ANTHROPIC_API_KEY (or another provider) and ELEVENLABS_API_KEY

cd core                     # all paths in the pipeline are relative to core/
python create_animation.py --script ../example/story/story-short.txt -n seed

# the video is silent; add the synthesized voice track
ffmpeg -i videos/seed.mp4 -i build/seed/voice.mp3 -c:v copy -c:a aac -shortest seed_final.mp4
```

First run downloads NLTK data for `g2p-en`. The LLM step makes 8 calls per script; with Gemini free tier it sleeps 6 s between calls.

Full CLI (`core/create_animation.py`):

| Flag | Meaning |
|---|---|
| `--script PATH` | Story text file (required) |
| `-n, --name NAME` | Output video name; default is the script's basename |
| `--audio PATH` | Use this audio instead of synthesizing; needs `ALIGNER=gentle` and the Gentle container |
| `--out-dir DIR` | Where `voice.mp3`, alignment JSON and `output_test.json` go; default `build/<name>` |
| `--fps N` | Frames per second (default 24) |
| `--skip-core` | Skip LLM + alignment; render from the existing `video_frames_info.csv` |
| `--skip-frames` | Skip frame rendering; only rebuild the video from existing PNGs |

## Supported LLM providers

Set `LLM_PROVIDER` in `.env`. `LLM_MODEL` overrides the default model for any provider.

| `LLM_PROVIDER` | Talks to | Env vars | Default model |
|---|---|---|---|
| `anthropic` | Anthropic SDK | `ANTHROPIC_API_KEY` (a real API key, not an OAuth token) | `claude-sonnet-5` |
| `claude-cli` | Local Claude Code CLI: `claude -p --output-format json --model <LLM_MODEL>` | none; uses your logged-in `claude` session | `sonnet` |
| `gemini` | Google Generative Language REST API | `GOOGLE_API_KEY`, optional `LLM_SLEEP_SECONDS` (default 6) | `gemini-3.6-flash` |
| `openai` | Any OpenAI-compatible `/v1/chat/completions`: Ollama, LM Studio, vLLM, OpenAI | `LLM_BASE_URL` (default `http://localhost:11434/v1`), optional `OPENAI_API_KEY` | `llama3.2` |

Local example with Ollama:

```bash
ollama pull llama3.2
# .env
LLM_PROVIDER=openai
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3.2
```

The LLM must return valid JSON for eight small schemas (head, eyes, emotion, gesture, intensity, zoom, background, character). Each prompt retries up to 3 times with the validation error appended, then fails loudly.

## Voice / alignment

synctoon needs word start and end times to place mouth shapes. Two sources:

| `ALIGNER` | When | What happens |
|---|---|---|
| `elevenlabs` (default in `.env.example`) | You pass `--script` only | `POST /v1/text-to-speech/{voice}/with-timestamps`; audio and character times come back together and are converted to word times. No Docker. |
| `gentle` | You pass `--audio` | Your audio and the script are sent to Gentle at `http://localhost:49153`. Start it with `cd Docker && docker-compose up -d`. |

Voice settings: `ELEVENLABS_VOICE_ID` (default `21m00Tcm4TlvDq8ikWAM`) and `ELEVENLABS_MODEL_ID` (default `eleven_multilingual_v2`).

Passing `--audio` while `ALIGNER=elevenlabs` raises an error on purpose: ElevenLabs only aligns audio it generated.

## Every frame is controllable

Today the editable file is `core/video_frames_info.csv`. `core.py` writes it, one row per frame:

| Column | Read by renderer | Notes |
|---|---|---|
| `Character` | yes | Folder under `core/images/characters/`, e.g. `character_1` |
| `Emotion` | yes | Eyes folder, e.g. `happy`, `angry`, `worried`; `_2` suffix = higher intensity |
| `Body` | yes | Gesture folder under `body/`, e.g. `explain`, `standing`, `idea` |
| `Head_Direction` | yes | `L`, `M`, or `R` |
| `Eyes_Direction` | yes | Must be `<Emotion>_<L|M|R>` or a blink frame `02`/`03`/`04` |
| `Background` | yes | Folder under `background/`, e.g. `classroom`, `white` |
| `Mouth_Emotion` | yes | `happy` or `sad` mouth set |
| `Mouth_Name` | yes | Viseme file stem, e.g. `a_e_h`, `m_b_close_s`, `th_h` |
| `Zoom` | yes | `0`, `1`, or `2` |
| `Blink` | no | Currently ignored (bug; see Known issues) |
| `Frame`, `Word`, `Start_Time`, `End_Time`, `Phoneme` | no | Informational only |

Edit rows, then `python create_animation.py --script ../example/story/story-short.txt -n seed --skip-core`. Frames whose attribute set was already rendered are reused from `video_frames/`; new combinations render. Timing is row count only: to hold a pose longer, add rows.

Re-running without `--skip-core` overwrites the CSV, so keep a copy of hand edits.

A compact `character.json` + `timeline.json` format (runs instead of rows, sparse overrides, Rhubarb A–H+X visemes, deterministic seed) is specified in [docs/ASSET_FORMAT.md](docs/ASSET_FORMAT.md). It is a proposal and is not implemented yet.

## Create your own character

A character is a folder of transparent PNGs: `head/{L,M,R}`, `eyes/<emotion>/`, `mouth/{happy,sad}/`, `body/<gesture>/`, plus positions in `core/images/metadata/metadata.json`. Only `character_1` ships today.

The plan for generating a full layer set from one reference image (base plate, masked image-edits, chroma-key cut, auto anchors, QA grid) is in [docs/TALEEMABAD_CHARACTER_PIPELINE.md](docs/TALEEMABAD_CHARACTER_PIPELINE.md). The reference image comes from [Design-your-perfect-AI-Persona](https://github.com/oyekamal/Design-your-perfect-AI-Persona).

## Known issues

From the full [code audit](docs/AUDIT.md); top items:

1. All paths are relative to `core/`; the pipeline only works after `cd core`.
2. `Blink` is read with `bool("False") == True`, so the blink column has no effect ([AUDIT §3](docs/AUDIT.md)).
3. Blink rows are inserted rather than overwritten, so the video runs about 3.6 % longer than the audio ([AUDIT §3](docs/AUDIT.md)).
4. Mouth timing splits frames evenly across g2p phonemes instead of using the aligner's per-phone durations, which makes lip-sync look floaty ([AUDIT §5](docs/AUDIT.md)).
5. `frame_to_video.py` returns `False` on failure but the pipeline still prints SUCCESS; `body_actions` has duplicate ids; `metadata.json` distorts eyes and body aspect ([AUDIT §1, §3](docs/AUDIT.md)).

Language: `g2p-en` and Gentle are English-only. Urdu and code-switched scripts are on the roadmap.

## Roadmap

- Implement `character.json` + `timeline.json` and a deterministic renderer (ASSET_FORMAT.md, phase 1).
- Use aligner phone durations for visemes; fix blink and drift bugs.
- Character generation tooling from a persona reference image (TALEEMABAD_CHARACTER_PIPELINE.md, phases 2–4).
- Urdu / code-switched lip-sync via ElevenLabs character timestamps.
- `pyproject.toml`, tests for the pure functions, CI.

## FAQ

**Can I run it fully offline?**
The LLM step yes, via Ollama or LM Studio. Voice needs ElevenLabs, or your own audio plus the Gentle Docker container. Nothing else calls the network after the first NLTK download.

**Does it work with ElevenLabs?**
Yes; it is the default. synctoon uses the `with-timestamps` endpoint so no separate alignment step is needed.

**Can I use my own recorded voice?**
Yes. Set `ALIGNER=gentle`, start the Gentle container, and pass `--audio your.mp3`. English only.

**How do I change what a character does in one scene?**
Edit the rows for those frames in `core/video_frames_info.csv` and re-run with `--skip-core`.

**Is this free for commercial use?**
Yes. GPL-3.0 lets you use and sell the videos you make. If you distribute a modified synctoon, you must share its source under the same license. API costs (ElevenLabs, Claude, Gemini) are yours.

## Contributing

Issues and pull requests are welcome. Good first contributions: any item in [docs/AUDIT.md §7](docs/AUDIT.md), tests for `distribute_frames`, `update_values`, `extract_json_content` and `video_frames_info`, or a new character. Run the existing test with `python -m pytest core/tests`.

## License

GPL-3.0. See [LICENSE](LICENSE).

## Credits

Created by **Muhammad Kamal** — [portfolio](https://oyekamal.github.io/oykamal/) · [YouTube @oykamal](https://youtube.com/@oykamal) · [LinkedIn](https://linkedin.com/in/muhammad-kamal-025600121) · [Instagram @oykamal](https://instagram.com/oykamal) · [Twitter @oykamal](https://twitter.com/oykamal). Thanks to Gentle and g2p-en.

Keywords: 2d-animation, lip-sync, text-to-video, cut-out-animation, explainer-video, ai-animation, elevenlabs, ollama, claude, gemini, python, gpl
