
### T1. Weighted static insecurity score per repository (lower is better)

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | 19 | 11 | 11 | 11 |
| zebbern/claude-code-discord | 17 | 4 | 8 | 4 |
| zqbxdev/webchat2api | 16 | 11 | 10 | 11 |
| Climate-Vision/ClimateVision | 14 | 11 | 9 | 7 |
| zhravan/github-readme-quotes | 12 | 2 | 2 | 2 |
| coolstartnow/isms-builder | 11 | 5 | 5 | 5 |
| pelican/wings | 11 | 11 | 6 | 6 |
| lissy93/who-dat | 11 | 2 | 5 | 2 |
| leonovk/wg-rest-api | 11 | 11 | 11 | 9 |
| chelunfu/qiluo_admin | 11 | 6 | 6 | 6 |
| **Mean** | 13.3 | 7.4 | 7.3 | 6.3 |

### T2. Hadolint findings per repository

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | 9 | 4 | 4 | 4 |
| zebbern/claude-code-discord | 8 | 2 | 5 | 2 |
| zqbxdev/webchat2api | 5 | 3 | 2 | 3 |
| Climate-Vision/ClimateVision | 6 | 6 | 5 | 4 |
| zhravan/github-readme-quotes | 3 | 1 | 1 | 1 |
| coolstartnow/isms-builder | 2 | 3 | 3 | 3 |
| pelican/wings | 3 | 3 | 1 | 1 |
| lissy93/who-dat | 5 | 1 | 3 | 1 |
| leonovk/wg-rest-api | 5 | 4 | 4 | 3 |
| chelunfu/qiluo_admin | 5 | 3 | 3 | 3 |
| **Mean** | 5.1 | 3 | 3.1 | 2.5 |

### T3. Trivy misconfiguration findings per repository

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | 1 | 1 | 1 | 1 |
| zebbern/claude-code-discord | 2 | 1 | 1 | 1 |
| zqbxdev/webchat2api | 3 | 2 | 3 | 2 |
| Climate-Vision/ClimateVision | 2 | 0 | 0 | 0 |
| zhravan/github-readme-quotes | 3 | 1 | 1 | 1 |
| coolstartnow/isms-builder | 2 | 0 | 0 | 0 |
| pelican/wings | 3 | 3 | 2 | 2 |
| lissy93/who-dat | 1 | 1 | 0 | 1 |
| leonovk/wg-rest-api | 2 | 1 | 1 | 1 |
| chelunfu/qiluo_admin | 2 | 1 | 1 | 1 |
| **Mean** | 2.1 | 1.1 | 1 | 1 |

### T4. Does the image build?

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | yes | yes | yes | yes |
| zebbern/claude-code-discord | yes | yes | yes | yes |
| zqbxdev/webchat2api | yes | yes | yes | yes |
| Climate-Vision/ClimateVision | yes | yes | yes | yes\* |
| zhravan/github-readme-quotes | yes | yes | yes | yes |
| coolstartnow/isms-builder | yes | yes | yes | yes |
| pelican/wings | yes | yes | yes | yes |
| lissy93/who-dat | yes | yes | yes | yes |
| leonovk/wg-rest-api | yes | yes | yes | yes |
| chelunfu/qiluo_admin | yes | yes | yes | yes |
| **All build steps succeed** | 10/10 | 10/10 | 10/10 | 10/10 |
| **Image exported and scanned** | 10/10 | 10/10 | 10/10 | 9/10 |

\* Every Dockerfile step completed, but the finished image was too large to export inside the build sandbox (disk limit), so it has no image scan.

### T5. Critical + High CVEs in the built image (Trivy image scan)

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | 1 | 0 | 0 | 105 |
| zebbern/claude-code-discord | 132 | 232 | 150 | 140 |
| zqbxdev/webchat2api | 785 | 585 | 781 | 709 |
| Climate-Vision/ClimateVision | 364 | 64 | 65 | – |
| zhravan/github-readme-quotes | 2008 | 45 | 45 | 64 |
| coolstartnow/isms-builder | 6 | 48 | 48 | 48 |
| pelican/wings | 2 | 2 | 2 | 40 |
| lissy93/who-dat | 0 | 0 | 0 | 0 |
| leonovk/wg-rest-api | 13 | 135 | 127 | 135 |
| chelunfu/qiluo_admin | 0 | 38 | 38 | 38 |
| **Mean** | 331.1 | 114.9 | 125.6 | 142.11 |

A dash marks the one image that could not be exported and scanned (see T4).

### T5b. Critical + High CVEs that have a fix available

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | 1 | 0 | 0 | 0 |
| zebbern/claude-code-discord | 11 | 63 | 27 | 27 |
| zqbxdev/webchat2api | 157 | 81 | 157 | 81 |
| Climate-Vision/ClimateVision | 2 | 2 | 3 | – |
| zhravan/github-readme-quotes | 1493 | 45 | 45 | 26 |
| coolstartnow/isms-builder | 6 | 10 | 10 | 10 |
| pelican/wings | 2 | 2 | 2 | 2 |
| lissy93/who-dat | 0 | 0 | 0 | 0 |
| leonovk/wg-rest-api | 13 | 32 | 25 | 32 |
| chelunfu/qiluo_admin | 0 | 0 | 0 | 0 |
| **Mean** | 168.5 | 23.5 | 26.9 | 19.78 |

### T6. Total CVEs in the built image

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | 3 | 1 | 1 | 432 |
| zebbern/claude-code-discord | 501 | 675 | 567 | 491 |
| zqbxdev/webchat2api | 2550 | 1469 | 1822 | 1790 |
| Climate-Vision/ClimateVision | 2895 | 290 | 297 | – |
| zhravan/github-readme-quotes | 10450 | 131 | 131 | 287 |
| coolstartnow/isms-builder | 20 | 249 | 249 | 249 |
| pelican/wings | 9 | 13 | 10 | 247 |
| lissy93/who-dat | 1 | 4 | 1 | 4 |
| leonovk/wg-rest-api | 58 | 457 | 424 | 456 |
| chelunfu/qiluo_admin | 1 | 238 | 238 | 238 |
| **Mean** | 1648.8 | 352.7 | 374 | 466 |

### T6b. CVEs in operating-system packages (decided by the base image and installed packages)

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | 1 | 1 | 1 | 432 |
| zebbern/claude-code-discord | 475 | 626 | 495 | 419 |
| zqbxdev/webchat2api | 2322 | 1351 | 1594 | 1672 |
| Climate-Vision/ClimateVision | 2885 | 287 | 287 | – |
| zhravan/github-readme-quotes | 10202 | 54 | 54 | 226 |
| coolstartnow/isms-builder | 1 | 226 | 226 | 226 |
| pelican/wings | 0 | 4 | 1 | 238 |
| lissy93/who-dat | 1 | 4 | 1 | 4 |
| leonovk/wg-rest-api | 23 | 422 | 420 | 421 |
| chelunfu/qiluo_admin | 1 | 238 | 238 | 238 |
| **Mean** | 1591.1 | 321.3 | 331.7 | 430.67 |

### T6c. CVEs in application dependencies (decided mostly by the project lockfile)

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | 2 | 0 | 0 | 0 |
| zebbern/claude-code-discord | 26 | 49 | 72 | 72 |
| zqbxdev/webchat2api | 228 | 118 | 228 | 118 |
| Climate-Vision/ClimateVision | 10 | 3 | 10 | – |
| zhravan/github-readme-quotes | 248 | 77 | 77 | 61 |
| coolstartnow/isms-builder | 19 | 23 | 23 | 23 |
| pelican/wings | 9 | 9 | 9 | 9 |
| lissy93/who-dat | 0 | 0 | 0 | 0 |
| leonovk/wg-rest-api | 35 | 35 | 4 | 35 |
| chelunfu/qiluo_admin | 0 | 0 | 0 | 0 |
| **Mean** | 57.7 | 31.4 | 42.3 | 35.33 |

### T7. Image size (MB)

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | 125 | 124 | 125 | 248 |
| zebbern/claude-code-discord | 638 | 817 | 1393 | 821 |
| zqbxdev/webchat2api | 2351 | 1625 | 2153 | 1936 |
| Climate-Vision/ClimateVision | 6852 | 4693 | 12150 | – |
| zhravan/github-readme-quotes | 2487 | 225 | 229 | 362 |
| coolstartnow/isms-builder | 598 | 525 | 723 | 521 |
| pelican/wings | 63 | 63 | 81 | 184 |
| lissy93/who-dat | 27 | 18 | 28 | 18 |
| leonovk/wg-rest-api | 636 | 326 | 294 | 334 |
| chelunfu/qiluo_admin | 67 | 260 | 193 | 192 |
| **Mean** | 1384.4 | 867.6 | 1736.9 | 512.89 |

### T8. User the container runs as

| Repository | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|
| rdborg/Mediarium | root | root | root | root |
| zebbern/claude-code-discord | non-root | non-root | non-root | non-root |
| zqbxdev/webchat2api | root | root | root | root |
| Climate-Vision/ClimateVision | root | non-root | non-root | – |
| zhravan/github-readme-quotes | root | non-root | non-root | non-root |
| coolstartnow/isms-builder | root | non-root | non-root | non-root |
| pelican/wings | root | root | root | root |
| lissy93/who-dat | non-root | non-root | non-root | non-root |
| leonovk/wg-rest-api | root | root | root | root |
| chelunfu/qiluo_admin | non-root | non-root | non-root | non-root |

### T9. Summary by Dockerfile author

| Author | Mean static score | Mean Hadolint | Mean Trivy config | Mean score reduction | Better / worse / same vs original | All build steps succeed | Non-root (of scanned images) | Median Crit+High CVEs | Median total CVEs | Crit+High CVEs: fewer / more / same vs original | Median size (MB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Original (human) | 13.3 | 5.1 | 2.1 | – | – | 10/10 | 3/10 | 9.5 | 39 | – | 617 |
| Opus 5.5 | 7.4 | 3 | 1.1 | 43.64% | 8/0/2 | 10/10 | 6/10 | 46.5 | 243.5 | 4/4/2 | 293 |
| Sonnet 5.5 | 7.3 | 3.1 | 1 | 45.16% | 9/0/1 | 10/10 | 6/10 | 46.5 | 243.5 | 4/4/2 | 261.5 |
| Haiku 5.5 | 6.3 | 2.5 | 1 | 52.86% | 10/0/0 | 10/10 | 5/9 | 64 | 287 | 2/6/1 | 334 |

### T10. Number of Dockerfiles (of 10) that trigger each rule

| Rule | What it flags | Original (human) | Opus 5.5 | Sonnet 5.5 | Haiku 5.5 |
|---|---|---|---|---|---|
| DS-0002 | Image user should not be 'root' | 7 | 4 | 4 | 4 |
| DL3018 | Pin versions in apk add. Instead of `apk add <package>` use `apk add <package>=<version>` | 6 | 2 | 3 | 0 |
| DL3059 | Multiple consecutive `RUN` instructions. Consider consolidation. | 6 | 1 | 0 | 0 |
| DS-0026 | No HEALTHCHECK defined | 6 | 5 | 5 | 5 |
| DL3025 | Use arguments JSON notation for CMD and ENTRYPOINT arguments | 5 | 4 | 5 | 4 |
| DL3007 | Using latest is prone to errors if the image will ever update. Pin the version explicitly  | 4 | 1 | 0 | 0 |
| DL3008 | Pin versions in apt get install. Instead of `apt-get install <package>` use `apt-get insta | 4 | 6 | 6 | 8 |
| DL3066 | Non-numeric user-id may not be resolvable by host system | 4 | 6 | 6 | 6 |
| DS-0001 | ':latest' tag used | 4 | 1 | 0 | 0 |
| DL3003 | Use WORKDIR to switch to a directory | 3 | 1 | 1 | 1 |
| DS-0013 | 'RUN cd ...' to change directory | 3 | 1 | 1 | 1 |
| DL3013 | Pin versions in pip. Instead of `pip install <package>` use `pip install <package>==<versi | 2 | 1 | 0 | 1 |
| DL3064 | Potentially sensitive data should not be used in the `ARG` or `ENV` commands | 2 | 2 | 2 | 1 |
| DL3002 | Last USER should not be root | 1 | 0 | 0 | 0 |
| DL3016 | Pin versions in npm. Instead of `npm install <package>` use `npm install <package>@<versio | 1 | 0 | 1 | 0 |
| DL3046 | `useradd` without flag `-l` and high UID will result in excessively large Image. | 1 | 0 | 0 | 0 |
| DL3065 | Setting `FROM --platform` to predefined `$TARGETPLATFORM` in is redundant as this is the d | 1 | 0 | 0 | 0 |
| DL4006 | Set the SHELL option -o pipefail before RUN with a pipe in it. If you are using /bin/sh in | 1 | 0 | 0 | 0 |
| DS-0031 | Secrets passed via `build-args` or envs or copied secret files | 1 | 0 | 0 | 0 |
| SC2164 | Use 'cd ... || exit' or 'cd ... || return' in case cd fails. | 1 | 0 | 0 | 0 |
| DL4005 | Use SHELL to change the default shell | 0 | 1 | 1 | 1 |

### T11. Generation effort per model

| Model | Model ID reported | Mean seconds | Mean turns | Mean tool calls | Mean output tokens | Total cost (USD, as reported by the CLI) | Existing files modified | Reads outside workspace | Attempts to call a tool that was not offered (all rejected) |
|---|---|---|---|---|---|---|---|---|---|
| Opus 5.5 | claude-opus-5-5 | 104.86 | 28.8 | 27.8 | 10823.6 | 6.43 | 0 | 0 | 0 |
| Sonnet 5.5 | claude-sonnet-5-5 | 40.17 | 21.2 | 20.2 | 5476.3 | 1.67 | 0 | 0 | 1 |
| Haiku 5.5 | claude-haiku-5-5 | 134.6 | 31.4 | 30.4 | 30515.5 | 0.65 | 0 | 0 | 3 |
