from collections import deque
from datetime import datetime
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
        graph_complete=bool(context.get("dependency_graph_complete",True))
        gaps=set(context.get("telemetry_gaps",[])) | {str(x.get("service")) for x in context.get("coverage_gaps",[]) if isinstance(x,dict) and x.get("service")}
        result=[]
        onset_map={}
        for onset in context.get("onsets",[]):
            if isinstance(onset,dict) and onset.get("service") and onset.get("onset_time"):
                onset_map.setdefault(str(onset["service"]),[]).append(onset)
        for c in candidates:
            if c.target_type!="service":
                result.append(VerificationFinding(candidate_id=c.id,target=c.target,verdict="inconclusive",effect_size=0,rationale="Dependency check applies to service candidates.",evidence_ids=[])); continue
            seen={c.target}; todo=deque([c.target])
            while todo:
                node=todo.popleft()
                for nxt in adj.get(node,[]):
                    if nxt not in seen: seen.add(nxt); todo.append(nxt)
            ids={eid for a,b,eid in edges if a in seen and b in seen}
            for onset in context.get("onsets",[]):
                if isinstance(onset,dict) and onset.get("service") in seen:
                    for metric in context.get("metrics",[]):
                        if isinstance(metric,dict) and metric.get("service")==onset.get("service") and metric.get("metric")==onset.get("metric") and metric.get("timestamp")==onset.get("onset_time") and str(metric.get("id")) in vault: ids.add(str(metric["id"]))
            own_reachable=seen & symptoms
            own_onsets=onset_map.get(c.target,[])
            reachable_onsets=[item for service in own_reachable for item in onset_map.get(service,[])]
            temporal_downstream=False
            temporal_ids=set()
            if own_onsets and reachable_onsets:
                own_onset=min(own_onsets,key=lambda x:x["onset_time"])
                own_ts=datetime.fromisoformat(own_onset["onset_time"]).timestamp()
                for symptom_onset in reachable_onsets:
                    symptom_ts=datetime.fromisoformat(symptom_onset["onset_time"]).timestamp()
                    uncertainty=(int(own_onset.get("timestamp_uncertainty_ms",0))+int(symptom_onset.get("timestamp_uncertainty_ms",0)))/1000
                    if symptom_ts < own_ts-uncertainty:
                        temporal_downstream=True
                        for point in context.get("metrics",[]):
                            if isinstance(point,dict) and point.get("service")==symptom_onset.get("service") and point.get("metric")==symptom_onset.get("metric") and point.get("timestamp")==symptom_onset.get("onset_time") and str(point.get("id")) in vault:
                                temporal_ids.add(str(point["id"]))
                for point in context.get("metrics",[]):
                    if isinstance(point,dict) and point.get("service")==c.target and point.get("metric")==own_onset.get("metric") and point.get("timestamp")==own_onset.get("onset_time") and str(point.get("id")) in vault:
                        temporal_ids.add(str(point["id"]))
            other_coverage=[]
            for other in candidates:
                if other.id==c.id or other.target_type!="service": continue
                other_seen={other.target}; other_todo=deque([other.target])
                while other_todo:
                    node=other_todo.popleft()
                    for nxt in adj.get(node,[]):
                        if nxt not in other_seen: other_seen.add(nxt); other_todo.append(nxt)
                other_coverage.append(len(other_seen & symptoms))
            unique_best=bool(own_reachable) and len(own_reachable)>max(other_coverage,default=0)
            if c.target in gaps: verdict,effect,reason="inconclusive",0,"Candidate telemetry is incomplete; no dependency verdict is inferred."
            elif not graph_complete: verdict,effect,reason="inconclusive",len(own_reachable)/max(1,len(symptoms)),"Declared graph is partial; an observed path is necessary but cannot establish exclusive explanation."
            elif not own_reachable and symptoms and not (symptoms & gaps): verdict,effect,reason="contradicts",0.0,"No recorded dependency path connects candidate to observed symptoms."
            elif not own_onsets: verdict,effect,reason="inconclusive",len(own_reachable)/max(1,len(symptoms)),"Candidate has no observed local onset to establish temporal priority over reachable symptoms."
            elif temporal_downstream: verdict,effect,reason="contradicts",len(own_reachable)/max(1,len(symptoms)),"Candidate onset follows an earlier onset among the symptoms it reaches; path alone does not establish causal priority."
            elif unique_best: verdict,effect,reason="supports",len(own_reachable)/max(1,len(symptoms)),"Candidate reaches symptoms, is not temporally downstream of them, and uniquely covers more symptomatic services than competitors."
            elif own_reachable: verdict,effect,reason="inconclusive",len(own_reachable)/max(1,len(symptoms)),"A path exists, but shared/equal ancestry is not sufficient causal evidence."
            elif symptoms & gaps: verdict,effect,reason="inconclusive",0,"Symptom telemetry gaps prevent a reliable dependency contradiction."
            elif not edges or not symptoms: verdict,effect,reason="inconclusive",0,"Graph or onset evidence is insufficient for this check."
            else: verdict,effect,reason="contradicts",0.0,"No recorded dependency path connects candidate to observed symptoms."
            result.append(VerificationFinding(candidate_id=c.id,target=c.target,verdict=verdict,effect_size=effect,rationale=reason,evidence_ids=sorted(ids|temporal_ids)))
        return result
