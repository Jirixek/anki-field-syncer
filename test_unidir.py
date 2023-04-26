import pytest
from . import unidir
from .util import get_empty_col


def test_sync_cloze():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one</div>\n</span>'


def test_sync_n_clozes():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}} {{c2::two}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one two</div>\n</span>'


def test_sync_cloze_hints():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one::hint}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one</div>\n</span>'


def test_sync_n_clozes_hints():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one::h1}} {{c2::two::h2}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one two</div>\n</span>'


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize('model', ['EQ', 'EQ (assumptions)'])
def test_eq(model, with_assumptions):
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    eq = col.models.by_name(model)

    n1 = col.new_note(eq)
    n1['EQ1'] = 'EQ1'
    n1['Delimiter'] = 'Delimiter'
    n1['EQ2'] = 'EQ2'
    n1['Assumptions'] = 'Assumptions' if with_assumptions else ''
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

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

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['EQ1'] = 'EQ1'
    n1['Delimiter'] = 'Delimiter'
    n1['EQ2'] = 'EQ2'
    n1['Assumptions'] = 'Assumptions' if with_assumptions else ''
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

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

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['Context Left'] = 'Context Left'
    n1['Cloze'] = 'Cloze'
    n1['Assumptions'] = 'Assumptions' if with_assumptions else ''
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

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

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['Context Left'] = 'Context Left'
    n1['Cloze Left'] = 'Cloze Left'
    n1['Context Middle'] = 'Context Middle'
    n1['Cloze Right'] = 'Cloze Right'
    n1['Assumptions'] = 'Assumptions' if with_assumptions else ''
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

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

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['Cloze Left'] = 'Cloze Left'
    n1['Context Middle'] = 'Context Middle'
    n1['Cloze Right'] = 'Cloze Right'
    n1['Assumptions'] = 'Assumptions' if with_assumptions else ''
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\">Assumptions</div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div>\\[{n1["Cloze Left"]} {n1["Context Middle"]} {n1["Cloze Right"]}\\]</div>\n'
        '</span>'
    )


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize('model', ['EQ', 'EQ (assumptions)'])
def test_eq_with_hint(model, with_assumptions):
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    eq = col.models.by_name(model)

    n1 = col.new_note(eq)
    n1['EQ1'] = 'EQ1::hint_eq1'
    n1['Delimiter'] = 'Delimiter'
    n1['EQ2'] = 'EQ2::hint_eq2'
    n1['Assumptions'] = '<ol><li>Assumption1</li><li>Before [[assumption2::assumption hint]]</li></ol>' if with_assumptions else ''
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\"><ol><li>Assumption1</li><li>Before assumption2</li></ol></div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div class="first-upper">EQ1DelimiterEQ2.</div>\n'
        '</span>'
    )


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize('model', ['EQ (TEX)', 'EQ (TEX, assumptions)'])
def test_eq_tex_with_hint(model, with_assumptions):
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['EQ1'] = 'EQ1::hint_eq1'
    n1['Delimiter'] = 'Delimiter'
    n1['EQ2'] = 'EQ2::hint_eq2'
    n1['Assumptions'] = '<ol><li>Assumption1</li><li>Before [[assumption2::assumption hint]]</li></ol>' if with_assumptions else ''
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\"><ol><li>Assumption1</li><li>Before assumption2</li></ol></div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div>\\[EQ1 {n1["Delimiter"]} EQ2\\]</div>\n'
        '</span>'
    )


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize('model', ['IM', 'IM (assumptions)'])
def test_im_with_hint(model, with_assumptions):
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['Context Left'] = 'Context Left'
    n1['Cloze'] = 'Cloze::hint'
    n1['Assumptions'] = '<ol><li>Assumption1</li><li>Before [[assumption2::assumption hint]]</li></ol>' if with_assumptions else ''
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\"><ol><li>Assumption1</li><li>Before assumption2</li></ol></div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div class="first-upper">{n1["Context Left"]}Cloze.</div>\n'
        '</span>'
    )


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize('model', ['IM (reversed)', 'IM (assumptions, reversed)'])
def test_im_reversed_with_hint(model, with_assumptions):
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['Context Left'] = 'Context Left'
    n1['Cloze Left'] = 'Cloze Left::hint_cloze_left'
    n1['Context Middle'] = 'Context Middle'
    n1['Cloze Right'] = 'Cloze Right::hint_cloze_right'
    n1['Assumptions'] = '<ol><li>Assumption1</li><li>Before [[assumption2::assumption hint]]</li></ol>' if with_assumptions else ''
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\"><ol><li>Assumption1</li><li>Before assumption2</li></ol></div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div class="first-upper">{n1["Context Left"]}Cloze Left{n1["Context Middle"]}Cloze Right.</div>\n'
        '</span>'
    )


@pytest.mark.parametrize('with_assumptions', [False, True])
@pytest.mark.parametrize(
    'model', ['IM (TEX)', 'IM (TEX, assumptions)',
              'IM (TEX, reversed)', 'IM (TEX, assumptions, reversed)'])
def test_im_tex_with_hint(model, with_assumptions):
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    m = col.models.by_name(model)

    n1 = col.new_note(m)
    n1['Cloze Left'] = 'Cloze Left::hint_cloze_left'
    n1['Context Middle'] = 'Context Middle'
    n1['Cloze Right'] = 'Cloze Right::hint_cloze_right'
    n1['Assumptions'] = '<ol><li>Assumption1</li><li>Before [[assumption2::assumption hint]]</li></ol>' if with_assumptions else ''
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assumptions_expected = '<div id=\"assumptions\"><ol><li>Assumption1</li><li>Before assumption2</li></ol></div>\n' if with_assumptions else ''
    assert n2['Front'] == (
        f'<span class="sync" note="{n1.id}">\n' +
        assumptions_expected +
        f'<div>\\[Cloze Left {n1["Context Middle"]} Cloze Right\\]</div>\n'
        '</span>'
    )


def test_nbsp():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one&nbsp;two}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one&nbsp;two</div>\n</span>'


def test_changed():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '<div class="first-upper">cringeis&nbsp;cringe.</div>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}">\n<div><div class="first-upper">cringeis&nbsp;cringe.</div></div>\n</span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is False


def test_invalid_target_id_int():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" note="1234"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == '<span class="sync" note="1234"><div>Invalid note ID</div></span>'


def test_invalid_target_id_string():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" note="foo"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == '<span class="sync" note="foo"><div>Invalid note ID</div></span>'


def test_card_is_being_created():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'

    assert unidir.sync_field(col, n2, 0) is False
    # No exception raised


def test_invalid_arg_field_id():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" note="foo"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 42) is False
    # No exception raised


def test_dont_change_spans_without_note_attribute():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is False
    assert n2['Front'] == '<span class="sync"></span>'


def test_dont_change_spans_without_sync_class():
    col = get_empty_col()

    basic = col.models.by_name('Basic')
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    n1['Text'] = '{{c1::one}}'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span note="{n1.id}"></span>'
    col.add_note(n2, 0)

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
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
    col.add_note(n2, 0)

    assert unidir.sync_field(col, n2, 0) is True
    assert n2['Front'] == f'<span class="sync" note="{n1.id}"><div>Unknown model</div></span>'


def test_cycles():
    col = get_empty_col()
    cloze = col.models.by_name('Cloze')

    n1 = col.new_note(cloze)
    col.add_note(n1, 0)
    n2 = col.new_note(cloze)
    n2['Text'] = f'Before2 <span class="sync" note="{n1.id}"></span> After2'
    col.add_note(n2, 0)
    n1['Text'] = f'Before1 <span class="sync" note="{n2.id}"></span> After1'
    col.update_note(n1)

    assert unidir.sync_field(col, n1, 0) is True
    assert unidir.sync_field(col, n2, 0) is True
    assert n1['Text'] == f'Before1 <span class="sync" note="{n2.id}"><div>Cycle detected</div></span> After1'
    assert n2['Text'] == f'Before2 <span class="sync" note="{n1.id}"><div>Cycle detected</div></span> After2'
