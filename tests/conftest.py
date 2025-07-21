# tests/conftest.py
import pytest
import playwright.async_api as pw_api

@pytest.fixture(autouse=True)
def force_playwright_headless(monkeypatch):
    """
    Intercepta playwright.async_api.async_playwright() para que
    los BrowserType (chromium, firefox, webkit) siempre lancen headless=True.
    """
    orig_async_playwright = pw_api.async_playwright

    async def fake_async_playwright():
        # Obtén el objeto real
        ap = await orig_async_playwright()

        # Clase envoltorio para inyectar headless=True en .launch()
        class HeadlessWrapper:
            def __init__(self, real_bt):
                self._real = real_bt
            async def launch(self, *args, **kwargs):
                # forzar headless, mantén los demás kwargs
                kwargs.setdefault("headless", True)
                return await self._real.launch(*args, **kwargs)
            # delega cualquier otro atributo al objeto real
            def __getattr__(self, name):
                return getattr(self._real, name)

        # Envuelve los tres tipos de navegador
        ap.chromium = HeadlessWrapper(ap.chromium)
        ap.firefox  = HeadlessWrapper(ap.firefox)
        ap.webkit   = HeadlessWrapper(ap.webkit)
        return ap

    # Patchea async_playwright en el módulo
    monkeypatch.setattr(pw_api, "async_playwright", fake_async_playwright)
