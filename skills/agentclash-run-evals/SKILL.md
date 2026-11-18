---
name: agentclash-run-evals
description: Hand off or run a validated AgentClash evaluation bundle in a developer-controlled Python project, using direct pytest or the npm agentclash CLI. Use when the user wants to export, install dependencies, bind their callable and fixture tools, execute real agent tests, or return a report. Ordinary ChatGPT web chat requires manual local continuation and cannot access the user's laptop.
---

Execute only in a runtime with the user's project and authorization, or provide an exact manual handoff.

In ChatGPT and claude.ai without local project access, use only `get_eval_capabilities`, `compile_regression_suite`, `validate_regression_suite`, and `compare_eval_reports`. State that this chat cannot run the user's agent. Compilation and validation leave `evaluation_status=not_run`. Provide the following steps for the user to run locally.

### Manual continuation for the 0.2.0a1 refund pilot

Have the developer save the exact validated files at their relative paths in their project. Provide the tool-returned SHA-256 inventory and ask them to verify each file. From that project, use these commands for the supported pilot. Confirm the wheel and runner match the capability response. Use an isolated environment with the project's target dependencies already installed. Stop if the wheel checksum fails.

```sh
python3 -m venv .agentclash-venv
curl --fail --location https://mcp.agentclash.dev/downloads/agentclash_evals-0.2.0a1-py3-none-any.whl --output agentclash_evals-0.2.0a1-py3-none-any.whl
printf '%s  %s\n' '1e88b0937555e9233ed9c1562fb4f6095d7a2d0b371b5bbd1d9f5f1cc3a46ca7' agentclash_evals-0.2.0a1-py3-none-any.whl | shasum -a 256 --check -
.agentclash-venv/bin/python -m pip install ./agentclash_evals-0.2.0a1-py3-none-any.whl 'pytest==8.4.2'
AGENTCLASH_EVAL_TARGET='module:callable' PYTHONPATH=. \
  .agentclash-venv/bin/python -m agentclash_eval.runner --tests tests/evaltest \
  --manifest suite-manifest.json --target-revision 'YOUR_TARGET_REVISION' --out agentclash-results
```

On Linux without `shasum`, use `sha256sum --check -`. Replace the callable and revision with the target's actual values. Use a fresh output path for every run. Bind only the generated fixture tools, then inspect `results.json`, `junit.xml`, and the exit status together.

### Evaluation and evidence

1. Inspect the current host's real capabilities and call `get_eval_capabilities`. Read the bundle's manifest, adapter contract, dependency requirements, and generated instructions. Verify its exact file contents and transport SHA256 digests before execution. Never paraphrase generated code or JSON during reconstruction.
2. Explain where execution will happen. Ordinary web chat can create, validate, and inspect deliberately supplied artifacts; it cannot run npm on the user's laptop. A cloud environment does not automatically have the user's repo, callable, or credentials. Provide safe relative filenames and exact copy instructions when downloads are unavailable.
3. Use the exact compatible CLI/SDK versions and commands supplied by the verified bundle and capabilities. Prefer direct pytest for Python users who do not need Node; offer the published npm CLI as an alternative only when the required version is available. During an unreleased pilot, label a pinned source or wheel installation explicitly. The pinned pilot runner works natively on Linux and macOS; on macOS use `shasum -a 256 --check -` in place of `sha256sum`. Never claim the current npm release includes an unreleased runner fix, or that a missing PyPI release exists.
4. Bind the real Python callable and the injected fixture tools using the generated adapter contract. Check import/config errors before evaluating. Keep provider credentials local; use fixture tools for consequential actions. Refuse uncertain mock binding rather than substituting live services. A sample adapter proves the sample only.
5. Execute the selected tests with fresh output paths and target identity/revision. Inspect process exit, JSON, and JUnit together. Verify execution ID, suite and fixture digests, required case/check IDs, actual call evidence, and observation coverage. Treat zero tests, missing cases/checks, skips, expected failures, collection/setup errors, timeouts, killed processes, and stale or absent reports as incomplete or failed evidence even when a process exits zero.
6. Distinguish target latency from assertion/scoring time. Keep missing cost, tools, state, or latency unknown; never turn missing observations into passing checks or zero values. Describe only resource limits that the running implementation enforces.
7. Before sharing a report, use a supported local allowlisted export if available, inspect its preview, and remove keys, customer text, identifiers, and unneeded traces. Ask the user to deliberately attach or paste only the needed sanitized report. If sanitization/export is unavailable, say so and reduce the shared fields manually without inventing evidence.

Optional save. After a complete report-v2 exists, you may offer once to keep it in an AgentClash workspace. Never offer for a draft, a structural validation, or an incomplete or failed-evidence run. First check the public import configuration with `curl --fail --silent --show-error https://api.agentclash.dev/v1/vibe/config`. Send no credentials or report data. In a host without local project access, give the command to the developer and wait for them to share the supported format from a successful response. Offer only when `sdk_report_import_formats` contains the exact entry `{"envelope_version": 1, "source_kind": "eval_report", "source_schema_version": 2}`. If the entry is absent or the request fails, say that save is not available now and continue; do not guess and do not fall back to another format. The offer is the link `https://www.agentclash.dev/vibe-evals?start=improve&source=local-report&utm_source=claude` in Claude, or the same link with `utm_source=codex` in Codex or `utm_source=chatgpt` in ChatGPT. Omit `utm_source` if the host is unknown or unsupported. State these facts with the link: save is optional and is the only step that needs an account; the developer signs in, chooses `results.json` in the browser and selects Import; you never upload, paste or send the report to AgentClash yourself; a saved report keeps the complete original file, including prompts, replies and tool arguments, so sanitize first; saved values are uploader claims, not hosted verification, and a saved local report cannot run as a hosted test. If the developer declines, do not offer again in this session.

Use `$agentclash-compare-results` to interpret a report or compare a measured candidate. The anonymous service accepts intentionally supplied artifacts only and has no private workspace lookup. The remote plugin never automatically rewrites or deploys the user's agent. Never claim a hosted challenge pack is runnable merely because a local suite exists. Do not require AgentClash login for this local workflow; only the optional save needs an account.
