"""
Tests for responsive layout.

Captures screenshots at desktop, tablet, and mobile viewports
to verify the site looks good at all breakpoints.
"""

import pytest

from utils.screenshot_helper import capture_playwright_page, screenshot_name

VIEWPORTS = [
    ("desktop", 1280, 800),
    ("tablet", 768, 1024),
    ("mobile", 375, 812),
]


@pytest.mark.website
@pytest.mark.screenshot
class TestResponsiveLayouts:
    """Capture screenshots at multiple viewport sizes."""

    @pytest.mark.parametrize("name,width,height", VIEWPORTS)
    def test_home_responsive(self, browser_context, mkdocs_server, website_screenshot_dir,
                              name, width, height):
        page = browser_context.new_page()
        page.set_viewport_size({"width": width, "height": height})
        page.goto(mkdocs_server)
        page.wait_for_load_state("networkidle")
        path = website_screenshot_dir / screenshot_name("website", f"home_{name}")
        capture_playwright_page(page, path)
        page.close()

    @pytest.mark.parametrize("name,width,height", VIEWPORTS)
    def test_docs_responsive(self, browser_context, mkdocs_server, website_screenshot_dir,
                              name, width, height):
        page = browser_context.new_page()
        page.set_viewport_size({"width": width, "height": height})
        page.goto(f"{mkdocs_server}/docs/")
        page.wait_for_load_state("networkidle")
        path = website_screenshot_dir / screenshot_name("website", f"docs_{name}")
        capture_playwright_page(page, path)
        page.close()

    @pytest.mark.parametrize("name,width,height", VIEWPORTS)
    def test_blog_responsive(self, browser_context, mkdocs_server, website_screenshot_dir,
                              name, width, height):
        page = browser_context.new_page()
        page.set_viewport_size({"width": width, "height": height})
        page.goto(f"{mkdocs_server}/blog/")
        page.wait_for_load_state("networkidle")
        path = website_screenshot_dir / screenshot_name("website", f"blog_{name}")
        capture_playwright_page(page, path)
        page.close()
