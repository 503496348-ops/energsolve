#!/usr/bin/env python3
"""Energsolve — 元气方程竞品分析 CLI."""
import argparse
import importlib.util
import json
import sys


def _has_crawl4ai():
    """Check if crawl4ai is available."""
    return importlib.util.find_spec("crawl4ai") is not None


def cmd_crawl(args):
    """Crawl a URL for competitor analysis."""
    if _has_crawl4ai():
        print(
            json.dumps(
                {
                    "url": args.url,
                    "depth": args.depth,
                    "engine": "crawl4ai",
                    "status": "ready",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(
            json.dumps(
                {
                    "url": args.url,
                    "status": "crawl4ai_not_installed",
                    "fix": "pip install crawl4ai",
                },
                ensure_ascii=False,
            )
        )


def cmd_analyze(args):
    """Analyze competitor content."""
    print(
        json.dumps(
            {
                "input": args.input,
                "analysis_type": args.type or "general",
                "status": "ready",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_report(args):
    """Generate competitor analysis report."""
    print(
        json.dumps(
            {
                "output": args.output or "report.html",
                "format": args.format or "html",
                "status": "ready",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_info(args):
    """Show product info."""
    if _has_crawl4ai():
        try:
            import crawl4ai

            version = getattr(crawl4ai, "__version__", "unknown")
        except ImportError:
            version = "unknown"
        engine_status = "available"
    else:
        version = "not installed"
        engine_status = "missing"
    print(
        json.dumps(
            {
                "product": "Energsolve 元气方程",
                "type": "竞品分析系统",
                "engine": f"crawl4ai {version}",
                "engine_status": engine_status,
                "status": "ok",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def main():
    p = argparse.ArgumentParser(description="Energsolve 元气方程竞品分析工具")
    sub = p.add_subparsers(dest="command")

    c = sub.add_parser("crawl", help="爬取竞品页面")
    c.add_argument("url", help="目标 URL")
    c.add_argument("--depth", type=int, default=1)

    a = sub.add_parser("analyze", help="分析竞品内容")
    a.add_argument("input", help="输入文件或 URL")
    a.add_argument("--type", help="分析类型")

    r = sub.add_parser("report", help="生成分析报告")
    r.add_argument("--output", "-o", help="输出文件")
    r.add_argument("--format", default="html", choices=["html", "json", "md"])

    sub.add_parser("info", help="产品信息")

    args = p.parse_args()
    if args.command == "crawl":
        cmd_crawl(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "info":
        cmd_info(args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
