import pytest
import anki
import os
import shutil
import tempfile
from . import unidir
from bs4 import MarkupResemblesLocatorWarning
from anki.collection import Collection as aopen

pytestmark = pytest.mark.filterwarnings(
    'ignore', category=MarkupResemblesLocatorWarning, module='bs4')


def create_custom_notes(col: anki.Collection):
    CUSTOM_NOTES = {
        'EQ': ('EQ1', 'Delimiter', 'EQ2', 'Assumptions'),
        'EQ (assumptions)': ('EQ1', 'Delimiter', 'EQ2', 'Assumptions'),
        'EQ (TEX)': ('EQ1', 'Delimiter', 'EQ2', 'Assumptions'),
        'EQ (TEX, assumptions)': ('EQ1', 'Delimiter', 'EQ2', 'Assumptions'),
        'IM': ('Context Left', 'Cloze', 'Assumptions'),
        'IM (assumptions)': ('Context Left', 'Cloze', 'Assumptions'),
        'IM (assumptions, reversed)': ('Context Left', 'Cloze Left', 'Context Middle', 'Cloze Right', 'Assumptions'),
        'IM (reversed)': ('Context Left', 'Cloze Left', 'Context Middle', 'Cloze Right', 'Assumptions'),
        'IM (TEX)': ('Cloze Left', 'Context Middle', 'Cloze Right', 'Assumptions'),
        'IM (TEX, assumptions)': ('Cloze Left', 'Context Middle', 'Cloze Right', 'Assumptions'),
        'IM (TEX, assumptions, reversed)': ('Cloze Left', 'Context Middle', 'Cloze Right', 'Assumptions'),
        'IM (TEX, reversed)': ('Cloze Left', 'Context Middle', 'Cloze Right', 'Assumptions'),
    }

    for name, fields in CUSTOM_NOTES.items():
        models = col.models
        model = models.new(name)
        template = models.new_template('Template 1')
        for field in fields:
            models.add_field(model, models.new_field(field))
            template["qfmt"] += '{{' + field + '}}'
            template["afmt"] += '{{' + field + '}}'
        models.add_template(model, template)
        models.add_dict(model)

# Creating new decks is expensive. Just do it once, and then spin off
# copies from the master.
_emptyCol: str | None = None


def get_empty_col():
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
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one</div>\n</span>'


def test_sync_n_clozes():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}} {{c2::two}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one two</div>\n</span>'


def test_sync_cloze_hints():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one::hint}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one</div>\n</span>'


def test_sync_n_clozes_hints():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one::h1}} {{c2::two::h2}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one two</div>\n</span>'


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize('model', ['EQ', 'EQ (assumptions)'])
def test_eq(model, with_assumptions):
    col = get_empty_col()
    create_custom_notes(col)

    basic = col.models.by_name('Basic')
    eq = col.models.by_name(model)

    n1 = col.new_note(eq)
    n1['EQ1'] = 'EQ1'
    n1['Delimiter'] = 'Delimiter'
    n1['EQ2'] = 'EQ2'
    n1['Assumptions'] = 'Assumptions' if with_assumptions else ''
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\">Assumptions</div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div class="first-upper">{n1["EQ1"]}{n1["Delimiter"]}{n1["EQ2"]}.</div>\n'
        '</span>'
    )


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize('model', ['EQ (TEX)', 'EQ (TEX, assumptions)'])
def test_eq_tex(model, with_assumptions):
    col = get_empty_col()
    create_custom_notes(col)

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['EQ1'] = 'EQ1'
    n1['Delimiter'] = 'Delimiter'
    n1['EQ2'] = 'EQ2'
    n1['Assumptions'] = 'Assumptions' if with_assumptions else ''
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\">Assumptions</div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div>\\[{n1["EQ1"]} {n1["Delimiter"]} {n1["EQ2"]}\\]</div>\n'
        '</span>'
    )


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize('model', ['IM', 'IM (assumptions)'])
def test_im(model, with_assumptions):
    col = get_empty_col()
    create_custom_notes(col)

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['Context Left'] = 'Context Left'
    n1['Cloze'] = 'Cloze'
    n1['Assumptions'] = 'Assumptions' if with_assumptions else ''
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\">Assumptions</div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div class="first-upper">{n1["Context Left"]}{n1["Cloze"]}.</div>\n'
        '</span>'
    )


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize('model', ['IM (reversed)', 'IM (assumptions, reversed)'])
def test_im_reversed(model, with_assumptions):
    col = get_empty_col()
    create_custom_notes(col)

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['Context Left'] = 'Context Left'
    n1['Cloze Left'] = 'Cloze Left'
    n1['Context Middle'] = 'Context Middle'
    n1['Cloze Right'] = 'Cloze Right'
    n1['Assumptions'] = 'Assumptions' if with_assumptions else ''
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\">Assumptions</div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div class="first-upper">{n1["Context Left"]}{n1["Cloze Left"]}{n1["Context Middle"]}{n1["Cloze Right"]}.</div>\n'
        '</span>'
    )


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize(
    'model', ['IM (TEX)', 'IM (TEX, assumptions)',
              'IM (TEX, reversed)', 'IM (TEX, assumptions, reversed)'])
def test_im_tex(model, with_assumptions):
    col = get_empty_col()
    create_custom_notes(col)

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['Cloze Left'] = 'Cloze Left'
    n1['Context Middle'] = 'Context Middle'
    n1['Cloze Right'] = 'Cloze Right'
    n1['Assumptions'] = 'Assumptions' if with_assumptions else ''
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\">Assumptions</div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div>\\[{n1["Cloze Left"]} {n1["Context Middle"]} {n1["Cloze Right"]}\\]</div>\n'
        '</span>'
    )


def test_nbsp():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one&nbsp;two}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one&nbsp;two</div>\n</span>'


def test_changed():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '<div class="first-upper">cringeis&nbsp;cringe.</div>'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}">\n<div><div class="first-upper">cringeis&nbsp;cringe.</div></div>\n</span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is False


def test_invalid_target_id_int():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" note="1234"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == '<span class="sync" note="1234"><div>Invalid note ID</div></span>'


def test_invalid_target_id_string():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" note="foo"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == '<span class="sync" note="foo"><div>Invalid note ID</div></span>'


def test_invalid_arg_note():
    # e.g. card is being created
    col = get_empty_col()
    assert unidir.sync_field(col, None, 0) is False
    # No exception raised


def test_invalid_arg_field_id():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" note="foo"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 42) is False
    # No exception raised


def test_dont_change_spans_without_note_attribute():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is False
    assert n2['Front'] == '<span class="sync"></span>'


def test_dont_change_spans_without_sync_class():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is False
    assert n2['Front'] == f'<span note="{n1.id}"></span>'


def test_unknown_note_type():
    col = get_empty_col()

    basic = col.models.by_name('Basic')

    models = col.models
    unknown = models.new('Foo')
    models.add_field(unknown, models.new_field('Front'))
    template = models.new_template('Template 1')
    template["qfmt"] += '{{Front}}'
    template["afmt"] += '{{Front}}'
    models.add_template(unknown, template)
    models.add_dict(unknown)

    unknown = col.models.by_name('Foo')
    n1 = col.new_note(unknown)
    n1['Front'] = 'one'
    col.addNote(n1)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.addNote(n2)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}"><div>Unknown model</div></span>'


def test_cycles():
    col = get_empty_col()
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    col.addNote(n1)
    n2 = col.new_note(cloze)
    n2['Text'] = f'Before2 <span class="sync" note="{n1.id}"></span> After2'
    col.addNote(n2)
    n1['Text'] = f'Before1 <span class="sync" note="{n2.id}"></span> After1'
    col.update_note(n1)

    assert unidir.sync_field(col, n1, 0) is True
    assert unidir.sync_field(col, n2, 0) is True
    assert n1['Text'] == f'Before1 <span class="sync" note="{n2.id}"><div>Cycle detected</div></span> After1'
    assert n2['Text'] == f'Before2 <span class="sync" note="{n1.id}"><div>Cycle detected</div></span> After2'
