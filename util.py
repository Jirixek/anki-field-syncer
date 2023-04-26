import anki
import os
import shutil
import tempfile
from anki.collection import Collection as aopen


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
        create_custom_notes(col)
        col.close(downgrade=False)
        _emptyCol = path
    (fd, path) = tempfile.mkstemp(suffix='.anki2')
    shutil.copy(_emptyCol, path)
    col = aopen(path)
    return col
