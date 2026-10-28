from datetime import datetime
from inquest.contracts import VerificationFinding

class TemporalConsistencyMethod:
    name="temporal_consistency"
    def run(self,candidates,context,vault):
        onsets=[x for x in context.get("onsets",[]) if isinstance(x,dict) and x.get("service") and x.get("onset_time")]
        changes=[x for x in context.get("changes",[]) if isinstance(x,dict) and x.get("service") and x.get("timestamp")]
        gaps=set(context.get("telemetry_gaps",[])) | {str(x.get("service")) for x in context.get("coverage_gaps",[]) if isinstance(x,dict) and x.get("service")}
        metric_map=context.get("metrics",[]); out=[]
        for c in candidates:
            matches=[x for x in onsets if x["service"]==c.target]
            relevant=[x for x in changes if x["service"]==c.target]
            ids={str(x["id"]) for x in relevant if str(x.get("id")) in vault}
            if matches and isinstance(metric_map,list):
                chosen=min(matches,key=lambda x:x["onset_time"])
                ids.update(str(x["id"]) for x in metric_map if isinstance(x,dict) and x.get("service")==c.target and x.get("metric")==chosen.get("metric") and x.get("timestamp")==chosen.get("onset_time") and str(x.get("id")) in vault)
            if c.target_type!="service" or not matches or not relevant or c.target in gaps: verdict,effect,reason="inconclusive",0,"Candidate event/onset timestamps or telemetry coverage are insufficient."
            else:
                onset=min(matches,key=lambda x:x["onset_time"]); onset_time=datetime.fromisoformat(onset["onset_time"])
                before=[]; after=[]
                for event in relevant:
                    ts=datetime.fromisoformat(event["timestamp"])
                    uncertainty=(int(event.get("timestamp_uncertainty_ms",0))+int(onset.get("timestamp_uncertainty_ms",0)))/1000
                    (before if ts.timestamp() <= onset_time.timestamp()+uncertainty else after).append(event)
                if before: verdict,effect,reason="supports",1.0,"A candidate-service change precedes its onset within timestamp uncertainty."
                elif after: verdict,effect,reason="contradicts",0.0,"Recorded candidate-service changes occur only after its onset."
                else: verdict,effect,reason="inconclusive",0,"No candidate-service event timestamp can be compared with onset."
            out.append(VerificationFinding(candidate_id=c.id,target=c.target,verdict=verdict,effect_size=effect,rationale=reason,evidence_ids=sorted(ids)))
        return out
