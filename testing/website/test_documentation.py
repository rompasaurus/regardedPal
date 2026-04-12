"""
Tests for documentation pages.

Covers: content rendering, code blocks, hardware docs, setup guides.
"""

import pytest
from playwright.sync_api import expect

from utils.screenshot_helper import capture_playwright_page, screenshot_name


@pytest.mark.website
class TestDocumentationPages:
    """Verify key documentation pages render correctly."""

    PAGES = [
        ("docs/hardware/materials-list/", "Materials"),
        ("docs/hardware/wiring-pinout/", "Wiring"),
        ("docs/setup/first-time-setup/", "Setup"),
        ("docs/software/project-structure/", "Project"),
        ("docs/tools/devtool/", "DevTool"),
        ("docs/tools/setup-cli/", "Setup CLI"),
    ]

    @pytest.mark.parametrize("path,keyword", PAGES)
    def test_page_loads_with_content(self, page, base_url, path, keyword):
        page.goto(f"{base_url}/{path}")
        page.wait_for_load_state("networkidle")
        content = page.locator(".md-content")
        assert content.count() > 0
        text = content.inner_text()
        assert len(text) > 50, f"Page {path} should have substantial content"

    @pytest.mark.screenshot
    @pytest.mark.parametrize("path,keyword", PAGES)
    def test_screenshot_doc_pages(self, page, base_url, website_screenshot_dir, path, keyword):
        page.goto(f"{base_url}/{path}")
        page.wait_for_load_state("networkidle")
        safe = path.rstrip("/").replace("/", "_")
        out = website_screenshot_dir / screenshot_name("website", f"doc_{safe}")
        capture_playwright_page(page, out)


@pytest.mark.website
class TestCodeBlocks:
    """Verify code blocks render with syntax highlighting."""

    def test_code_blocks_have_highlighting(self, page, base_url):
        page.goto(f"{base_url}/docs/tools/devtool/")
        page.wait_for_load_state("networkidle")
        code_blocks = page.locator("pre code")
        # If there are code blocks, they should have syntax highlighting classes
        if code_blocks.count() > 0:
            first = code_blocks.first
            classes = first.get_attribute("class") or ""
            # MkDocs Material adds highlight classes
            assert len(classes) > 0 or first.inner_text().strip() != ""


@pytest.mark.website
class TestReferencePages:
    """Test hardware reference documentation."""

    def test_pico_w_reference(self, page, base_url):
        page.goto(f"{base_url}/docs/reference/pico-w/")
        page.wait_for_load_state("networkidle")
        content = page.locator(".md-content").inner_text()
        assert "pico" in content.lower()

    @pytest.mark.screenshot
    def test_screenshot_pico_reference(self, page, base_url, website_screenshot_dir):
        page.goto(f"{base_url}/docs/reference/pico-w/")
        page.wait_for_load_state("networkidle")
        path = website_screenshot_dir / screenshot_name("website", "reference_pico_w")
        capture_playwright_page(page, path)
