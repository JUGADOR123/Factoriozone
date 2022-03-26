from typing import Any

from discord import SelectOption, Interaction
from discord.ui import Select, View

from src.extras.database import FzToken


class TokenSelector(Select):
    def __init__(self, tokens: list[FzToken]):
        self.tokens = tokens
        options = []
        for token in self.tokens:
            options.append(SelectOption(label=f"{token.name} - {token.token_id}", value=token.token_id))
        super().__init__(placeholder="Select a Token", options=options, min_values=1, max_values=1)

    async def callback(self, ctx: Interaction) -> Any:
        await ctx.response.defer()
        await ctx.edit_original_message(content=f"Selected Token: {self.values[0]}", view=None)
        self.view.token = self.values[0]
        self.view.stop()


class TokenSelectorView(View):
    def __init__(self, tokens: list[FzToken]):
        super().__init__()
        self.token = None
        self.add_item(TokenSelector(tokens))
