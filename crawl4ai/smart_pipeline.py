"""
Smart Extraction Pipeline — Graph-driven LLM extraction (Scrapegraph-ai style).

Builds a DAG of extraction steps, uses LLM to plan the pipeline from a natural
language prompt, then executes each node in order.

Brand: AtomCollide-智械工坊
"""

from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pipeline node types
# ---------------------------------------------------------------------------

class NodeType(str, Enum):
    FETCH = "fetch"
    PARSE = "parse"
    EXTRACT = "extract"
    SEARCH = "search"
    VALIDATE = "validate"
    TRANSFORM = "transform"
    MERGE = "merge"


@dataclass
class PipelineNode:
    """A single node in the extraction DAG."""
    node_id: str
    node_type: NodeType
    config: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "config": self.config,
            "depends_on": self.depends_on,
        }


@dataclass
class PipelineResult:
    """Result of running the full pipeline."""
    success: bool
    data: Any = None
    errors: List[str] = field(default_factory=list)
    node_outputs: Dict[str, Any] = field(default_factory=dict)
    pipeline_plan: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "errors": self.errors,
            "node_outputs": {k: str(v)[:500] for k, v in self.node_outputs.items()},
            "pipeline_plan": self.pipeline_plan,
        }


# ---------------------------------------------------------------------------
# Planner: uses LLM to build a DAG from a natural-language prompt
# ---------------------------------------------------------------------------

_PIPELINE_PLANNER_PROMPT = """You are an expert web scraping pipeline planner.
Given a user instruction, a URL, and (optionally) a sample of the page content,
produce a JSON array of pipeline nodes. Each node must have:
  - node_id: unique string
  - node_type: one of "fetch", "parse", "extract", "search", "validate", "transform", "merge"
  - config: object with type-specific keys
  - depends_on: list of node_ids this node depends on

Rules:
- Always start with a "fetch" node to retrieve the page.
- Then a "parse" node to convert HTML to structured data.
- Add "extract" nodes for each data field requested. Config keys:
    "selector" (CSS/XPath), "field_name", "extraction_mode" ("css"|"xpath"|"llm")
- Optionally add "validate" nodes to check output quality.
- End with a "merge" node that combines all extracted fields.
- Keep the plan minimal — 3-7 nodes.

Respond ONLY with valid JSON array. No markdown fences.

User instruction: {prompt}
URL: {url}
Page sample (first 2000 chars):
{sample}
"""


class PipelinePlanner:
    """Uses an LLM to plan the extraction DAG from a prompt."""

    def __init__(self, provider: str = "openai/gpt-4o", api_token: str = ""):
        self.provider = provider
        self.api_token = api_token

    async def plan(self, prompt: str, url: str, sample: str = "") -> List[PipelineNode]:
        """Return a list of PipelineNodes planned by the LLM."""
        from .utils import perform_completion_with_backoff

        full_prompt = _PIPELINE_PLANNER_PROMPT.format(
            prompt=prompt, url=url, sample=sample[:2000]
        )
        try:
            response = perform_completion_with_backoff(
                provider=self.provider,
                prompt_with_variables=full_prompt,
                api_token=self.api_token,
                json_response=True,
            )
            raw = response.choices[0].message.content.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            nodes_raw = json.loads(raw)
            nodes = []
            for n in nodes_raw:
                nodes.append(PipelineNode(
                    node_id=n["node_id"],
                    node_type=NodeType(n["node_type"]),
                    config=n.get("config", {}),
                    depends_on=n.get("depends_on", []),
                ))
            return nodes
        except Exception as e:
            logger.warning(f"Pipeline planner failed, using fallback: {e}")
            return self._fallback_plan(url)

    def _fallback_plan(self, url: str) -> List[PipelineNode]:
        """Deterministic default plan when LLM is unavailable."""
        return [
            PipelineNode("fetch", NodeType.FETCH, {"url": url}),
            PipelineNode("parse", NodeType.PARSE, {}, ["fetch"]),
            PipelineNode(
                "extract_main",
                NodeType.EXTRACT,
                {"selector": "body", "field_name": "content", "extraction_mode": "llm"},
                ["parse"],
            ),
            PipelineNode(
                "merge",
                NodeType.MERGE,
                {"fields": ["content"]},
                ["extract_main"],
            ),
        ]


# ---------------------------------------------------------------------------
# Node executors
# ---------------------------------------------------------------------------

class _NodeExecutor(ABC):
    @abstractmethod
    async def execute(
        self, node: PipelineNode, context: Dict[str, Any]
    ) -> Any:
        ...


class _FetchExecutor(_NodeExecutor):
    async def execute(self, node: PipelineNode, context: Dict[str, Any]) -> Any:
        url = node.config.get("url", context.get("url", ""))
        if not url:
            raise ValueError("Fetch node requires a URL")

        from .async_configs import BrowserConfig, CrawlerRunConfig
        from .async_webcrawler import AsyncWebCrawler

        browser_cfg = BrowserConfig(headless=True, verbose=False)
        run_cfg = CrawlerRunConfig(
            cache_mode=context.get("cache_mode"),
            verbose=False,
        )
        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=url, config=run_cfg)
        return {
            "html": result.html if hasattr(result, "html") else "",
            "markdown": result.markdown if hasattr(result, "markdown") else "",
            "success": result.success if hasattr(result, "success") else True,
        }


class _ParseExecutor(_NodeExecutor):
    async def execute(self, node: PipelineNode, context: Dict[str, Any]) -> Any:
        fetch_out = context.get("_fetch", {})
        html = fetch_out.get("html", "")
        if not html:
            return {"parsed_html": "", "text": ""}
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            return {
                "parsed_html": str(soup),
                "text": soup.get_text(separator="\n", strip=True),
            }
        except Exception:
            return {"parsed_html": html, "text": ""}


class _ExtractExecutor(_NodeExecutor):
    async def execute(self, node: PipelineNode, context: Dict[str, Any]) -> Any:
        config = node.config
        mode = config.get("extraction_mode", "css")
        selector = config.get("selector", "body")
        field_name = config.get("field_name", "content")

        parsed = context.get("_parse", {})
        html = parsed.get("parsed_html", "")

        if mode == "llm":
            return await self._llm_extract(field_name, config, context)

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            if mode == "css":
                elements = soup.select(selector)
            else:
                from lxml import html as lxml_html
                tree = lxml_html.fromstring(html)
                elements = tree.xpath(selector)

            texts = []
            for el in elements:
                text = el.get_text(strip=True) if hasattr(el, "get_text") else str(el)
                if text:
                    texts.append(text)
            return {field_name: "\n".join(texts) if texts else ""}
        except Exception as e:
            logger.warning(f"Extract node {node.node_id} failed: {e}")
            return {field_name: ""}

    async def _llm_extract(
        self, field_name: str, config: Dict[str, Any], context: Dict[str, Any]
    ) -> Any:
        from .utils import perform_completion_with_backoff
        from .config import DEFAULT_PROVIDER, DEFAULT_PROVIDER_API_KEY

        parsed = context.get("_parse", {})
        text = parsed.get("text", "")[:4000]
        instruction = config.get("instruction", f"Extract the {field_name} from this content.")

        prompt = f"""{instruction}

Content:
{text}

Respond with JSON: {{"{field_name}": <extracted value>}}"""

        try:
            provider = context.get("provider", DEFAULT_PROVIDER)
            api_token = context.get("api_token", "")
            response = perform_completion_with_backoff(
                provider=provider,
                prompt_with_variables=prompt,
                api_token=api_token,
                json_response=True,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"LLM extraction failed for {field_name}: {e}")
            return {field_name: ""}


class _ValidateExecutor(_NodeExecutor):
    async def execute(self, node: PipelineNode, context: Dict[str, Any]) -> Any:
        checks = node.config.get("checks", [])
        results = {}
        for check in checks:
            field = check.get("field", "")
            required = check.get("required", False)
            min_length = check.get("min_length", 0)
            value = context.get(field, "")
            passed = True
            if required and not value:
                passed = False
            if isinstance(value, str) and len(value) < min_length:
                passed = False
            results[field] = {"passed": passed, "length": len(str(value))}
        return {"validation": results, "all_passed": all(r["passed"] for r in results.values())}


class _TransformExecutor(_NodeExecutor):
    async def execute(self, node: PipelineNode, context: Dict[str, Any]) -> Any:
        ops = node.config.get("operations", [])
        result = dict(context)
        for op in ops:
            op_type = op.get("type", "")
            if op_type == "trim":
                field = op.get("field", "")
                max_len = op.get("max_length", 5000)
                if field in result and isinstance(result[field], str):
                    result[field] = result[field][:max_len]
            elif op_type == "json_parse":
                field = op.get("field", "")
                if field in result and isinstance(result[field], str):
                    try:
                        result[field] = json.loads(result[field])
                    except json.JSONDecodeError:
                        pass
        return result


class _MergeExecutor(_NodeExecutor):
    async def execute(self, node: PipelineNode, context: Dict[str, Any]) -> Any:
        fields = node.config.get("fields", [])
        if not fields:
            # Merge all non-internal keys
            return {k: v for k, v in context.items() if not k.startswith("_")}
        merged = {}
        for f in fields:
            if f in context:
                merged[f] = context[f]
        return merged


_EXECUTORS = {
    NodeType.FETCH: _FetchExecutor(),
    NodeType.PARSE: _ParseExecutor(),
    NodeType.EXTRACT: _ExtractExecutor(),
    NodeType.VALIDATE: _ValidateExecutor(),
    NodeType.TRANSFORM: _TransformExecutor(),
    NodeType.MERGE: _MergeExecutor(),
}


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

class SmartExtractionPipeline:
    """Graph-driven extraction pipeline.

    Usage::

        pipeline = SmartExtractionPipeline(
            provider="openai/gpt-4o",
            api_token="sk-..."
        )
        result = await pipeline.run(
            prompt="Extract product name and price from this page",
            url="https://example.com/product",
        )
        print(result.data)
    """

    def __init__(
        self,
        provider: str = "openai/gpt-4o",
        api_token: str = "",
        cache_mode=None,
    ):
        self.provider = provider
        self.api_token = api_token
        self.cache_mode = cache_mode
        self.planner = PipelinePlanner(provider=provider, api_token=api_token)

    async def run(
        self,
        prompt: str,
        url: str,
        nodes: Optional[List[PipelineNode]] = None,
    ) -> PipelineResult:
        """Plan (if needed) and execute the extraction pipeline."""
        try:
            if nodes is None:
                nodes = await self.planner.plan(prompt, url)

            if not nodes:
                return PipelineResult(success=False, errors=["Empty pipeline plan"])

            # Topological sort
            sorted_nodes = self._topo_sort(nodes)

            context: Dict[str, Any] = {
                "url": url,
                "provider": self.provider,
                "api_token": self.api_token,
                "cache_mode": self.cache_mode,
            }

            for node in sorted_nodes:
                executor = _EXECUTORS.get(node.node_type)
                if executor is None:
                    logger.warning(f"No executor for node type {node.node_type}")
                    continue
                logger.info(f"Executing pipeline node: {node.node_id} ({node.node_type.value})")
                output = await executor.execute(node, context)
                # Store output with underscore prefix for dependency resolution
                context[f"_{node.node_id}"] = output
                # Also merge top-level keys into context
                if isinstance(output, dict):
                    context.update(output)
                context["node_outputs"] = context.get("node_outputs", {})
                context["node_outputs"][node.node_id] = output

            # Get final merge output
            final = context.get("_merge", context.get("node_outputs", {}))
            plan_dicts = [n.to_dict() for n in sorted_nodes]

            return PipelineResult(
                success=True,
                data=final,
                node_outputs=context.get("node_outputs", {}),
                pipeline_plan=plan_dicts,
            )
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return PipelineResult(success=False, errors=[str(e)])

    @staticmethod
    def _topo_sort(nodes: List[PipelineNode]) -> List[PipelineNode]:
        """Topological sort of pipeline nodes by depends_on."""
        node_map = {n.node_id: n for n in nodes}
        visited = set()
        order: List[PipelineNode] = []

        def visit(nid: str):
            if nid in visited:
                return
            visited.add(nid)
            node = node_map.get(nid)
            if node is None:
                return
            for dep in node.depends_on:
                visit(dep)
            order.append(node)

        for n in nodes:
            visit(n.node_id)
        return order

    @staticmethod
    def create_nodes_from_schema(
        url: str,
        schema: Dict[str, str],
    ) -> List[PipelineNode]:
        """Helper: build nodes from a simple {field_name: selector} schema.

        Example::

            nodes = SmartExtractionPipeline.create_nodes_from_schema(
                "https://example.com",
                {"title": "h1.product-title", "price": "span.price"},
            )
        """
        nodes = [
            PipelineNode("fetch", NodeType.FETCH, {"url": url}),
            PipelineNode("parse", NodeType.PARSE, {}, ["fetch"]),
        ]
        field_names = []
        for field_name, selector in schema.items():
            nodes.append(PipelineNode(
                f"extract_{field_name}",
                NodeType.EXTRACT,
                {"selector": selector, "field_name": field_name, "extraction_mode": "css"},
                ["parse"],
            ))
            field_names.append(field_name)
        nodes.append(PipelineNode(
            "merge",
            NodeType.MERGE,
            {"fields": field_names},
            [f"extract_{fn}" for fn in field_names],
        ))
        return nodes
