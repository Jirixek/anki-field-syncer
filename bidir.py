from copy import copy
from random import randrange
from typing import Callable, Sequence
import warnings

import anki
from aqt.utils import askUserDialog
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

warnings.filterwarnings('ignore', category=MarkupResemblesLocatorWarning, module='bs4')

Popup = Callable[[str], str]


def default_popup(sid: str) -> str:
    return askUserDialog(f'Span with sid {sid} has changed.', ('Upload', 'Download')).run()


def generate_sid(col: anki.Collection, note: anki.notes.Note, field_idx: int) -> str:
    def generate_sid_internal():
        return f'{note.id}_{field_idx}_{randrange(0, 10000):04}'
    sid = generate_sid_internal()
    while len(col.find_notes(f'sid="{sid}"')) > 0:
        sid = generate_sid_internal()
    return sid


def are_spans_coherent(col: anki.Collection, nids: Sequence[anki.notes.NoteId], sid: int) -> bool:
    if len(nids) <= 1:
        return True

    span_str = None
    for nid in nids:
        note = col.get_note(nid)
        for field_val in note.values():
            bs = BeautifulSoup(field_val, 'html.parser')
            spans = bs.find_all('span', {'class': 'sync', 'sid': sid}, recursive=False)
            for span in spans:
                if span_str is None:
                    span_str = span.string if span.string is not None else ''
                elif span_str != span.string:
                    return False
    return True


def upload(col: anki.Collection, nids: Sequence[anki.notes.NoteId], span: BeautifulSoup):
    '''
    Upload a span to all given notes. Span must have a sid attribute.
    '''
    sid = span.get('sid')
    for nid in nids:
        note = col.get_note(nid)
        for field_key, field_val in note.items():
            bs = BeautifulSoup(field_val, 'html.parser')
            spans = bs.find_all('span', {'class': 'sync', 'sid': sid}, recursive=False)
            if len(spans) == 0:
                continue
            for other_span in spans:
                other_span.replace_with(copy(span))
            note[field_key] = bs.encode(formatter='html5').decode('utf-8')
        col.update_note(note)


def download(col: anki.Collection, nid: anki.notes.NoteId, sid: int):
    '''
    Return value of random span with the sid given notes to search in.
    '''
    note = col.get_note(nid)
    for field_val in note.values():
        bs = BeautifulSoup(field_val, 'html.parser')
        spans = bs.find_all('span', {'class': 'sync', 'sid': sid}, recursive=False)
        if len(spans) > 0:
            return spans[0]
    return None


def sync_field(col: anki.Collection, this_note: anki.notes.Note, field_idx: int,
               popup: Popup = default_popup) -> bool:
    if this_note.id == 0:
        return False  # the card is being created
    if field_idx < 0 or field_idx >= len(this_note.values()):
        return False  # should not happen

    changed = False
    bs = BeautifulSoup(this_note.values()[field_idx], 'html.parser')

    # recursive=False: transitive references are not propagated (only top spans are synced)
    spans = bs.find_all('span', {'class': 'sync', 'note': False}, recursive=False)
    for span in spans:
        if not span.has_attr('sid'):
            sid = generate_sid(col, this_note, field_idx)
            span['sid'] = sid
            changed = True
            continue

        sid = span['sid']
        nids = col.find_notes(f'<span class=\\"sync\\" sid=\\"{sid}\\">')
        if are_spans_coherent(col, nids, sid):
            continue

        if span.string is None:
            answer = 'Download'
        else:
            answer = popup(sid)

        if this_note.id in nids:
            nids.remove(this_note.id)

        if answer == 'Upload':
            upload(col, nids, span)
        else:
            # Idx 0 will always exist. If len(nids) == 1, spans are always coherent
            span.replace_with(download(col, nids[0], sid))

        changed = True

    if changed:
        this_note.values()[field_idx] = bs.encode(formatter='html5').decode('utf-8')
        col.update_note(this_note)
    return changed
