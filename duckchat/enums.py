from enum import Enum


class ModelType(Enum):
    GPT4o = "gpt-4o-mini"
    Claude = "claude-3-haiku-20240307"
    Llama = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    Mixtral = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    @classmethod
    def from_settings(cls, txt: str):
        return {
            "ChatGPT-4o": cls.GPT4o,
            "Claude": cls.Claude,
            "Llama": cls.Llama,
            "Mixtral": cls.Mixtral,
        }[txt]
