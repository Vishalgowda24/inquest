"""Verify S03 candidates, assign statuses, and optionally rank by verification."""
from inquest.contracts import CandidateAnalysis, StageInput, StageResult, StageStatus, VerificationAnalysis, VerificationDecision, VerificationMethodResult
from inquest.core.vault import read_vault_entries
from .methods.registry import default_method_registry

_PRIORITY={"verified":0,"contested":1,"insufficient_evidence":2,"unsupported":3}

class VerifyStage:
    name="s04_verify"
    def run(self,ctx,inp):
        previous=inp.payload.get("previous_output")
        previous=previous if isinstance(previous,dict) else {}
        try:
            candidates=CandidateAnalysis.model_validate(previous.get("analysis"))
            context=previous.get("verification_context",{})
            if not isinstance(context,dict): context={}
        except Exception as exc:
            return StageResult(stage=self.name,status=StageStatus.DEGRADED,output={"reason":f"S03 ensemble unavailable: {exc}"},elapsed_ms=0)
        try: vault=read_vault_entries(ctx.runs_dir/ctx.run_id/"vault"/"chain.jsonl")
        except Exception as exc:
            failed=[VerificationDecision(candidate_id=c.id,target=c.target,status="unsupported",confidence=0,s03_rank=i,s03_score=c.score,method_scores=c.method_scores,s03_disagreement=candidates.disagreement,rationale="Evidence vault integrity could not be verified.",evidence_ids=[]) for i,c in enumerate(candidates.candidates,start=1)]
            methods=[VerificationMethodResult(method=name,status="DEGRADED",note=f"Vault integrity failure: {type(exc).__name__}: {exc}") for name in default_method_registry().names()]
            failed_analysis=VerificationAnalysis(decisions=failed,per_method={},method_results=methods,disagreement=0,original_order=failed,reranked_order=failed,reranking_enabled=bool(ctx.config.verification_rerank))
            return StageResult(stage=self.name,status=StageStatus.FAILED,output={"analysis":failed_analysis.model_dump(mode="json"),"source":previous.get("source","real"),"synthetic":bool(previous.get("synthetic",False))},error_type=type(exc).__name__,error=str(exc),elapsed_ms=0)
        registry=default_method_registry(); results=[]
        for name in registry.names():
            if not ctx.config.verification_methods.get(name,True):
                results.append(VerificationMethodResult(method=name,status="DISABLED",note="Disabled in config.yaml")); continue
            try:
                findings=registry.get(name).run(candidates.candidates,context,vault)
                invalid=sorted({eid for f in findings for eid in f.evidence_ids if eid not in vault})
                if invalid: raise ValueError(f"Finding evidence IDs absent from verified vault: {invalid}")
                results.append(VerificationMethodResult(method=name,status="OK",findings=findings))
            except Exception as exc: results.append(VerificationMethodResult(method=name,status="DEGRADED",note=f"{type(exc).__name__}: {exc}"))
        active=[x for x in results if x.status!="DISABLED"]
        maps={x.method:{f.candidate_id:f for f in x.findings} for x in active}
        decisions=[]
        for rank,candidate in enumerate(candidates.candidates,start=1):
            votes=[m[candidate.id] for m in maps.values() if candidate.id in m]
            causal_votes=[m[candidate.id] for method,m in maps.items() if method!="vault_evidence" and candidate.id in m]
            support_families=set()
            for method in maps:
                if method=="vault_evidence": continue
                finding=maps[method].get(candidate.id)
                if finding is None or finding.verdict!="supports": continue
                family="graph" if method in {"dependency_path","alternative_check"} else method
                support_families.add(family)
            supports=len(support_families)
            contradicts=sum(x.verdict=="contradicts" for x in causal_votes)
            inconclusive=sum(x.verdict=="inconclusive" for x in causal_votes)
            missing=set(candidate.evidence_ids)-vault.keys()
            equal_competitor=any(other.id!=candidate.id and abs(other.score-candidate.score)<=1e-12 for other in candidates.candidates)
            if missing or (contradicts>0 and supports==0): status="unsupported"
            elif contradicts>0 or equal_competitor: status="contested"
            elif supports>=2 and contradicts==0: status="verified"
            elif not causal_votes or inconclusive>len(causal_votes)/2: status="insufficient_evidence"
            else: status="insufficient_evidence"
            enabled_families={"graph" if item.method in {"dependency_path","alternative_check"} else item.method for item in results if item.method!="vault_evidence" and item.status!="DISABLED"}
            confidence=(supports/max(1,len(enabled_families)))
            evidence=sorted({eid for finding in votes for eid in finding.evidence_ids})
            if missing: reason=f"Vault integrity failed for {len(missing)} candidate citation(s)."
            elif equal_competitor: reason="An equally scored competing candidate exists."
            else: reason=f"{supports} supporting, {contradicts} contradicting, and {inconclusive} inconclusive checks."
            decisions.append(VerificationDecision(candidate_id=candidate.id,target=candidate.target,status=status,confidence=confidence,s03_rank=rank,s03_score=candidate.score,method_scores=candidate.method_scores,s03_disagreement=candidates.disagreement,rationale=reason,evidence_ids=evidence))
        disagreement_count=sum(len({m[d.candidate_id].verdict for m in maps.values() if d.candidate_id in m})>1 for d in decisions)
        rerank=bool(ctx.config.verification_rerank)
        ranked=sorted(decisions,key=lambda d:(_PRIORITY[d.status],d.s03_rank)) if rerank else list(decisions)
        analysis=VerificationAnalysis(decisions=decisions,per_method={x.method:x.findings for x in results if x.status!="DISABLED"},method_results=results,disabled_methods=[x.method for x in results if x.status=="DISABLED"],disagreement=disagreement_count/max(1,len(decisions)),original_order=decisions,reranked_order=ranked,reranking_enabled=rerank)
        status=StageStatus.DEGRADED if any(x.status=="DEGRADED" for x in results) else StageStatus.OK
        ids=sorted({e for d in decisions for e in d.evidence_ids})
        source=previous.get("source","real")
        return StageResult(stage=self.name,status=status,output={"analysis":analysis.model_dump(mode="json"),"source":source,"synthetic":bool(previous.get("synthetic",source=="synthetic"))},evidence_ids=ids,elapsed_ms=0)
