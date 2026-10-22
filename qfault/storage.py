"""Exclusive immutable file artifacts, separate evaluator truth and bound human reviews."""
import json
import re
from pathlib import Path
from .evidence import canonical,digest,identifier,timestamp


def _supported_investigation(record):
    if not isinstance(record,dict) or type(record.get('schema_version')) is not int:
        return False
    version=record['schema_version']
    return ((version==1 and record.get('investigation_kind') is None) or
            (version==2 and record.get('investigation_kind')=='custom_circuit') or
            (version==3 and record.get('investigation_kind')=='counterfactual_recovery'))


class ArtifactStore:
    def __init__(self,root):
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)

    def folder(self,eid):
        if not re.fullmatch(r"experiment_[0-9a-f]{32}",eid): raise ValueError("invalid experiment identifier")
        return self.root/eid

    def save(self,result):
        eid=result["experiment_id"]
        folder=self.folder(eid)
        folder.mkdir()  # exclusive, never overwrite an earlier investigation
        report=dict(result)
        truth=report.pop("evaluation_truth")
        documents={"investigation.json":report,"evaluation.json":truth}
        manifest={"schema_version":1,"algorithm":"sha256","canonicalization":"qfault-json-v1",
                  "experiment_id":eid,"reviews":{},"artifacts":{name:digest(value) for name,value in documents.items()}}
        for name,value in {**documents,"manifest.json":manifest}.items():
            with (folder/name).open("xb") as stream: stream.write(canonical(value))
        return eid

    def verify(self,eid):
        folder=self.folder(eid)
        errors=[]
        try:
            manifest=json.loads((folder/"manifest.json").read_bytes())
            if not isinstance(manifest,dict) or not isinstance(manifest.get("artifacts"),dict):
                raise ValueError("manifest and artifact map must be objects")
            if type(manifest.get('schema_version')) is not int or manifest['schema_version']!=1:
                errors.append('unsupported manifest schema')
            if manifest.get("algorithm")!="sha256" or manifest.get("canonicalization")!="qfault-json-v1":
                errors.append("unsupported integrity format")
            if set(manifest.get("artifacts",{}))!={"investigation.json","evaluation.json"} or manifest.get("experiment_id")!=eid:
                errors.append("invalid manifest membership")
            for name in ["investigation.json","evaluation.json"]:
                document=json.loads((folder/name).read_bytes())
                if name=='investigation.json' and not _supported_investigation(document):
                    errors.append('unsupported investigation schema')
                actual=digest(document)
                if actual!=manifest["artifacts"].get(name): errors.append(f"digest mismatch: {name}")
            reviews=manifest.get("reviews",{})
            if not isinstance(reviews,dict): raise ValueError("review index must be an object")
            present={p.name for p in folder.glob("review_*.json")}
            if set(reviews)!=present: errors.append("review membership mismatch")
            for path in sorted(folder.glob("review_*.json")):
                review=json.loads(path.read_bytes())
                if digest(review)!=reviews.get(path.name): errors.append(f"review digest mismatch: {path.name}")
                record=review["record"]
                if digest(record)!=review["digest"] or record["investigation_digest"]!=manifest["artifacts"]["investigation.json"]:
                    errors.append(f"review mismatch: {path.name}")
        except (OSError,ValueError,KeyError,TypeError) as exc:
            errors.append(f"missing or malformed artifacts: {type(exc).__name__}")
        return {"valid":not errors,"experiment_id":eid,"errors":errors,
                "assurance":"Hash consistency only; a party replacing both data and manifest can rehash. No signature or external anchor."}

    def load(self,eid):
        folder=self.folder(eid)
        if not folder.is_dir(): raise FileNotFoundError(eid)
        if not self.verify(eid)["valid"]: raise ValueError("investigation integrity check failed")
        result=json.loads((folder/"investigation.json").read_bytes())
        if not isinstance(result,dict): raise ValueError("investigation must be an object")
        result["human_decisions"]=[json.loads(p.read_bytes())["record"] for p in sorted(folder.glob("review_*.json"))]
        return result

    def list(self):
        rows=[]
        for folder in sorted(self.root.glob("experiment_*"),key=lambda p:p.stat().st_mtime,reverse=True):
            try:
                r=self.load(folder.name)
                rows.append({"experiment_id":folder.name,"created_at":r["created_at"],"family":r["contract"]["family"],
                             "category":r["diagnosis"]["category"],"integrity_valid":self.verify(folder.name)["valid"]})
            except (ValueError,OSError,KeyError):
                rows.append({"experiment_id":folder.name,"category":"CORRUPT_ARTIFACT","integrity_valid":False})
        return rows

    def review(self,eid,reviewer,action,reason):
        if action not in {"acknowledge","reject","request_evidence"}: raise ValueError("invalid human action")
        if not reviewer.strip() or not reason.strip(): raise ValueError("reviewer and reason required")
        if not self.verify(eid)["valid"]: raise ValueError("cannot review artifacts that fail integrity verification")
        folder=self.folder(eid)
        manifest=json.loads((folder/"manifest.json").read_bytes())
        record={"review_id":identifier("review"),"experiment_id":eid,"reviewer":reviewer,"action":action,
                "reason":reason,"created_at":timestamp(),"investigation_digest":manifest["artifacts"]["investigation.json"],
                "identity_assurance":"self-declared local reviewer; no authentication"}
        name=record["review_id"]+".json"
        envelope={"record":record,"digest":digest(record)}
        with (folder/name).open("xb") as stream: stream.write(canonical(envelope))
        manifest.setdefault("reviews",{})[name]=digest(envelope)
        temporary=folder/(identifier("manifest")+".tmp")
        with temporary.open("xb") as stream: stream.write(canonical(manifest))
        temporary.replace(folder/"manifest.json")  # intentional atomic review-index update

        return record

    def export(self,eid):
        folder=self.folder(eid)
        return {"investigation":json.loads((folder/"investigation.json").read_bytes()),
                "evaluation":json.loads((folder/"evaluation.json").read_bytes()),
                "manifest":json.loads((folder/"manifest.json").read_bytes()),
                "reviews":[json.loads(p.read_bytes()) for p in sorted(folder.glob("review_*.json"))],
                "verification":self.verify(eid)}


def verify_export(report):
    """Verify an exported bundle without trusting its embedded verification result."""
    if isinstance(report,dict) and report.get('kind')=='blind_challenge':
        return verify_challenge_export(report)
    errors=[]
    try:
        if not isinstance(report,dict): raise ValueError('report must be an object')
        manifest=report['manifest']
        if not isinstance(manifest,dict) or not isinstance(manifest.get('artifacts'),dict): raise ValueError('invalid manifest')
        if type(manifest.get('schema_version')) is not int or manifest['schema_version']!=1:
            errors.append('unsupported manifest schema')
        if not _supported_investigation(report['investigation']):
            errors.append('unsupported investigation schema')
        if manifest.get('algorithm')!='sha256' or manifest.get('canonicalization')!='qfault-json-v1':
            errors.append('unsupported integrity format')
        if set(manifest['artifacts'])!={'investigation.json','evaluation.json'}: errors.append('invalid artifact membership')
        if report['investigation']['experiment_id']!=manifest['experiment_id']: errors.append('experiment identity mismatch')
        for name,key in [('investigation.json','investigation'),('evaluation.json','evaluation')]:
            if digest(report[key])!=manifest['artifacts'].get(name): errors.append('digest mismatch: '+name)
        reviews=manifest.get('reviews',{})
        if not isinstance(reviews,dict) or not isinstance(report['reviews'],list): raise ValueError('invalid reviews')
        envelopes={r['record']['review_id']+'.json':r for r in report['reviews']}
        if len(envelopes)!=len(report['reviews']) or set(envelopes)!=set(reviews): errors.append('review membership mismatch')
        for name,envelope in envelopes.items():
            record=envelope['record']
            if digest(envelope)!=reviews.get(name) or digest(record)!=envelope['digest'] or record['investigation_digest']!=manifest['artifacts']['investigation.json']:
                errors.append('review mismatch: '+name)
    except (ValueError,TypeError,KeyError) as exc:
        errors.append('malformed report: '+type(exc).__name__)
    return {'valid':not errors,'errors':errors,'assurance':'Unsigned hash consistency relative to supplied manifest; no external trust anchor or scientific correctness proof'}


def verify_challenge_export(report):
    """Check participant documents and their freeze/reveal chain independently."""
    errors=[]
    steps={'observed':'OBSERVED','diagnosed':'DIAGNOSED','freeze':'FROZEN','reveal':'REVEALED'}
    try:
        if type(report.get('schema_version')) is not int or report['schema_version']!=1:
            raise ValueError('unsupported challenge schema')
        if report['kind']!='blind_challenge' or report['manifest']['algorithm']!='sha256':raise ValueError('format')
        state=report['state'];names=list(steps)[:list(steps.values()).index(state)+1]
        docs=report['documents'];hashes=report['manifest']['artifacts']
        if set(docs)!=set(names) or set(hashes)!=set(names):errors.append('challenge document membership mismatch')
        previous=''
        for sequence,name in enumerate(names,1):
            value=docs[name]
            if digest(value)!=hashes.get(name):errors.append('digest mismatch: '+name)
            if value['challenge_id']!=report['challenge_id'] or value['sequence']!=sequence or value['state']!=steps[name]:errors.append('challenge ordering mismatch')
            if value['created_at']<previous:errors.append('challenge timestamp ordering mismatch')
            previous=value['created_at']
        if 'diagnosed' in docs and docs['diagnosed']['observation_digest']!=digest(docs['observed']):errors.append('observation binding mismatch')
        if 'freeze' in docs and docs['freeze']['prediction_digest']!=digest(docs['diagnosed']):errors.append('frozen prediction mismatch')
        if 'reveal' in docs and docs['reveal']['prediction_digest']!=docs['freeze']['prediction_digest']:errors.append('reveal binding mismatch')
        if 'revealed_investigation' in report:
            if state!='REVEALED' or not verify_export(report['revealed_investigation'])['valid']:errors.append('invalid revealed investigation')
            internal=report['revealed_investigation']['investigation']
            if internal['prediction_digest']!=docs['diagnosed']['engine_prediction_digest'] or internal['prediction_digest']!=digest({'diagnosis':internal['diagnosis'],'recovery':internal['recovery']}):
                errors.append('revealed prediction binding mismatch')
    except (KeyError,TypeError,ValueError,AttributeError):errors.append('malformed challenge report')
    return {'valid':not errors,'errors':errors,'assurance':'Unsigned hash consistency and recorded ordering; not secrecy from a local server administrator or an external timestamp proof'}
