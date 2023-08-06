from dearpygui import dearpygui as dpg
from mel_client import MelodyClient
from mel_yum import MelodyYUM
from PIL import (
    Image,
    ImageDraw,
    ImageChops,
    ImageFilter,
    ImageEnhance,
)
import constants as const
import numpy as np
import os
import threading
import time


class Melody:
    def __init__(self) -> None:
        self._melody_client = MelodyClient()
        self._melody_yum = MelodyYUM()

        self._yum_stop_flag = threading.Event()

        self._yum_worker = threading.Thread(
            target=self._melody_yum.update_song,
            args=(self._yum_stop_flag,)
        )
        self._client_worker = threading.Thread(
            target=self._melody_client.update,
            args=(self._melody_yum,)
        )

        self._textures_loaded = False
        self._textures = {}

        self._text_item_num = 0

        self._btn_text_pairs = [
            ("--btn-start", "--text-3"),
            ("--btn-quit", "--text-4"),
            ("--btn-on", "--text-7"),
            ("--btn-off", "--text-8")
        ]
        self._filter_btn_on = True
        self._filter_btn_off = False

        self._setup_app()

    def _popup_on_fetch_fail(self):
        if not self._melody_yum.prefetch_ok():
            self._show_error_popup("Failed to prefetch content")

    def _start_client_cmd(self):
        if self._yum_worker.is_alive() or self._client_worker.is_alive():
            self._show_error_popup("RPC currently running!")
            return

        self._yum_worker.start()
        self._melody_client.start()
        self._client_worker.start()

        check_prefetch = threading.Timer(20.0, self._popup_on_fetch_fail)
        check_prefetch.start()
        check_prefetch.join()

    def _quit_client_cmd(self):
        if self._melody_client.client_is_active():
            self._melody_client.kill_client()

        self._yum_stop_flag.set()

        if self._client_worker.is_alive():
            self._client_worker.join()

        if self._yum_worker.is_alive():
            self._yum_worker.join()

        # let the system finish anything it needs to do with this program before closing
        time.sleep(5)

        print("Done!")

    def _show_error_popup(self, msg: str):
        main_data = self._window_data(self._main_window)

        window_args = {
            "width": 150,
            "height": 150,
            "show": True,
            "modal": True,
            "no_title_bar": True,
            "no_move": True,
            "no_resize": True,
            "pos": (
                (main_data["width"] + 150) / 4.2,
                (main_data["height"] / 4) - 17
            ),
        }

        with dpg.window(**window_args) as popup:
            msg_width = dpg.get_text_size(msg, font=self._16pt_font)[0]

            new_popup_x_pos = (main_data["width"] + 150) / 4.2
            if msg_width > 150:
                new_popup_x_pos = (main_data["width"] + msg_width) / 4.8

            dpg.set_item_pos(
                popup,
                pos=(
                    new_popup_x_pos,
                    (main_data["height"] / 4) - 17
                )
            )

            # for modal button and texture to be closer to the center
            dpg.set_item_width(popup, msg_width)

            popup_data = self._window_data(popup)

            dpg.add_image(
                "--texture-error",
                pos=((popup_data["width"] / 2.2) + 1, 10)
            )

            with dpg.group(pos=(12, 60)):
                modal_text = dpg.add_text(msg, color=(255, 255, 255))
                dpg.bind_item_font(modal_text, self._16pt_font)

                # sets the proper width of the modal (scaled by text width + font)
                dpg.set_item_width(popup, dpg.get_item_width(modal_text))

                add_to_x = (popup_data["width"] / 4) - \
                    (window_args["width"] / 4)

                modal_btn = dpg.add_button(
                    label="Close",
                    callback=lambda: dpg.configure_item(popup, show=False),
                    pos=(
                        (popup_data["width"] / 4) +
                        (add_to_x + 5 if add_to_x > 0 else 0),
                        (popup_data["height"] / 2) + 20
                    )
                )
                dpg.bind_item_font(modal_btn, self._16pt_font)

            dpg.bind_item_theme(popup, "--modal-filter-theme")

    def _set_title_filter(self, sender, app_data, user_data):
        match [user_data, self._melody_yum.filter_state()]:
            case [True, True]:
                if self._filter_btn_on:
                    self._show_error_popup("Filter is already on!")
                return

            case [False, False]:
                if self._filter_btn_off:
                    self._show_error_popup("Filter is already off!")
                return

        print("Set Filter:", user_data, self._melody_yum.filter_state())

        self._melody_yum.filter_title(user_data)

    def _load_textures(self):
        def __open_img(file_name: str) -> Image:
            return Image.open(const.ASSET_PATH + file_name)

        def __blend_to_img(img: Image) -> Image:
            if not os.path.exists(const.ASSET_PATH + "bg_col.png"):
                bg_col_layer = Image.new(
                    "RGBA", (const.WIDTH, const.HEIGHT), (0, 0, 0, 0))
                draw = ImageDraw.Draw(bg_col_layer)
                draw.rectangle((0, 0, const.WIDTH, const.HEIGHT),
                               fill=(23, 14, 2, 94))
                bg_col_layer.save(const.ASSET_PATH + "/bg_col.png")

            bg_col = __open_img("bg_col.png")

            # blend img with the background colour
            blended_img = ImageChops.blend(img, bg_col, alpha=0.25)
            blended_img = ImageEnhance.Color(blended_img).enhance(1.5)

            return blended_img.filter(ImageFilter.GaussianBlur(radius=2))

        def __add_img(img: Image, name: str):
            img_buf = np.frombuffer(img.tobytes(), dtype=np.uint8) / 255.0

            self._textures[name] = {
                "img": img,
                "buf": img_buf
            }

        try:
            __add_img(__blend_to_img(__open_img(
                "background3.png")), name="background")
            __add_img(__open_img("icon_power3.png"), name="power")
            __add_img(__open_img("icon_feather3.png"), name="feather")
            __add_img(__open_img("icon_error4.png"), name="error")

            self._textures_loaded = True

        except Exception as e:
            print("Failed to load textures:", e)

    def _check_btn_clicked(self, sender, app_data):
        for x in self._btn_text_pairs:
            if dpg.is_item_clicked(x[0]):
                if x == self._btn_text_pairs[2::][0]:
                    self._filter_btn_on = True
                    self._filter_btn_off = False
                else:
                    self._filter_btn_on = False
                    self._filter_btn_off = True

                dpg.configure_item(x[1], color=(0, 0, 0))

    def _use_hover_color(self, sender, app_data):
        for x in self._btn_text_pairs:
            if dpg.is_item_hovered(x[0]):
                dpg.configure_item(x[1], color=(255, 255, 255))
            else:
                if x in self._btn_text_pairs[0::2]:
                    dpg.configure_item(x[1], color=(0, 0, 0))
                else:
                    dpg.configure_item(x[1], color=(255, 255, 255))

    def _setup_registers(self):
        def __add_font(file_name: str, size: int):
            return dpg.add_font(const.ASSET_PATH + file_name, size)

        with dpg.font_registry():
            self._22pt_font = __add_font("Inter-Regular.ttf", 22)
            self._16pt_font = __add_font("Inter-Regular.ttf", 16)
            self._12pt_font = __add_font("Inter-Regular.ttf", 12)

        if self._textures_loaded:
            with dpg.texture_registry():
                for item in self._textures.items():
                    dpg.add_static_texture(
                        width=item[1]["img"].width,
                        height=item[1]["img"].height,
                        default_value=item[1]["buf"],
                        tag="--texture-" + item[0]
                    )

        with dpg.handler_registry(tag="--btn-handler"):
            dpg.add_mouse_move_handler(callback=self._use_hover_color)
            dpg.add_mouse_click_handler(callback=self._check_btn_clicked)

    def _setup_window_theme(self):
        with dpg.theme(tag="--app-theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)

            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonHovered,
                    (255, 150, 0)
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonActive,
                    (207, 122, 2, 255)
                )
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 25, 3.5)

        dpg.bind_theme("--app-theme")

        with dpg.theme(tag="--btn-theme-1"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(
                    dpg.mvThemeCol_Button,
                    (255, 255, 255)
                )

        with dpg.theme(tag="--btn-theme-2"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(
                    dpg.mvThemeCol_Button,
                    (191, 191, 191, 128)
                )

        with dpg.theme(tag="--modal-filter-theme"):
            with dpg.theme_component(dpg.mvWindowAppItem):
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5)
                dpg.add_theme_color(
                    dpg.mvThemeCol_Border,
                    (255, 255, 255, 0)
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_PopupBg,
                    (255, 255, 255, 128)
                )

    def _setup_window_content(self):
        main_kwargs = {
            "width": const.WIDTH,
            "height": const.HEIGHT,
            "pos": [0, 0],
            "no_collapse": True,
            "no_move": True,
            "no_scrollbar": True,      
            "no_title_bar": True,
            "no_resize": True,
            "no_bring_to_front_on_focus": True
        }

        with dpg.window(**main_kwargs) as self._main_window:
            dpg.add_image("--texture-background")

            self._win_data = self._window_data(self._main_window)

            child_kwargs = {
                "width": 194,
                "height": 135,
                "no_title_bar": True,
                "no_move": True,
                "no_resize": True,
                "no_background": True
            }

            self._setup_rp_window(child_kwargs)
            self._setup_tf_window(child_kwargs)

    def _place_text(self, **kwargs):
        self._text_item_num += 1

        placeholder = dpg.draw_text(
            pos=kwargs["pos"],
            text=kwargs["text"],
            color=kwargs["color"],
            size=kwargs["size"],
            tag="--text-" + str(self._text_item_num)
        )
        dpg.bind_item_font(placeholder, kwargs["font"])

    def _window_data(self, window: int | str) -> dict:
        return {
            "width": dpg.get_item_width(window),
            "height": dpg.get_item_height(window),
            "x_pos": dpg.get_item_pos(window)[0],
            "y_pos": dpg.get_item_pos(window)[1],
        }

    def _draw_window_base(self, width: int, height: int):
        dpg.draw_rectangle(
            [0, 0],
            [width, height],
            color=(0, 0, 0, 0),
            fill=(255, 255, 255, 100),
            rounding=5
        )

    def _setup_rp_window(self, child_kwargs):
        with dpg.window(pos=(14, 60), **child_kwargs) as self._rp_window:
            self._draw_window_base(
                child_kwargs["width"], child_kwargs["height"])

            dpg.add_image(
                "--texture-power",
                pos=((self._window_data(self._rp_window)["width"] / 2) + 45, 7)
            )

            icon_height = self._textures["power"]["img"].height

            self._place_text(
                text="Rich Presence",
                font=self._22pt_font,
                pos=(10, (icon_height / 4) + 4),
                color=(255, 255, 255),
                size=22
            )
            self._place_text(
                text="Share what you're\n    listening to!",
                font=self._12pt_font,
                pos=(10, (icon_height / 4) + 34),
                color=(255, 255, 255),
                size=12
            )

            with dpg.group(horizontal=True):
                dpg.add_button(
                    width=85,
                    height=25,
                    pos=(8, (self._window_data(self._rp_window)
                         ["height"] * 0.75) + 1),
                    callback=self._start_client_cmd,
                    tag="--btn-start"
                )
                dpg.bind_item_theme("--btn-start", "--btn-theme-1")

                dpg.add_button(
                    width=85,
                    height=25,
                    pos=(
                        (self._window_data(self._rp_window)["width"] / 2) + 4,
                        (self._window_data(self._rp_window)
                         ["height"] * 0.75) + 1
                    ),
                    callback=self._quit_client_cmd,
                    tag="--btn-quit"
                )
                dpg.bind_item_theme("--btn-quit", "--btn-theme-2")

            self._place_text(
                text="Start",
                font=self._16pt_font,
                pos=(35, (self._window_data(self._rp_window)
                     ["height"] * 0.75) + 5),
                color=(0, 0, 0),
                size=16
            )
            self._place_text(
                text="Quit",
                font=self._16pt_font,
                pos=(85 + ((85 / 2) + 2),
                     (self._window_data(self._rp_window)["height"] * 0.75) + 5),
                color=(255, 255, 255),
                size=16
            )

    def _setup_tf_window(self, child_kwargs):
        with dpg.window(
            pos=(self._win_data["width"] - 226, 60),
            **child_kwargs
        ) as self._tf_window:
            self._draw_window_base(
                child_kwargs["width"], child_kwargs["height"])

            dpg.add_image(
                "--texture-feather",
                pos=((self._window_data(self._tf_window)["width"] / 2) + 45, 7)
            )

            icon_height = self._textures["feather"]["img"].height

            self._place_text(
                text="Title Filter",
                font=self._22pt_font,
                pos=(10, (icon_height / 4) + 4),
                color=(255, 255, 255),
                size=22
            )
            self._place_text(
                text="Sometimes you just\n      want less",
                font=self._12pt_font,
                pos=(10, (icon_height / 4) + 34),
                color=(255, 255, 255),
                size=12
            )

            with dpg.group(horizontal=True):
                dpg.add_button(
                    width=85,
                    height=25,
                    pos=(8, (self._window_data(self._tf_window)
                         ["height"] * 0.75) + 1),
                    callback=self._set_title_filter,
                    user_data=True,
                    tag="--btn-on"
                )
                dpg.bind_item_theme("--btn-on", "--btn-theme-1")

                dpg.add_button(
                    width=85,
                    height=25,
                    pos=(
                        (self._window_data(self._tf_window)["width"] / 2) + 4,
                        (self._window_data(self._tf_window)
                         ["height"] * 0.75) + 1
                    ),
                    callback=self._set_title_filter,
                    user_data=False,
                    tag="--btn-off"
                )
                dpg.bind_item_theme("--btn-off", "--btn-theme-2")

                with dpg.tooltip("--btn-off"):
                    off_btn_tooltip = dpg.add_text(
                        " When the title filter fails, use this "
                    )
                    dpg.bind_item_font(off_btn_tooltip, self._16pt_font)

            self._place_text(
                text="On",
                font=self._16pt_font,
                pos=(40, (self._window_data(self._tf_window)
                     ["height"] * 0.75) + 5),
                color=(0, 0, 0),
                size=16
            )
            self._place_text(
                text="Off",
                font=self._16pt_font,
                pos=(85 + ((85 / 2) + 4),
                     (self._window_data(self._tf_window)["height"] * 0.75) + 5),
                color=(255, 255, 255),
                size=16
            )

    def _run_event_loop(self):
        dpg.show_viewport()
        dpg.start_dearpygui()

    def _setup_app(self):
        self._load_textures()

        dpg.create_context()

        self._setup_registers()
        self._setup_window_theme()

        dpg.create_viewport(
            title=const.APP_NAME,
            large_icon=const.APP_ICON,
            width=const.WIDTH - 10,  # in release build, the window is wider, remove in debug
            height=const.HEIGHT,
            resizable=False
        )
        dpg.setup_dearpygui()
        dpg.set_exit_callback(callback=self._quit_client_cmd)

        self._setup_window_content()
        self._run_event_loop()

        dpg.destroy_context()


def main():
    _ = Melody()


if __name__ == "__main__":
    main()
