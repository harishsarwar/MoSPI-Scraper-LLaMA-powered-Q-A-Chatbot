
from pipeline.run import chunk_text
def test_chunk_text_empty():
    assert chunk_text('') == []
def test_chunk_text_small():
    t = 'a'*1000
    chunks = chunk_text(t)
    assert len(chunks) >= 1
