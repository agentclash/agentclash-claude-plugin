# AgentClash for Claude

Turn a support agent failure into a regression test. AgentClash helps you define the expected behavior, compile a suite, check its files, and compare reports from your own runs. The supported target is a Python callable with injected refund fixtures. You can design and validate a suite without an AgentClash account.

## Install

In Claude Code 2.1.292 or later, run:

```sh
claude plugin install agentclash --marketplace agentclash/agentclash-claude-plugin
```

On earlier versions that support marketplaces, add the marketplace first:

```sh
claude plugin marketplace add agentclash/agentclash-claude-plugin
claude plugin install agentclash@agentclash
```

Start a new session and try: “Help me turn a duplicate refund into a regression test.” Use fictional transaction IDs and describe which payment and subscription the test must preserve.

## How it works

The plugin includes five skills for setup, agent improvement, failure regression, local execution, and report comparison. Its four tools use the anonymous [AgentClash MCP service](https://mcp.agentclash.dev/mcp). The service processes the suite, bundle, or report you deliberately provide without storing it. Use sanitized data. Keep provider keys and real customer data in your own environment.

Compilation and validation prepare exact tests for local execution. Follow the run skill to verify the files, install the pinned Python wheel, bind a callable to the fixture tools, and inspect JSON and JUnit reports. The bundled demo can run two scripted sample targets with in-memory fixtures. It downloads the pinned wheel only if you follow the demo setup commands.

On claude.ai and Cowork, add or connect the remote MCP from the plugin's **Connectors** tab if prompted. If the host lacks access to your project, the run skill gives you commands to run locally.

Save is optional. The run and compare skills check the public import configuration without sending a report. To save a supported complete report, sign in on the AgentClash website and choose the file yourself. Review the file for sensitive data before import.

## Supported platforms

The pinned refund pilot supports Linux and macOS. On Windows, run the pilot in WSL. On November 11, 2026, the scripted demo ran natively on Apple silicon with macOS 26.7.1, Python 3.12.13, pytest 8.4.2, and the verified `agentclash-evals` 0.2.0a1 wheel. The faulty example failed the two expected checks. The corrected example passed all ten checks. This fixture run used no model inference and covers that tested macOS setup.

See the [privacy policy](https://mcp.agentclash.dev/privacy) and [support page](https://mcp.agentclash.dev/support).
