import os
import shutil
import tempfile
from . import *

from anki.collection import Collection as aopen

# Creating new decks is expensive. Just do it once, and then spin off
# copies from the master.
_emptyCol: str | None = None

# TODO: Co když karta neexistuje
# TODO: Co když kartu zrovna přidávám?


def getEmptyCol():
    global _emptyCol
    if not _emptyCol:
        (fd, path) = tempfile.mkstemp(suffix='.anki2')
        os.close(fd)
        os.unlink(path)
        col = aopen(path)
        col.close(downgrade=False)
        _emptyCol = path
    (fd, path) = tempfile.mkstemp(suffix='.anki2')
    shutil.copy(_emptyCol, path)
    col = aopen(path)
    return col


def test_sync_cloze():
    col = getEmptyCol()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" id="{n1.id}"></span>'
    col.addNote(n2)

    update_field(col, n2, 0)
    assert n2['Front'] == f'<span class="sync" id="{n1.id}"><div>one</div></span>'


def test_sync_n_clozes():
    col = getEmptyCol()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}} {{c2::two}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" id="{n1.id}"></span>'
    col.addNote(n2)

    assert update_field(col, n2, 0) == True
    assert n2['Front'] == f'<span class="sync" id="{n1.id}"><div>one two</div></span>'


def test_sync_cloze_hints():
    col = getEmptyCol()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one::hint}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" id="{n1.id}"></span>'
    col.addNote(n2)

    assert update_field(col, n2, 0) == True
    assert n2['Front'] == f'<span class="sync" id="{n1.id}"><div>one</div></span>'


def test_sync_n_clozes_hints():
    col = getEmptyCol()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one::h1}} {{c2::two::h2}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" id="{n1.id}"></span>'
    col.addNote(n2)

    assert update_field(col, n2, 0) == True
    assert n2['Front'] == f'<span class="sync" id="{n1.id}"><div>one two</div></span>'


def test_nbsp():
    col = getEmptyCol()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one&nbsp;two}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" id="{n1.id}"></span>'
    col.addNote(n2)

    assert update_field(col, n2, 0) == True
    assert n2['Front'] == f'<span class="sync" id="{n1.id}"><div>one&nbsp;two</div></span>'

def test_changed():
    col = getEmptyCol()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '<div class="first-upper">cringeis&nbsp;cringe.</div>'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" id="{n1.id}"><div><div class="first-upper">cringeis&nbsp;cringe.</div></div></span>'
    col.addNote(n2)

    assert update_field(col, n2, 0) == False
