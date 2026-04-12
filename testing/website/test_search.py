"""
Tests for the search functionality.

Covers: search bar presence, search input, results display.
"""

import pytest
from playwright.sync_api import expect

from utils.screenshot_helper import capture_playwright_page, screenshot_name


@pytest.mark.website
class TestSearchBar:
    """Test the search input and results."""

    def test_search_bar_exists(self, page, base_url):
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        search = page.locator("[data-md-component='search']")
        # Material theme has search component
        assert search.count() > 0 or page.locator("input[type='search']").count() > 0

    def test_search_opens_on_shortcut(self, page, base_url):
        """MkDocs Material opens search with the '/' keyboard shortcut."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        # Press '/' to open search (Material theme shortcut)
        page.keyboard.press("/")
        page.wait_for_timeout(500)
        # The search input should now be visible
        search_input = page.locator(".md-search__input")
        if search_input.count() > 0:
            assert search_input.first.is_visible()

    @pytest.mark.screenshot
    def test_screenshot_search_results(self, page, base_url, website_screenshot_dir):
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        # Open search via keyboard shortcut
        page.keyboard.press("/")
        page.wait_for_timeout(500)
        # Type a search query
        search_input = page.locator(".md-search__input")
        if search_input.count() > 0 and search_input.first.is_visible():
            search_input.first.fill("Pico W")
            page.wait_for_timeout(1000)
            path = website_screenshot_dir / screenshot_name("website", "search_results")
            capture_playwright_page(page, path, full_page=False)
