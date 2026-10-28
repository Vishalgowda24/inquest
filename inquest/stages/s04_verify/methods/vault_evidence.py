from inquest.contracts import Candidate, VerificationFinding

class VaultEvidenceMethod:
    name = "vault_evidence"
    def run(self, candidates, context, vault):
        findings=[]
        for c in candidates:
            cited=set(c.evidence_ids); present=cited & vault.keys(); missing=cited-vault.keys()
            if not cited: verdict,effect,reason="inconclusive",0.0,"Candidate has no evidence citations to verify."
            elif missing: verdict,effect,reason="contradicts",0.0,f"{len(missing)} cited item(s) absent from verified vault."
            else: verdict,effect,reason="supports",1.0,f"All {len(present)} cited item(s) exist in verified vault."
            findings.append(VerificationFinding(candidate_id=c.id,target=c.target,verdict=verdict,effect_size=effect,rationale=reason,evidence_ids=sorted(present)))
        return findings
