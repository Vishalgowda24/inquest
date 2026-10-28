"""Compare candidates by the symptomatic callers reachable in the declared graph."""
from collections import deque
from datetime import datetime
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
        onset_map={}
        for onset in context.get("onsets",[]):
            if isinstance(onset,dict) and onset.get("service") and onset.get("onset_time"):
                onset_map.setdefault(str(onset["service"]),[]).append(onset)
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
            elif not context.get("dependency_graph_complete",True):
                own,own_ids=all_coverage.get(c.id,(set(),set()))
                verdict,effect,reason,ids="inconclusive",len(own)/max(1,len(symptoms)),"Declared graph is partial; alternatives cannot be compared reliably.",sorted(own_ids)
            else:
                own,own_ids=all_coverage.get(c.id,(set(),set())); competitors=[(other,covered) for other,(covered,_) in all_coverage.items() if other!=c.id]
                best=max((len(covered) for _,covered in competitors),default=0); own_fraction=len(own)/len(symptoms)
                competing_fraction=best/len(symptoms)
                candidate_onsets=onset_map.get(c.target,[])
                temporal_ids=set()
                downstream=False
                if candidate_onsets:
                    candidate_onset=min(candidate_onsets,key=lambda x:x["onset_time"])
                    candidate_ts=datetime.fromisoformat(candidate_onset["onset_time"]).timestamp()
                    for service in own:
                        for symptom_onset in onset_map.get(service,[]):
                            symptom_ts=datetime.fromisoformat(symptom_onset["onset_time"]).timestamp()
                            uncertainty=(int(candidate_onset.get("timestamp_uncertainty_ms",0))+int(symptom_onset.get("timestamp_uncertainty_ms",0)))/1000
                            if symptom_ts < candidate_ts-uncertainty:
                                downstream=True
                                for point in context.get("metrics",[]):
                                    if isinstance(point,dict) and point.get("service")==service and point.get("metric")==symptom_onset.get("metric") and point.get("timestamp")==symptom_onset.get("onset_time") and str(point.get("id")) in vault:
                                        temporal_ids.add(str(point["id"]))
                earlier_competitor=False
                for other_id, covered in competitors:
                    other=next((item for item in candidates if item.id==other_id),None)
                    other_onsets=onset_map.get(other.target,[]) if other else []
                    if len(covered)>=len(own) and candidate_onsets and other_onsets:
                        own_ts=datetime.fromisoformat(min(candidate_onsets,key=lambda x:x["onset_time"])["onset_time"]).timestamp()
                        other_onset=min(other_onsets,key=lambda x:x["onset_time"])
                        other_ts=datetime.fromisoformat(other_onset["onset_time"]).timestamp()
                        uncertainty=(int(min(candidate_onsets,key=lambda x:x["onset_time"]).get("timestamp_uncertainty_ms",0))+int(other_onset.get("timestamp_uncertainty_ms",0)))/1000
                        if other_ts < own_ts-uncertainty:
                            earlier_competitor=True
                            for point in context.get("metrics",[]):
                                if isinstance(point,dict) and point.get("service")==other.target and point.get("metric")==other_onset.get("metric") and point.get("timestamp")==other_onset.get("onset_time") and str(point.get("id")) in vault:
                                    temporal_ids.add(str(point["id"]))
                if (downstream or earlier_competitor) and candidate_onsets:
                    verdict,effect,reason="contradicts",competing_fraction,"Candidate is temporally downstream of its claimed symptoms or an equal-coverage competitor has an earlier onset."
                elif not candidate_onsets:
                    verdict,effect,reason="inconclusive",own_fraction,"Candidate onset is unavailable, so temporal priority cannot be established."
                elif len(own)>best:
                    verdict,effect,reason="supports",own_fraction,"Candidate uniquely explains the greatest symptom coverage and is not temporally downstream of those symptoms."
                else:
                    verdict,effect,reason="inconclusive",own_fraction,"A path exists, but equal/shared coverage is not causal discrimination."
                ids=set(own_ids)
                for onset in context.get("onsets",[]):
                    if isinstance(onset,dict) and onset.get("service") in own:
                        for point in context.get("metrics",[]):
                            if isinstance(point,dict) and point.get("service")==onset.get("service") and point.get("metric")==onset.get("metric") and point.get("timestamp")==onset.get("onset_time") and str(point.get("id")) in vault: ids.add(str(point["id"]))
                ids=sorted(ids|temporal_ids)
            out.append(VerificationFinding(candidate_id=c.id,target=c.target,verdict=verdict,effect_size=effect,rationale=reason,evidence_ids=ids))
        return out
