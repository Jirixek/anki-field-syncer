import os

from anki.utils import json
import aqt
import anki

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(os.path.join(__location__, "js21.js"), "r") as f:
    js_code_21 = f.read()


def on_editor_will_load_note(js, note: anki.notes.Note, editor: aqt.editor.Editor):
    if editor.addMode:
        flds = note.model()["flds"]
        sticky = [fld["sticky"] for fld in flds]

        eval_definitions = js_code_21
        eval_calls = f'setFrozenFields({json.dumps(flds)}, {json.dumps(sticky)})'

        js += eval_definitions
        js += eval_calls

    return js

# editor: _links, addButton


def onBridge(self, str, _old):
    """Extend the js <--> py bridge with our pycmd handler"""

    if not str.startswith("frozen"):
        if str.startswith("blur"):
            self.lastField = self.currentField  # save old focus
        return _old(self, str)
    if not self.note or not runHook:
        # shutdown
        return

    (cmd, txt) = str.split(":", 1)
    cur = int(txt)
    flds = self.note.model()['flds']
    flds[cur]['sticky'] = not flds[cur]['sticky']


def frozenToggle(self, batch=False):
    """Toggle state of current field"""

    flds = self.note.model()['flds']
    cur = self.currentField
    if cur is None:
        cur = 0
    is_sticky = flds[cur]["sticky"]
    if not batch:
        flds[cur]["sticky"] = not is_sticky
    else:
        for n in range(len(self.note.fields)):
            try:
                flds[n]['sticky'] = not is_sticky
            except IndexError:
                break

    self.loadNoteKeepingFocus()


# Add-on hooks, etc.
Editor.onBridgeCmd = anki.wrap(Editor.onBridgeCmd, onBridge, "around")
Editor.loadNote = loadNote21

Editor.frozenToggle = frozenToggle
