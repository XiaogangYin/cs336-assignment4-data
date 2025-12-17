from typing import Any
import pathlib
import re

from resiliparse.parse.encoding import EncodingDetector
from resiliparse.extract.html2text import extract_plain_text
import fasttext

__all__ = [
    "extract_plain_text_from_html_bytes",
    "language_identification",
    "mask_emails",
    "mask_us_phone_numbers"
]

def extract_plain_text_from_html_bytes(html_bytes: bytes):
    det = EncodingDetector()
    det.update(html_bytes)
    enc = det.encoding()

    html_str = str(html_bytes, encoding=enc)

    return extract_plain_text(html_str)

fasttext_model = None
def language_identification(text: str) -> tuple[Any, float]:
    global fasttext_model
    if fasttext_model is None:
        model_path = pathlib.Path(__file__).resolve().parent.parent / "my_data"
        fasttext_model = fasttext.load_model(str(model_path / "lid.176.bin"))
    text = text.replace('\n', ' ')
    langs, scores = fasttext_model.predict(text, k=1)
    if len(langs) >= 1:
        return langs[0][9:], scores[0]
    else:
        return "none", 0

def mask_emails(text: str, mask: str = "|||EMAIL_ADDRESS|||") -> tuple[str, int]:
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    new_text, mask_count = re.subn(email_pattern, mask, text, flags=re.IGNORECASE)
    return new_text, mask_count

def mask_us_phone_numbers(text: str, mask: str = "|||PHONE_NUMBER|||") -> tuple[str, int]:
    pattern = r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    new_text, mask_count = re.subn(pattern, mask, text, flags=re.IGNORECASE)

    return new_text, mask_count

if __name__ == "__main__":
    from fastwarc.warc import ArchiveIterator, WarcRecordType

    file_path = "../tmp/CC-MAIN-20250417135010-20250417165010-00065.warc.gz"
    for record in ArchiveIterator(open(file_path, 'rb'), record_types=WarcRecordType.response):
        print(record.record_id, record.record_type, type(record))
        body = record.reader.read()
        print(type(body), len(body))
        print(extract_plain_text_from_html_bytes(body))
        break