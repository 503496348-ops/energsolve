"""
Reader API — Simple URL-to-Markdown reader (Jina Reader style).

One-call interface to get clean, LLM-friendly content from any URL.
Handles web pages, PDFs, plain text, and raw HTML.

Usage::

    from crawl4ai.reader import SimpleReader

    reader = SimpleReader()
    result = await reader.read("https://example.com")
    print(result.markdown)
    print(result.title)

Brand: AtomCollide-智械工坊
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    WEB = "web"
    PDF = "pdf"
    TEXT = "text"
    IMAGE = "image"
    UNKNOWN = "unknown"


@dataclass
class ReaderResult:
    """Clean result from the Reader API."""
    url: str
    title: str = ""
    markdown: str = ""
    content_type: ContentType = ContentType.UNKNOWN
    status_code: int = 200
    success: bool = True
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "markdown": self.markdown,
            "content_type": self.content_type.value,
            "status_code": self.status_code,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
            "links": self.links[:50],
        }

    def __str__(self) -> str:
        if not self.success:
            return f"ReaderResult(ERROR: {self.error})"
        preview = self.markdown[:200] + "..." if len(self.markdown) > 200 else self.markdown
        return f"ReaderResult(title={self.title!r}, len={len(self.markdown)}, preview={preview!r})"


def _detect_content_type(url: str, content_type_header: str = "") -> ContentType:
    """Detect content type from URL extension or Content-Type header."""
    url_lower = url.lower().split("?")[0].split("#")[0]

    # Check by extension
    if url_lower.endswith(".pdf"):
        return ContentType.PDF
    if url_lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp")):
        return ContentType.IMAGE
    if url_lower.endswith((".txt", ".csv", ".tsv", ".json", ".xml")):
        return ContentType.TEXT

    # Check by Content-Type header
    ct = content_type_header.lower()
    if "pdf" in ct:
        return ContentType.PDF
    if "image/" in ct:
        return ContentType.IMAGE
    if "text/plain" in ct:
        return ContentType.TEXT

    return ContentType.WEB


def _extract_title(html: str) -> str:
    """Extract <title> from HTML."""
    import re as _re
    m = _re.search(r"<title[^>]*>(.*?)</title>", html, _re.IGNORECASE | _re.DOTALL)
    return m.group(1).strip() if m else ""


def _extract_links(html: str, base_url: str) -> List[str]:
    """Extract all href links from HTML."""
    from urllib.parse import urljoin
    links = []
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE):
        href = m.group(1)
        if href.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue
        full = urljoin(base_url, href)
        if full.startswith("http"):
            links.append(full)
    return list(dict.fromkeys(links))  # deduplicate, preserve order


class SimpleReader:
    """One-call reader that converts any URL to clean markdown.

    Usage::

        reader = SimpleReader()
        result = await reader.read("https://example.com")
        print(result.markdown)

    Advanced::

        result = await reader.read(
            "https://example.com",
            extract_links=True,
            max_length=5000,
            wait_for="css:.content",
        )
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        proxy: Optional[str] = None,
    ):
        self.headless = headless
        self.timeout = timeout
        self.proxy = proxy

    async def read(
        self,
        url: str,
        *,
        extract_links: bool = False,
        max_length: int = 0,
        wait_for: Optional[str] = None,
        javascript: Optional[str] = None,
        css_selector: Optional[str] = None,
    ) -> ReaderResult:
        """Read a URL and return clean markdown content.

        Args:
            url: The URL to read.
            extract_links: If True, populate result.links.
            max_length: Truncate markdown to this length (0 = no limit).
            wait_for: Wait for this CSS selector before extracting.
            javascript: JavaScript to execute before extraction.
            css_selector: CSS selector to limit extraction scope.

        Returns:
            ReaderResult with clean markdown.
        """
        if not url or not url.startswith(("http://", "https://")):
            return ReaderResult(url=url, success=False, error="Invalid URL scheme")

        try:
            return await self._read_with_crawler(
                url,
                extract_links=extract_links,
                max_length=max_length,
                wait_for=wait_for,
                javascript=javascript,
                css_selector=css_selector,
            )
        except Exception as e:
            logger.error(f"Reader failed for {url}: {e}")
            return ReaderResult(url=url, success=False, error=str(e))

    async def read_batch(
        self,
        urls: List[str],
        *,
        extract_links: bool = False,
        max_length: int = 0,
        max_concurrent: int = 5,
    ) -> List[ReaderResult]:
        """Read multiple URLs concurrently.

        Args:
            urls: List of URLs to read.
            extract_links: If True, populate result.links.
            max_length: Truncate markdown to this length.
            max_concurrent: Max concurrent requests.

        Returns:
            List of ReaderResult, one per URL.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _read_one(u: str) -> ReaderResult:
            async with semaphore:
                return await self.read(u, extract_links=extract_links, max_length=max_length)

        return await asyncio.gather(*[_read_one(u) for u in urls])

    async def _read_with_crawler(
        self,
        url: str,
        *,
        extract_links: bool,
        max_length: int,
        wait_for: Optional[str],
        javascript: Optional[str],
        css_selector: Optional[str],
    ) -> ReaderResult:
        """Use AsyncWebCrawler for the actual fetching."""
        from .async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
        from .async_webcrawler import AsyncWebCrawler

        browser_cfg = BrowserConfig(
            headless=self.headless,
            verbose=False,
        )
        if self.proxy:
            from .async_configs import ProxyConfig as PC
            browser_cfg = BrowserConfig(
                headless=self.headless,
                verbose=False,
                proxy=PC(server=self.proxy),
            )

        extra_args = {}
        if wait_for:
            extra_args["wait_for"] = wait_for
        if javascript:
            extra_args["js_code"] = javascript
        if css_selector:
            extra_args["css_selector"] = css_selector

        run_cfg = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            verbose=False,
            page_timeout=self.timeout,
            **extra_args,
        )

        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=url, config=run_cfg)

        if not result.success:
            return ReaderResult(
                url=url,
                success=False,
                error=getattr(result, "error_message", "Crawl failed"),
            )

        # Get markdown content
        md = ""
        if hasattr(result, "markdown"):
            md_obj = result.markdown
            if hasattr(md_obj, "raw_markdown"):
                md = md_obj.raw_markdown
            elif isinstance(md_obj, str):
                md = md_obj
            else:
                md = str(md_obj) if md_obj else ""

        title = getattr(result, "title", "") or ""
        if not title and hasattr(result, "html"):
            title = _extract_title(result.html)

        # Clean up markdown
        md = self._clean_markdown(md)

        if max_length > 0 and len(md) > max_length:
            md = md[:max_length] + "\n\n[Content truncated]"

        links = []
        if extract_links and hasattr(result, "html"):
            links = _extract_links(result.html, url)

        return ReaderResult(
            url=url,
            title=title,
            markdown=md,
            content_type=ContentType.WEB,
            success=True,
            links=links,
            metadata={
                "status_code": getattr(result, "status_code", 200),
                "response_headers": getattr(result, "response_headers", {}),
            },
        )

    @staticmethod
    def _clean_markdown(md: str) -> str:
        """Clean and normalize markdown content."""
        if not md:
            return ""
        # Remove excessive blank lines
        md = re.sub(r"\n{3,}", "\n\n", md)
        # Remove HTML comments
        md = re.sub(r"<!--.*?-->", "", md, flags=re.DOTALL)
        # Remove leftover HTML tags that aren't markdown
        md = re.sub(r"<(?!br|hr|img|a|/a|/strong|/em|/b|/i|/code|/pre|/h[1-6]|/ul|/ol|/li|/p|/blockquote|/table|/tr|/td|/th|/thead|/tbody)[^>]+>", "", md)
        return md.strip()
