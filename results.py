from __future__ import annotations
from flogin import Plugin, Query, Result
import tempfile
from duckchat.client import DuckChat
import aiohttp, random
from settings import DuckChatSettings
from typing import TYPE_CHECKING
from duckchat.enums import ModelType

if TYPE_CHECKING:
    from plugin import DuckChatPlugin


def get_slug() -> str:
    return "".join(
        random.choices(
            "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890", k=5
        )
    )


class OpenInTextEditorResult(Result["DuckChatPlugin"]):
    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__("Open in a text editor", auto_complete_text=get_slug())

    async def callback(self):
        assert self.plugin

        with tempfile.TemporaryFile("w", delete=False, suffix=".txt") as f:
            f.write(self.text)

            fp = f.name.replace(
                "\\\\\\\\", "/"
            )  # for some reason this works, idk why it occurs in the first place though
            await self.plugin.api.run_shell_cmd(f'notepad "{fp}"')


class AnswerResult(Result["DuckChatPlugin"]):
    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__(
            text,
            copy_text=text,
            auto_complete_text=get_slug(),
            sub="Click to reset query",
        )

    async def context_menu(self):
        return [OpenInTextEditorResult(self.text)]

    async def callback(self):
        assert self.plugin
        assert self.plugin.last_query

        await self.plugin.last_query.update(text="")
        return False


class QuestionResult(Result["DuckChatPlugin"]):
    def __init__(self, question: str):
        self.question = question
        super().__init__(
            f"Do you want to ask: {question!r}?", auto_complete_text=get_slug()
        )

    async def callback(self):
        assert self.plugin
        assert self.plugin.last_query

        resp = await self.plugin.duckchat.ask_question(self.question)
        new_results = [AnswerResult(resp)]
        await self.plugin.api.update_results(
            self.plugin.last_query.raw_text, new_results
        )
        # await self.plugin.api.change_query(self.plugin.last_query.keyword + " ")
        return False
