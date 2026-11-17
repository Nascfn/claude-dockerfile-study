# How the ten repositories were chosen

From 545 search results to 10 studied repositories, with the counts at each step.

## Search queries

Every query also carried `stars:15..400 pushed:>2025-11-17 archived:false fork:false`. Three result pages (up to 30 repositories) were taken per query, in GitHub's default "best match" order. A repository returned by two queries is counted under the first.

| Language group | Query | New repositories | With a root Dockerfile |
|---|---|---|---|
| python | `topic:fastapi language:Python` | 30 | 13 |
| python | `topic:flask language:Python` | 28 | 8 |
| python | `topic:django language:Python` | 28 | 8 |
| python | `topic:telegram-bot language:Python` | 30 | 18 |
| node | `topic:express language:TypeScript` | 30 | 10 |
| node | `topic:nestjs language:TypeScript` | 27 | 7 |
| node | `topic:express language:JavaScript` | 30 | 4 |
| node | `topic:discord-bot language:TypeScript` | 28 | 15 |
| go | `topic:gin language:Go` | 30 | 8 |
| go | `topic:self-hosted language:Go` | 30 | 13 |
| go | `topic:rest-api language:Go` | 27 | 15 |
| java | `topic:spring-boot language:Java` | 30 | 3 |
| java | `topic:spring-boot language:Kotlin` | 30 | 5 |
| ruby | `topic:rails language:Ruby` | 30 | 5 |
| ruby | `topic:sinatra language:Ruby` | 22 | 4 |
| php | `topic:laravel language:PHP` | 30 | 2 |
| php | `topic:symfony language:PHP` | 27 | 1 |
| rust | `topic:axum language:Rust` | 30 | 7 |
| rust | `topic:actix-web language:Rust` | 28 | 6 |
| **Total** |  | 545 | 152 |

## Filling the pool

Candidates were examined in search order until each language group reached its quota (python 12, node 12, go 8, java 6, ruby 4, php 4, rust 4). 391 candidates were examined.

| Outcome | Repositories |
|---|---|
| Kept in the pool | 43 |
| No Dockerfile at the repository root | 302 |
| More than one Dockerfile | 34 |
| Base image below the runtime floor | 9 |
| GPU base image | 2 |
| Uses git submodules | 1 |

## The pool by language

| Group | Repositories | Mean static score | Worst score |
|---|---|---|---|
| node | 12 | 7.2 | 17 |
| python | 10 | 8 | 16 |
| go | 8 | 8.8 | 19 |
| rust | 4 | 10.5 | 13 |
| java | 4 | 3.5 | 4 |
| ruby | 3 | 6.3 | 11 |
| php | 2 | 12 | 13 |

Java, Ruby and PHP did not fill their quotas because few search results had a single root Dockerfile. Python lost two repositories and Java one to filters added after the first pass (GPU base images, Java 8).

## How common each problem is across the 43 pool Dockerfiles

This is the unselected sample, so it says something about ordinary recent projects, not just the worst ten.

| Rule | What it flags | Dockerfiles | Share |
|---|---|---|---|
| DS-0026 | No HEALTHCHECK | 29 | 67% |
| DS-0002 | Image runs as root | 24 | 56% |
| DL3066 | Non-numeric user id | 17 | 40% |
| DL3018 | Unpinned `apk add` packages | 12 | 28% |
| DL3025 | CMD/ENTRYPOINT not in JSON form | 12 | 28% |
| DL3059 | Consecutive RUN instructions | 12 | 28% |
| DL3008 | Unpinned `apt-get install` packages | 11 | 26% |
| DS-0001 | `latest` tag used | 7 | 16% |
| DL3007 | `latest` tag used | 5 | 12% |
| DL3013 | Unpinned `pip install` packages | 4 | 9% |
| DL3003 | `cd` instead of WORKDIR | 3 | 7% |
| DS-0013 | `RUN cd …` instead of WORKDIR | 3 | 7% |

## The top of the ranking

Selection walked this list from the top, kept a repository if its original Dockerfile built, and allowed at most three per language group.

| Rank | Repository | Group | Score | Outcome |
|---|---|---|---|---|
| 1 | rdborg/Mediarium | go | 19 | **Selected** |
| 2 | zebbern/claude-code-discord | node | 17 | **Selected** |
| 3 | zqbxdev/webchat2api | python | 16 | **Selected** |
| 4 | Climate-Vision/ClimateVision | python | 14 | **Selected** |
| 5 | imdhemy/laravel-in-app-purchases | php | 13 | Skipped: `pecl install` needs plain HTTP, which the sandbox does not carry |
| 6 | imtaqin/waxum | rust | 13 | Skipped: build script downloads from github.com, blocked in the sandbox |
| 7 | zhravan/github-readme-quotes | node | 12 | **Selected** |
| 8 | physhik/ecg-mit-bih | python | 11 | Skipped: Dockerfile copies a dataset folder that is not in the repository |
| 9 | coolstartnow/isms-builder | node | 11 | **Selected** |
| 10 | pelican/wings | go | 11 | **Selected** |
| 11 | lissy93/who-dat | go | 11 | **Selected** |
| 12 | leonovk/wg-rest-api | ruby | 11 | **Selected** |
| 13 | MGeurts/genealogy | php | 11 | Skipped: Composer downloads from github.com, blocked in the sandbox |
| 14 | chelunfu/qiluo_admin | rust | 11 | **Selected** |

Scores in the pool run from 1 to 19 with a median of 7. The ten selected originals score 11–19.

[Back to the index](README.md)
