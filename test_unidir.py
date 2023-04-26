import pytest
import anki
from . import unidir
from .util import get_empty_col
from typing import Sequence


class TestBasicCloze():
    def setup_method(self, method):
        self.col = get_empty_col()
        self.basic = self.col.models.by_name('Basic')
        self.cloze = self.col.models.by_name('Cloze')

    def test_sync_cloze(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one</div>\n</span>'

    def test_sync_n_clozes(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one}} {{c2::two}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one two</div>\n</span>'

    def test_sync_cloze_hints(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one::hint}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one</div>\n</span>'

    def test_sync_n_clozes_hints(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one::h1}} {{c2::two::h2}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one two</div>\n</span>'

    def test_nbsp(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one&nbsp;two}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == f'<span class="sync" note="{n1.id}">\n<div>one&nbsp;two</div>\n</span>'

    def test_changed(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '<div class="first-upper">cringeis&nbsp;cringe.</div>'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}">\n<div><div class="first-upper">cringeis&nbsp;cringe.</div></div>\n</span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is False

    def test_invalid_target_id_int(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = '<span class="sync" note="1234"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == '<span class="sync" note="1234"><div>Invalid note ID</div></span>'

    def test_invalid_target_id_string(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = '<span class="sync" note="foo"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == '<span class="sync" note="foo"><div>Invalid note ID</div></span>'

    def test_card_is_being_created(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'

        assert unidir.sync_field(self.col, n2, 0) is False
        # No exception raised

    def test_invalid_arg_field_id(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = '<span class="sync" note="foo"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 42) is False
        # No exception raised

    def test_dont_change_spans_without_note_attribute(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is False
        assert n2['Front'] == '<span class="sync"></span>'

    def test_dont_change_spans_without_sync_class(self):
        n1 = self.col.new_note(self.cloze)
        n1['Text'] = '{{c1::one}}'
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is False
        assert n2['Front'] == f'<span note="{n1.id}"></span>'


@pytest.mark.parametrize('with_assumptions', [False, True])
class TestImEq():
    def setup_method(self, method):
        self.col = get_empty_col()
        self.basic = self.col.models.by_name('Basic')

    def fill_im_eq_note(self, note: anki.notes.Note, with_assumptions: bool, hint_fields: Sequence[str]):
        hint_fields = set(hint_fields)
        for key in note.keys():
            if key in hint_fields:
                note[key] = f'{key}::Hint {key}'
            else:
                note[key] = str(key)

        assumptions_expected_str = (
            '<div id=\"assumptions\">'
            '<ol><li>Assumption1</li><li>Before assumption2</li></ol>'
            '</div>\n'
        )
        if with_assumptions and 'Assumptions' in hint_fields:
            note['Assumptions'] = '<ol><li>Assumption1</li><li>Before [[assumption2::Hint Assumptions]]</li></ol>'
            self.assumptions_expected = assumptions_expected_str
        elif with_assumptions:
            note['Assumptions'] = '<ol><li>Assumption1</li><li>Before assumption2</li></ol>'
            self.assumptions_expected = assumptions_expected_str
        else:
            note['Assumptions'] = ''
            self.assumptions_expected = ''

    @pytest.mark.parametrize('hint_fields', [(), ('EQ1', 'EQ2')])
    @pytest.mark.parametrize('model', ['EQ', 'EQ (assumptions)'])
    def test_eq(self, model, with_assumptions, hint_fields):
        eq = self.col.models.by_name(model)
        n1 = self.col.new_note(eq)
        self.fill_im_eq_note(n1, with_assumptions, hint_fields)
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == (
            f'<span class="sync" note="{n1.id}">\n' +
            self.assumptions_expected +
            f'<div class="first-upper">EQ1{n1["Delimiter"]}EQ2.</div>\n'
            '</span>'
        )

    @pytest.mark.parametrize('hint_fields', [(), ('EQ1', 'EQ2')])
    @pytest.mark.parametrize('model', ['EQ (TEX)', 'EQ (TEX, assumptions)'])
    def test_eq_tex(self, model, with_assumptions, hint_fields):
        m = self.col.models.by_name(model)
        n1 = self.col.new_note(m)
        self.fill_im_eq_note(n1, with_assumptions, hint_fields)
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == (
            f'<span class="sync" note="{n1.id}">\n' +
            self.assumptions_expected +
            f'<div>\\[EQ1 {n1["Delimiter"]} EQ2\\]</div>\n'
            '</span>'
        )

    @pytest.mark.parametrize('hint_fields', [(), ('Cloze')])
    @pytest.mark.parametrize('model', ['IM', 'IM (assumptions)'])
    def test_im(self, model, with_assumptions, hint_fields):
        m = self.col.models.by_name(model)
        n1 = self.col.new_note(m)
        self.fill_im_eq_note(n1, with_assumptions, hint_fields)
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == (
            f'<span class="sync" note="{n1.id}">\n' +
            self.assumptions_expected +
            f'<div class="first-upper">{n1["Context Left"]}Cloze.</div>\n'
            '</span>'
        )

    @pytest.mark.parametrize('hint_fields', [(), ('Cloze Left', 'Cloze Right')])
    @pytest.mark.parametrize('model', ['IM (reversed)', 'IM (assumptions, reversed)'])
    def test_im_reversed(self, model, with_assumptions, hint_fields):
        m = self.col.models.by_name(model)
        n1 = self.col.new_note(m)
        self.fill_im_eq_note(n1, with_assumptions, hint_fields)
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == (
            f'<span class="sync" note="{n1.id}">\n' +
            self.assumptions_expected +
            f'<div class="first-upper">{n1["Context Left"]}Cloze Left{n1["Context Middle"]}Cloze Right.</div>\n'
            '</span>'
        )

    @pytest.mark.parametrize('hint_fields', [(), ('Cloze Left', 'Cloze Right')])
    @pytest.mark.parametrize(
        'model', ['IM (TEX)', 'IM (TEX, assumptions)',
                  'IM (TEX, reversed)', 'IM (TEX, assumptions, reversed)'])
    def test_im_tex(self, model, with_assumptions, hint_fields):
        m = self.col.models.by_name(model)
        n1 = self.col.new_note(m)
        self.fill_im_eq_note(n1, with_assumptions, hint_fields)
        self.col.add_note(n1, 0)

        n2 = self.col.new_note(self.basic)
        n2['Front'] = f'<span class="sync" note="{n1.id}"></span>'
        self.col.add_note(n2, 0)

        assert unidir.sync_field(self.col, n2, 0) is True
        assert n2['Front'] == (
            f'<span class="sync" note="{n1.id}">\n' +
            self.assumptions_expected +
            f'<div>\\[Cloze Left {n1["Context Middle"]} Cloze Right\\]</div>\n'
            '</span>'
        )


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
