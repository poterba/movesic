import abc
from dataclasses import dataclass


@dataclass
class UserInfo:
    name: str
    avatar: str
    id: str
    external_url: str


@dataclass
class Song:
    name: str
    author: str
    id: str
    external_url: str


@dataclass
class Playlist:
    name: str
    id: str
    external_url: str


class Engine:
    # from
    @abc.abstractmethod
    def info(self): ...

    @abc.abstractmethod
    def get_playlists(self): ...

    @abc.abstractmethod
    def get_songs(self, playlist): ...

    # to
    @abc.abstractmethod
    def find_song(self, name, author=None): ...
