#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


AGENT_NAMES = ("codex", "opencode", "claude")


@dataclass(frozen=True)
class InstallTarget:
    agent: str
    directory: Path
    note: str


@dataclass(frozen=True)
class InstallResult:
    agent: str
    skill: str
    status: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install this repository's skills for Codex, OpenCode, and Claude."
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        choices=(*AGENT_NAMES, "all"),
        default=["all"],
        help="Which agents to install for. Default: all.",
    )
    parser.add_argument(
        "--skills",
        nargs="+",
        help="Specific skill directory names to install. Default: install all discovered skills.",
    )
    parser.add_argument(
        "--method",
        choices=("symlink", "copy"),
        default="symlink",
        help="Installation method. Default: symlink.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root containing skill directories. Default: parent of this script.",
    )
    parser.add_argument(
        "--codex-dir",
        type=Path,
        help="Override Codex target directory. Useful if your Codex setup uses a custom path.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned actions without modifying the filesystem.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Backup conflicting destinations and replace them.",
    )
    return parser.parse_args()


def resolve_home(path: Path | None = None) -> Path:
    if path is None:
        return Path.home().expanduser().resolve()
    return path.expanduser().resolve()


def discover_skills(repo_root: Path) -> dict[str, Path]:
    skills: dict[str, Path] = {}
    for child in sorted(repo_root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if (child / "SKILL.md").is_file():
            skills[child.name] = child.resolve()
    return skills


def expand_agents(raw_agents: list[str]) -> list[str]:
    if "all" in raw_agents:
        return list(AGENT_NAMES)
    return list(dict.fromkeys(raw_agents))


def resolve_codex_directory(home: Path, override: Path | None) -> InstallTarget:
    if override is not None:
        directory = override.expanduser().resolve()
        return InstallTarget("codex", directory, "using --codex-dir override")

    legacy = home / ".codex" / "skills"
    official = home / ".agents" / "skills"

    if legacy.exists():
        return InstallTarget("codex", legacy, "detected existing legacy Codex skills directory")
    if official.exists():
        return InstallTarget("codex", official, "detected existing agent skills directory")

    return InstallTarget(
        "codex",
        official,
        "defaulting to official Codex user skills directory",
    )


def resolve_targets(home: Path, codex_dir: Path | None) -> dict[str, InstallTarget]:
    return {
        "codex": resolve_codex_directory(home, codex_dir),
        "opencode": InstallTarget(
            "opencode",
            home / ".config" / "opencode" / "skills",
            "OpenCode global skills directory",
        ),
        "claude": InstallTarget(
            "claude",
            home / ".claude" / "skills",
            "Claude personal skills directory",
        ),
    }


def select_skills(discovered: dict[str, Path], requested: list[str] | None) -> dict[str, Path]:
    if not requested:
        return discovered

    missing = [name for name in requested if name not in discovered]
    if missing:
        available = ", ".join(sorted(discovered))
        missing_str = ", ".join(missing)
        raise SystemExit(
            f"Unknown skill(s): {missing_str}. Available skills: {available}"
        )

    return {name: discovered[name] for name in requested}


def path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def already_matches(source: Path, destination: Path, method: str) -> bool:
    if not path_exists(destination):
        return False

    if method == "symlink" and destination.is_symlink():
        try:
            return destination.resolve() == source.resolve()
        except FileNotFoundError:
            return False

    try:
        return destination.resolve() == source.resolve()
    except FileNotFoundError:
        return False


def make_backup_path(home: Path, agent: str, skill_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return (
        home
        / ".agent-skill-installer-backups"
        / agent
        / f"{skill_name}-{timestamp}"
    )


def ensure_parent(path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    path.mkdir(parents=True, exist_ok=True)


def backup_destination(
    destination: Path,
    backup_path: Path,
    dry_run: bool,
) -> str:
    ensure_parent(backup_path.parent, dry_run)
    if dry_run:
        return f"would move existing destination to {backup_path}"

    shutil.move(str(destination), str(backup_path))
    return f"moved existing destination to {backup_path}"


def install_one(
    source: Path,
    destination: Path,
    method: str,
    dry_run: bool,
) -> str:
    ensure_parent(destination.parent, dry_run)
    if dry_run:
        return f"would {method} {source} -> {destination}"

    if method == "symlink":
        destination.symlink_to(source, target_is_directory=True)
        return f"symlinked {source} -> {destination}"

    shutil.copytree(source, destination, dirs_exist_ok=False)
    return f"copied {source} -> {destination}"


def install_skill(
    home: Path,
    target: InstallTarget,
    skill_name: str,
    source: Path,
    method: str,
    dry_run: bool,
    force: bool,
) -> InstallResult:
    destination = target.directory / skill_name

    if already_matches(source, destination, method):
        return InstallResult(target.agent, skill_name, "skip", "already installed")

    if path_exists(destination):
        if not force:
            return InstallResult(
                target.agent,
                skill_name,
                "conflict",
                f"destination exists: {destination}",
            )

        backup_path = make_backup_path(home, target.agent, skill_name)
        backup_detail = backup_destination(destination, backup_path, dry_run)
        install_detail = install_one(source, destination, method, dry_run)
        return InstallResult(
            target.agent,
            skill_name,
            "replace",
            f"{backup_detail}; {install_detail}",
        )

    install_detail = install_one(source, destination, method, dry_run)
    return InstallResult(target.agent, skill_name, "install", install_detail)


def print_header(selected_agents: list[str], targets: dict[str, InstallTarget], skills: dict[str, Path]) -> None:
    print("Agents:")
    for agent in selected_agents:
        target = targets[agent]
        print(f"  - {agent}: {target.directory} ({target.note})")
    print("Skills:")
    for name, path in skills.items():
        print(f"  - {name}: {path}")


def print_results(results: list[InstallResult]) -> int:
    exit_code = 0
    print("\nResults:")
    for result in results:
        print(
            f"  - [{result.status}] {result.agent}/{result.skill}: {result.detail}")
        if result.status == "conflict":
            exit_code = 1
    return exit_code


def main() -> int:
    args = parse_args()
    repo_root = resolve_home(args.repo_root)
    home = resolve_home()

    if not repo_root.is_dir():
        raise SystemExit(f"Repository root does not exist: {repo_root}")

    discovered = discover_skills(repo_root)
    if not discovered:
        raise SystemExit(
            f"No skill directories with SKILL.md found under {repo_root}")

    selected_agents = expand_agents(args.agents)
    targets = resolve_targets(home, args.codex_dir)
    selected_skills = select_skills(discovered, args.skills)

    print_header(selected_agents, targets, selected_skills)

    results: list[InstallResult] = []
    for agent in selected_agents:
        target = targets[agent]
        for skill_name, source in selected_skills.items():
            results.append(
                install_skill(
                    home=home,
                    target=target,
                    skill_name=skill_name,
                    source=source,
                    method=args.method,
                    dry_run=args.dry_run,
                    force=args.force,
                )
            )

    return print_results(results)


if __name__ == "__main__":
    sys.exit(main())
