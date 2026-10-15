from __future__ import annotations
import csv,hashlib,json,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ARC=HERE/'user_uploaded_routing_dataset.zip'
out={'archive':ARC.name,'sha256':hashlib.sha256(ARC.read_bytes()).hexdigest(),'members':[],'classification':'routing-only CSV dataset; not TPPLIB .tpp','usable_as_official_tpplib':False}
with zipfile.ZipFile(ARC) as z:
    for info in z.infolist():
        entry={'name':info.filename,'compressed_bytes':info.compress_size,'bytes':info.file_size}
        with z.open(info) as f:
            head=f.readline().decode('utf-8','replace').strip().split(',')
        entry['columns']=head
        out['members'].append(entry)
(HERE/'upload_audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
