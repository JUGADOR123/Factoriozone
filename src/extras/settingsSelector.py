from typing import Any

from discord import SelectOption, Interaction
from discord.ui import Select, View


class RegionSelector(Select):
    def __init__(self, regions: dict):
        self.regions = regions
        options = []
        for key in regions.keys():
            options.append(SelectOption(label=regions[key], value=key))
        super().__init__(placeholder="Select a Region", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction) -> Any:
        await interaction.response.defer()
        self.view.selected_region = self.values[0]
        if _check_for_settings(self.view):
            self.view.stop()


class SavesSelector(Select):
    def __init__(self, saves: dict):
        self.saves = saves
        options = []
        for key in saves.keys():
            options.append(SelectOption(label=saves[key], value=key))
        super().__init__(placeholder="Select a Save File", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction) -> Any:
        await interaction.response.defer()
        self.view.selected_save = self.values[0]
        if _check_for_settings(self.view):
            self.view.stop()


class VersionSelector(Select):
    def __init__(self, versions: dict):
        self.versions = versions
        options = []
        keys = list(versions.keys())
        for index in range(0, 24):
            options.append(SelectOption(label=versions[keys[index]], value=keys[index]))
        super().__init__(placeholder="Select a Version", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction) -> Any:
        await interaction.response.defer()
        self.view.selected_version = self.values[0]
        if _check_for_settings(self.view):
            self.view.stop()


class SettingsSelectorView(View):
    def __init__(self, regions: dict, saves: dict, versions: dict):
        super().__init__()
        self.selected_region = None
        self.selected_save = None
        self.selected_version = None
        self.add_item(RegionSelector(regions))
        self.add_item(SavesSelector(saves))
        self.add_item(VersionSelector(versions))


def _check_for_settings(parent: SettingsSelectorView):
    if parent.selected_region is not None and parent.selected_version is not None and parent.selected_save is not None:
        return True
