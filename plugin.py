from __future__ import annotations
from flogin import Plugin, Query
from duckchat.client import DuckChat
import aiohttp
from settings import DuckChatSettings
from duckchat.enums import ModelType
from .results import QuestionResult


class DuckChatPlugin(Plugin[DuckChatSettings]):
    session: aiohttp.ClientSession
    _duckchat: DuckChat | None = None

    @property
    def model(self) -> ModelType:
        return ModelType.from_settings(self.settings.model)

    @property
    def duckchat(self) -> DuckChat:
        if self._duckchat is None or self._duckchat.model != self.model:
            self._duckchat = DuckChat(self.model, self.session)
        return self._duckchat

    async def start(self):
        async with aiohttp.ClientSession() as cs:
            self.session = cs
            await super().start()

    @Plugin.search()
    async def on_search(self, query: Query):
        return QuestionResult(query.text)
