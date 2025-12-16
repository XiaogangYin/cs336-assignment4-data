from io import BytesIO

from fastwarc.warc import ArchiveIterator, WarcRecordType
from resiliparse.parse.encoding import EncodingDetector
from resiliparse.extract.html2text import extract_plain_text

def extract_plain_text_from_html_bytes(html_bytes: bytes):
    det = EncodingDetector()
    det.update(html_bytes)
    enc = det.encoding()

    html_str = str(html_bytes, encoding=enc)

    return extract_plain_text(html_str)
