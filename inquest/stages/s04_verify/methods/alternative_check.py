"""Compare candidates by the symptomatic callers reachable in the declared graph."""
from collections import deque
from inquest.contracts import VerificationFinding

class AlternativeCheckMethod:
    name="alternative_check"
    def run(self,candidates,context,vault):
        edges=[]
        for eid,entry in vault.items():
            p=entry.get("payload",{})
            if isinstance(p,dict) and "caller" in p and "callee" in p: edges.append((str(p["callee"]),str(p["caller"]),eid))
        adj={}
        for cause,caller,eid in edges: adj.setdefault(cause,[]).append((caller,eid))
        symptoms={str(x.get("service")) for x in context.get("onsets",[]) if isinstance(x,dict) and x.get("service")}
        gaps=set(context.get("telemetry_gaps",[])) | {str(x.get("service")) for x in context.get("coverage_gaps",[]) if isinstance(x,dict) and x.get("service")}
        def coverage(service):
            seen={service}; todo=deque([service]); evidence=set()
            while todo:
                node=todo.popleft()
                for nxt,eid in adj.get(node,[]):
                    evidence.add(eid)
                    if nxt not in seen: seen.add(nxt); todo.append(nxt)
            return seen & symptoms,evidence
        all_coverage={c.id:coverage(c.target) for c in candidates if c.target_type=="service" and c.target not in gaps}
        out=[]
        for c in candidates:
            if c.target_type!="service" or not symptoms or c.target in gaps:
                verdict,effect,reason,ids="inconclusive",0.0,"Symptom coverage or telemetry is insufficient to compare alternatives.",[]
            else:
                own,own_ids=all_coverage.get(c.id,(set(),set())); competitors=[(other,covered) for other,(covered,_) in all_coverage.items() if other!=c.id]
                best=max((len(covered) for _,covered in competitors),default=0); own_fraction=len(own)/len(symptoms)
                competing_fraction=best/len(symptoms)
                if best>=len(own) and competitors:
                    verdict,effect,reason="contradicts",competing_fraction,"Another candidate explains at least as many symptomatic services through the recorded graph."
                else:
                    verdict,effect,reason="supports",own_fraction,"No competing candidate explains as many symptomatic services through the recorded graph."
                ids=set(own_ids)
                for onset in context.get("onsets",[]):
                    if isinstance(onset,dict) and onset.get("service") in own:
                        for point in context.get("metrics",[]):
                            if isinstance(point,dict) and point.get("service")==onset.get("service") and point.get("metric")==onset.get("metric") and point.get("timestamp")==onset.get("onset_time") and str(point.get("id")) in vault: ids.add(str(point["id"]))
                ids=sorted(ids)
            out.append(VerificationFinding(candidate_id=c.id,target=c.target,verdict=verdict,effect_size=effect,rationale=reason,evidence_ids=ids))
        return out
