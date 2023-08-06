from contextlib import closing
import constants as const
import mel_browser as browser
import shutil
import sqlite3


class MelodyDB:
    def __init__(self) -> None:
        self._query_data = None
        self._query_op = None
        self._database = None
        (self._browser, self._renderer) = browser.fetch_browser()
        self._br_mapping = self._apply_mapping()

    def copy_fetch(self):
        # make/update a copy of the browser database
        # so we can run queries on fresh data
        def __update_copy_db(
            query_op: str,
            history_path: str,
            history_copy_path: str
        ):
            shutil.copy(history_path, history_copy_path)
            self.query_op = self._get_query_op(query_op)
            self.database = history_copy_path

        for (browser, renderer), (history_path, history_copy_path) in self._br_mapping.items():
            if browser == self._browser and renderer == self._renderer:
                __update_copy_db(renderer, history_path, history_copy_path)
                break

        with closing(sqlite3.connect(self.database)) as self._db:
            self._do_query(self.query_op)

    def _get_query_op(self, renderer: str) -> str:
        if renderer == "Blink":
            return "SELECT url FROM urls ORDER BY last_visit_time DESC LIMIT 11"

        # assume it's gecko
        return "SELECT url FROM moz_places ORDER BY last_visit_date DESC LIMIT 11"

    def _do_query(self, sql_cmd):
        with closing(self._db.cursor()) as self._cursor:
            self._cursor.execute(sql_cmd)
            self.query_data = self._cursor.fetchall()

    def _apply_mapping(self) -> dict[tuple[str, str], tuple[str, str]]:
        return {
            ("CHROM", "Blink"): (const.CHROME_HISTORY_PATH, const.CHROME_HISTORY_COPY_PATH),
            ("MSEDGE", "Blink"): (const.EDGE_HISTORY_PATH, const.EDGE_HISTORY_COPY_PATH),
            ("FIREFOX", "Gecko"): (const.FIREFOX_HISTORY_PATH, const.FIREFOX_HISTORY_COPY_PATH),
            ("LIBREWOLF", "Gecko"): (const.LIBREWOLF_HISTORY_PATH, const.LIBREWOLF_HISTORY_COPY_PATH),
        }

    @property
    def query_data(self):
        return self._query_data

    @query_data.setter
    def query_data(self, value):
        self._query_data = value

    @property
    def query_op(self):
        return self._query_op

    @query_op.setter
    def query_op(self, value):
        self._query_op = value

    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, value):
        self._database = value
