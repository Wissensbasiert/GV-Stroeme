"""Belegte sprachliche Erläuterung; Zahlen und Pflichtgrenzen bleiben serverseitig."""
import re
from .contracts import fields, validate

NARRATIVE = fields(
    result_id={'type': 'string'}, data_snapshot_id={'type': 'string'},
    paragraphs={'type': 'array', 'maxItems': 3, 'items': fields(
        text={'type': 'string', 'maxLength': 650},
        evidence_ids={'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 8})})


def evidence(result, answer):
    records = {}
    for table in answer['tables']:
        for row in table['rows']:
            for fact_id in row.get('fact_ids', []):
                records[fact_id] = row['label'] + ': ' + row['value'] + ' ' + row['unit'] + ('. ' + row['note'] if row['note'] else '')
    for i, note in enumerate(answer['notes']): records['n' + str(i + 1)] = note
    for i, text in enumerate(answer['paragraphs']): records['p' + str(i + 1)] = text
    # A compact evidence packet, never the full result table or source data.
    ids = list(records)
    selected = ids[:20] + [k for k in ids if k.startswith(('n', 'p')) or 'Summe' in records[k]]
    return {k: records[k] for k in dict.fromkeys(selected)}


def apply_narrative(result, answer, selection, records):
    validate(NARRATIVE, selection)
    if selection['result_id'] != result['result_id'] or selection['data_snapshot_id'] != result['data_snapshot_id']:
        raise ValueError('Fremder Ergebnisbezug')
    rendered = []
    for paragraph in selection['paragraphs']:
        text = paragraph['text']
        refs = paragraph['evidence_ids']
        tokens = re.findall(r'\{\{([a-z]+\d+)\}\}', text)
        remainder = re.sub(r'\{\{[a-z]+\d+\}\}', '', text)
        if not set(refs) <= records.keys() or not set(tokens) <= set(refs):
            raise ValueError('Unbelegte Erläuterung')
        # Numeric claims must be inserted from current evidence, never typed by the model.
        if re.search(r'\d|[%€$<>]|\b(?:null|kein\s+verkehr|verkehrsfrei|verursacht|aufgrund|weil|deshalb|folglich|kapazität|auslastung|standortvorteil|verlagerungspotenzial)\b', remainder, re.I):
            raise ValueError('Unbelegte Zahl oder Ursachenbehauptung')
        if not tokens:
            raise ValueError('Kein sichtbarer aktueller Beleg')
        for token in tokens: text = text.replace('{{' + token + '}}', records[token])
        rendered.append(text)
    if rendered:
        # Table, factual introduction, scope and mandatory notes cannot be removed.
        first = answer['paragraphs'][:1]
        answer['paragraphs'] = [*rendered, *[p for p in first if not any(p in text for text in rendered)]]
        result['answer_mode'] = 'grounded_narrative'
    return answer
