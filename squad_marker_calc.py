import pathlib
import re
import time

import mouse
import mss
import mss.base
import mss.tools
import pytesseract
import requests
import yarl
from PIL import Image, ImageOps
from PIL.Image import Resampling
from win32gui import GetForegroundWindow, GetWindowText

POSITION_REGEX = re.compile(r"([\w\d\[][\w\d]\d*)\s*(-)\s*(\d)\s*-\s*(\d)")
BASE_PATH = pathlib.Path(__file__).resolve().parent


def main(config: dict):

    tesseract_cmd = pathlib.Path(config["program"]["tesseract_exe"])
    if not tesseract_cmd.is_absolute():
        tesseract_cmd = BASE_PATH / tesseract_cmd

    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    tesseract_params = (
        config["program"]["tesseract_params"]
        + " --tessdata-dir "
        + str((BASE_PATH / config["program"]["tessdata_dir"]))
    )

    with mss.mss() as sct:
        sct.compression_level = 0

        while True:
            mouse.wait("right", target_types=mouse.UP)
            time.sleep(0.1)

            if not is_squad_window_active():
                print("[-] Окно сквада закрыто")
                continue

            if not is_map_open(sct, config["resolutions"]["monitor"]):
                print("[-] Карта закрыта")
                continue

            screenshot = get_screenshot_coords(sct, get_selected_screen_space(config))
            if config["program"]["debug"]:
                screenshot.save("image.png")
            text = get_text_from_screenshot(screenshot, tesseract_params)

            all_positions = get_coordinates_from_text(text, POSITION_REGEX)

            if len(all_positions) != 2:
                print(f"[-] Не удалось получить обе координаты: '{text}' распознано как {all_positions}")
                continue

            origin = clear_coordinate(all_positions[0])
            target = clear_coordinate(all_positions[1])
            print(f"[+] {origin} -> {target}")

            ok, info = send_coord_to_server(config["server"]["url"], config["server"]["unique_key"], origin, target)

            if not ok:
                print(info)


def get_selected_screen_space(config: dict):
    selected_resolution = config["resolutions"]["selected"]
    hardware_mon = config["resolutions"]["monitor"]
    return {
        "mon": hardware_mon,
        "top": config["resolutions"][selected_resolution]["top"],
        "left": config["resolutions"][selected_resolution]["left"],
        "width": config["resolutions"][selected_resolution]["width"],
        "height": config["resolutions"][selected_resolution]["height"],
    }


def get_screenshot_coords(sct: mss.base.MSSBase, screen_space: dict):
    sct_img = sct.grab(screen_space)
    img = ImageOps.scale(Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX"), 5, Resampling.BILINEAR)

    return img


def get_text_from_screenshot(screenshot: Image, params: str):
    return pytesseract.image_to_string(screenshot, config=params).strip()


def is_squad_window_active():
    if GetWindowText(GetForegroundWindow()).startswith("SquadGame"):
        return True
    return False


def get_coordinates_from_text(text: str, regex: re.Pattern):
    return ["".join(match) for match in regex.findall(text)]


def clear_coordinate(coord: str):
    splitted = list(coord.strip().replace(" ", "").upper())

    if splitted[0] in ("1", "["):
        splitted[0] = "I"

    if splitted[1] == "T":
        splitted[1] = "7"

    return "".join(splitted)


def is_map_open(sct: mss.base.MSSBase, monitor: int):
    sct_img = sct.grab({"mon": monitor, "top": 40, "left": 40, "width": 1, "height": 30})

    for row in sct_img.pixels:
        for pixel in row:
            if pixel[0] == 255 and pixel[1] == 210 and pixel[2] == 0:
                return True

    return False


def send_coord_to_server(server_url: str, unique_key: str, origin: str, target: str):
    try:
        resp = requests.post(yarl.URL(server_url) / str(unique_key), json={"origin": origin, "target": target})
        if resp.status_code == 201:
            return True, ""

        return False, f"[-] Ошибка при отправке координат: status_code {resp.status_code}"
    except requests.RequestException as e:
        return False, f"[-] Ошибка при отправке координат: {e}"


def print_help():
    print(
        "Squad Marker Calc by TARAN",
        "",
        "Это приложение считывает текущую вашу позицию в скваде и то место куда вы ставите метку на карте.",
        "После этого - приложение отправляет вычисленные позиции на сервер",
        "",
        sep="\n",
    )


if __name__ == "__main__":

    import traceback

    import toml

    try:
        print_help()
        main(toml.load(BASE_PATH / "config.toml"))
    except Exception:
        traceback.print_exc()
        input("Нажми любую клавишу чтобы закрыть окно")
