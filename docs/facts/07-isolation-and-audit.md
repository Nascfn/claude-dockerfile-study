# What the models could see, and the evidence

The isolation rules, the audit of all 30 sessions, and the hints that still leaked.

## What a model could and could not do

| Could | Could not |
|---|---|
| Read any file in its own copy of the stripped repository | Read anything outside that copy |
| Search file names and file contents | Run commands, build or test anything |
| Create new files | Edit a file in place |
|  | Use the web, call another agent, or use any extension |
|  | See the original Dockerfile, `.dockerignore`, compose files, CI, Docker scripts or git history |
|  | See another model's output or remember another run |

## What the run records show (all 30 sessions)

| Check | Result |
|---|---|
| Sessions answered by the pinned model | 30/30 |
| Sessions that ended normally | 30/30 |
| Tools available at session start | Glob, Grep, Read, Write in all 30; no MCP servers |
| Tool calls in total | 784 |
| File reads or writes outside the workspace | 0 |
| Searches rooted outside the workspace | 0 |
| Existing files modified or deleted | 0 |
| Container files present before the model wrote its own | 0 |
| Attempts to call a tool that was not offered | 4 |

## The four rejected tool attempts

The CLI answered each with "No such tool available". None had any effect.

| Repository | Model | Tool | What it tried to do |
|---|---|---|---|
| zebbern/claude-code-discord | Haiku 5.5 | Bash | `curl` the npm registry to look up a package version |
| zhravan/github-readme-quotes | Haiku 5.5 | Edit | Edit the Dockerfile it had just written |
| coolstartnow/isms-builder | Sonnet 5.5 | Bash | List the workspace directory (`ls -a`) |
| chelunfu/qiluo_admin | Haiku 5.5 | Bash | List the workspace directory (`ls -la`) |

## What was hidden, per repository

| Repository | Paths deleted | Doc files trimmed | Doc lines removed | Code files still mentioning Docker | Mentions left |
|---|---|---|---|---|---|
| rdborg/Mediarium | 11 | 56 | 717 | 119 | 1465 |
| zebbern/claude-code-discord | 5 | 5 | 93 | 9 | 46 |
| zqbxdev/webchat2api | 8 | 3 | 216 | 2 | 4 |
| Climate-Vision/ClimateVision | 7 | 7 | 14 | 0 | 0 |
| zhravan/github-readme-quotes | 6 | 1 | 10 | 1 | 6 |
| coolstartnow/isms-builder | 7 | 19 | 303 | 22 | 96 |
| pelican/wings | 5 | 2 | 66 | 41 | 419 |
| lissy93/who-dat | 3 | 0 | 0 | 4 | 13 |
| leonovk/wg-rest-api | 4 | 1 | 38 | 0 | 0 |
| chelunfu/qiluo_admin | 4 | 2 | 2 | 0 | 0 |

Source code was never edited, so projects that are themselves about Docker (Mediarium, wings) keep many mentions.

## Hints that got through

Found by checking the generated files against what was hidden:

- **rdborg/Mediarium:** Go source files name `docker/entrypoint.sh`, the path of the hidden entrypoint script. Opus and Haiku wrote their own script at that path.
- **zqbxdev/webchat2api:** one documentation line names `scripts/entrypoint.sh` and the start command. It was not removed because it does not contain the word "docker". Haiku wrote its script at that path.
- **pelican/wings:** Go code checks for a "distroless" system, which reveals the kind of base image the project expects. Only Opus used it.

None of these exposes the original Dockerfile's text, but they show that "code only" still carries deployment knowledge.

## Separate from isolation: training data

All ten repositories are public. A model may have seen an earlier version of a Dockerfile during training. Repositories were limited to 15–400 stars to make that less likely, but it cannot be ruled out or measured here.

[Back to the index](README.md)
