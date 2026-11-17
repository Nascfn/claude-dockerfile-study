# Fact sheets

Short, single-topic pages about the experiment. Every number is computed from
the files in `data/` and `results/` by `scripts/13_fact_sheets.py`. The full
write-up, with all tables and the limitations, is [`FINDINGS.md`](../../FINDINGS.md).

| Page | What it answers |
|---|---|
| [At a glance](01-at-a-glance.md) | What are the key numbers? |
| [How the ten repositories were chosen](02-selection-funnel.md) | What was searched, filtered, ranked and skipped? |
| [The ten repositories, one by one](03-repositories.md) | What did each model do to each project? |
| [How the three models behaved](04-model-behaviour.md) | Effort, tool use, cost, writing habits, agreement |
| [Which problems were fixed and which were introduced](05-rules-fixed-and-introduced.md) | Rule-by-rule changes |
| [Base images and vulnerability counts](06-base-images-and-cves.md) | Why did lint scores improve but CVEs not? |
| [What the models could see, and the evidence](07-isolation-and-audit.md) | Isolation rules, audit, leaked hints |
| [Environment, tooling and reruns](08-environment-and-tooling.md) | Versions, sandbox workarounds, what was rerun |
| [Notable cases](09-notable-cases.md) | Individual stories worth a sentence in the report |
