import anki
from aqt import gui_hooks, mw

from . import bidir, unidir


def on_editor_did_unfocus_field(changed: bool, note: anki.notes.Note, field_idx: int) -> bool:
    # return True if changes were made, otherwise return changed
    changed |= unidir.sync_field(mw.col, note, field_idx)
    changed |= bidir.sync_field(mw.col, note, field_idx)
    return changed


def on_sync_will_start():
    unidir.sync_all()


gui_hooks.editor_did_unfocus_field.append(on_editor_did_unfocus_field)
gui_hooks.sync_will_start.append(on_sync_will_start)
