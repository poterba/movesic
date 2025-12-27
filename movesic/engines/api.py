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
    id: str
    external_url: str
    name: str
    author: str
    album: str
    cover: bytes | str


@dataclass
class Playlist:
    name: str
    id: str
    external_url: str

    def __hash__(self):
        return hash(self.id)


class Engine:
    # user

    @abc.abstractmethod
    def info(self) -> UserInfo | None: ...

    @abc.abstractmethod
    def authenticate(self): ...

    # playlists

    @abc.abstractmethod
    def get_playlists(self) -> list[Playlist]: ...

    @abc.abstractmethod
    def get_playlist(self, id) -> Playlist: ...

    @abc.abstractmethod
    def add_playlist(self, name, description="") -> Playlist: ...

    @abc.abstractmethod
    def delete_playlist(self, playlist: Playlist): ...

    # songs

    @abc.abstractmethod
    def get_songs(self, playlist: Playlist) -> list[Song]: ...

    @abc.abstractmethod
    def find_song(self, name, author=None) -> list[Song]: ...

    @abc.abstractmethod
    def add_song_to_playlist(self, song: Song, playlist: Playlist): ...
