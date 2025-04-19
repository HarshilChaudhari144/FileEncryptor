from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import TextArea
import html
import re

# Password strength criteria checker
def check_criteria(password):
    return {
        "Length ≥ 8": len(password) >= 8,
        "Uppercase": bool(re.search(r"[A-Z]", password)),
        "Lowercase": bool(re.search(r"[a-z]", password)),
        "Digit": bool(re.search(r"[0-9]", password)),
        "Special Char": bool(re.search(r"[^A-Za-z0-9]", password)),
    }

def calculate_strength(criteria):
    passed = sum(criteria.values())
    if passed == 5:
        return "Very Strong", "green"
    elif passed >= 4:
        return "Strong", "cyan"
    elif passed >= 3:
        return "Moderate", "yellow"
    elif passed >= 2:
        return "Weak", "magenta"
    else:
        return "Very Weak", "red"

# Shared state
password_holder = {"value": ""}

# Real-time toolbar updater
def get_toolbar():
    password = password_holder["value"]
    criteria = check_criteria(password)
    strength, color = calculate_strength(criteria)

    checklist = ""
    for crit, passed in criteria.items():
        icon = "✓" if passed else "✗"
        clr = "ansigreen" if passed else "ansired"
        checklist += f"<{clr}>{icon} {crit}</{clr}>  "

    return HTML(
        f"<b>Password:</b> <ansiblue>{html.escape(password)}</ansiblue>\n"
        f"{checklist}\n"
        f"<b>Strength:</b> <{color}>{strength}</{color}>"
    )

# Password entry field
text_area = TextArea(
    height=1,
    prompt="Enter password: ",
    password=False,
    multiline=False,
)

# Toolbar window
toolbar = Window(
    height=3,
    content=FormattedTextControl(get_toolbar),
    always_hide_cursor=True
)

# Update state on key press
kb = KeyBindings()

@kb.add("c-c")
def _(event):
    event.app.exit()

@kb.add("backspace")
def _(event):
    password_holder["value"] = password_holder["value"][:-1]
    text_area.text = password_holder["value"]

@kb.add("<any>")
def _(event):
    key = event.data
    password_holder["value"] += key
    text_area.text = password_holder["value"]

# Application setup
layout = Layout(HSplit([text_area, toolbar]))
app = Application(layout=layout, key_bindings=kb, full_screen=False)

def ask_password_with_strength():
    app.run()
    return password_holder["value"]

if __name__ == "__main__":
    password = ask_password_with_strength()
    print(f"\nYou entered: {password}")