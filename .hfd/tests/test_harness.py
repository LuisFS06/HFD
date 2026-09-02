"""Self-tests for the HFD harness scripts.

These test the preset itself, not a project built with it. Each test runs
the real scripts in a throwaway project directory, so a broken script fails
here instead of in someone's session.

    python -m pytest .hfd/tests -q
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".hfd" / "scripts"
SKILLS = REPO / ".claude" / "skills"


def run(script: str, *args: str, cwd: Path, expect: "int | None" = 0):
    proc = subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                          cwd=cwd, capture_output=True, text=True)
    if expect is not None:
        assert proc.returncode == expect, (
            f"{script} {' '.join(args)} -> {proc.returncode}\n{proc.stdout}\n{proc.stderr}")
    return proc


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    """A bare project directory carrying the harness but no artifacts yet."""
    shutil.copytree(REPO / ".hfd", tmp_path / ".hfd",
                    ignore=shutil.ignore_patterns("tests", "__pycache__"))
    (tmp_path / "docs").mkdir()
    shutil.copy(REPO / "docs" / "coding-standards.md", tmp_path / "docs")
    return tmp_path


@pytest.fixture()
def scaffolded(project: Path) -> Path:
    run("init_project.py", "--track", "both", cwd=project)
    return project


# --------------------------------------------------------------- scaffolding

def test_init_creates_both_tracks(scaffolded: Path):
    for rel in ("src/models/train_model.py", "src/analysis/example_question.py",
                "sql/README.md", "reports/README.md", "pyproject.toml",
                "docs/state", "tests"):
        assert (scaffolded / rel).exists(), rel


def test_init_is_idempotent(scaffolded: Path):
    marker = scaffolded / "src" / "data" / "load_data.py"
    marker.write_text("# edited by the user\n", encoding="utf-8")
    out = run("init_project.py", "--track", "both", cwd=scaffolded).stdout
    assert "SKIPPED" in out
    assert marker.read_text(encoding="utf-8") == "# edited by the user\n"


def test_init_analysis_track_skips_model_dirs(project: Path):
    run("init_project.py", "--track", "analysis", cwd=project)
    assert (project / "src/analysis").is_dir()
    assert not (project / "src/models").exists()


# ------------------------------------------------------------------- context

def test_every_skill_has_a_contract_and_frontmatter():
    registry = json.loads((REPO / ".hfd" / "context.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(SCRIPTS))
    from sync_skills import parse_frontmatter

    skills = sorted(p.name for p in SKILLS.iterdir() if p.is_dir())
    assert set(skills) == set(registry["contracts"]), "skills and contracts disagree"
    for name in skills:
        meta = parse_frontmatter((SKILLS / name / "SKILL.md").read_text(encoding="utf-8"))
        assert meta.get("name") == name, f"{name}: frontmatter name mismatch"
        assert meta.get("description"), f"{name}: missing description"
        assert meta.get("copilot-model"), f"{name}: missing copilot-model"


def test_contract_refs_resolve():
    registry = json.loads((REPO / ".hfd" / "context.json").read_text(encoding="utf-8"))
    known = set(registry["artifacts"]) | {f"probe:{p}" for p in registry["probes"]}
    for skill, contract in registry["contracts"].items():
        for ref in contract["load"]:
            base = ref.split("#")[0].lstrip("?")
            assert base in known, f"{skill} loads unknown ref {ref}"
        for ref in contract.get("never", []):
            assert ref in registry["artifacts"], f"{skill} forbids unknown artifact {ref}"


def test_optional_refs_do_not_warn_when_absent(scaffolded: Path):
    """An analysis-only project has no constitution; that is not a problem."""
    pack = json.loads(run("context.py", "pack", "hfd-analyze", "--json",
                          cwd=scaffolded).stdout)
    absent = [i for i in pack["load_order"] if i["status"] == "optional-absent"]
    assert absent, "expected the optional constitution ref to be absent here"
    assert pack["warnings"] == []


def test_pack_orders_stable_tiers_first(scaffolded: Path):
    out = run("context.py", "pack", "hfd-run", "--slice", "1", "--json",
              cwd=scaffolded).stdout
    pack = json.loads(out)
    orders = [{"frozen": 0, "append-only": 1, "revisable": 2, "volatile": 3,
               "probe": 4, "task": 5}[i["tier"]] for i in pack["load_order"]]
    assert orders == sorted(orders), "pack must load stable tiers first"
    assert pack["never_load"], "hfd-run must declare forbidden artifacts"


def test_budget_is_respected_for_every_skill(scaffolded: Path):
    rows = json.loads(run("context.py", "budget", "--json", cwd=scaffolded).stdout)
    over = [r["skill"] for r in rows if r["over"]]
    assert not over, f"contracts over budget: {over}"


def test_show_extracts_one_section_ignoring_accents(scaffolded: Path):
    (scaffolded / "docs" / "constitution.md").write_text(
        "# C\n\n## Glosario del dominio\n- churn: 90 dias\n\n"
        "## Criterios de cancelación\n- CC-0001\n", encoding="utf-8")
    out = run("context.py", "show", "constitution#Criterios de cancelacion",
              cwd=scaffolded).stdout
    assert "CC-0001" in out
    assert "Glosario" not in out


def test_verify_accepts_appends_and_rejects_mid_file_edits(scaffolded: Path):
    doc = scaffolded / "docs" / "blind-research.md"
    doc.write_text("# R\n\n## Resumen ejecutivo\nok\n", encoding="utf-8")
    run("context.py", "freeze", cwd=scaffolded)

    with doc.open("a", encoding="utf-8") as f:
        f.write("\n## Addendum 2026-09-02\nmas datos\n")
    out = run("context.py", "verify", cwd=scaffolded).stdout
    assert "appended" in out

    doc.write_text(doc.read_text(encoding="utf-8").replace("ok", "NO"), encoding="utf-8")
    proc = run("context.py", "verify", cwd=scaffolded, expect=1)
    assert "blind-research" in proc.stdout


def test_lock_ignores_volatile_state(scaffolded: Path):
    run("context.py", "freeze", cwd=scaffolded)
    lock = json.loads((scaffolded / "docs/state/context-lock.json").read_text(encoding="utf-8"))
    assert "context-lock" not in lock["artifacts"]
    assert "coding-standards" in lock["artifacts"]


# ------------------------------------------------------------------- worklog

def test_worklog_folds_events_into_current_state(scaffolded: Path):
    run("worklog.py", "add", "--kind", "analysis", "--title", "churn",
        "--intent", "q", "--verification", "python -c \"pass\"", cwd=scaffolded)
    run("worklog.py", "update", "W001", "--status", "blocked", "--notes", "sin acceso",
        cwd=scaffolded)
    run("worklog.py", "close", "W001", "--verified", "pass", "--finding", "63% (n=12481)",
        cwd=scaffolded)
    rows = json.loads(run("worklog.py", "show", "--json", cwd=scaffolded).stdout)
    unit = rows[0]
    assert unit["status"] == "done" and unit["verified"] == "pass"
    assert unit["finding"].startswith("63%")
    # the ledger itself is append-only: four events, none rewritten
    lines = (scaffolded / "docs/state/worklog.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3


def test_worklog_recheck_reports_failures(scaffolded: Path):
    run("worklog.py", "add", "--kind", "feature", "--title", "x", "--intent", "y",
        "--verification", "python -c \"raise SystemExit(3)\"", cwd=scaffolded)
    proc = run("worklog.py", "recheck", "--all", cwd=scaffolded, expect=1)
    assert "fail" in proc.stdout
    rows = json.loads(run("worklog.py", "show", "--json", cwd=scaffolded).stdout)
    assert rows[0]["verified"] == "fail"


def test_worklog_rejects_unknown_id(scaffolded: Path):
    run("worklog.py", "close", "W999", "--verified", "pass", cwd=scaffolded, expect=1)


# ---------------------------------------------------------- slices and status

def test_checkpoint_gate_and_status_next_command(scaffolded: Path):
    for name in ("constitution.md", "hypothesis-doc.md", "blind-research.md",
                 "design-decisions.md", "model-card.md"):
        (scaffolded / "docs" / name).write_text("## Resumen ejecutivo\nplan\n", encoding="utf-8")
    (scaffolded / "docs" / "prd-slices.md").write_text(
        "## Resumen ejecutivo\nplan\n\n## Slice 1: Calidad de labels\ncontenido\n\n"
        "## Slice 2: Baseline\notro\n", encoding="utf-8")
    run("checkpoint.py", "add-slice", "1", "--title", "Calidad de labels",
        "--metric", "label_agreement", "--op", ">=", "--threshold", "0.9",
        "--fail-action", "cancelar CC-0001", "--steps", "cargar;auditar", cwd=scaffolded)
    run("checkpoint.py", "start", "1", cwd=scaffolded)
    run("checkpoint.py", "step", "1", "1", "done", cwd=scaffolded)

    status = json.loads(run("hfd_status.py", "--json", cwd=scaffolded).stdout)
    assert status["track"] == "modeling"
    assert "Slice 1" in status["next"]

    run("checkpoint.py", "gate", "1", "--value", "0.95", cwd=scaffolded)
    status = json.loads(run("hfd_status.py", "--json", cwd=scaffolded).stdout)
    assert status["slice_counts"]["pass"] == 1

    out = run("get_slice.py", "1", cwd=scaffolded).stdout
    assert "Calidad de labels" in out and "Baseline" not in out


def test_status_prioritises_open_work(scaffolded: Path):
    run("worklog.py", "add", "--kind", "feature", "--title", "parquet loader",
        "--intent", "soportar parquet", cwd=scaffolded)
    status = json.loads(run("hfd_status.py", "--json", cwd=scaffolded).stdout)
    assert "/hfd-feature" in status["next"] and "W001" in status["next"]


def test_experiment_ledger_computes_delta(scaffolded: Path):
    run("experiment.py", "add", "--change", "a", "--hypothesis", "h",
        "--metric", "AUC", "--value", "0.78", "--verdict", "adopt", cwd=scaffolded)
    out = run("experiment.py", "add", "--change", "b", "--hypothesis", "h",
              "--metric", "AUC", "--value", "0.80", "--verdict", "adopt",
              cwd=scaffolded).stdout
    assert "+0.02" in out
    best = json.loads(run("experiment.py", "best", "--metric", "AUC", cwd=scaffolded).stdout)
    assert best["value"] == 0.80


# -------------------------------------------------------------------- verify

def test_verify_flags_missing_declared_artifacts(scaffolded: Path):
    run("context.py", "freeze", cwd=scaffolded)
    run("worklog.py", "add", "--kind", "analysis", "--title", "x", "--intent", "y",
        "--verification", "true", cwd=scaffolded)
    run("worklog.py", "close", "W001", "--verified", "pass",
        "--artifacts", "reports/no-existe.md", cwd=scaffolded)
    proc = run("verify.py", "--quick", "--json", cwd=scaffolded, expect=1)
    payload = json.loads(proc.stdout)
    assert "state" in payload["failures"]
    assert "no-existe" in payload["checks"]["state"]["detail"]


def test_verify_passes_on_a_clean_project(scaffolded: Path):
    run("context.py", "freeze", cwd=scaffolded)
    payload = json.loads(run("verify.py", "--quick", "--json", cwd=scaffolded).stdout)
    assert payload["failures"] == []


# ---------------------------------------------------------------- copilot sync

def test_claude_and_copilot_surfaces_are_in_sync():
    proc = subprocess.run([sys.executable, str(SCRIPTS / "sync_skills.py"), "--check"],
                          cwd=REPO, capture_output=True, text=True)
    assert proc.returncode == 0, f"run sync_skills.py:\n{proc.stdout}"


def test_generated_prompts_pin_a_model():
    for prompt in (REPO / ".github" / "prompts").glob("hfd-*.prompt.md"):
        text = prompt.read_text(encoding="utf-8")
        assert "model:" in text.split("---")[1], f"{prompt.name} has no model pinned"
        assert "context.py pack" in text, f"{prompt.name} skips the context pack"
