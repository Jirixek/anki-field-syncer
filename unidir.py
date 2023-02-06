import re
import anki
from copy import copy
from aqt import mw
from aqt.utils import showInfo
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings

warnings.filterwarnings('ignore', category=MarkupResemblesLocatorWarning, module='bs4')

# TODO: additional hook editor_did_load_note?
def _check_cycles(this, other):
    pass


def _show_synced_notes():
    # text field with clickable ids in menu bar
    pass


class Fetcher():
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

    RE_CLOZE = re.compile(r'{{c\d+::(.*?)(::.*?)?}}', re.DOTALL)
    RE_CLOZE_OVERLAPPER = re.compile(r'\[\[oc\d+::(.*?)(::.*?)?\]\]', re.DOTALL)


    def __init__(self, this_note: anki.notes.Note, other_note: anki.notes.Note):
        self.this_note = this_note
        self.other_note = other_note

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

        notetype = self.other_note.note_type()['name']
        if notetype not in DEFAULT_FIELDS:
            raise ValueError('Unknown model')
        self.other_fields = DEFAULT_FIELDS[notetype]


    @staticmethod
    def __strip_cloze(text: str):
        # TODO: nested clozes (add rust function)
        return re.sub(Fetcher.RE_CLOZE, r'\1', text)


    @staticmethod
    def __strip_cloze_overlapping(text: str):
        # TODO: nested clozes
        return re.sub(Fetcher.RE_CLOZE_OVERLAPPER, r'\1', text)


    def __check_cycles(self, text_other: str):
        bs = BeautifulSoup(text_other, 'html.parser')
        spans = bs.find_all('span', {'class': 'sync', 'note': True}, recursive=False)
        for span in spans:
            other_id = span.get('note')
            if other_id == str(self.this_note.id):
                raise ValueError('Cycle detected')
        return text_other


    def __fetch_field(self, field: str):
        text = self.other_note[field]
        return self.__check_cycles(text)


    def __fetch_cloze_field(self, field: str):
        text = self.__strip_cloze(self.other_note[field])
        return self.__check_cycles(text)


    def __fetch_cloze_overlapping_field(self, field: str):
        text = self.__strip_cloze_overlapping(self.other_note[field])
        return self.__check_cycles(text)


    def __fetch_assumptions(self, bs: BeautifulSoup):
        assumptions = self.__fetch_field('Assumptions')
        if len(assumptions) > 0:
            div = bs.new_tag('div')
            div['id'] = 'assumptions'
            div.append(BeautifulSoup(assumptions, 'html.parser'))
            return div
        else:
            return ''


    def __fetch_eq_im_text(self, bs: BeautifulSoup):
        text = ''
        for field in self.TEXT_FIELD_MAP[self.other_note.note_type()['name']]:
            text += self.__fetch_field(field)
        text += '.'
        div = bs.new_tag('div')
        div['class'] = ['first-upper']
        div.append(BeautifulSoup(text, 'html.parser'))
        return div


    def __fetch_eq_im_text_tex(self, bs: BeautifulSoup):
        text = '\\[' + ' '.join([self.__fetch_field(field) for field in self.TEXT_FIELD_MAP[self.other_note.note_type()['name']]]) + '\\]'
        div = bs.new_tag('div')
        div.append(BeautifulSoup(text, 'html.parser'))
        return div


    def __fetch_eq_im(self):
        bs = BeautifulSoup(features='html.parser')
        if 'Assumptions' in self.other_fields:
            bs.append(self.__fetch_assumptions(bs))
        if 'Text' in self.other_fields:
            bs.append(self.__fetch_eq_im_text(bs))
        return bs


    def __fetch_eq_im_tex(self):
        bs = BeautifulSoup(features='html.parser')
        if 'Assumptions' in self.other_fields:
            bs.append(self.__fetch_assumptions(bs))
        if 'Text' in self.other_fields:
            bs.append(self.__fetch_eq_im_text_tex(bs))
        return bs


    def __fetch_cloze(self):
        bs = BeautifulSoup(features='html.parser')
        if 'Text' in self.other_fields:
            div = bs.new_tag('div')
            div.append(BeautifulSoup(self.__fetch_cloze_field('Text'), 'html.parser'))
            bs.append(div)
        return bs


    def __fetch_cloze_overlapping(self):
        bs = BeautifulSoup(features='html.parser')
        if 'Original' in self.other_fields:
            div = bs.new_tag('div')
            div.append(BeautifulSoup(self.__fetch_cloze_overlapping_field('Original'), 'html.parser'))
            bs.append(div)
        return bs


    def __fetch_cloze_overlapping_algo(self):
        bs = BeautifulSoup(features='html.parser')
        if 'Input' in self.other_fields:
            text = self.other_note['Input']
            if len(text) > 0:
                div = bs.new_tag('div')
                span = bs.new_tag('span')
                span['class'] = ['bold']
                span.string = 'Vstup: '
                div.append(span)
                div.append(text)
                bs.append(div)
        if 'Output' in self.other_fields:
            text = self.other_note['Output']
            if len(text) > 0:
                div = bs.new_tag('div')
                span = bs.new_tag('span')
                span['class'] = ['bold']
                span.string = 'Výstup: '
                div.append(span)
                div.append(text)
                bs.append(div)
        if 'Original' in self.other_fields:
            div = bs.new_tag('div')
            div.append(BeautifulSoup(self.__fetch_cloze_overlapping_field('Original'), 'html.parser'))
            bs.append(div)
        return bs


    def fetch(self):
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

        notetype = self.other_note.note_type()['name']

        if notetype in {'Cloze', 'Cloze (center)'}:
            return self.__fetch_cloze()
        elif notetype == 'Cloze (overlapping)':
            return self.__fetch_cloze_overlapping()
        elif notetype == 'Cloze (overlapping) - algo':
            return self.__fetch_cloze_overlapping_algo()
        elif notetype in EQ_IM_NAMES:
            return self.__fetch_eq_im()
        elif notetype in EQ_IM_TEX_NAMES:
            return self.__fetch_eq_im_tex()

        raise ValueError('Unknown model')


def sync_field(col: anki.Collection, this_note: anki.notes.Note, field_idx: int):
    # - find span with class 'sync' with 'note' attribute
    # - fetch optional 'fields' attribute (can contain special fields: text)
    # - or use defaults depending on the target note type)
    #   - EQ/IM: copy assumptions and text
    #   - Cloze [overlapper]: copy text
    #   - Algos: copy text, input, and output
    # - strip {{c1::}} and [[oc1::]]

    # TODO: multi_valued_attributes={'*': ['class', 'fields']}

    if this_note is None:
        return False  # e.g. card is being created
    if field_idx < 0 or field_idx >= len(this_note.values()):
        return False  # should not happen

    changed = False
    bs = BeautifulSoup(this_note.values()[field_idx], 'html.parser')

    # recursive=False: transitive references are not propagated (only top spans are synced)
    spans = bs.find_all('span', {'class': 'sync', 'note': True}, recursive=False)
    for span in spans:
        other_id = span.get('note')
        if other_id is None:
            continue

        span_new = copy(span)
        span_new.clear()
        try:
            other_note = col.get_note(int(other_id))
            # other_fields = span.get('fields')
            bs_new = Fetcher(this_note, other_note).fetch()
            span_new.append(bs_new)
        except (ValueError, anki.errors.NotFoundError) as e:
            div = bs.new_tag('div')
            if str(e) in {'Unknown model', 'Cycle detected'}:
                div.string = str(e)
            else:
                div.string = 'Invalid note ID'
            span_new.append(div)

        if span != span_new:
            span.replace_with(span_new)
            changed = True

    if changed:
        this_note.values()[field_idx] = bs.encode(formatter='html5').decode('utf-8')
        col.update_note(this_note)
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
