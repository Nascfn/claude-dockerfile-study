# How the three models behaved

Settings, effort, tool use and writing habits of Opus 5.5, Sonnet 5.5 and Haiku 5.5.

## Settings (identical for all three)

| Setting | Value |
|---|---|
| Runner | Claude Code CLI 2.1.326, headless (`claude -p`), one new process per run |
| Effort | `--effort high` |
| Tools offered | Read, Glob, Grep, Write |
| Not offered | Shell, in-place edit, web access, sub-agents, MCP servers, skills |
| Runs | One per repository per model |
| Prompt | The same neutral prompt (`scripts/prompt.txt`), no mention of security |

## Effort spent per run (means over 10 repositories)

| Measure | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|
| Wall-clock seconds | 104.9 | 40.2 | 134.6 |
| Fastest / slowest run (s) | 28.5 / 298.4 | 19.0 / 75.6 | 33.2 / 427.8 |
| Turns | 28.8 | 21.2 | 31.4 |
| Distinct files read | 14.7 | 9.3 | 15.4 |
| Output tokens | 10,824 | 5,476 | 30,516 |
| …of which thinking tokens | 4,273 | 1,123 | 22,768 |
| Thinking tokens, smallest / largest run | 530 / 15,252 | 153 / 2,867 | 3,923 / 84,501 |
| Cost per run (USD) | 0.643 | 0.167 | 0.065 |
| Cost for all 10 repositories (USD) | 6.43 | 1.67 | 0.65 |

Haiku thought the most and Sonnet the least at the same effort setting. Cost is the figure the CLI reports and includes prompt-cache discounts, so read it as relative.

## Tool calls over all 10 runs

| Tool | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|
| Read | 150 | 97 | 165 |
| Grep | 71 | 47 | 64 |
| Glob | 29 | 33 | 45 |
| Write | 28 | 24 | 27 |
| Attempted, not offered (rejected) | 0 | 1 | 3 |
| **Total** | 278 | 202 | 304 |

## What they wrote

| Measure | Original | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| Mean Dockerfile length (lines) | 58 | 73.5 | 62 | 77.3 |
| Mean comment lines | 16.1 | 22.5 | 17.1 | 28.4 |
| Longest Dockerfile (lines) | 149 | 110 | 91 | 120 |
| Wrote a `.dockerignore` | 8 have one | 10 | 10 | 10 |
| Wrote an entrypoint script | – | 4 | 3 | 3 |
| Wrote another support file | – | 2 | 1 | 2 |
| Multi-stage builds | 7 | 9 | 10 | 9 |
| Final base: Alpine / Debian-based / distroless | 5 / 4 / 1 | 2 / 6 / 2 | 4 / 6 / 0 | 0 / 9 / 1 |

Opus and Haiku write longer files than the originals and comment more. The number of instructions is about the same for every author (22.3 for the originals against 21.9, 21.3 and 22.7).

## How much the models agree with each other

- In 4 of 10 repositories all three models got the same static score.
- In 3 of 10 repositories all three chose the same final base image.
- All three made the same root or non-root decision in every repository where all three images were scanned.
- No pairwise difference between models is statistically significant (see table T14 in `FINDINGS.md`).

[Back to the index](README.md)
