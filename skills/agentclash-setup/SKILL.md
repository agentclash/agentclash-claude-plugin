---
name: agentclash-setup
description: Use when AgentClash is newly installed, the user asks how to start or connect it, or local target, dependency, operating-system, or host-access requirements are unclear.
---

# Start with available capabilities

Reach one supported case and a concrete next action. Compilation, validation and supplied-report inspection require no AgentClash account or provider keys.

In ChatGPT and claude.ai without local project access, start with `get_eval_capabilities`. Use only the packaged MCP tools for supported compilation, validation, or report comparison. Tell the user their agent runs in their own project, and use the manual continuation below.

1. Identify this host's actual shell, filesystem, OS, project access and execution authorization. A web chat or cloud shell does not imply access to the user's laptop. Use the packaged `agentclash` connection once; do not create a second connection. Call `get_eval_capabilities` before claiming workload, dependency or OS support. If unavailable, label support unverified and request its response or supply a manual continuation.
2. Read the returned target, template, SDK installation and runner contracts. The captured pilot supports only a Python callable with injected refund tools. Linux and macOS are supported; native Windows is blocked (use WSL/Linux). The service can still report `macos: pending_native_ci`. That field is older than the plugin's native macOS evidence, so do not send a Mac user to Linux or Docker for this pilot. On macOS, check hashes with `shasum -a 256 --check -` and keep result paths out of `/tmp` (a symlink). WSL does not add retrieval, judges or framework support. For unsupported work, name the missing integration and review a sanitized case manually with `$agentclash-improve-agent`.
3. Select the available route:
   - **Actual user's target execution:** authorized project, importable callable, supported OS, exact validated bundle and compatible dependencies are available. Use `$agentclash-run-evals`; keep credentials local and bind consequential actions to fixture tools. Only observed execution and inspected reports establish a result.
   - **Demonstration execution:** an explicitly identified sample callable AND compatible bundle actually exist. Label all results sample-only. Capabilities' `example_suite` is a suite spec, not a sample callable or runnable bundle. The generated adapter has no default target. Without a real sample, name the missing callable and compile/validate the supplied supported example spec only.
   - **Structural validation:** compile supported supplied cases with `compile_regression_suite`, then validate exact returned files with `validate_regression_suite`. Keep `evaluation_status=not_run`. Reading instructions or compiling cannot produce a report.
   - **Manual continuation:** no shell/project, missing dependency or unsupported runtime. Give exact next local steps using returned installation/runner commands, relative file paths, digests, manifest and target contract. A missing dependency installation is a preparation step, not execution. Missing target: request the importable `module:callable` and project/revision; offer supported structural validation meanwhile.
4. For the pilot, use its hash-pinned 0.2.0a1 wheel and direct Python runner. Verify integrity before installation. Public SDK 0.1.0 and npm 2.3.2 smoke execution are different contracts; do not substitute ordinary PyPI/npm installation. Keep the SDK's no-default-telemetry behavior; provider calls occur only through authorized target execution.
5. End with **state**, **evidence**, **missing pieces**, and **next action**. For execution, inspect exit status, fresh JSON/JUnit, suite/fixture digests, target revision, case/check coverage and actual-call evidence. Missing/skipped checks, zero tests, stale reports and import errors are incomplete, never a pass. Use `$agentclash-compare-results` only for deliberately supplied reports.
