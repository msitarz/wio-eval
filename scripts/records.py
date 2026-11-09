# SPDX-License-Identifier: Apache-2.0
"""Check and collect the `Wio-*` trailer records of this repository's commits.

This is a stand-in for `wio trailers check` until that command exists. It reads
records the way the `scan` reader does: a record is a paragraph in which every
line is a `Key: value` trailer and some key starts with `Wio-`, outside fenced
code blocks. It checks only the shape of a record, not whether its Work, stage
or item ids exist. Unlike `wio trailers check` without `--require`, it reports
an unknown `Wio-` key, such as the retired `Wio-Criteria`, as an error in every
command: it checks only a pull request's own commits, never the older history,
so a branch that still uses a retired key rewords those commits instead.

`Wio-Work` takes one id, several ids separated by a comma and one space, or
`none`. A list is the same as one record per id, in the order written; a Work
listed later counts as recorded later. A pull
request body shows the records folded: for each Work, consecutive records of the
same action and stage become one, and then consecutive records that differ only
in the Work become one list.

Commands:

- `check FILE`: check one commit message (the commit-msg hook).
- `commits RANGE`: check the commits in a revision range (CI).
- `block RANGE`: print the paragraphs that `body` would put at the end of a pull
  request body, for a contributor to paste when the workflow cannot edit it.
- `body RANGE`: read a pull request body on standard input and print it with the
  records of the range's commits at its end, after the revert lines of commits
  that revert work outside the range, or nothing when it already has them
  (CI).

`block` and `body` assume that `commits` accepted the range, so they do not
check the records they fold.
"""

import argparse
import re
import subprocess
import sys
from itertools import groupby
from pathlib import Path
lazy from collections.abc import Iterable, Sequence

type Record = tuple[tuple[str, str], ...]
type Fields = dict[str, str]  # the Wio-* fields of one record, in KEY_ORDER
type Commit = tuple[str, str]  # (sha, message)

TRAILER = re.compile(r"^(?P<key>[A-Za-z0-9][A-Za-z0-9-]*): (?P<value>\S.*)$")
FENCE = re.compile(r"^\s*(```|~~~)")
WORK_ID = re.compile(r"^[0-9a-hjkmnp-tv-z]{6,8}$")  # lowercase Crockford base32
ITEMS = re.compile(r"^[^\s,]+(, [^\s,]+)*$")  # item ids, a comma and one space apart
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
RESULT = re.compile(r"^(pass|fail|unknown)$")
JUDGE = re.compile(r"^(human|agent)$")
KEY_ORDER = (
    "Wio-Work",
    "Wio-Action",
    "Wio-Stage",
    "Wio-Items",
    "Wio-Result",
    "Wio-Judge",
)
KEYS = frozenset(KEY_ORDER)
SKIPPED_SUBJECTS = (
    "Merge ",
    "Revert ",
    "Reapply ",
    "fixup! ",
    "squash! ",
)
BLANK_LINE = re.compile(r"\n[ \t]*\n")
REVERT_LINE = re.compile(r"^This reverts commit [0-9a-f]{7,40}\.?$")
REVERTS = re.compile(r"^This reverts commit (?P<sha>[0-9a-f]{7,40})\b", re.MULTILINE)
NO_WORK = "none"
FORMATS = (
    ("Wio-Action", NAME, "is not a name"),
    ("Wio-Stage", NAME, "is not a name"),
    ("Wio-Items", ITEMS, "must be ids without spaces or commas, like `AC-1, A-2`"),
    ("Wio-Result", RESULT, "must be one of pass, fail, unknown"),
    ("Wio-Judge", JUDGE, "must be one of human, agent"),
)


def _kept_lines(message: str) -> list[str | None]:
    """List a message's lines, with `None` for every line that is left out.

    Blank lines, comment lines and fenced code are left out, so each `None`
    ends a paragraph.

    Args:
        message: A commit message or a pull request body.

    Returns:
        One entry per line of the message.
    """
    kept: list[str | None] = []
    in_fence = False
    for line in message.replace("\r\n", "\n").split("\n"):
        is_fence = FENCE.match(line) is not None
        in_fence = in_fence != is_fence
        dropped = is_fence or in_fence or line.startswith("#") or not line.strip()
        kept.append(None if dropped else line)
    return kept


def paragraphs(message: str) -> list[list[str]]:
    """Split a message into paragraphs, leaving out comments and fenced code.

    Args:
        message: A commit message or a pull request body.

    Returns:
        The paragraphs in order, each as its list of lines.
    """
    result: list[list[str]] = [[]]
    for line in _kept_lines(message):
        if line is None:
            result.append([])
        else:
            result[-1].append(line)
    return [paragraph for paragraph in result if paragraph]


def as_record(paragraph: list[str]) -> Record | None:
    """Read a paragraph as a record.

    Args:
        paragraph: The lines of one paragraph.

    Returns:
        The paragraph's fields, or `None` when it is not a record.
    """
    matches = [TRAILER.match(line) for line in paragraph]
    fields = tuple((m["key"], m["value"]) for m in matches if m is not None)
    if len(fields) != len(paragraph):
        return None
    if not any(key.startswith("Wio-") for key, _ in fields):
        return None
    return fields


def records(message: str) -> list[Record]:
    """Find every record in a message.

    Args:
        message: A commit message or a pull request body.

    Returns:
        The records in the order they appear.
    """
    found = (as_record(paragraph) for paragraph in paragraphs(message))
    return [record for record in found if record is not None]


def _key_problems(keys: list[str]) -> list[str]:
    """Report unknown and repeated `Wio-*` keys in one record.

    Args:
        keys: The record's `Wio-*` keys, in order.

    Returns:
        One message per problem.
    """
    unknown = [f"unknown trailer {key}" for key in keys if key not in KEYS]
    repeated = [
        f"{key} appears more than once in one record"
        for key in sorted(set(keys))
        if keys.count(key) > 1
    ]
    return unknown + repeated


def work_ids(value: str) -> list[str]:
    """Split a `Wio-Work` value into the ids it lists.

    Ids are separated by a comma and one space, the form `Wio-Items` uses.

    Args:
        value: The value, such as `k3m9xq` or `k3m9xq, a7b2c4`.

    Returns:
        The ids in the order written.
    """
    return value.split(", ")


def _ids_problems(ids: list[str]) -> list[str]:
    """Report problems of the ids a record lists.

    Args:
        ids: The ids of a `Wio-Work` value that is not `none` alone.

    Returns:
        One message per problem.
    """
    if NO_WORK in ids:
        return [f"Wio-Work {NO_WORK} cannot be listed with Work ids"]
    malformed = [
        f"Wio-Work {work!r} is not a Work id" for work in ids if not WORK_ID.match(work)
    ]
    repeated = [
        f"Wio-Work lists {work} more than once"
        for work in sorted(set(ids))
        if ids.count(work) > 1
    ]
    return malformed + repeated


def _work_problems(values: dict[str, str]) -> list[str]:
    """Report problems of a record that names a Work.

    Args:
        values: The record's `Wio-*` fields.

    Returns:
        One message per problem.
    """
    required = ("Wio-Action", "Wio-Stage")
    missing = [f"{key} is missing" for key in required if key not in values]
    if "Wio-Judge" in values and "Wio-Result" not in values:
        missing.append("Wio-Judge needs a Wio-Result: only a gate has a judge")
    malformed = [
        f"{key} {values[key]!r} {message}"
        for key, pattern, message in FORMATS
        if key in values and not pattern.match(values[key])
    ]
    return missing + _ids_problems(work_ids(values["Wio-Work"])) + malformed


def _value_problems(values: dict[str, str]) -> list[str]:
    """Report problems of a record's values.

    Args:
        values: The record's `Wio-*` fields.

    Returns:
        One message per problem.
    """
    match values.get("Wio-Work"):
        case None:
            return ["Wio-Work is missing"]
        case work if work == NO_WORK:
            return [
                f"{key} is not allowed when Wio-Work is {NO_WORK}"
                for key in sorted(values)
                if key != "Wio-Work"
            ]
        case _:
            return _work_problems(values)


def record_problems(record: Record) -> list[str]:
    """Check the shape of one record.

    Args:
        record: The fields of one record.

    Returns:
        One message per problem, empty when the record is valid.
    """
    fields = [(key, value) for key, value in record if key.startswith("Wio-")]
    keys = [key for key, _ in fields]
    return _key_problems(keys) + _value_problems(dict(fields))


def message_problems(message: str) -> list[str]:
    """Check every record of a commit message.

    Merge, revert and reapply commits, and fixup and squash commits made to
    be squashed into another one, need no record. An `amend!` commit does:
    its message replaces its target's when it is squashed.

    Args:
        message: A commit message.

    Returns:
        One message per problem, empty when the message is valid.
    """
    if message.lstrip().startswith(SKIPPED_SUBJECTS):
        return []
    found = records(message)
    if not found:
        return [f"no Wio-* record; add one, or `Wio-Work: {NO_WORK}`"]
    return [problem for record in found for problem in record_problems(record)]


def _canonical(fields: dict[str, str]) -> Fields:
    """Keep the `Wio-*` fields of a record, in the order of `KEY_ORDER`.

    Args:
        fields: The fields of a record, any keys in any order.

    Returns:
        The `Wio-*` fields, in a fixed order, so equal records compare equal.
    """
    return {key: fields[key] for key in KEY_ORDER if key in fields}


def expand(record: Record) -> list[Fields]:
    """Split a record into one set of fields per Work it names.

    Args:
        record: The fields of one record.

    Returns:
        One entry per listed id, in the order written. A record of no Work
        gives none.
    """
    fields = _canonical(dict(record))
    ids = work_ids(fields.get("Wio-Work", NO_WORK))
    return [] if ids == [NO_WORK] else [{**fields, "Wio-Work": work} for work in ids]


def _united(earlier: str | None, later: str | None) -> str | None:
    """Unite two lists of item ids, keeping the order of first appearance.

    Args:
        earlier: The `Wio-Items` value of the earlier record, if any.
        later: The `Wio-Items` value of the later record, if any.

    Returns:
        The united list, or `None` when neither record has item ids.
    """
    parts = [part for value in (earlier, later) if value for part in value.split(", ")]
    return ", ".join(dict.fromkeys(parts)) or None


def _merge(earlier: Fields, later: Fields) -> Fields:
    """Merge two records of one Work and stage into one.

    Args:
        earlier: The older record.
        later: The newer record, whose result and judge win.

    Returns:
        The newer record with the item ids of both.
    """
    merged = {key: value for key, value in later.items() if key != "Wio-Items"}
    items = _united(earlier.get("Wio-Items"), later.get("Wio-Items"))
    if items:
        merged["Wio-Items"] = items
    return _canonical(merged)


def _same_stage(first: Fields, second: Fields) -> bool:
    """Tell whether two records are for the same action and stage.

    Args:
        first: One record.
        second: Another record.

    Returns:
        True when both the action and the stage are equal.
    """
    keys = ("Wio-Action", "Wio-Stage")
    return all(first.get(key) == second.get(key) for key in keys)


def _last_of(folded: list[Fields], work: str) -> int | None:
    """Find the newest record of a Work.

    Args:
        folded: Records of single Works, oldest first.
        work: A Work id.

    Returns:
        The index of the Work's newest record, or `None` when it has none.
    """
    indices = (i for i in reversed(range(len(folded))) if folded[i]["Wio-Work"] == work)
    return next(indices, None)


def fold_works(items: Sequence[Fields]) -> list[Fields]:
    """Merge each Work's consecutive records of one action and stage.

    The merged record takes the later position, because only the latest record
    of a stage counts for the order of progress.

    Args:
        items: Records of single Works, oldest first.

    Returns:
        The records with each such run merged into one.
    """
    folded: list[Fields] = []
    for item in items:
        index = _last_of(folded, item["Wio-Work"])
        if index is not None and _same_stage(folded[index], item):
            item = _merge(folded.pop(index), item)
        folded.append(item)
    return folded


def _shape(fields: Fields) -> tuple[tuple[str, str], ...]:
    """List the fields of a record other than its Work.

    Args:
        fields: One record.

    Returns:
        The other fields, in order, as a comparable value.
    """
    return tuple((key, value) for key, value in fields.items() if key != "Wio-Work")


def merge_blocks(items: Sequence[Fields]) -> list[Fields]:
    """Merge consecutive records that differ only in their Work into one list.

    Records are read in order across Works, so only neighbors merge: a record
    between two others could be one that makes a Work's progress stale.

    Args:
        items: Records of single Works, oldest first.

    Returns:
        The records, with each run of neighbors that share every other field
        as one record whose ids are listed oldest first.
    """
    blocks: list[Fields] = []
    for _, run in groupby(items, key=_shape):
        members = list(run)
        works = ", ".join(member["Wio-Work"] for member in members)
        blocks.append({**members[0], "Wio-Work": works})
    return blocks


def fold(found: Iterable[Record]) -> list[Fields]:
    """Fold records for a pull request body.

    Args:
        found: Records in the order of the history, any of which may list
            several Works.

    Returns:
        One record per Work and stage run, and neighbors that differ only in
        the Work as one list.
    """
    expanded = [fields for record in found for fields in expand(record)]
    return merge_blocks(fold_works(expanded))


def render(fields: Fields) -> str:
    """Render the fields of a record as one paragraph.

    Args:
        fields: One record, as `expand` and `fold` return it.

    Returns:
        The trailer lines, joined by newlines.
    """
    return "\n".join(f"{key}: {value}" for key, value in fields.items())


def _kept(commits: Sequence[Commit]) -> list[Commit]:
    """Leave out the commits that a later commit in the list reverts.

    A revert undoes the work its records named, so neither keeps a record. A
    revert of a revert restores the original commit.

    Args:
        commits: Commits as (sha, message), oldest first.

    Returns:
        The commits that still count, oldest first.
    """
    dropped: set[str] = set()
    kept: list[Commit] = []
    for sha, message in reversed(commits):
        if any(sha.startswith(reverted) for reverted in dropped):
            continue
        dropped.update(match["sha"] for match in REVERTS.finditer(message))
        kept.append((sha, message))
    return kept[::-1]


def collect(commits: Sequence[Commit]) -> list[str]:
    """Collect the records of several commits that name a Work, folded.

    Records of commits reverted later in the list are left out.

    Args:
        commits: Commits as (sha, message), oldest first.

    Returns:
        The rendered records, in the order of the history, with each Work's
        consecutive records of one stage merged and then neighbors that differ
        only in the Work merged into one list.
    """
    found = (record for _, message in _kept(commits) for record in records(message))
    return [render(fields) for fields in fold(found)]


def outside_reverts(commits: Sequence[Commit]) -> list[str]:
    """List the revert lines of commits that revert work outside the list.

    A squash merge drops the commits' messages, so these lines are copied into
    the pull request body, where a reader still sees which earlier commit the
    merged change reverts.

    Args:
        commits: Commits as (sha, message), oldest first.

    Returns:
        One `This reverts commit <sha>.` line per such revert, in commit order.
    """
    shas = [sha for sha, _ in commits]
    return [
        f"This reverts commit {match['sha']}."
        for _, message in _kept(commits)
        for match in REVERTS.finditer(message)
        if not any(sha.startswith(match["sha"]) for sha in shas)
    ]


def _is_managed(block: str) -> bool:
    """Tell whether a body paragraph is one this script writes.

    Args:
        block: One paragraph of a pull request body.

    Returns:
        True for a record and for a paragraph of revert lines.
    """
    lines = block.strip().split("\n")
    is_reverts = all(REVERT_LINE.match(line) for line in lines)
    return is_reverts or as_record(lines) is not None


def with_records(
    body: str, rendered: Sequence[str], reverts: Sequence[str] = ()
) -> str:
    """Replace the records and revert lines at the end of a pull request body.

    Args:
        body: The current body.
        rendered: The records to put at its end.
        reverts: Revert lines to put before the records, as one paragraph.

    Returns:
        The body without its trailing managed paragraphs, followed by the
        revert lines and `rendered`.
    """
    blocks = BLANK_LINE.split(body.replace("\r\n", "\n").strip())
    while blocks and (not blocks[-1].strip() or _is_managed(blocks[-1])):
        blocks.pop()
    extra = ["\n".join(reverts)] if reverts else []
    return "\n\n".join([*blocks, *extra, *rendered]).strip() + "\n"


def commits_in(revision_range: str) -> list[Commit]:
    """Read the commits in a revision range.

    Args:
        revision_range: A range such as `main..HEAD`.

    Returns:
        The commits as (sha, message), oldest first.
    """
    output = subprocess.run(
        [
            "git",
            "log",
            "--reverse",
            "--topo-order",
            "--format=%H%n%B%x00",
            revision_range,
        ],
        capture_output=True,
        check=True,
        text=True,
    ).stdout
    entries = (entry.strip() for entry in output.split("\0"))
    pairs = (entry.partition("\n") for entry in entries if entry)
    return [(sha, message.strip()) for sha, _, message in pairs]


def _report(label: str, problems: list[str]) -> None:
    """Write the problems of one message to standard error.

    Args:
        label: What the problems belong to.
        problems: The messages to write.
    """
    for problem in problems:
        sys.stderr.write(f"{label}: {problem}\n")


def _check(path: str) -> int:
    """Check one commit message file.

    Args:
        path: The file that holds the message.

    Returns:
        The exit code: 0 when valid, 1 otherwise.
    """
    problems = message_problems(Path(path).read_text(encoding="utf-8"))
    _report(path, problems)
    return 1 if problems else 0


def _commit_problems(message: str) -> list[str]:
    """Check one commit of a range, warning when it has no record.

    A commit without a record is only a warning here, because commits made
    in GitHub's web interface skip the commit-msg hook.

    Args:
        message: The commit message.

    Returns:
        One message per malformed field.
    """
    found = records(message)
    if not found and not message.startswith(SKIPPED_SUBJECTS):
        subject = message.split("\n", 1)[0]
        sys.stderr.write(f"warning: {subject}: no Wio-* record\n")
    return [problem for record in found for problem in record_problems(record)]


def _commits(revision_range: str) -> int:
    """Check the commits in a revision range.

    Args:
        revision_range: A range such as `main..HEAD`.

    Returns:
        The exit code: 0 when every record is valid, 1 otherwise.
    """
    failed = False
    for _, message in commits_in(revision_range):
        problems = _commit_problems(message)
        _report(message.split("\n", 1)[0], problems)
        failed = failed or bool(problems)
    return 1 if failed else 0


def _body(revision_range: str) -> int:
    """Print the pull request body from standard input with the range's records.

    Nothing is printed when the body already ends with exactly those records,
    so the caller edits the pull request only when something changed.

    Args:
        revision_range: A range such as `main..HEAD`.

    Returns:
        The exit code, always 0.
    """
    body = sys.stdin.read()
    commits = commits_in(revision_range)
    updated = with_records(body, collect(commits), outside_reverts(commits))
    if updated.strip() != body.replace("\r\n", "\n").strip():
        sys.stdout.write(updated)
    return 0


def _block(revision_range: str) -> int:
    """Print the record and revert paragraphs of a range's commits.

    Args:
        revision_range: A range such as `main..HEAD`.

    Returns:
        The exit code, always 0.
    """
    commits = commits_in(revision_range)
    sys.stdout.write(with_records("", collect(commits), outside_reverts(commits)))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command.

    Args:
        argv: The arguments, without the program name.

    Returns:
        The exit code.
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check").add_argument("path")
    commands.add_parser("commits").add_argument("revision_range")
    commands.add_parser("block").add_argument("revision_range")
    commands.add_parser("body").add_argument("revision_range")
    arguments = parser.parse_args(argv)
    match arguments.command:
        case "check":
            return _check(arguments.path)
        case "commits":
            return _commits(arguments.revision_range)
        case "block":
            return _block(arguments.revision_range)
        case _:
            return _body(arguments.revision_range)


if __name__ == "__main__":
    sys.exit(main())
