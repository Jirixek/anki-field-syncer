import re
from . import bidir
from .util import get_empty_col

# TODO: reload all notes after sync
# TODO: assert sync_field


class MockPopup():
    def __init__(self, return_value: str):
        self.return_value = return_value
        self.n_called = 0

    def __call__(self, sid: int):
        self.n_called += 1
        return self.return_value

    def n_called(self):
        return self.n_called


def test_download_single():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">New content</span>'
    col.add_note(n2, 0)

    bidir.sync_field(col, n2, 0, MockPopup('Download'))
    n1.load()
    n2.load()

    assert n1['Front'] == '<span class="sync" sid="1">Original content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">Original content</span>'


def test_download_multiple():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    n3 = col.new_note(basic)
    n3['Front'] = '<span class="sync" sid="1">New content</span>'
    col.add_note(n3, 0)

    bidir.sync_field(col, n3, 0, MockPopup('Download'))
    n1.load()
    n2.load()
    n3.load()

    assert n1['Front'] == '<span class="sync" sid="1">Original content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">Original content</span>'
    assert n3['Front'] == '<span class="sync" sid="1">Original content</span>'


def test_upload_single():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">New content</span>'
    col.add_note(n2, 0)

    bidir.sync_field(col, n2, 0, MockPopup('Upload'))
    n1.load()
    n2.load()

    assert n1['Front'] == '<span class="sync" sid="1">New content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">New content</span>'


def test_upload_multiple():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    n3 = col.new_note(basic)
    n3['Front'] = '<span class="sync" sid="1">New content</span>'
    col.add_note(n3, 0)

    bidir.sync_field(col, n3, 0, MockPopup('Upload'))
    n1.load()
    n2.load()
    n3.load()

    assert n1['Front'] == '<span class="sync" sid="1">New content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">New content</span>'
    assert n3['Front'] == '<span class="sync" sid="1">New content</span>'


def test_download_different_ids():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">ID1</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="2">ID2</span>'
    col.add_note(n2, 0)

    bidir.sync_field(col, n2, 0, MockPopup('Download'))
    assert n1['Front'] == '<span class="sync" sid="1">ID1</span>'
    assert n2['Front'] == '<span class="sync" sid="2">ID2</span>'


def test_upload_different_ids():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">ID1</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="2">ID2</span>'
    col.add_note(n2, 0)

    bidir.sync_field(col, n2, 0, MockPopup('Upload'))
    assert n1['Front'] == '<span class="sync" sid="1">ID1</span>'
    assert n2['Front'] == '<span class="sync" sid="2">ID2</span>'


def test_download_single_card():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Content</span>'
    col.add_note(n1, 0)

    bidir.sync_field(col, n1, 0, MockPopup('Download'))
    assert n1['Front'] == '<span class="sync" sid="1">Content</span>'


def test_upload_single_card():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Content</span>'
    col.add_note(n1, 0)

    bidir.sync_field(col, n1, 0, MockPopup('Upload'))
    assert n1['Front'] == '<span class="sync" sid="1">Content</span>'


def test_no_change():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    popup = MockPopup('Download')
    assert bidir.sync_field(col, n2, 0, popup) is False
    assert popup.n_called == 0
    assert n1['Front'] == '<span class="sync" sid="1">Original content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">Original content</span>'


def test_empty_span_always_downloaded():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1"></span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    popup = MockPopup('Download')
    assert bidir.sync_field(col, n1, 0, popup) is True
    assert popup.n_called == 0
    assert n1['Front'] == '<span class="sync" sid="1">Original content</span>'
    assert n2['Front'] == '<span class="sync" sid="1">Original content</span>'


def test_change_popup():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Garbage</span>'
    col.add_note(n2, 0)

    popup_called = False

    def popup_func(sid: str):
        nonlocal popup_called
        popup_called = True
        return 'Download'
    assert bidir.sync_field(col, n2, 0, popup_func) is True
    assert popup_called is True


def test_span_coherency_homogenous():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    assert bidir.are_spans_coherent(col, [n1.id, n2.id], 1) is True


def test_span_coherency_non_homogenous():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = '<span class="sync" sid="1">Original content</span>'
    col.add_note(n2, 0)

    n3 = col.new_note(basic)
    n3['Front'] = '<span class="sync" sid="1">New content</span>'
    col.add_note(n3, 0)

    assert bidir.are_spans_coherent(col, [n1.id, n2.id, n3.id], 1) is False


def test_card_is_being_created():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span class="sync" sid="1"></span>'

    assert bidir.sync_field(col, n2, 0, MockPopup('Download')) is False
    # No exception raised


def test_dont_change_spans_without_class():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync" sid="1">Content</span>'
    col.add_note(n1, 0)

    n2 = col.new_note(basic)
    n2['Front'] = f'<span sid="1"></span>'
    col.add_note(n2, 0)

    assert bidir.sync_field(col, n2, 0, MockPopup('Download')) is False
    assert n2['Front'] == f'<span sid="1"></span>'


def test_id_missing():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync">Content</span>'
    col.add_note(n1, 0)

    assert bidir.sync_field(col, n1, 0, MockPopup('Download')) is True
    assert re.fullmatch(f'<span class="sync" sid="{n1.id}_0_' + r'\d{4}' + f'">Content</span>', n1['Front'])


def test_id_missing_multiple_spans_in_note():
    col = get_empty_col()
    basic = col.models.by_name('Basic')

    n1 = col.new_note(basic)
    n1['Front'] = '<span class="sync">Content</span>'
    col.add_note(n1, 0)

    assert bidir.sync_field(col, n1, 0, MockPopup('Download')) is True
    n1.load()
    assert re.fullmatch(f'<span class="sync" sid="{n1.id}_0_' + r'\d{4}' + f'">Content</span>', n1['Front'])

    n1['Front'] = (
        f'<span class="sync" sid="{n1.id}1">Content</span>'
        '<span class="sync">Another</span>'
    )
    col.update_note(n1)

    assert bidir.sync_field(col, n1, 0, MockPopup('Download')) is True
    n1.load()
    assert re.fullmatch((
        f'<span class="sync" sid="{n1.id}1">Content</span>'
        f'<span class="sync" sid="{n1.id}_0_' + r'\d{4}' + f'">Another</span>'
    ), n1['Front'])


# def test_nested_spans():
#     pass

# def test_inside_single_card():
#     pass
