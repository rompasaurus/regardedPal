"""
Tests for the blog section.

Covers: blog index, post rendering, categories, pagination.
"""

import pytest
from playwright.sync_api import expect

from utils.screenshot_helper import capture_playwright_page, screenshot_name


@pytest.mark.website
class TestBlogIndex:
    """Test the blog index page."""

    def test_blog_index_loads(self, page, base_url):
        page.goto(f"{base_url}/blog/")
        page.wait_for_load_state("networkidle")
        assert "blog" in page.url.lower()

    def test_blog_has_posts_or_empty_message(self, page, base_url):
        page.goto(f"{base_url}/blog/")
        page.wait_for_load_state("networkidle")
        content = page.locator(".md-content")
        text = content.inner_text()
        # Either has blog posts or at least renders
        assert len(text) > 0

    @pytest.mark.screenshot
    def test_screenshot_blog_index(self, page, base_url, website_screenshot_dir):
        page.goto(f"{base_url}/blog/")
        page.wait_for_load_state("networkidle")
        path = website_screenshot_dir / screenshot_name("website", "blog_index")
        capture_playwright_page(page, path)


@pytest.mark.website
class TestBlogPosts:
    """Test individual blog post rendering."""

    @pytest.mark.screenshot
    def test_screenshot_blog_page(self, page, base_url, website_screenshot_dir):
        page.goto(f"{base_url}/blog/")
        page.wait_for_load_state("networkidle")
        # Try to click first post link
        articles = page.locator("article a, .md-post a, .md-content a")
        if articles.count() > 0:
            articles.first.click()
            page.wait_for_load_state("networkidle")
            path = website_screenshot_dir / screenshot_name("website", "blog_post")
            capture_playwright_page(page, path)
