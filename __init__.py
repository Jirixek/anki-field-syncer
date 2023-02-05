import re
import anki
from copy import copy
from aqt import mw
from aqt import gui_hooks
from aqt.utils import showInfo
from aqt.qt import *
from bs4 import BeautifulSoup
from typing import Optional

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='bs4')

RE_CLOZE = re.compile(r'{{c\d+::(.*?)(::.*?)?}}', re.DOTALL)
RE_CLOZE_OVERLAPPER = re.compile(r'\[\[oc\d+::(.*?)(::.*?)?\]\]', re.DOTALL)

TEXT_FIELD_MAP = {
    'EQ': ('EQ1', 'Delimiter', 'EQ2'),
    'EQ (assumptions)': ('EQ1', 'Delimiter', 'EQ2'),
    'EQ (TEX)': ('EQ1', 'Delimiter', 'EQ2'),
    'EQ (TEX, assumptions)': ('EQ1', 'Delimiter', 'EQ2'),
    'IM': ('Context Left', 'Cloze'),
    'IM (assumptions)': ('Context Left', 'Cloze'),
    'IM (assumptions, reversed)': ('Context Left', 'Cloze Left', 'Context Middle', 'Cloze Right'),
    'IM (reversed)': ('Context Left', 'Cloze Left', 'Context Middle', 'Cloze Right'),
    'IM (TEX)': ('Cloze Left', 'Context Middle', 'Cloze Right'),
    'IM (TEX, assumptions)': ('Cloze Left', 'Context Middle', 'Cloze Right'),
    'IM (TEX, assumptions, reversed)': ('Cloze Left', 'Context Middle', 'Cloze Right'),
    'IM (TEX, reversed)': ('Cloze Left', 'Context Middle', 'Cloze Right'),
}



# TODO: double synced spans

# TODO: additional hook editor_did_load_note?
def check_cycles():
    pass


def show_synced_notes():
    # text field with clickable ids in menu bar
    pass


def strip_cloze(text: str):
    # TODO: nested clozes (add rust function)
    return re.sub(RE_CLOZE, r'\1', text)


def strip_cloze_overlapping(text: str):
    # TODO: nested clozes
    return re.sub(RE_CLOZE_OVERLAPPER, r'\1', text)


def fetch_bs_assumptions(bs, note):
    assumptions = note['Assumptions']
    if len(assumptions) > 0:
        div = bs.new_tag('div')
        div['id'] = 'assumptions'
        div.append(BeautifulSoup(note['Assumptions'], 'html.parser'))
        return div
    else:
        return ''


def fetch_bs_eq_im_text(bs, note):
    text = ''
    for field in TEXT_FIELD_MAP[note.note_type()['name']]:
        text += note[field]
    text += '.'
    div = bs.new_tag('div')
    div['class'] = ['first-upper']
    div.append(BeautifulSoup(text, 'html.parser'))
    return div


def fetch_bs_eq_im_text_tex(bs, note):
    text = '\\['
    # TODO: join()
    for field in TEXT_FIELD_MAP[note.note_type()['name']]:
        text += note[field] + ' '
    text += '\\]'
    div = bs.new_tag('div')
    div.append(BeautifulSoup(text, 'html.parser'))
    return div


def fetch_bs_eq_im(note: anki.notes.Note, fields: set):
    bs = BeautifulSoup(parser='html.parser')
    if 'Assumptions' in fields:
        bs.append(fetch_bs_assumptions(bs, note))
    if 'Text' in fields:
        bs.append(fetch_bs_eq_im_text(bs, note))
    return bs


def fetch_bs_eq_im_tex(note: anki.notes.Note, fields: set):
    bs = BeautifulSoup(parser='html.parser')
    if 'Assumptions' in fields:
        bs.append(fetch_bs_assumptions(bs, note))
    if 'Text' in fields:
        bs.append(fetch_bs_eq_im_text_tex(bs, note))
    return bs


def fetch_bs_cloze(note: anki.notes.Note, fields: set):
    bs = BeautifulSoup(parser='html.parser')
    if 'Text' in fields:
        div = bs.new_tag('div')
        div.append(BeautifulSoup(strip_cloze(note['Text']), 'html.parser'))
        bs.append(div)
    return bs


def fetch_bs_cloze_overlapping(note: anki.notes.Note, fields: set):
    bs = BeautifulSoup(parser='html.parser')
    if 'Original' in fields:
        div = bs.new_tag('div')
        div.append(BeautifulSoup(strip_cloze_overlapping(note['Original']), 'html.parser'))
        bs.append(div)
    return bs


def fetch_bs_cloze_overlapping_algo(note: anki.notes.Note, fields: set):
    bs = BeautifulSoup(parser='html.parser')
    if 'Input' in fields:
        text = note['Input']
        if len(text) > 0:
            div = bs.new_tag('div')
            span = bs.new_tag('span')
            span['class'] = ['bold']
            span.string = 'Vstup: '
            div.append(span)
            div.append(text)
            bs.append(div)
    if 'Output' in fields:
        text = note['Output']
        if len(text) > 0:
            div = bs.new_tag('div')
            span = bs.new_tag('span')
            span['class'] = ['bold']
            span.string = 'Výstup: '
            div.append(span)
            div.append(text)
            bs.append(div)
    if 'Original' in fields:
        div = bs.new_tag('div')
        div.append(BeautifulSoup(strip_cloze_overlapping(note['Original']), 'html.parser'))
        bs.append(div)
    return bs


def fetch_bs(note: anki.notes.Note, fields: Optional[set] = None):
    DEFAULT_FIELDS = {
        'Cloze': {'Text'},
        'Cloze (center)': {'Text'},
        'Cloze (overlapping)': {'Original'},
        'Cloze (overlapping) - algo': {'Input', 'Output', 'Original'},
        'EQ': {'Assumptions', 'Text'},
        'EQ (assumptions)': {'Assumptions', 'Text'},
        'EQ (TEX)': {'Assumptions', 'Text'},
        'EQ (TEX, assumptions)': {'Assumptions', 'Text'},
        'IM': {'Assumptions', 'Text'},
        'IM (assumptions)': {'Assumptions', 'Text'},
        'IM (assumptions, reversed)': {'Assumptions', 'Text'},
        'IM (reversed)': {'Assumptions', 'Text'},
        'IM (TEX)': {'Assumptions', 'Text'},
        'IM (TEX, assumptions)': {'Assumptions', 'Text'},
        'IM (TEX, assumptions, reversed)': {'Assumptions', 'Text'},
        'IM (TEX, reversed)': {'Assumptions', 'Text'},
    }

    # TODO: basics
    # TODO: error handling when no default field

    EQ_IM_NAMES = {
        'EQ',
        'EQ (assumptions)',
        'IM',
        'IM (assumptions)',
        'IM (assumptions, reversed)',
        'IM (reversed)'
    }

    EQ_IM_TEX_NAMES = {
        'EQ (TEX)',
        'EQ (TEX, assumptions)',
        'IM (TEX)',
        'IM (TEX, assumptions)',
        'IM (TEX, assumptions, reversed)',
        'IM (TEX, reversed)'
    }

    notetype = note.note_type()['name']

    if fields is None:
        fields = DEFAULT_FIELDS[notetype]

    if notetype in {'Cloze', 'Cloze (center)'}:
        return fetch_bs_cloze(note, fields)
    if notetype == 'Cloze (overlapping)':
        return fetch_bs_cloze_overlapping(note, fields)
    if notetype == 'Cloze (overlapping) - algo':
        return fetch_bs_cloze_overlapping_algo(note, fields)
    elif notetype in EQ_IM_NAMES:
        return fetch_bs_eq_im(note, fields)
    elif notetype in EQ_IM_TEX_NAMES:
        return fetch_bs_eq_im_tex(note, fields)


def sync_field(col: anki.Collection, note: anki.notes.Note, field_idx: int):
    # - find span with class 'sync'
    # - fetch 'id' attribute
    # - fetch optional 'fields' attribute (can contain special fields: text)
    # - or use defaults depending on the target note type)
    #   - EQ/IM: copy assumptions and text
    #   - Cloze [overlapper]: copy text
    #   - Algos: copy text, input, and output
    # - strip {{c1::}} and [[oc1::]]

    # multi_valued_attributes={'*': ['class', 'fields']}

    changed = False
    bs = BeautifulSoup(note.values()[field_idx], 'html.parser')

    # TODO: only with attribute note
    # Transitive references are not propagated (only top spans are synced)
    spans = bs.find_all('span', {'class': 'sync'}, recursive=False)
    for span in spans:
        other_id = span.get('id')
        if other_id is None:
            continue
        other_fields = span.get('fields')
        # TODO: try/catch for int
        other_note = col.get_note(int(other_id))
        bs_new = fetch_bs(other_note, other_fields)
        span_new = copy(span)
        span_new.clear()
        span_new.append(bs_new)
        if span != span_new:
            span.replace_with(span_new)
            changed = True

    # TODO
    # cycles references are forbidden: if target field contains ref to src field:
    # - no changes are made (no sync)
    # - error text on top of field appears

    if changed:
        note.values()[field_idx] = bs.encode(formatter='html5').decode('utf-8')
        col.update_note(note)
        return True
    else:
        return False


def sync_note(col: anki.Collection, note: anki.notes.Note):
    for field in note.keys():
        sync_field(col, note, note._field_index(field))


def sync_all():
    ids = mw.col.find_notes('span class=\\"sync\\"')
    for id in ids:
        note = mw.col.get_note(id)
        sync_note(mw.col, note)
    showInfo('Spans synced')


def on_editor_did_unfocus_field(changed: bool, note: anki.notes.Note, field_idx: int) -> bool:
    # return True if changes were made, otherwise return changed
    changed |= sync_field(mw.col, note, field_idx)
    return changed


gui_hooks.editor_did_unfocus_field.append(on_editor_did_unfocus_field)

action = QAction('Sync spans', mw)
qconnect(action.triggered, sync_all)
mw.form.menuTools.addAction(action)
