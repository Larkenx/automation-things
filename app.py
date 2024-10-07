from PIL import ImageGrab

import win32gui  # https://stackoverflow.com/questions/7142342/get-window-position-size-with-python
import pyautogui
import cv2
import numpy as np
import random
import time

# print(pyautogui.size())

reset_aggression_minimap_img = cv2.imread("./images/reset-aggression.png", 1)
return_to_crabs_minimap_img = cv2.imread("./images/return-to-crabs.png", 1)
target_crab_tile_img = cv2.imread("./images/crabs-tile.png", 1)

bankstall_img = cv2.imread("./images/bank-stall.png", 1)
bankstall_from_furnace_img = cv2.imread("./images/bank-stall-from-furnace.png", 1)
deposit_inventory_img = cv2.imread("./images/deposit-inventory.png", 1)

furnace_img = cv2.imread("./images/furnace.png", 1)
furnace_highlighted_img = cv2.imread("./images/furnace-highlighted.png", 1)


glassblowing_pipe_img = cv2.imread("./images/glassblowing-pipe.png", 1)
molten_glass_img = cv2.imread("./images/molten-glass.png", 1)
lantern_lens_img = cv2.imread("./images/lantern-lens.png", 1)
sand_bucket_img = cv2.imread("./images/sand-bucket.png", 1)
soda_ash_img = cv2.imread("./images/soda-ash.png", 1)


def hex2rgb(hex_value):
    h = hex_value.strip("#")
    rgb = tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
    return rgb


def rgb2hsv(r, g, b):
    # Normalize R, G, B values
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    # h, s, v = hue, saturation, value
    max_rgb = max(r, g, b)
    min_rgb = min(r, g, b)
    difference = max_rgb - min_rgb

    # if max_rgb and max_rgb are equal then h = 0
    if max_rgb == min_rgb:
        h = 0

    # if max_rgb==r then h is computed as follows
    elif max_rgb == r:
        h = (60 * ((g - b) / difference) + 360) % 360

    # if max_rgb==g then compute h as follows
    elif max_rgb == g:
        h = (60 * ((b - r) / difference) + 120) % 360

    # if max_rgb=b then compute h
    elif max_rgb == b:
        h = (60 * ((r - g) / difference) + 240) % 360

    # if max_rgb==zero then s=0
    if max_rgb == 0:
        s = 0
    else:
        s = (difference / max_rgb) * 100

    # compute v
    v = max_rgb * 100
    # return rounded values of H, S and V
    return np.array(list(map(round, (h, s, v))))


def hex2hsv(hex_value):
    r, g, b = hex2rgb(hex_value)
    return rgb2hsv(r, g, b)


def show_image(image):
    cv2.imshow("Screenshot", cv2.resize(image, (1920, 1080)))
    cv2.waitKey(0)


def fetch_runelite_window_from_win32gui():
    window_id = win32gui.FindWindow(None, "RuneLite")
    if window_id == 0:
        raise Exception("Unable to find Runelite window from Windows API")

    return win32gui.GetWindowRect(window_id)


def grab_runelite_image():
    window_rect = fetch_runelite_window_from_win32gui()
    screenshot = ImageGrab.grab(
        bbox=window_rect, include_layered_windows=False, all_screens=True
    ).convert("RGB")
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return frame


def find_in_game(image_to_find, show_preview=False):
    return find(grab_runelite_image(), image_to_find, show_preview)


def find(image, image_to_find, show_preview=False):
    z, w, h = image_to_find.shape[::-1]
    result = cv2.matchTemplate(image, image_to_find, cv2.TM_CCOEFF_NORMED)
    threshold = 0.50
    loc = np.where(result >= threshold)
    if len(loc[0]) <= 0:
        raise Exception("Couldn't find image")
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    top_left = (max_loc[0], max_loc[1])
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(image, top_left, bottom_right, 255, 5)
    if show_preview:
        show_image(image)
    return (max_loc[0], max_loc[1], w, h)


def find_solid_yellow_color_bounding_rect_in_image(image):
    frame_to_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # https://stackoverflow.com/questions/10948589/choosing-the-correct-upper-and-lower-hsv-boundaries-for-color-detection-withcv
    # approximation of #FFFF00 yellow bands in hsv
    lower_hsv_color_band_magenta = np.array([150, 160, 20])
    upper_hsv_color_band_magenta = np.array([150, 255, 255])

    # Threshold the HSV image to get only desired colors
    # may need to pad the range of the colors if the color isnt an absolute value
    mask = cv2.inRange(
        frame_to_hsv, lower_hsv_color_band_magenta, upper_hsv_color_band_magenta
    )
    contours = cv2.findContours(
        mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )[-2]

    # ctrs, hierarchy = cv2.findContours(
    #     mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    # )
    # cv2.drawContours(frame_to_hsv, ctrs, -1, (255, 0, 0), 10)
    # show_image(frame_to_hsv)

    if len(contours) > 0:
        target_area = max(contours, key=cv2.contourArea)
        (x, y, w, h) = cv2.boundingRect(target_area)
        cv2.rectangle(frame_to_hsv, (x, y), (x + w, y + h), (255, 0, 0), 10)
        show_image(frame_to_hsv)
        return (x, y, x + w, y + h)


def click_contour():
    find_solid_yellow_color_bounding_rect_in_image(grab_runelite_image())
    pass


def delay(duration, variance=300):
    duration_in_ms = duration + random.uniform(-variance, variance)
    print(f"sleeping {duration_in_ms}ms")
    time.sleep(duration_in_ms / 1000)


def click(rect, variance=20):
    x, y, w, h = rect
    # click within the rectangle, but try to always click somewhat in the center with a random distribution
    cx = x + w // 2
    cy = y + h // 2
    target_x = cx + random.uniform(-variance, variance)
    target_y = cy + random.uniform(-variance, variance)
    pyautogui.moveTo(target_x, target_y)
    pyautogui.click(target_x, target_y)
    print(f"clicking {cx},{cy} within bounding box of [{x}, {y}, {x+w}, {y+h}]")


def press_key(key_to_press, variance=50):
    pyautogui.keyDown(key_to_press)
    delay(100, variance)
    pyautogui.keyUp(key_to_press)


def smelt_glass():
    quick_action_delay = 500
    run_time = 7000
    craft_time = 21000
    for i in range(0, 10):
        # overall timing delay
        # delay(10000, 10000)
        deposit_all = find_in_game(deposit_inventory_img, False)
        click(deposit_all)
        delay(quick_action_delay)
        sand = find_in_game(soda_ash_img, False)
        ash = find_in_game(sand_bucket_img, False)
        delay(quick_action_delay)
        click(sand)
        delay(quick_action_delay)
        click(ash)
        delay(900)
        furnace = find_in_game(furnace_highlighted_img, False)
        click(furnace)
        delay(run_time, 5000)
        press_key("space")
        delay(craft_time, 4000)
        bank_stall = find_in_game(bankstall_from_furnace_img, False)
        click(bank_stall)
        delay(run_time, 500)


def craft_glass():
    quick_action_delay = 500
    random_afk_time = 10000
    run_time = 7000
    craft_time = 60000
    for i in range(0, 4):
        # CLICK bank
        click(find_in_game(bankstall_img))
        delay(quick_action_delay * 2)
        # Deposit lantern lens
        click(find_in_game(lantern_lens_img))
        delay(quick_action_delay)

        # Withdraw molten glass
        click(find_in_game(molten_glass_img))
        delay(quick_action_delay * 2)
        # Close bank - escape key
        press_key("esc")
        delay(quick_action_delay)
        if random.randrange(0, 10) < 3:
            delay(random_afk_time, 5000)
        # Click pipe then click molten glass
        click(find_in_game(glassblowing_pipe_img))
        delay(quick_action_delay)
        click(find_in_game(molten_glass_img))
        delay(quick_action_delay * 2)
        # Space Bar to craft
        press_key("space")
        # Wait
        delay(craft_time, 5000)
        if random.randrange(0, 10) < 3:
            delay(random_afk_time, 5000)


def test():
    find_in_game(lantern_lens_img, True)


def click_automation():
    for i in range(0, 20):
        # toggle prayer on/off when hovered over it
        pyautogui.click()
        delay(200, variance=100)
        pyautogui.click()
        delay(45000, 10000)


# smelt_glass()
# craft_glass()
# test()

click_automation()
