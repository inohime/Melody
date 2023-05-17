from mel_yum import MelodyYUM
from pypresence import Presence
import asyncio
import constants as const
import time
import datetime


class MelodyClient():
    def __init__(self) -> None:
        self._rpc_client_active = False
        self._start_time = 0

    def start(self):
        self._attach_rpc()

    def update(self, yum: MelodyYUM):
        yum.do_prefetch()
        self._start_time = int(time.time())

        while self.client_is_active():
            if yum.yum_is_active():
                song = yum.current_song()
                print(datetime.datetime.now(), ":", song)
                self._rpc_client.update(
                    large_image=song.album_cover,
                    large_text=f"on {song.album_title} - {song.song_length}",
                    details=song.song_title,
                    state=f"by {song.artist_name}",
                    buttons=[
                        {
                            "label": "Play on YouTube Music",
                            "url": f"https://music.youtube.com/watch?v={song.song_id}"
                        }
                    ],
                    start=self._start_time,
                )
            else:
                self._rpc_client.update(details="Idle..", start=self._start_time)

            time.sleep(15)

    def kill_client(self):
        self._detach_rpc()

    def client_is_active(self) -> bool:
        return self._rpc_client_active

    def _attach_rpc(self):
        # pypresence requires an existing event loop in order to work
        # since this is running in a separate thread
        asyncio.set_event_loop(asyncio.new_event_loop())

        self._rpc_client = Presence(const.DEVELOPER_APP_ID)
        self._rpc_client.connect()
        self._rpc_client_active = True

    def _detach_rpc(self):
        self._rpc_client_active = False