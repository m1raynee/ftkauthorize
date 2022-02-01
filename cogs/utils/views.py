from disnake import ui
import disnake

class Linked(ui.View):
    def __init__(self, link, label='Перейти'):
        super().__init__(timeout=None)
        self.add_item(
            ui.Button(
                style=disnake.ButtonStyle.link,
                label=label,
                url=link
            )
        )
        self.stop()