import atexit
import time

from cloakbrowser import launch

from scraper.config import BASE_URL, HEADLESS, VIEWPORT, PAGE_LOAD_TIMEOUT

_browser = None
_context = None
_page = None


def get_browser():
    global _browser
    if _browser is None:
        _browser = launch(headless=HEADLESS)
        atexit.register(shutdown)
    return _browser


def shutdown():
    global _browser, _context, _page
    if _page:
        try:
            _page.close()
        except Exception:
            pass
        _page = None
    if _context:
        try:
            _context.close()
        except Exception:
            pass
        _context = None
    if _browser:
        try:
            _browser.close()
        except Exception:
            pass
        _browser = None


def _get_page():
    """获取全局持久化 page（首次自动创建 + 过 Vercel 挑战）。"""
    global _context, _page
    if _page is None or _page.is_closed():
        browser = get_browser()
        _context = browser.new_context(viewport=VIEWPORT)
        _page = _context.new_page()
        _page.set_default_timeout(PAGE_LOAD_TIMEOUT)
        _ensure_session()
    return _page


def _ensure_session():
    """持久化 page 过 Vercel 挑战，最多重试 5 次。"""
    for attempt in range(5):
        _page.goto(BASE_URL, wait_until="networkidle")
        try:
            title = _page.title()
        except Exception:
            title = ""
        if "Security" not in title:
            return
        time.sleep(2)
    raise RuntimeError(f"Failed to bypass Vercel challenge after 5 attempts. Last title: {title}")


def _evaluate_fetch(url: str, page=None):
    """执行 fetch 并返回完整 JSON 响应。"""
    if page is None:
        page = _get_page()

    for attempt in range(3):
        try:
            return page.evaluate(f"""
                fetch('{url}')
                    .then(r => {{
                        if (!r.ok) throw new Error('API error: HTTP ' + r.status);
                        return r.json();
                    }})
            """)
        except Exception:
            if attempt < 2:
                time.sleep(1)
            else:
                raise


def fetch_api(api_path: str) -> dict:
    """过 Vercel 验证后调用 API，返回 data 字段内容。"""
    url = api_path if api_path.startswith("/") else f"/{api_path}"
    result = _evaluate_fetch(url)
    data = result.get("data", result) if isinstance(result, dict) else result
    return data


def fetch_api_full(api_path: str) -> dict:
    """过 Vercel 验证后调用 API，返回完整 JSON 响应。"""
    url = api_path if api_path.startswith("/") else f"/{api_path}"
    return _evaluate_fetch(url)
