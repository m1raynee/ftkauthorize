from discord.utils import get
from conf import role_ids


class Roles:
    def __init__(self, guild):
        self.admin = get(guild.roles, id=role_ids['admin'])
        self.pupil = get(guild.roles, id=role_ids['pupil'])
        self.teacher = get(guild.roles, id=role_ids['teacher'])
        self.undefined = get(guild.roles, id=role_ids['undefined'])