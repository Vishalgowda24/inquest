"""Measure whether a later restart is followed by metric recovery."""
from datetime import datetime
from statistics import median
from inquest.contracts import VerificationFinding

class RecoveryCheckMethod:
    name = "recovery_check"
    def run(self, candidates, context, vault):
        onsets=[x for x in context.get("onsets",[]) if isinstance(x,dict)]
        changes=[x for x in context.get("changes",[]) if isinstance(x,dict) and x.get("timestamp") and (x.get("kind")=="restart" or "rollback" in str(x.get("kind","")).casefold())]
        metrics=[x for x in context.get("metrics",[]) if isinstance(x,dict)]
        gaps=set(context.get("telemetry_gaps",[])) | {str(x.get("service")) for x in context.get("coverage_gaps",[]) if isinstance(x,dict) and x.get("service")}
        out=[]
        for c in candidates:
            service_onsets=[x for x in onsets if x.get("service")==c.target]
            evidence=[]; effects=[]
            if service_onsets and c.target not in gaps:
                for onset in service_onsets:
                    onset_time=datetime.fromisoformat(onset["onset_time"])
                    onset_measurements=[x for x in metrics if x.get("service")==c.target and x.get("metric")==onset.get("metric") and x.get("timestamp")==onset.get("onset_time") and str(x.get("id")) in vault]
                    evidence.extend(str(x["id"]) for x in onset_measurements)
                    actions=[x for x in changes if x.get("service")==c.target and datetime.fromisoformat(x["timestamp"])>onset_time]
                    for event in actions:
                        event_time=datetime.fromisoformat(event["timestamp"])
                        points=sorted((x for x in metrics if x.get("service")==c.target and x.get("metric")==onset.get("metric") and isinstance(x.get("value"),(int,float))),key=lambda x:x["timestamp"])
                        before=[x for x in points if onset_time<=datetime.fromisoformat(x["timestamp"])<event_time][-3:]
                        after=[x for x in points if datetime.fromisoformat(x["timestamp"])>event_time][:3]
                        if len(before)<3 or len(after)<3: continue
                        center=float(onset.get("baseline_median",0)); scale=max(float(onset.get("baseline_mad",0)),0.05)
                        before_dev=median(abs(float(x["value"])-center)/scale for x in before)
                        after_dev=median(abs(float(x["value"])-center)/scale for x in after)
                        if before_dev>0: effects.append((max(0.0,min(1.0,(before_dev-after_dev)/before_dev)),before_dev,after_dev))
                        if str(event.get("id")) in vault: evidence.extend([str(event["id"]),*(str(x["id"]) for x in before+after if str(x.get("id")) in vault)])
            recovered=[item for item in effects if item[1]>1.5 and item[2]<=1.5]
            if recovered:
                verdict,effect,reason="supports",max(item[0] for item in recovered),"An onset precedes a later recovery action; three metric windows return within 1.5 baseline MAD."
            elif effects:
                verdict,effect,reason="contradicts",max(item[0] for item in effects),"A later recovery action is observed, but three metric windows do not return within 1.5 baseline MAD."
            else:
                verdict,effect,reason="inconclusive",0.0,"No complete post-restart metric window set is available; telemetry gaps are not contradictions."
            out.append(VerificationFinding(candidate_id=c.id,target=c.target,verdict=verdict,effect_size=effect,rationale=reason,evidence_ids=sorted(set(evidence))))
        return out
