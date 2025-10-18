
from scraper.parse import parse_detail
def test_parse_detail_minimal():
    html = '<html><head><title>Test</title></head><body><h1>Title</h1><a href="file.pdf">PDF</a></body></html>'
    meta = parse_detail(html, "https://example.test")
    assert isinstance(meta, dict)
    assert 'file_links' in meta
