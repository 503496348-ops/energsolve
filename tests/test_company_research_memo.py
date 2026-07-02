import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from energsolve_intel.company_research import CompanyFact, FactStatus, build_company_memo, classify_fact


def test_only_double_verified_facts_enter_read_first_layer():
    facts = [
        CompanyFact("融资", "B轮 5000万美元", sources=("https://news.example/a", "https://vc.example/b")),
        CompanyFact("客户", "服务 300 家客户", sources=("https://company.example/customers",), reported_by_company=True),
        CompanyFact("估值", "10亿美元", sources=("https://blog.example/rumor",)),
        CompanyFact("创始人", "创始人说法冲突", sources=("https://a.example", "https://b.example"), conflicts=("两个来源给出不同姓名",)),
    ]

    memo = build_company_memo("Acme", facts, lens="潜在合作")

    assert [fact.category for fact in memo.read_first] == ["融资"]
    assert classify_fact(facts[1]) is FactStatus.SELF_REPORTED
    assert classify_fact(facts[2]) is FactStatus.SINGLE_SOURCE
    assert classify_fact(facts[3]) is FactStatus.CONFLICTED
    assert "30秒速读" in memo.thirty_second_card()
    assert memo.verification[0]["independent_sources"] == 2
