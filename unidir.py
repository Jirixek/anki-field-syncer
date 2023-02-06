import re
import anki
from copy import copy
from aqt import mw
from aqt.utils import showInfo
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from typing import Optional
import warnings

warnings.filterwarnings('ignore', category=MarkupResemblesLocatorWarning, module='bs4')

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



# TODO: additional hook editor_did_load_note?
def _check_cycles(this, other):
    pass


def _show_synced_notes():
    # text field with clickable ids in menu bar
    pass


def _strip_cloze(text: str):
    # TODO: nested clozes (add rust function)
    return re.sub(RE_CLOZE, r'\1', text)


def _strip_cloze_overlapping(text: str):
    # TODO: nested clozes
    return re.sub(RE_CLOZE_OVERLAPPER, r'\1', text)


def _fetch_bs_assumptions(bs, note):
    assumptions = note['Assumptions']
    if len(assumptions) > 0:
        div = bs.new_tag('div')
        div['id'] = 'assumptions'
        div.append(BeautifulSoup(note['Assumptions'], 'html.parser'))
        return div
    else:
        return ''


def _fetch_bs_eq_im_text(bs, note):
    text = ''
    for field in TEXT_FIELD_MAP[note.note_type()['name']]:
        text += note[field]
    text += '.'
    div = bs.new_tag('div')
    div['class'] = ['first-upper']
    div.append(BeautifulSoup(text, 'html.parser'))
    return div


def _fetch_bs_eq_im_text_tex(bs, note):
    text = '\\[' + ' '.join([note[field] for field in TEXT_FIELD_MAP[note.note_type()['name']]]) + '\\]'
    div = bs.new_tag('div')
    div.append(BeautifulSoup(text, 'html.parser'))
    return div


def _fetch_bs_eq_im(note: anki.notes.Note, fields: set):
    bs = BeautifulSoup(features='html.parser')
    if 'Assumptions' in fields:
        bs.append(_fetch_bs_assumptions(bs, note))
    if 'Text' in fields:
        bs.append(_fetch_bs_eq_im_text(bs, note))
    return bs


def _fetch_bs_eq_im_tex(note: anki.notes.Note, fields: set):
    bs = BeautifulSoup(features='html.parser')
    if 'Assumptions' in fields:
        bs.append(_fetch_bs_assumptions(bs, note))
    if 'Text' in fields:
        bs.append(_fetch_bs_eq_im_text_tex(bs, note))
    return bs


def _fetch_bs_cloze(note: anki.notes.Note, fields: set):
    bs = BeautifulSoup(features='html.parser')
    if 'Text' in fields:
        div = bs.new_tag('div')
        div.append(BeautifulSoup(_strip_cloze(note['Text']), 'html.parser'))
        bs.append(div)
    return bs


def _fetch_bs_cloze_overlapping(note: anki.notes.Note, fields: set):
    bs = BeautifulSoup(features='html.parser')
    if 'Original' in fields:
        div = bs.new_tag('div')
        div.append(BeautifulSoup(_strip_cloze_overlapping(note['Original']), 'html.parser'))
        bs.append(div)
    return bs


def _fetch_bs_cloze_overlapping_algo(note: anki.notes.Note, fields: set):
    bs = BeautifulSoup(features='html.parser')
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
        div.append(BeautifulSoup(_strip_cloze_overlapping(note['Original']), 'html.parser'))
        bs.append(div)
    return bs


def _fetch_bs(note: anki.notes.Note, fields: Optional[set] = None):
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
        if notetype not in DEFAULT_FIELDS:
            raise ValueError('Unknown model')
        fields = DEFAULT_FIELDS[notetype]

    if notetype in {'Cloze', 'Cloze (center)'}:
        return _fetch_bs_cloze(note, fields)
    elif notetype == 'Cloze (overlapping)':
        return _fetch_bs_cloze_overlapping(note, fields)
    elif notetype == 'Cloze (overlapping) - algo':
        return _fetch_bs_cloze_overlapping_algo(note, fields)
    elif notetype in EQ_IM_NAMES:
        return _fetch_bs_eq_im(note, fields)
    elif notetype in EQ_IM_TEX_NAMES:
        return _fetch_bs_eq_im_tex(note, fields)

    raise ValueError('Unknown model')


def sync_field(col: anki.Collection, note: anki.notes.Note, field_idx: int):
    # - find span with class 'sync'
    # - _fetch 'id' attribute
    # - _fetch optional 'fields' attribute (can contain special fields: text)
    # - or use defaults depending on the target note type)
    #   - EQ/IM: copy assumptions and text
    #   - Cloze [overlapper]: copy text
    #   - Algos: copy text, input, and output
    # - strip {{c1::}} and [[oc1::]]

    # TODO: multi_valued_attributes={'*': ['class', 'fields']}

    if note is None:
        # e.g. card is being created
        return False
    if field_idx < 0 or field_idx >= len(note.values()):
        # Should not happen
        return False

    changed = False
    bs = BeautifulSoup(note.values()[field_idx], 'html.parser')

    # Transitive references are not propagated (only top spans are synced)
    spans = bs.find_all('span', {'class': 'sync', 'note': True}, recursive=False)
    for span in spans:
        other_id = span.get('note')
        if other_id is None:
            continue

        span_new = copy(span)
        span_new.clear()
        try:
            other_note = col.get_note(int(other_id))
            other_fields = span.get('fields')
            bs_new = _fetch_bs(other_note, other_fields)
            span_new.append(bs_new)
        except (ValueError, anki.errors.NotFoundError) as e:
            div = bs.new_tag('div')
            if str(e) == 'Unknown model':
                div.string = 'Unknown model'
            else:
                div.string = 'Invalid note ID'
            span_new.append(div)

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
    return changed


def sync_note(col: anki.Collection, note: anki.notes.Note):
    for field in note.keys():
        sync_field(col, note, note._field_index(field))


def sync_all():
    ids = mw.col.find_notes('span class=\\"sync\\"')
    for id in ids:
        note = mw.col.get_note(id)
        sync_note(mw.col, note)
    showInfo('Spans synced')
