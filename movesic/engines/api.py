import abc
from dataclasses import dataclass


@dataclass
class Playlist:
    name: str
    external_url: str


class Engine:
    @abc.abstractmethod
    def auth(self): ...

    # from
    @abc.abstractmethod
    def get_playlists(self): ...

    @abc.abstractmethod
    def get_songs(self, playlist): ...

    # to
    @abc.abstractmethod
    def find_song(self, name): ...
