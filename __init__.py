import anki
from aqt.qt import QAction
from aqt import gui_hooks, qconnect, mw
from . import unidir


def sync_spans():
    unidir.sync_all()


def on_editor_did_unfocus_field(changed: bool, note: anki.notes.Note, field_idx: int) -> bool:
    # return True if changes were made, otherwise return changed
    changed |= unidir.sync_field(mw.col, note, field_idx)
    # changed |= bidir.sync_field(mw.col, note, field_idx)
    return changed


gui_hooks.editor_did_unfocus_field.append(on_editor_did_unfocus_field)

if mw is not None:
    action = QAction('Sync spans', mw)
    qconnect(action.triggered, sync_spans)
    mw.form.menuTools.addAction(action)
