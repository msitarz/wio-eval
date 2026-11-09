# SPDX-License-Identifier: Apache-2.0
"""Tests for the record script that stands in for `wio trailers check`."""

import io
from typing import TYPE_CHECKING
lazy from pathlib import Path

import pytest

from scripts import records
from tests.support import enter, git

if TYPE_CHECKING:
    from tests.sandbox import Sandbox

RECORD = "Wio-Work: k3m9xq\nWio-Action: deliver\nWio-Stage: architecture"


def _message(*paragraphs: str) -> str:
    """Join paragraphs into a commit message.

    Args:
        *paragraphs: The paragraphs, subject first.

    Returns:
        The message.
    """
    return "\n\n".join(paragraphs) + "\n"


@pytest.mark.parametrize(
    "record",
    [
        RECORD,
        f"{RECORD}\nWio-Items: AC-1, AC-3",
        f"{RECORD}\nWio-Result: pass",
        f"{RECORD}\nWio-Result: pass\nWio-Judge: human",
        "Wio-Work: k3m9xq, a7b2c4\nWio-Action: define\nWio-Stage: define",
        f"{RECORD}\nWio-Result: fail\nWio-Judge: agent",
        f"{RECORD}\nCo-Authored-By: A Person <a@example.com>",
        "Wio-Work: none",
    ],
)
def test_valid_records_have_no_problems(record: str) -> None:
    """A well-formed record, or the explicit opt-out, passes."""
    # Given a commit message that ends with a well-formed record
    message = _message("docs: x", record)

    # When its problems are computed
    problems = records.message_problems(message)

    # Then there are none
    assert problems == []


@pytest.mark.parametrize(
    ("record", "problem"),
    [
        ("Wio-Action: deliver", "Wio-Work is missing"),
        ("Wio-Work: k3m9xq\nWio-Action: deliver", "Wio-Stage is missing"),
        ("Wio-Work: K3M9XQ\nWio-Action: a\nWio-Stage: b", "is not a Work id"),
        ("Wio-Work: k3m9xi\nWio-Action: a\nWio-Stage: b", "is not a Work id"),
        (f"{RECORD}\nWio-Items: AC-1,AC-3", "must be ids without spaces"),
        (f"{RECORD}\nWio-Result: maybe", "must be one of"),
        (f"{RECORD}\nWio-Result: pass\nWio-Judge: robot", "must be one of human"),
        (f"{RECORD}\nWio-Judge: human", "Wio-Judge needs a Wio-Result"),
        (
            "Wio-Work: k3m9xq, k3m9xq\nWio-Action: a\nWio-Stage: b",
            "lists k3m9xq more than once",
        ),
        (
            "Wio-Work: k3m9xq, none\nWio-Action: a\nWio-Stage: b",
            "cannot be listed with Work ids",
        ),
        (
            "Wio-Work: k3m9xq, A7B2C4\nWio-Action: a\nWio-Stage: b",
            "'A7B2C4' is not a Work id",
        ),
        ("Wio-Work: k3m9xq,\nWio-Action: a\nWio-Stage: b", "is not a Work id"),
        ("Wio-Work: k3m9xq,a7b2c4\nWio-Action: a\nWio-Stage: b", "is not a Work id"),
        ("Wio-Work: k3m9xq,  a7b2c4\nWio-Action: a\nWio-Stage: b", "is not a Work id"),
        ("Wio-Work: k3m9xq,, a7b2c4\nWio-Action: a\nWio-Stage: b", "is not a Work id"),
        (
            "Wio-Work: k3m9xq,\u00a0a7b2c4\nWio-Action: a\nWio-Stage: b",
            "is not a Work id",
        ),
        ("Wio-Work: k3m9x\nWio-Action: a\nWio-Stage: b", "is not a Work id"),
        ("Wio-Work: k3m9xqzzz\nWio-Action: a\nWio-Stage: b", "is not a Work id"),
        ("Wio-Work: none\nWio-Judge: human", "not allowed when Wio-Work is none"),
        (f"{RECORD}\nWio-Stage: wiring", "appears more than once"),
        (f"{RECORD}\nWio-Typo: x", "unknown trailer Wio-Typo"),
        (f"{RECORD}\nWio-Criteria: AC-1", "unknown trailer Wio-Criteria"),
        ("Wio-Work: none\nWio-Stage: define", "not allowed when Wio-Work is none"),
        ("Wio-Work: k3m9xq\nWio-Action: Deliver\nWio-Stage: x", "is not a name"),
    ],
)
def test_malformed_records_are_reported(record: str, problem: str) -> None:
    """Each malformed field gives a message that names it."""
    # Given a commit message whose record has one malformed field
    message = _message("docs: x", record)

    # When its problems are computed
    problems = records.message_problems(message)

    # Then one of them describes that field
    assert any(problem in found for found in problems), problems


def test_a_message_without_a_record_is_reported() -> None:
    """A commit must say which Work it belongs to, or that it belongs to none."""
    # Given a commit message with prose and no record
    message = _message("docs: x", "Body.")

    # When its problems are computed
    problems = records.message_problems(message)

    # Then the only problem says how to add a record
    assert problems == ["no Wio-* record; add one, or `Wio-Work: none`"]


@pytest.mark.parametrize(
    "subject",
    ["Merge branch 'x'", 'Revert "docs: x"', 'Reapply "docs: x"', "fixup! docs: x"],
)
def test_merge_revert_and_fixup_commits_need_no_record(subject: str) -> None:
    """Commits that are merged, reverted or squashed away are not checked."""
    # Given a merge, revert or fixup commit message without a record
    message = _message(subject, "Body.")

    # When its problems are computed
    problems = records.message_problems(message)

    # Then there are none
    assert problems == []


def test_an_amend_commit_needs_a_record() -> None:
    """An amend! message replaces its target's, so it must carry the record."""
    # Given an amend! commit message without a record
    message = _message("amend! docs: x", "Body.")

    # When its problems are computed
    problems = records.message_problems(message)

    # Then the missing record is reported
    assert problems == ["no Wio-* record; add one, or `Wio-Work: none`"]


def test_records_in_fenced_code_and_comments_are_ignored() -> None:
    """Quoted example records and git's comment lines do not count."""
    # Given a message whose only records are in fenced code and in a comment
    message = _message("docs: x", f"```text\n{RECORD}\n```", "# Wio-Work: k3m9xq")

    # When its records are read
    found = records.records(message)

    # Then none are found
    assert found == []


def test_a_paragraph_with_prose_is_not_a_record() -> None:
    """Every line of a record must be a trailer."""
    # Given a paragraph that starts with prose and ends with trailers
    message = _message("docs: x", f"Some prose.\n{RECORD}")

    # When the message's records are read
    found = records.records(message)

    # Then the paragraph is not a record
    assert found == []


def test_several_records_are_read_in_order() -> None:
    """A message can hold one record per paragraph."""
    # Given a message with a record for architecture, then one for wiring
    second = "Wio-Work: k3m9xq\nWio-Action: deliver\nWio-Stage: wiring"
    message = _message("docs: x", RECORD, second)

    # When its records are read
    found = records.records(message)

    # Then both are found, in the order of the message
    assert [dict(record)["Wio-Stage"] for record in found] == ["architecture", "wiring"]


def test_collect_keeps_records_of_works_and_drops_the_rest() -> None:
    """Only `Wio-*` fields of records that name a Work are collected."""
    # Given a commit with a record and a co-author, and a commit with no Work
    commits = [
        ("a1", _message("a", f"{RECORD}\nCo-Authored-By: A <a@example.com>")),
        ("b2", _message("b", "Wio-Work: none")),
    ]

    # When their records are collected
    collected = records.collect(commits)

    # Then only the first record's Wio-* fields remain
    assert collected == [RECORD]


def test_collect_leaves_out_reverted_commits() -> None:
    """A commit reverted later in the range keeps no record."""
    # Given a commit with a record and a later commit that reverts it
    commits = [
        ("c0ffee1234", _message("docs: a", RECORD)),
        ("deadbeef56", _message('Revert "docs: a"', "This reverts commit c0ffee1234.")),
    ]

    # When their records are collected
    collected = records.collect(commits)

    # Then the reverted commit's record is left out
    assert collected == []


def test_collect_restores_a_commit_whose_revert_is_reverted() -> None:
    """A revert of a revert brings the original record back."""
    # Given a commit, its revert, and a revert of that revert
    commits = [
        ("c0ffee1234", _message("docs: a", RECORD)),
        ("deadbeef56", _message('Revert "docs: a"', "This reverts commit c0ffee1234.")),
        ("f00dcafe78", _message('Revert "Revert"', "This reverts commit deadbeef56.")),
    ]

    # When their records are collected
    collected = records.collect(commits)

    # Then the original record counts again
    assert collected == [RECORD]


def _record(work: str, stage: str, *extra: str, action: str = "define") -> str:
    """Build a record for a Work.

    Args:
        work: The Work id, or a list of ids.
        stage: The stage.
        *extra: Further trailer lines, such as a result.
        action: The action.

    Returns:
        The record as one paragraph.
    """
    lines = [f"Wio-Work: {work}", f"Wio-Action: {action}", f"Wio-Stage: {stage}"]
    return "\n".join([*lines, *extra])


def _collect(*messages: str) -> list[str]:
    """Collect the records of commits with these messages, oldest first.

    Args:
        *messages: The paragraphs of each commit, joined by blank lines.

    Returns:
        The folded records.
    """
    commits = [(f"{i:040x}", _message("docs: x", m)) for i, m in enumerate(messages)]
    return records.collect(commits)


def test_a_works_consecutive_records_of_one_stage_become_one() -> None:
    """Four commits of a stage leave one record, with the item ids united."""
    # Given a Work with a record in each of four commits of one stage
    messages = [
        _record("k3m9xq", "define", "Wio-Items: AC-1"),
        _record("k3m9xq", "define"),
        _record("k3m9xq", "define", "Wio-Items: AC-2, AC-1"),
        _record("k3m9xq", "define", "Wio-Items: AC-3"),
    ]

    # When their records are collected
    collected = _collect(*messages)

    # Then one record remains, with each item id once, in order of appearance
    assert collected == [_record("k3m9xq", "define", "Wio-Items: AC-1, AC-2, AC-3")]


def test_the_latest_result_and_judge_of_a_merged_gate_win() -> None:
    """A gate recorded twice keeps its later result and judge."""
    # Given a gate recorded by an agent as failed, then by a human as passed
    first = _record("k3m9xq", "review", "Wio-Result: fail", "Wio-Judge: agent")
    second = _record("k3m9xq", "review", "Wio-Result: pass", "Wio-Judge: human")

    # When their records are collected
    collected = _collect(first, second)

    # Then only the later result and judge remain
    assert collected == [second]


def test_a_stage_done_again_after_another_stays_a_separate_record() -> None:
    """Records of a Work that are not consecutive keep their order."""
    # Given a Work that defines, is reviewed, and defines again
    messages = [
        _record("k3m9xq", "define"),
        _record("k3m9xq", "review", "Wio-Result: fail"),
        _record("k3m9xq", "define"),
    ]

    # When their records are collected
    collected = _collect(*messages)

    # Then all three remain
    assert collected == messages


def test_neighbors_that_differ_only_in_their_work_become_one_list() -> None:
    """Identical records of consecutive commits list their Works, oldest first."""
    # Given the same gate result recorded for four Works in four commits
    gate = ("Wio-Result: pass", "Wio-Judge: human")
    works = ["k3m9xq", "jsk0yt", "a7b2c4", "vds425"]
    messages = [_record(work, "review", *gate) for work in works]

    # When their records are collected
    collected = _collect(*messages)

    # Then one record lists the four Works in the order of the commits
    assert collected == [_record("k3m9xq, jsk0yt, a7b2c4, vds425", "review", *gate)]


def test_a_list_in_a_commit_is_read_as_one_record_per_work() -> None:
    """A listed record folds the same way as separate records."""
    # Given one commit that lists two Works, and a later commit for a third
    messages = [
        _record("k3m9xq, jsk0yt", "define"),
        _record("a7b2c4", "define"),
    ]

    # When their records are collected
    collected = _collect(*messages)

    # Then the three Works are listed together, in order
    assert collected == [_record("k3m9xq, jsk0yt, a7b2c4", "define")]


def test_blocks_with_any_other_difference_stay_apart() -> None:
    """Different item ids, results or stages keep records separate."""
    # Given consecutive records for two Works that differ in their item ids
    messages = [
        _record("k3m9xq", "define", "Wio-Items: AC-1"),
        _record("jsk0yt", "define", "Wio-Items: AC-2"),
    ]

    # When their records are collected
    collected = _collect(*messages)

    # Then neither record merges with the other
    assert collected == messages


def test_a_record_between_two_works_keeps_them_apart() -> None:
    """A child delivered again after its parent integrates keeps its place."""
    # Given two children delivered with the same record, and the parent's
    # integration between them
    child = ("deliver", "implementation")
    messages = [
        _record("c1c1c1", child[1], action=child[0]),
        _record("a7b2c4", "integration", action="deliver"),
        _record("c2c2c2", child[1], action=child[0]),
    ]

    # When their records are collected
    collected = _collect(*messages)

    # Then the three records stay in the order of the history
    assert collected == messages


def test_a_merged_record_takes_its_later_position() -> None:
    """A Work's repeated record moves past the records written between them."""
    # Given a Work recorded, another Work recorded, and the first recorded again
    messages = [
        _record("k3m9xq", "define", "Wio-Items: AC-1"),
        _record("jsk0yt", "review", "Wio-Result: pass"),
        _record("k3m9xq", "define", "Wio-Items: AC-2"),
    ]

    # When their records are collected
    collected = _collect(*messages)

    # Then the first Work's merged record comes after the other Work's
    assert collected == [
        messages[1],
        _record("k3m9xq", "define", "Wio-Items: AC-1, AC-2"),
    ]


def test_the_records_of_a_pull_request_fold_to_one_paragraph_per_run() -> None:
    """A stage with several commits and a gate for four Works fold to two."""
    # Given four define commits for one Work, one for another, and a gate that
    # was first recorded for the parent alone, then for all four Works
    gate = ("Wio-Result: pass", "Wio-Judge: human")
    messages = [
        *[_record("zpnbj3", "define")] * 4,
        _record("vds425", "define"),
        _record("zpnbj3", "review-contract", "Wio-Result: pass"),
        "\n\n".join(
            _record(work, "review-contract", *gate)
            for work in ("zpnbj3", "jsk0yt", "1g7xnh", "vds425")
        ),
    ]

    # When their records are collected
    collected = _collect(*messages)

    # Then the first stage and the gate are one paragraph each
    assert collected == [
        _record("zpnbj3, vds425", "define"),
        _record("zpnbj3, jsk0yt, 1g7xnh, vds425", "review-contract", *gate),
    ]


def test_folding_twice_changes_nothing_and_no_work_is_listed_twice() -> None:
    """Interleaved records of two Works fold to one list, and stay folded."""
    # Given two Works recorded in turn, twice each, with the same record
    messages = [_record(work, "define") for work in ("k3m9xq", "jsk0yt") * 2]

    # When their records are collected, then collected again from the result
    collected = _collect(*messages)
    again = _collect(*collected)

    # Then the list names each Work once, and a second fold changes nothing
    assert collected == [_record("k3m9xq, jsk0yt", "define")]
    assert again == collected


def test_a_reverted_commit_leaves_the_rest_of_a_list() -> None:
    """Reverting one commit of a folded run drops only its record."""
    # Given three commits for three Works, and a revert of the middle one
    commits = [
        ("aaaaaa1111", _message("docs: a", _record("k3m9xq", "define"))),
        ("bbbbbb2222", _message("docs: b", _record("jsk0yt", "define"))),
        ("cccccc3333", _message("docs: c", _record("a7b2c4", "define"))),
        ("dddddd4444", _message('Revert "docs: b"', "This reverts commit bbbbbb2222.")),
    ]

    # When their records are collected
    collected = records.collect(commits)

    # Then the list holds the two Works that were not reverted
    assert collected == [_record("k3m9xq, a7b2c4", "define")]


def test_collect_ignores_a_no_work_paragraph_next_to_a_work_record() -> None:
    """A paragraph of `Wio-Work: none` adds nothing to the folded records."""
    # Given a commit with a record for a Work and a record of no Work
    message = f"{_record('k3m9xq', 'define')}\n\nWio-Work: none"

    # When its records are collected
    collected = _collect(message)

    # Then only the Work's record remains
    assert collected == [_record("k3m9xq", "define")]


@pytest.mark.parametrize("separator", ["\n\n\n\n", "\n \n", "\n\t\n", "\n\n\n"])
def test_with_records_replaces_records_set_apart_by_any_blank_lines(
    separator: str,
) -> None:
    """Old records are replaced however the blank lines between them look."""
    # Given a body whose old records are separated by unusual blank lines
    old = separator.join(["Wio-Work: abcdef\nWio-Action: a\nWio-Stage: b"] * 2)
    body = f"## Outcome{separator}Text.{separator}{old}"

    # When the current record is put at its end
    updated = records.with_records(body, [RECORD])

    # Then no old record remains
    assert updated.count("Wio-Work:") == 1
    assert updated.endswith(f"{RECORD}\n")


def test_outside_reverts_keeps_only_reverts_of_earlier_work() -> None:
    """A revert of a commit outside the range keeps its revert line."""
    # Given a revert of a commit from an earlier pull request, and a commit
    # reverted inside the range
    commits = [
        ("c0ffee1234", _message("docs: a", RECORD)),
        ("deadbeef56", _message('Revert "docs: a"', "This reverts commit c0ffee1234.")),
        ("f00dcafe78", _message('Revert "#28"', "This reverts commit 8a8ee78abc.")),
    ]

    # When the revert lines to copy are listed
    lines = records.outside_reverts(commits)

    # Then only the revert of the earlier work is kept
    assert lines == ["This reverts commit 8a8ee78abc."]


def test_with_records_keeps_revert_lines_once() -> None:
    """Revert lines go before the records and are not added twice."""
    # Given a body and a revert line to copy
    revert = "This reverts commit 8a8ee78abc."

    # When the records and revert lines are put at its end, once and again
    updated = records.with_records("## Outcome\n\nText.", [RECORD], [revert])
    again = records.with_records(updated, [RECORD], [revert])

    # Then the revert line comes once, before the record
    assert updated == f"## Outcome\n\nText.\n\n{revert}\n\n{RECORD}\n"
    assert again == updated


def test_with_records_replaces_the_records_at_the_end_of_a_body() -> None:
    """The body keeps its prose and gets exactly the given records."""
    # Given a pull request body with Windows line ends and an outdated record
    body = "## Outcome\r\n\r\nText.\r\n\r\nWio-Work: abcdef\r\nWio-Action: a"

    # When the current records are put at its end, once and then again
    updated = records.with_records(body, [RECORD])
    again = records.with_records(updated, [RECORD])

    # Then the outdated record is replaced, and a second pass changes nothing
    assert updated == f"## Outcome\n\nText.\n\n{RECORD}\n"
    assert again == updated


@pytest.mark.parametrize(
    ("paragraphs", "exit_code"), [(("docs: x", RECORD), 0), (("docs: x",), 1)]
)
def test_check_command_reads_a_message_file(
    tmp_path: Path, paragraphs: tuple[str, ...], exit_code: int
) -> None:
    """The commit-msg hook passes the message file and gets the exit code."""
    # Given a message file, with or without a record
    path = tmp_path / "COMMIT_EDITMSG"
    path.write_text(_message(*paragraphs), encoding="utf-8")

    # When the check command reads it
    code = records.main(["check", str(path)])

    # Then it exits with 0 for a record and 1 without one
    assert code == exit_code


def _commit(repo: Sandbox, message: str) -> None:
    """Make an empty commit in a repository.

    Args:
        repo: The repository's sandbox.
        message: The commit message.
    """
    git(repo, "commit", "-q", "--allow-empty", "-m", message, check=True)


@pytest.fixture
def repo(sandbox: Sandbox, monkeypatch: pytest.MonkeyPatch) -> Sandbox:
    """Create a git repository with one root commit and work inside it.

    Args:
        sandbox: The test's sandbox.
        monkeypatch: pytest's monkeypatch fixture.

    Returns:
        The sandbox of the repository, whose environment the process now has.
    """
    git(sandbox, "init", "-q", check=True)
    _commit(sandbox, "chore: root")
    enter(sandbox, monkeypatch)
    return sandbox


@pytest.mark.slow
def test_commits_command_only_warns_about_a_missing_record(repo: Sandbox) -> None:
    """A commit made outside the hook, without a record, does not fail CI."""
    # Given a commit without a record
    _commit(repo, _message("docs: no record"))

    # When the commits command checks it
    code = records.main(["commits", "HEAD~1..HEAD"])

    # Then it succeeds
    assert code == 0


@pytest.mark.slow
def test_commits_command_fails_on_a_malformed_record(repo: Sandbox) -> None:
    """A record that is there but malformed fails CI."""
    # Given a commit whose record names a Work but no action or stage
    _commit(repo, _message("docs: bad", "Wio-Work: k3m9xq"))

    # When the commits command checks it
    code = records.main(["commits", "HEAD~1..HEAD"])

    # Then it fails
    assert code == 1


@pytest.mark.slow
def test_body_command_appends_the_commits_records(
    repo: Sandbox, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The body gets the records of the range's commits, oldest first."""
    # Given a commit with a record and a pull request body without one
    _commit(repo, _message("docs: a", RECORD))
    monkeypatch.setattr("sys.stdin", io.StringIO("## Outcome\n\nText."))

    # When the body command updates the body
    code = records.main(["body", "HEAD~1..HEAD"])

    # Then it prints the body with the record at its end
    assert code == 0
    assert capsys.readouterr().out == f"## Outcome\n\nText.\n\n{RECORD}\n"


@pytest.mark.slow
def test_body_command_prints_nothing_when_the_body_is_current(
    repo: Sandbox, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A body that already ends with the records needs no edit."""
    # Given a commit with a record and a body that ends with it, with CRLF line ends
    _commit(repo, _message("docs: a", RECORD))
    record = RECORD.replace("\n", "\r\n")
    monkeypatch.setattr("sys.stdin", io.StringIO(f"## Outcome\r\n\r\n{record}"))

    # When the body command updates the body
    code = records.main(["body", "HEAD~1..HEAD"])

    # Then it prints nothing, so the workflow does not edit the pull request
    assert code == 0
    assert not capsys.readouterr().out


@pytest.mark.slow
@pytest.mark.parametrize("line_end", ["\n", "\r\n"])
def test_body_command_prints_nothing_when_a_folded_body_is_current(
    repo: Sandbox,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    line_end: str,
) -> None:
    """A body that already lists the Works of the range needs no edit."""
    # Given two commits with the same record for two Works, and a body that ends
    # with their folded record
    _commit(repo, _message("docs: a", _record("k3m9xq", "define")))
    _commit(repo, _message("docs: b", _record("jsk0yt", "define")))
    folded = _record("k3m9xq, jsk0yt", "define").replace("\n", line_end)
    body = f"## Outcome{line_end}{line_end}{folded}"
    monkeypatch.setattr("sys.stdin", io.StringIO(body))

    # When the body command updates the body
    code = records.main(["body", "HEAD~2..HEAD"])

    # Then it prints nothing, so the workflow does not edit the pull request
    assert code == 0
    assert not capsys.readouterr().out


@pytest.mark.slow
def test_body_command_replaces_an_unfolded_body_once(
    repo: Sandbox, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A body with one paragraph per commit gets the folded list instead."""
    # Given two commits for two Works and a body with a paragraph for each
    _commit(repo, _message("docs: a", _record("k3m9xq", "define")))
    _commit(repo, _message("docs: b", _record("jsk0yt", "define")))
    old = f"{_record('k3m9xq', 'define')}\n\n{_record('jsk0yt', 'define')}"
    monkeypatch.setattr("sys.stdin", io.StringIO(f"## Outcome\n\n{old}"))

    # When the body command updates the body
    code = records.main(["body", "HEAD~2..HEAD"])

    # Then it prints the body with the one folded record at its end
    folded = _record("k3m9xq, jsk0yt", "define")
    assert code == 0
    assert capsys.readouterr().out == f"## Outcome\n\n{folded}\n"


@pytest.mark.slow
def test_block_command_prints_the_paragraphs_to_paste(
    repo: Sandbox, capsys: pytest.CaptureFixture[str]
) -> None:
    """A contributor from a fork gets exactly the paragraphs to add to the body."""
    # Given a commit with a record
    _commit(repo, _message("docs: a", RECORD))

    # When the block command prints the paragraphs for the range
    code = records.main(["block", "HEAD~1..HEAD"])

    # Then it prints the record alone
    assert code == 0
    assert capsys.readouterr().out == f"{RECORD}\n"
