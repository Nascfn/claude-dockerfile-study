# Notable cases

Individual things that happened and are worth a sentence in the report. Each was checked against the generated files.

## Opus read a base-image requirement out of Go code

pelican/wings checks `/etc/os-release` for `ID="distroless"` in two Go files. Opus kept a distroless base and added a step that writes that file, exactly what the hidden original does. Sonnet and Haiku chose other bases and skipped it. Opus's static score equals the original's (11); the other two score 6. Here the higher-scoring file is probably the more correct one.

## One model matched a human's size optimisation; two did not

ClimateVision's authors install CPU-only PyTorch and say why in a comment. Opus made the same choice without being told (4.7 GB against the original's 6.9 GB). Sonnet and Haiku installed the default wheels, which bundle GPU libraries: 12.2 GB for Sonnet, and too large to export for Haiku.

## A model tried to look something up online

In zebbern/claude-code-discord, Haiku tried to run `curl` against the npm registry to check a package version. No shell was offered, so the call was rejected and it carried on from the code alone.

## Staying root was argued, not forgotten

Haiku wrote its reasons into the Dockerfiles: Wings "runs as root by design: it needs the Docker socket"; wg-rest-api "runs as root because it must create and configure the wg0 interface"; webchat2api binds port 83, "below 1024". All three models made the same root or non-root call in every repository.

## The largest single improvement

zhravan/github-readme-quotes: the original image is 2,487 MB, runs as root and carries 10,450 CVEs. All three models produced a non-root image under 400 MB with fewer than 300 CVEs.

## The models disagreed with a human about a port, and agreed with each other

The original github-readme-quotes Dockerfile exposes ports 3000 and 3004. All three models expose 3002, the default in `src/app.js`.

## A third-party registry mirror was dropped

chelunfu/qiluo_admin pulls its base images through `docker.1ms.run`. With that hidden, all three models used the official images, which removes a dependency on an unofficial mirror. They also moved the runtime from Alpine to Debian, which took Critical+High CVEs from 0 to 38.

## Secret-looking build arguments were kept

Mediarium's original passes four API keys as build arguments. All three models kept all four, because the Go build embeds them. Hadolint flags this in every version.

## The same setting, very different amounts of thinking

At `--effort high`, Sonnet used between 153 and 2,867 thinking tokens per run, Opus between 530 and 15,252, and Haiku between 3,923 and 84,501. The single most expensive Haiku run (Mediarium, 428 seconds) cost about as much as Sonnet's run on the same repository.

## Stripping hints is harder than it looks

Three of the rules written to hide Docker hints were wrong on first use: one deleted a front-end folder called `charts`, one deleted a Go package called `docker`, and trimming Docker lines from documentation broke a project that compiles its docs into the application. And two script paths still leaked: one through source code and one through an overlooked documentation line.

[Back to the index](README.md)
