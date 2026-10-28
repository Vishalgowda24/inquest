from collections import deque
from inquest.contracts import VerificationFinding

class DependencyPathMethod:
    name="dependency_path"
    def run(self,candidates,context,vault):
        edges=[]
        for eid,entry in vault.items():
            p=entry.get("payload",{})
            if isinstance(p,dict) and "caller" in p and "callee" in p: edges.append((str(p["caller"]),str(p["callee"]),eid))
        # Stored edges point caller -> callee; reverse them so a proposed
        # cause can be followed toward the callers that exhibit symptoms.
        adj={}
        for caller,callee,_ in edges: adj.setdefault(callee,[]).append(caller)
        symptoms={str(x.get("service")) for x in context.get("onsets",[]) if isinstance(x,dict) and x.get("service")}
        gaps=set(context.get("telemetry_gaps",[])) | {str(x.get("service")) for x in context.get("coverage_gaps",[]) if isinstance(x,dict) and x.get("service")}
        result=[]
        for c in candidates:
            if c.target_type!="service":
                result.append(VerificationFinding(candidate_id=c.id,target=c.target,verdict="inconclusive",effect_size=0,rationale="Dependency check applies to service candidates.",evidence_ids=[])); continue
            seen={c.target}; todo=deque([c.target]); supported=False
            while todo:
                node=todo.popleft()
                if node in symptoms: supported=True; break
                for nxt in adj.get(node,[]):
                    if nxt not in seen: seen.add(nxt); todo.append(nxt)
            ids={eid for a,b,eid in edges if a in seen and b in seen}
            for onset in context.get("onsets",[]):
                if isinstance(onset,dict) and onset.get("service") in seen:
                    for metric in context.get("metrics",[]):
                        if isinstance(metric,dict) and metric.get("service")==onset.get("service") and metric.get("metric")==onset.get("metric") and metric.get("timestamp")==onset.get("onset_time") and str(metric.get("id")) in vault: ids.add(str(metric["id"]))
            if c.target in gaps: verdict,effect,reason="inconclusive",0,"Candidate telemetry is incomplete; no dependency verdict is inferred."
            elif supported: verdict,effect,reason="supports",1.0,"Candidate lies on a recorded upstream dependency path to a symptomatic service."
            elif symptoms & gaps: verdict,effect,reason="inconclusive",0,"Symptom telemetry gaps prevent a reliable dependency contradiction."
            elif not edges or not symptoms: verdict,effect,reason="inconclusive",0,"Graph or onset evidence is insufficient for this check."
            else: verdict,effect,reason="contradicts",0.0,"No recorded dependency path connects candidate to observed symptoms."
            result.append(VerificationFinding(candidate_id=c.id,target=c.target,verdict=verdict,effect_size=effect,rationale=reason,evidence_ids=sorted(ids)))
        return result
