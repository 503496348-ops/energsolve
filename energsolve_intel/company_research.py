"""Company research gates for evidence-first competitive intelligence.

The module turns raw company facts into a two-layer memo:
- read-first conclusions only contain independently verified facts;
- audit details keep single-source, self-reported, missing, and conflicting facts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Sequence


class FactStatus(str, Enum):
    VERIFIED = "verified"
    SINGLE_SOURCE = "single_source"
    SELF_REPORTED = "self_reported"
    CONFLICTED = "conflicted"
    MISSING = "missing"


@dataclass(frozen=True)
class CompanyFact:
    """A single company intelligence claim with source evidence."""

    category: str
    claim: str
    sources: tuple[str, ...] = ()
    source_types: tuple[str, ...] = ()
    reported_by_company: bool = False
    conflicts: tuple[str, ...] = ()
    notes: str = ""

    def independent_source_count(self) -> int:
        """Count unique non-empty source URLs/domains as a conservative proxy."""
        return len({s.strip().lower() for s in self.sources if s and s.strip()})


@dataclass(frozen=True)
class CompanyResearchMemo:
    """Two-layer company memo payload ready for rendering."""

    company: str
    lens: str
    read_first: tuple[CompanyFact, ...] = field(default_factory=tuple)
    audit_trail: Mapping[FactStatus, tuple[CompanyFact, ...]] = field(default_factory=dict)
    verification: tuple[dict[str, object], ...] = field(default_factory=tuple)

    def thirty_second_card(self) -> str:
        facts = [f"- {fact.category}: {fact.claim}" for fact in self.read_first[:5]]
        if not facts:
            facts = ["- 暂无达到双信源门槛的速读事实；请查看深读区。"]
        return "\n".join([
            f"🎯 {self.company} 30秒速读（视角：{self.lens}）",
            *facts,
        ])


def classify_fact(fact: CompanyFact) -> FactStatus:
    """Classify a fact before deciding whether it may enter the read-first layer."""
    if not fact.claim or fact.claim.strip() in {"未披露", "unknown", "n/a"}:
        return FactStatus.MISSING
    if fact.conflicts:
        return FactStatus.CONFLICTED
    if fact.reported_by_company and fact.independent_source_count() < 2:
        return FactStatus.SELF_REPORTED
    if fact.independent_source_count() >= 2:
        return FactStatus.VERIFIED
    return FactStatus.SINGLE_SOURCE


def verification_matrix(facts: Iterable[CompanyFact]) -> tuple[dict[str, object], ...]:
    """Build a compact verification matrix for downstream docs or dashboards."""
    rows: list[dict[str, object]] = []
    for fact in facts:
        status = classify_fact(fact)
        rows.append({
            "category": fact.category,
            "claim": fact.claim or "未披露",
            "status": status.value,
            "independent_sources": fact.independent_source_count(),
            "source_types": list(fact.source_types),
            "conflicts": list(fact.conflicts),
            "notes": fact.notes,
        })
    return tuple(rows)


def build_company_memo(company: str, facts: Sequence[CompanyFact], lens: str = "通用了解") -> CompanyResearchMemo:
    """Split company intelligence into read-first and audit layers.

    Only VERIFIED facts are allowed into read_first. All other facts are preserved
    in audit_trail so a reviewer can challenge or refresh the conclusion later.
    """
    buckets: dict[FactStatus, list[CompanyFact]] = {status: [] for status in FactStatus}
    for fact in facts:
        buckets[classify_fact(fact)].append(fact)

    return CompanyResearchMemo(
        company=company,
        lens=lens,
        read_first=tuple(buckets[FactStatus.VERIFIED]),
        audit_trail={status: tuple(items) for status, items in buckets.items()},
        verification=verification_matrix(facts),
    )
