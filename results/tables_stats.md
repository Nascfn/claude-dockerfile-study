
### T14. Paired tests across repositories

| Comparison | Metric | Pairs | A lower / B lower / tie | Sign test p | Wilcoxon signed-rank p |
|---|---|---|---|---|---|
| Opus 5.5 (A) vs Original (B) | static score | 10 | 8 / 0 / 2 | 0.008 | 0.008 |
| Sonnet 5.5 (A) vs Original (B) | static score | 10 | 9 / 0 / 1 | 0.004 | 0.004 |
| Haiku 5.5 (A) vs Original (B) | static score | 10 | 10 / 0 / 0 | 0.002 | 0.002 |
| Opus 5.5 (A) vs Original (B) | Critical+High CVEs | 10 | 4 / 4 / 2 | 1.000 | 0.641 |
| Sonnet 5.5 (A) vs Original (B) | Critical+High CVEs | 10 | 4 / 4 / 2 | 1.000 | 1.000 |
| Haiku 5.5 (A) vs Original (B) | Critical+High CVEs | 9 | 2 / 6 / 1 | 0.289 | 0.523 |
| Opus 5.5 (A) vs Sonnet 5.5 (B) | static score | 10 | 2 / 3 / 5 | 1.000 | 1.000 |
| Opus 5.5 (A) vs Haiku 5.5 (B) | static score | 10 | 0 / 3 / 7 | 0.250 | 0.250 |
| Sonnet 5.5 (A) vs Haiku 5.5 (B) | static score | 10 | 1 / 4 / 5 | 0.375 | 0.125 |
| Opus 5.5 (A) vs Sonnet 5.5 (B) | Critical+High CVEs | 10 | 2 / 2 / 6 | 1.000 | 1.000 |
| Opus 5.5 (A) vs Haiku 5.5 (B) | Critical+High CVEs | 9 | 4 / 1 / 4 | 0.375 | 0.312 |
| Sonnet 5.5 (A) vs Haiku 5.5 (B) | Critical+High CVEs | 9 | 4 / 2 / 3 | 0.688 | 0.562 |
