from __future__ import annotations
from flogin import Plugin, Query, Result
import tempfile
from duckchat.client import DuckChat
import aiohttp, random
from settings import DuckChatSettings
from duckchat.enums import ModelType

class OpenInTextEditorResult(Result["DuckChatPlugin"]):
    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__("Open in a text editor", auto_complete_text="".join(random.choices("qwertyuiopsdfghjklxcvbnm") ))
    
    async def callback(self):
        assert self.plugin

        with tempfile.TemporaryFile("w", delete=False, suffix=".txt") as f:
            f.write(self.text)

            fp = f.name.replace("\\\\\\\\", "/")
            await self.plugin.api.run_shell_cmd(f'notepad "{fp}"')

class AnswerResult(Result["DuckChatPlugin"]):
    def __init__(self, text:str) -> None:
        self.text = text
        super().__init__(text, copy_text=text, auto_complete_text="".join(random.choices("qwertyuiopsdfghjklxcvbnm") ), sub="Click to reset query")
    
    async def context_menu(self):
        return [
            OpenInTextEditorResult(self.text)
        ]

    async def callback(self):
        assert self.plugin
        assert self.plugin.last_query

        await self.plugin.last_query.update(text="")
        return False

class QuestionResult(Result["DuckChatPlugin"]):
    def __init__(self, question: str):
        self.question = question
        super().__init__(f"Do you want to ask: {question!r}?",auto_complete_text="".join(random.choices("qwertyuiopsdfghjklxcvbnm") ))
    async def callback(self):
        assert self.plugin
        assert self.plugin.last_query

        resp = await self.plugin.duckchat.ask_question(self.question)
        new_results = [
            AnswerResult(resp)
        ]
        await self.plugin.api.update_results(self.plugin.last_query.raw_text, new_results) # type: ignore
        #await self.plugin.api.change_query(self.plugin.last_query.keyword + " ")
        return False
    
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
