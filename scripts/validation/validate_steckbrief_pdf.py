"""Reopen Steckbrief PDFs and check full summary, tables, sources and page bounds.
Usage: python -B scripts/validation/validate_steckbrief_pdf.py OUTPUT_DIRECTORY
Requires PyMuPDF; no dependencies are installed inside the repository.
"""
from pathlib import Path
import json
import re
import sys
import fitz

out = Path(sys.argv[1])
results = json.loads((out / 'steckbrief-results.json').read_text(encoding='utf-8'))
reports = []
normalize = lambda text: re.sub(r'\s+', '', text)
for name in ['Deutschland', 'Duisburg', 'Berlin', 'Bottrop', 'Mobil']:
    pdf_path = out / f'{name}.pdf'
    profile = next(row for row in results['profiles'] if row['name'] == ('Bottrop' if name == 'Mobil' else name))
    with fitz.open(pdf_path) as document:
        text = '\n'.join(page.get_text() for page in document)
        assert normalize(profile['text']).casefold() in normalize(text).casefold(), pdf_path.name
        assert 'Datengrundlage' in text, pdf_path.name
        for table in profile['tables']:
            assert normalize(table) in normalize(text), (pdf_path.name, table)
        assert '\ufffd' not in text, pdf_path.name
        for index, page in enumerate(document):
            blocks = page.get_text('blocks')
            assert blocks and all(block[0] >= 20 and block[2] <= page.rect.width - 20 and block[1] >= 20 and block[3] <= page.rect.height - 20 for block in blocks), (pdf_path.name, index)
            page.get_pixmap(matrix=fitz.Matrix(1, 1)).save(out / f'{name}-Seite-{index + 1}.png')
        reports.append({'file': pdf_path.name, 'pages': len(document), 'summary': True, 'all_relation_rows': True, 'sources': True, 'text_inside_page': True})
(out / 'pdf-results.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(reports, ensure_ascii=False))
