from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
import math
import math as m

# URL of your WebGL Gaussian Splatting viewer
URL = "https://lioqing.com/wgpu-3dgs-viewer-app/"  # change to your viewer URL

# https://vid2scene.com/viewer/e5b647ef-21a5-4397-b95d-f18e396973f2/
# https://antimatter15.com/splat/
# https://jatentaki.github.io/assets/gaussianviewer/index.html
# https://lioqing.com/wgpu-3dgs-viewer-app/

# Start Firefox Nightly
options = webdriver.FirefoxOptions()
options.set_preference("layout.frame_rate", 999)

driver = webdriver.Firefox(options=options)
driver.get(URL)

# Wait for viewer to load
canvas = driver.find_element(By.TAG_NAME, "canvas")
time.sleep(30)

# Inject JS snippet to measure FPS
fps_script = """
(function() {
  let frames = [];
  function loop(t) {
    frames.push(t);
    if (frames.length > 120) frames.shift();
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
  window._getFPS = function() {
    if (frames.length < 2) return 0;
    let diffs = [];
    for (let i = 1; i < frames.length; i++) {
      diffs.push(frames[i] - frames[i-1]);
    }
    let avg = diffs.reduce((a,b) => a+b, 0) / diffs.length;
    return 1000 / avg;
  };
})();
"""
driver.execute_script(fps_script)

# Perform circular mouse drag
actions = ActionChains(driver)
rect = canvas.rect
center_x = rect["x"] + rect["width"] // 2
center_y = rect["y"] + rect["height"] // 2
radius = min(rect["width"], rect["height"]) // 4

# click and hold at start point
start_x = center_x + radius
start_y = center_y
actions.move_to_element_with_offset(canvas, radius, 0)
actions.click_and_hold().perform()

# open log file
log_file = open("fps_log.txt", "w")

# move in circle with live FPS logging
steps = 180
prev_x, prev_y = start_x, start_y
for i in range(steps):
    angle = 2 * math.pi * i / steps
    x = center_x + int(radius * math.cos(angle))
    y = center_y + int(radius * math.sin(angle))
    actions.move_by_offset(x - prev_x, y - prev_y).perform()
    prev_x, prev_y = x, y
    time.sleep(0.05)  # pace interaction

    # log FPS live (rounded up to next integer)
    fps = driver.execute_script("return window._getFPS();")
    fps_rounded = m.ceil(fps)
    log_line = f"{fps_rounded}"
    print(log_line)
    log_file.write(log_line + "\n")

# release mouse
actions.release().perform()

# close log file
log_file.close()

driver.quit()
