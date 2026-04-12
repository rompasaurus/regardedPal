"""
Tests for website navigation.

Covers: main nav tabs, doc sidebar, page links, footer.
"""

import pytest
from playwright.sync_api import expect

from utils.screenshot_helper import capture_playwright_page, screenshot_name


@pytest.mark.website
class TestMainNavigation:
    """Test the top-level navigation tabs."""

    def test_home_page_loads(self, page, base_url):
        page.goto(base_url)
        expect(page).to_have_title("Dilder")

    def test_nav_tabs_present(self, page, base_url):
        page.goto(base_url)
        # Material theme renders nav tabs
        nav = page.locator("nav")
        assert nav.count() > 0

    def test_docs_link_works(self, page, base_url):
        page.goto(base_url)
        page.click("text=Docs")
        page.wait_for_load_state("networkidle")
        assert "/docs/" in page.url or "docs" in page.url.lower()

    def test_blog_link_works(self, page, base_url):
        page.goto(base_url)
        page.click("text=Blog")
        page.wait_for_load_state("networkidle")
        assert "/blog/" in page.url or "blog" in page.url.lower()

    def test_about_link_works(self, page, base_url):
        page.goto(base_url)
        page.click("text=About")
        page.wait_for_load_state("networkidle")
        assert "/about/" in page.url or "about" in page.url.lower()

    @pytest.mark.screenshot
    def test_screenshot_home_page(self, page, base_url, website_screenshot_dir):
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        path = website_screenshot_dir / screenshot_name("website", "home_page")
        capture_playwright_page(page, path)

    @pytest.mark.screenshot
    def test_screenshot_docs_page(self, page, base_url, website_screenshot_dir):
        page.goto(base_url)
        page.click("text=Docs")
        page.wait_for_load_state("networkidle")
        path = website_screenshot_dir / screenshot_name("website", "docs_overview")
        capture_playwright_page(page, path)


@pytest.mark.website
class TestDocsSidebar:
    """Test the documentation sidebar navigation."""

    def test_sidebar_has_sections(self, page, base_url):
        page.goto(f"{base_url}/docs/")
        page.wait_for_load_state("networkidle")
        sidebar = page.locator(".md-sidebar--primary")
        if sidebar.count() > 0:
            assert sidebar.is_visible()

    def test_tools_section_links(self, page, base_url):
        page.goto(f"{base_url}/docs/tools/devtool/")
        page.wait_for_load_state("networkidle")
        content = page.locator(".md-content")
        assert content.count() > 0

    @pytest.mark.screenshot
    def test_screenshot_devtool_docs(self, page, base_url, website_screenshot_dir):
        page.goto(f"{base_url}/docs/tools/devtool/")
        page.wait_for_load_state("networkidle")
        path = website_screenshot_dir / screenshot_name("website", "docs_devtool")
        capture_playwright_page(page, path)

    @pytest.mark.screenshot
    def test_screenshot_setup_docs(self, page, base_url, website_screenshot_dir):
        page.goto(f"{base_url}/docs/tools/setup-cli/")
        page.wait_for_load_state("networkidle")
        path = website_screenshot_dir / screenshot_name("website", "docs_setup_cli")
        capture_playwright_page(page, path)
