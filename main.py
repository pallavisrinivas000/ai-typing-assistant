import pyperclip
import httpx
import time
from pynput import keyboard
from pynput.keyboard import Controller
from pynput.keyboard import Key
from string import Template

# to control the actions that happens with keyboard:
# Initialse a instance of controller
controller = Controller()

OLAMA_ENDPOINT= "http://localhost:11434/api/generate" 
OLAMA_CONFIG = {
    "model": "mistral:7b-instruct-q4_K_M",
    "keep_alive": "5m",
    "stream": False,
}
PROMT_TEMPLETE = Template(
"""Fix all typos and casing and punctuation in this text, but preserve all new line characters:

$text

Return only the corrected text, don't include a preamble.
"""
)

def fix_text(text):
    prompt = PROMT_TEMPLETE.substitute(text=text)
    response = httpx.post(OLAMA_ENDPOINT, json={"prompt": prompt, **OLAMA_CONFIG},
                          headers={"Content-Type": "application/json"},
                          timeout=10,)
    if response.status_code != 200:
        return None
    return response.json()["response"].strip()


def fix_current_line():
    controller.press(Key.cmd)
    controller.press(Key.shift)
    controller.press(Key.left)

    controller.release(Key.cmd)
    controller.release(Key.shift)
    controller.release(Key.left)

    fix_selection()

def fix_selection():
    # step 1: copy the text to clipboard
    with controller.pressed(Key.cmd):
        controller.tap("c")
    # Step 2: get the text from clipboard
    time.sleep(0.1)
    text = pyperclip.paste()
    
    if not text:
        return
    fixed_text = fix_text(text)

    pyperclip.copy(fixed_text)
    time.sleep(0.1)
    
    with controller.pressed(Key.cmd):
        controller.tap("v")


def on_esc():
    fix_current_line()

def on_tab():
    fix_selection()
# first we get the values of keys which you want to use
print(Key.esc.value, Key.tab.value)

with keyboard.GlobalHotKeys({
    '<53>': on_esc,
    '<48>': on_tab
}) as key:
    
    key.join()
