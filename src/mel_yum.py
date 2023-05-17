from bs4 import BeautifulSoup as Soup
from dataclasses import dataclass
from enum import Enum
from mel_db import MelodyDB
from requests_html import HTMLSession as Request
import atexit
import datetime
import re
import threading


@dataclass(frozen=True)
class Song:
    unfiltered_song_title: str
    album_title: str
    album_cover: str
    artist_name: str
    song_length: str
    song_title: str
    filtered: bool
    song_url: str
    song_id: str

    def __hash__(self) -> int:
        return hash((
            self.unfiltered_song_title,
            self.album_title,
            self.album_cover,
            self.artist_name,
            self.song_length,
            self.song_title,
            self.filtered,
            self.song_url,
            self.song_id
        ))

    @staticmethod
    def default():
        return Song(
            "",
            "",
            "",
            "",
            "",
            "",
            True,
            "",
            ""
        )


class YUMState(Enum):
    IDLE = 0,
    ACTIVE = 1


class PrefetchState(Enum):
    FAILED = 0,
    OK = 1


class MelodyYUM:
    def __init__(self) -> None:
        atexit.register(self._quit)

        self._melody_db = MelodyDB()

        self.request = Request()
        self.request.browser
        self._video_content = None

        self._yum_state = YUMState.IDLE
        self._yum_in_query = False

        self._prefetch_state = PrefetchState.FAILED

        self.__video_url = ""
        self.__video_id = ""

        self._use_filter = True

        self._curr_song = Song.default()
        self._song_book = dict({"": self._curr_song})

        self._yum_parsed = threading.Event()
        self._block_once = False

    def update_song(self, ev: threading.Event):
        while not ev.is_set():
            if self._yum_in_db():
                self.__video_id = self._split_video_url(self.__video_url)
                self._curr_song = self._fetch_song(self.__video_id)

                if not self._block_once:
                    self._yum_parsed.set()
                    self._prefetch_state = PrefetchState.OK
                    self._block_once = True

                self._yum_state = YUMState.ACTIVE
            else:
                self._yum_state = YUMState.IDLE

            ev.wait(5)

    def current_song(self) -> Song:
        return self._curr_song

    def do_prefetch(self):
        count = 15

        while not self._yum_parsed.is_set():
            self._yum_parsed.wait(1)
            count -= 1
            if count <= 0 and not self._yum_parsed.is_set():
                self._prefetch_state = PrefetchState.FAILED
                print("Failed to prefetch content")
                self._yum_parsed.set()

    def filter_title(self, filter: bool):
        self._use_filter = filter

    def filter_state(self) -> bool:
        return self._use_filter == True

    def prefetch_ok(self) -> bool:
        return self._prefetch_state == PrefetchState.OK

    def _quit(self):
        print("destroyed!")
        self.request.close()

    def _parse_song(self, song_id) -> Song:
        # this is the inverse, song_url is actually video_url, but it's still treated as the song
        self._song_url = f"https://www.youtube.com/watch?v={song_id}"
        soup = self._fetch_song_content(self._song_url)

        # get all of the data of the song now

        name_list = [
            soup.find("link", itemprop="name"),
            soup.find("span", itemprop="author").next.next
        ]
        tmp_artist_name = name_list[1]["content"] if name_list[1] else name_list[0]["content"]
        artist_name = self._parse_artist_name(tmp_artist_name)

        tmp_song_title = soup.find("meta", itemprop="name")["content"]
        tmp_title_buffer = tmp_song_title

        song_title = ""

        if self._use_filter:
            song_title = self._parse_song_title(tmp_song_title, artist_name)
        else:
            song_title = tmp_title_buffer

        tmp_album_cover = soup.find("meta", {"property": "og:image"})
        album_cover = tmp_album_cover[
            "content"] if tmp_album_cover else f"https://img.youtube.com/vi/{song_id}/0.jpg"

        album_title = self._parse_album_title(soup, song_title)

        tmp_song_length = soup.find(
            "meta", {"itemprop": "duration"})["content"]
        time_strip = datetime.datetime.strptime(tmp_song_length, "PT%MM%SS")
        to_timer = datetime.timedelta(
            minutes=time_strip.minute, seconds=time_strip.second)
        song_duration_in_sec = to_timer.total_seconds()
        song_len_min, song_len_sec = divmod(
            datetime.timedelta(seconds=song_duration_in_sec).seconds, 60)
        song_length = f"{int(song_len_min):01d}" + ":" + \
            f"{int(song_len_sec):02d}"

        return Song(
            unfiltered_song_title=tmp_title_buffer,

            album_title=album_title,
            album_cover=album_cover,

            artist_name=artist_name,

            song_length=song_length,

            song_title=song_title,
            filtered=True if self._use_filter else False,

            song_url=self._song_url,
            song_id=self.__video_id
        )

    def _fetch_song(self, song_id: str) -> Song:
        def __rm_par_add():
            # remove, parse, add song
            self._remove_song(song_id)
            song = self._parse_song(song_id)
            self._add_song(song_id, song)

        if song_id not in self._song_book:
            # parse a new song and add it to the cache
            new_song = self._parse_song(song_id)
            self._add_song(song_id, new_song)

            return new_song

        # because fields are frozen,
        # the easiest thing we can do is remove the song from the dict and replace it
        song = self._song_book[song_id]

        if self._use_filter:
            cmp_list = [
                song.song_title != song.unfiltered_song_title,
                song.song_title == song.unfiltered_song_title and song.filtered
            ]

            if any(cmp_list):
                return self._song_book[song_id]

            # title was filtered so we need to re-parse the song
            __rm_par_add()

            return song
        else:
            song = self._song_book[song_id]

            if song.song_title == song.unfiltered_song_title:
                return self._song_book[song_id]

            __rm_par_add()

            return song

    def _add_song(self, song_id: str, song: Song):
        self._song_book[song_id] = song

    def _remove_song(self, song_id: str):
        del self._song_book[song_id]

    def _fetch_song_content(self, song_url) -> Soup:
        self._video_content = self.request.get(song_url)
        self._video_content.html.render(sleep=1, timeout=10)

        return Soup(self._video_content.html.html, "lxml")

    def _parse_artist_name(self, name: str) -> str:
        if "- Topic" in name:
            pos = name.index("- Topic")
            name = name[0:pos - 1]

        return name

    def _parse_song_title(self, title: str, artist_name: str) -> str:
        # remove "Official" and any following words after
        x = re.search(r"official.*", title.lower())
        if x:
            # if there is a space before the official, strip it
            if title[x.start() - 2: x.start() - 1] == " ":
                title = title[0:x.start() - 2]
            else:
                title = title[0:x.start() - 1]

        name_bucket = ''.join(artist_name.split(' '))
        title_bucket = ''.join(title.split(' '))
        title_chunks = title.split(' ')

        en_dash = '\u2013'
        char_cmp_list = ["『", "』", "「", "」"]
        first_char_matched = False
        name_found = False

        # strip non-alphanumeric characters from the title
        for na_char in re.finditer(r"[^\w\d\s:]", title):
            char = na_char.group()

            # beginning bracket
            if char in char_cmp_list[0::2]:
                # for when the channel name is in the title
                # break this into chunks and check if (per space) the channel name is in the title
                for chunk in title_chunks:
                    if first_char_matched:
                        break

                    tb_char_pos = title_bucket.find(char)
                    if tb_char_pos == -1:
                        continue

                    this_chunk = chunk.lower()
                    this_tb_chunk = title_bucket[0: tb_char_pos].lower()

                    if this_chunk in artist_name.lower() or this_tb_chunk in name_bucket.lower():
                        # check if there are two adjacent non-alphanumeric chars
                        # and remove everything up until the name of the song
                        if title[na_char.end(): na_char.end() + 1] in char_cmp_list[0::len(char_cmp_list)]:
                            # non-alphanumeric char may have two, so we have to capture both
                            title = title[na_char.end() + 1:]
                        else:
                            title = title[na_char.end():]

                        first_char_matched = True
                        break

            if char in char_cmp_list[1::2]:
                char_pos = title.find(char)
                if char_pos == -1:
                    continue

                # if the bracket was matched, remove the end bracket
                title = title[:char_pos +
                              1] if not first_char_matched else title[:char_pos]

            # parse normal titles for song artist name (where they have a dash)
            elif char not in char_cmp_list:
                if char == '-' or char == en_dash:
                    for chunk in title_chunks:
                        if name_found:
                            break

                        tb_char_pos = title_bucket.find(char)
                        if tb_char_pos == -1:
                            continue

                        name_in_title = chunk.lower()
                        name_in_tb = title_bucket[0: tb_char_pos].lower()

                        if name_in_title in artist_name.lower() or name_in_tb in name_bucket.lower():
                            title = title[na_char.end() + 1:]
                            name_found = True

        if len(title) >= 2:
            return title

        elif len(title) <= 0 or title == " ":
            print("Something went wrong, rejecting parsed title!")
            return ' '.join([x for x in title_chunks])

        else:
            return title + ' '

    def _parse_album_title(self, soup: Soup, song_title: str) -> str:
        desc_details = soup(text=lambda x: "Provided to YouTube" in x.text)
        if desc_details:
            try:
                return str(desc_details[0]).strip().split("\n\n")[2]

            except IndexError as e:
                print("Improper description formatting:", e)
                return song_title
        else:
            return song_title

    def _yum_in_db(self) -> bool:
        self._melody_db.copy_fetch()
        url_match = "music.youtube.com/watch?v="
        for url in self._melody_db.query_data:
            if url_match in url[0]:
                self.__video_url = url[0]
                self._yum_in_query = True
                break
            else:
                self.__video_url = ""
                self._yum_in_query = False

        return self._yum_in_query

    def _split_video_url(self, str: str) -> str:
        if "list" in str:
            return str.split('=', 1)[1].split('&')[0]

        return str.split('=')[1]

    def yum_is_active(self) -> bool:
        return self._yum_state == YUMState.ACTIVE
