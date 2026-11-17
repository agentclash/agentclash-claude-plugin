"""Explicit Linux or macOS scripted-reference-demo. The user's real agent is unassessed."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import uuid
from xml.etree import ElementTree as ET

WHEEL = 'agentclash_evals-0.2.0a1-py3-none-any.whl'
WHEEL_SHA = '1e88b0937555e9233ed9c1562fb4f6095d7a2d0b371b5bbd1d9f5f1cc3a46ca7'
WHEEL_URL = 'https://mcp.agentclash.dev/downloads/' + WHEEL
RESOURCE_SHA = 'f4e79c933bcca522019f6447ddff0b5539c7961fdf18aa90feda3cc6d7e11515'
ASSETS = Path(__file__).absolute().parent.parent / 'assets/refund-demo'
IDENTITY = 'agentclash_demo:invoke'
CASE = 'DEMO-repeat-refund-01'
SUITE = 'DEMO-scripted-repeat-refund-v1'
SUITE_SHA = '374b4b4522e2f2596f7e94cf0dae7c2a17a41f48b5480ae553580d5ac8647611'
BUNDLE_FILES = {'suite.json', 'suite-manifest.json', 'adapter.py', 'README.md',
                '.agentclash/evaltest.yaml', 'tests/evaltest/test_refund.py'}
SUPPORTED_SYSTEMS = ('Linux', 'Darwin')


def preparation(system=None):
    """Exact preparation for this OS. macOS has shasum, not sha256sum, and /tmp is a symlink there."""
    system = system or platform.system()
    check = 'shasum -a 256 --check -' if system == 'Darwin' else 'sha256sum --check -'
    note = '# macOS: /tmp is a symlink; put results under your home directory.\n' if system == 'Darwin' else ''
    return f'''Use a fresh Linux or macOS virtual environment (Python 3.10+), then run this script with its Python:
python3 -m venv .demo-venv
curl --fail --location '{WHEEL_URL}' --output '{WHEEL}'
printf '%s  %s\\n' '{WHEEL_SHA}' '{WHEEL}' | {check}
# Continue only if the hash check succeeds:
.demo-venv/bin/python -m pip install './{WHEEL}' 'pytest==8.4.2'
{note}.demo-venv/bin/python /absolute/plugin/skills/agentclash-setup/scripts/refund_demo.py --run --out /absolute/fresh-results
'''


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def no_symlinks(path):
    path = Path(path).absolute()
    require('..' not in path.parts, 'Path traversal is forbidden')
    for part in [path, *path.parents]:
        require(not part.is_symlink(), f'Symlink forbidden: {part}')
    return path


def read_file(root, relative):
    rel = Path(relative)
    require(not rel.is_absolute() and '..' not in rel.parts, 'Unsafe resource path')
    path = no_symlinks(root / rel)
    require(path.is_file(), f'Missing regular file: {path}')
    return path.read_bytes()


def verify_assets(root=ASSETS):
    raw = read_file(root, 'resources.json')
    require(sha(raw) == RESOURCE_SHA, 'Resource inventory digest mismatch')
    inventory = json.loads(raw)
    actual = set()
    for path in root.rglob('*'):
        no_symlinks(path)
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
        else:
            require(path.is_dir(), 'Unexpected resource type')
    require(actual == set(inventory) | {'resources.json'}, 'Resource inventory mismatch')
    for path, digest in inventory.items():
        require(sha(read_file(root, path)) == digest, f'Resource digest mismatch: {path}')
    files = frozen_bundle(root)
    bundle = json.loads(files['suite-manifest.json'])
    require(set(bundle['files']) == BUNDLE_FILES - {'suite-manifest.json'}, 'Bundle inventory mismatch')
    require(bundle['suite_id'] == SUITE and bundle['suite_digest'] == SUITE_SHA
            and bundle['required_case_ids'] == [CASE], 'Frozen suite identity mismatch')
    for path, digest in bundle['files'].items():
        require(sha(files[path]) == digest, 'Bundle manifest digest mismatch')
    return inventory


def frozen_bundle(root):
    bundle = json.loads(read_file(root, 'bundle.json'))
    files = bundle['files']
    require(len(files) == 6 and {f['path'] for f in files} == BUNDLE_FILES, 'Bundle inventory mismatch')
    for item in files:
        require(sha(item['content'].encode()) == item['sha256'], 'Bundle transport digest mismatch')
    return {f['path']: f['content'].encode() for f in files}


def check_dependencies(root=ASSETS):
    require(sys.prefix != sys.base_prefix, 'An isolated virtual environment is required.\n' + preparation())
    config = Path(sys.prefix) / 'pyvenv.cfg'
    require(config.is_file() and 'include-system-site-packages = false' in config.read_text().lower(),
            'Virtual environment must exclude system site packages.\n' + preparation())
    try:
        sdk = metadata.distribution('agentclash-evals')
        pytest = metadata.distribution('pytest')
        require(sdk.version == '0.2.0a1' and pytest.version == '8.4.2', 'Pinned dependency versions required')
        for dist in (sdk, pytest):
            require(Path(dist.locate_file('')).resolve().is_relative_to(Path(sys.prefix).resolve()),
                    'Dependencies must be inside this virtual environment')
        direct = json.loads(sdk.read_text('direct_url.json') or '{}')
        require(direct.get('archive_info', {}).get('hashes', {}).get('sha256') == WHEEL_SHA,
                'SDK must be installed from the exact hash-verified wheel')
        expected = json.loads(read_file(root, 'sdk-files.json'))
        for path, digest in expected.items():
            installed = no_symlinks(sdk.locate_file(path))
            require(installed.is_file() and sha(installed.read_bytes()) == digest,
                    f'Installed SDK digest mismatch: {path}')
        installed_files = {str(p) for p in sdk.files or [] if str(p).startswith('agentclash_eval/') and str(p).endswith('.py')}
        require(installed_files == set(expected), 'Installed SDK source inventory mismatch')
    except (metadata.PackageNotFoundError, ValueError, OSError, KeyError) as exc:
        raise ValueError(f'Dependency preparation required: {exc}\n{preparation()}') from exc
    return {'python': platform.python_version(), 'platform': platform.platform(),
            'sdk': sdk.version, 'pytest': pytest.version, 'wheel_sha256': WHEEL_SHA,
            'sdk_source_sha256': expected}


def target_revision(root, variant):
    wrapper = read_file(root, f'targets/{variant}/agentclash_demo.py')
    return sha(wrapper + b'\0' + WHEEL_SHA.encode() + b'\0agentclash_eval.reference_targets')


def clean_environment(work):
    # Never inherit provider credentials, target bindings, Python/pytest config or HOME.
    return {'PATH': str(Path(sys.executable).parent) + ':/usr/bin:/bin', 'LANG': 'C.UTF-8',
            'PYTHONNOUSERSITE': '1', 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONSAFEPATH': '1',
            'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1', 'PYTEST_ADDOPTS': '--noconftest -p no:cacheprovider',
            'PYTHONPATH': str(work), 'AGENTCLASH_EVAL_TARGET': IDENTITY}


def check_report(report, junit, code, run_id, revision, faulty):
    """Check this fixed demo's complete evidence; not a general report evaluator."""
    expected_code = 1 if faulty else 0
    status = 'failed' if faulty else 'passed'
    require(code == expected_code == report['exit_code'], 'Runner/report exit disagreement')
    require(report['schema_version'] == 2 and report['run_id'] == report['report_id'] == run_id,
            'Wrong or stale report identity')
    require(report['suite_id'] == SUITE and report['suite_digest'] == SUITE_SHA, 'Wrong suite')
    require(report['target_identity'] == IDENTITY and report['target_revision'] == revision, 'Wrong target')
    require(report['runner'] == {'name': 'agentclash-evals', 'version': '0.2.0a1', 'language': 'python'}, 'Wrong runner')
    execution = report['execution']
    require(execution['status'] == 'completed' and execution['pytest_exit_code'] == expected_code
            and execution['required_case_ids'] == [CASE] and execution['missing_required_case_ids'] == []
            and execution['required_cases_complete'] is True, 'Incomplete execution')
    require(report['summary'] == {'total': 1, 'passed': int(not faulty), 'failed': int(faulty),
            'skipped': 0, 'errored': 0, 'incomplete': 0, 'metric_failures': 2 if faulty else 0}, 'Wrong coverage')
    require(len(report['cases']) == 1, 'Expected exactly one case')
    row = report['cases'][0]
    require(row['case']['case_id'] == CASE and row['case']['split'] == 'development'
            and row['status'] == status and row['target_invoked'] is True, 'Missing case invocation')
    require(row['observations'] == {'tool_calls': True, 'fixture_state': True, 'cost': False}
            and row['cost_usd'] is None, 'Missing observations or invented cost')
    expected = {'duplicate_refunds': 1, 'original_refunds': 0, 'subscription_active': True,
                'outcome': 'refunded', 'refund_amounts_correct': True, 'no_unexpected_refunds': True,
                'turn_1_outcome_truthful': True, 'turn_1_subscription_preserved': True,
                'turn_2_outcome_truthful': True, 'turn_2_subscription_preserved': True}
    checks = row['checks']
    require(len(checks) == len(expected) and {c['check_id'] for c in checks} == set(expected), 'Missing/duplicate checks')
    failed = {'duplicate_refunds', 'turn_2_outcome_truthful'} if faulty else set()
    for check in checks:
        key = check['check_id']
        actual = 2 if faulty and key == 'duplicate_refunds' else False if key in failed else expected[key]
        require(type(check['expected']) is type(expected[key]) and check['expected'] == expected[key]
                and type(check['actual']) is type(actual) and check['actual'] == actual
                and check['passed'] is (key not in failed), f'Unexpected check: {key}')
    evidence = row['evidence']
    require(len(evidence['turns']) == 2 and all(t['result']['outcome'] == 'refunded' for t in evidence['turns']), 'Missing two turns')
    require(len(evidence['ledger']) == (2 if faulty else 1)
            and all(r['charge_id'] == 'demo-duplicate-4207' and r['amount_cents'] == 4207 for r in evidence['ledger']), 'Wrong refund evidence')
    calls = evidence['tool_calls']
    require([c['turn_index'] for c in calls if c['name'] == 'lookup_charges'] == [0, 1]
            and [c['turn_index'] for c in calls if c['name'] == 'refund'] == ([0, 1] if faulty else [0]), 'Missing turn invocation evidence')
    xml = ET.fromstring(junit)
    require(xml.tag == 'testsuite' and xml.attrib.get('tests') == '1'
            and xml.attrib.get('failures') == str(int(faulty)) and xml.attrib.get('errors') == '0'
            and xml.attrib.get('skipped') == '0', 'JUnit coverage mismatch')
    nodes = xml.findall('testcase')
    require(len(nodes) == 1 and nodes[0].attrib.get('name') == CASE
            and len(nodes[0].findall('failure')) == int(faulty)
            and not nodes[0].findall('error') and not nodes[0].findall('skipped'), 'JUnit result mismatch')
    require(json.loads(nodes[0].findtext('system-out') or '{}') == {'checks': checks, 'evidence': evidence}, 'JUnit evidence mismatch')


def run_demo(out, root=ASSETS):
    require(platform.system() in SUPPORTED_SYSTEMS, 'Demo execution requires Linux or macOS; on Windows use Linux/WSL.')
    print("Scripted-reference-demo only: faulty and corrected samples; the user's agent is unassessed.")
    inventory = verify_assets(root)
    dependencies = check_dependencies(root)
    out = no_symlinks(out)
    require(not out.exists() and out.parent.is_dir(), 'Output must be a fresh nonexistent path with an existing parent')
    out.mkdir(mode=0o700)
    provenance = {'kind': 'scripted-reference-demo', 'user_agent': 'unassessed', 'cost_usd': None,
                  'status': 'incomplete', 'dependencies': dependencies, 'resources_sha256': inventory,
                  'helper_sha256': sha(Path(__file__).read_bytes()), 'runs': []}
    try:
        for variant, faulty in [('faulty-v1', True), ('correct-v2', False)]:
            revision = target_revision(root, variant)
            run_id = 'demo-' + uuid.uuid4().hex
            destination = out / variant
            with tempfile.TemporaryDirectory(prefix='agentclash-scripted-demo-') as temporary:
                work = Path(temporary).resolve()
                for path in BUNDLE_FILES:
                    target = work / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(frozen_bundle(root)[path])
                (work / 'agentclash_demo.py').write_bytes(read_file(root, f'targets/{variant}/agentclash_demo.py'))
                command = [sys.executable, '-s', '-m', 'agentclash_eval.runner', '--tests', 'tests/evaltest',
                           '--manifest', 'suite-manifest.json', '--target-revision', revision,
                           '--run-id', run_id, '--out', str(destination), '--timeout-seconds', '30']
                record = {'kind': 'scripted-reference-demo', 'variant': variant, 'target_identity': IDENTITY,
                          'target_revision': revision, 'run_id': run_id, 'command': command,
                          'expected_exit': 1 if faulty else 0, 'classification': 'unverified'}
                provenance['runs'].append(record)
                with (out / f'{variant}.log').open('wb') as log:
                    result = subprocess.run(command, cwd=work, env=clean_environment(work),
                                            stdout=log, stderr=subprocess.STDOUT, timeout=45, check=False)
                record['observed_exit'] = result.returncode
                report_bytes = read_file(destination, 'results.json')
                junit_bytes = read_file(destination, 'junit.xml')
                check_report(json.loads(report_bytes), junit_bytes, result.returncode, run_id, revision, faulty)
                record.update(classification='expected-failure' if faulty else 'corrected-reference-pass',
                              results_sha256=sha(report_bytes), junit_sha256=sha(junit_bytes))
        provenance['status'] = 'expected-reference-pattern-observed'
    finally:
        (out / 'demo-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(f'Scripted-reference-demo: expected failure and corrected reference pass observed. Results: {out}')
    print("Sample only; the user's real agent is unassessed. Cost unknown. No hosted run or account import.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--plan', action='store_true', help='Show the fixed sample plan without execution')
    action.add_argument('--run', action='store_true', help='Explicitly execute both scripted reference samples (Linux or macOS)')
    parser.add_argument('--out', type=Path, help='Fresh nonexistent results directory; parent must exist')
    args = parser.parse_args(argv)
    if args.plan:
        print('Scripted-reference-demo: faulty_double then correct, one frozen case/two turns. User agent unassessed.\n' + preparation())
        return 0
    if not args.out:
        parser.error('--run requires --out')
    try:
        run_demo(args.out)
    except (ValueError, OSError, KeyError, TypeError, ET.ParseError, subprocess.TimeoutExpired) as exc:
        print(f'Demo incomplete: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
