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
        self._gecko_query_op = f'''
            SELECT url 
            FROM moz_places 
            ORDER BY last_visit_date DESC 
            LIMIT 11
            '''
        self._blink_query_op = f'''
            SELECT url 
            FROM urls 
            ORDER BY last_visit_time DESC 
            LIMIT 11
            '''
        (self._browser, self._renderer) = browser.fetch_browser()

    def copy_fetch(self):
        match [self._browser, self._renderer]:
            case ["CHROME", "Blink"]:
                shutil.copy(const.WIN_CHROME_HISTORY_PATH,
                            const.WIN_CHROME_HISTORY_COPY_PATH)
                self.query_op = self._blink_query_op
                self.database = const.WIN_CHROME_HISTORY_COPY_PATH

            case ["MSEDGE", "Blink"]:
                shutil.copy(const.WIN_EDGE_HISTORY_PATH,
                            const.WIN_EDGE_HISTORY_COPY_PATH)
                self.query_op = self._blink_query_op
                self.database = const.WIN_EDGE_HISTORY_COPY_PATH

            case ["FIREFOX", "Gecko"]:
                self.query_op = self._gecko_query_op
                self.database = const.WIN_FIREFOX_HISTORY_PATH

            case ["LIBREWOLF", "Gecko"]:
                self.query_op = self._gecko_query_op
                self.database = const.WIN_LIBREWOLF_HISTORY_PATH

            case _:
                # temp
                print("Browser currently not supported!")
                return

        with closing(sqlite3.connect(self.database)) as self._db:
            self._do_query(self.query_op)

    def _do_query(self, sql_cmd):
        with closing(self._db.cursor()) as self._cursor:
            self._cursor.execute(sql_cmd)
            self.query_data = self._cursor.fetchall()

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
