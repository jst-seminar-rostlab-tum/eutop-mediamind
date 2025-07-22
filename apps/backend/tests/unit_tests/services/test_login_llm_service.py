from unittest.mock import MagicMock, patch

import pytest

from app.services.login_llm_service import LoginLLM


class DummyDriver:
    def __init__(self):
        self.page_source = (
            '<html><body><input id="user"><input id="pass"></body></html>'
        )
        self.logs = []
        self.switched_to = []
        self.quit_called = False

    def get_log(self, _):
        return self.logs

    def get_screenshot_as_png(self):
        return b"fakeimg"

    def execute_script(self, script, *args):
        if "shadowRoot" in script:
            return None
        if "querySelectorAll" in script:
            return []
        return None

    def switch_to(self):
        return self

    def frame(self, _):
        self.switched_to.append("frame")

    def default_content(self):
        self.switched_to.append("default")

    def get(self, _):
        pass

    def quit(self):
        self.quit_called = True


class DummyWait:
    def until(self, cond):
        return MagicMock()


@pytest.mark.asyncio
async def test_llm_response_to_json_valid():
    raw = '{"user_input": "//input[@id=\'user\']"}'
    result = LoginLLM._llm_response_to_json(raw)
    assert result["user_input"] == "//input[@id='user']"


@pytest.mark.asyncio
async def test_llm_response_to_json_invalid():
    raw = "not a json"
    result = LoginLLM._llm_response_to_json(raw)
    assert result is None


@pytest.mark.asyncio
async def test_add_new_keys_to_config_merges():
    config = {"user_input": "foo"}
    new_keys = {"user_input": "bar", "password_input": "baz"}
    merged = LoginLLM._add_new_keys_to_config(new_keys, config)
    assert isinstance(merged["user_input"], list)
    assert "bar" in merged["user_input"]
    assert merged["password_input"] == "baz"


@pytest.mark.asyncio
async def test_custom_clean_html_removes_scripts():
    html = "<body><script>bad()</script><div>ok</div></body>"
    cleaned = LoginLLM._custom_clean_html(html)
    assert "script" not in cleaned
    assert "ok" in cleaned


@pytest.mark.asyncio
async def test_split_html_chunks():
    html = "a" * 1000
    with patch.object(LoginLLM, "_count_tokens", return_value=2000):
        chunks = LoginLLM._split_html(html, 500)
        assert len(chunks) > 1


@pytest.mark.asyncio
async def test_take_screenshot_success():
    driver = DummyDriver()
    img = LoginLLM._take_screenshot(driver)
    assert img.startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_wait_for_page_change_200():
    driver = DummyDriver()
    driver.logs = [{"message": '"Network.responseReceived" "status":200'}]
    assert LoginLLM._wait_for_page_change(driver)


@pytest.mark.asyncio
async def test_wait_for_page_change_no_200():
    driver = DummyDriver()
    driver.logs = [{"message": "something else"}]
    assert not LoginLLM._wait_for_page_change(driver)


@pytest.mark.asyncio
async def test_reset_flags():
    LoginLLM.cookies_accepted = True
    LoginLLM.notifications_removed = True
    LoginLLM.user_inserted = True
    LoginLLM.password_inserted = True
    LoginLLM.submitted = True
    LoginLLM._reset_flags()
    assert not LoginLLM.cookies_accepted
    assert not LoginLLM.notifications_removed
    assert not LoginLLM.user_inserted
    assert not LoginLLM.password_inserted
    assert not LoginLLM.submitted
