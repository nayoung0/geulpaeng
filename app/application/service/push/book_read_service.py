from app.application.service.push.base_service import Checker
from app.domain.model.push import Channel


class 책읽어또(Checker):
    def __init__(self):
        super().__init__()
        self.channel = Channel.책읽어또.value

    def check(self):
        pass
