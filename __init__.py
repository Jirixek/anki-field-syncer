import anki
import aqt
from aqt import gui_hooks, mw
from . import unidir, bidir
import json


def on_editor_did_unfocus_field(changed: bool, note: anki.notes.Note, field_idx: int) -> bool:
    # return True if changes were made, otherwise return changed
    changed |= unidir.sync_field(mw.col, note, field_idx)
    changed |= bidir.sync_field(mw.col, note, field_idx)
    return changed


# def on_editor_did_init_buttons(righttopbtns: list[str], editor: aqt.editor.Editor):
#     righttopbtns.append(editor.addButton(icon=None, cmd='cringe', func=None, rightside=False, label='cringe'))


#     btn = editor.addButton(icon=None, cmd='cringe', func=None, rightside=False, label='cringe')
#     for mw.col.
#     editor.web.eval(f"{lefttopbtns_js} {righttopbtns_js}")
# TODO: setup links only once


def on_editor_will_load_note(js: str, note: anki.notes.Note, editor: aqt.editor.Editor) -> str:
    btn = editor.addButton(icon=None, cmd='cringe', func=None, rightside=False, label='cringe')
    btns = [btn]
    btns_defs = ", ".join([json.dumps(button) for button in btns])
    btns_js = (
        f"""
require("anki/NoteEditor").instances[0].fields[0].element.then((el) => {{
el.append({{
component: editorToolbar.AddonButtons,
id: "addons",
props: {{ buttons: [ {btns_defs} ] }},
}})}});
"""
        if len(btns) > 0
        else ""
    )
    return js + btns_js


def on_sync_will_start():
    unidir.sync_all()


gui_hooks.editor_did_unfocus_field.append(on_editor_did_unfocus_field)
# gui_hooks.editor_will_load_note.append(on_editor_will_load_note)
gui_hooks.sync_will_start.append(on_sync_will_start)
