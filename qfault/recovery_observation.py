"""Contract-to-observation adapter; decisions receive counts, never candidate state."""
from .lab import (plan, _State, PauliContract, DistributionContract, TargetStateContract,
                  parity_expectation, hoeffding_radius)
from .target import catalog, bounds, decide, point_estimate


class ContractObservation:
    """Single-look fixed measurement schedule. All target terms count in multiplicity.

    A future contract needs a validated schedule and simultaneous loss bounds here.
    The scalar loss is max normalized claim discrepancy (target: infidelity/tolerance).
    Loss <= 1 means the declared contract, not unitary equivalence.
    """
    def __init__(self, n, contract):
        self.n, self.contract = n, contract
        self.claims, self.groups = plan(n, contract)
        self.cat = catalog(contract.amplitudes) if isinstance(contract,TargetStateContract) else None
        if self.cat:
            weights = dict(self.cat['terms'])
            self.groups.sort(key=lambda g:-sum(abs(weights[t]) for t in g['terms']))
        self.interval_count = len(self.cat['terms']) if self.cat else len(self.claims)

    def observe(self, measure, shots, alpha, group_limit=16):
        events, est, radii, states = [], {}, {}, {}
        expected = self.contract.expected_probabilities if isinstance(self.contract,DistributionContract) else None
        if not self.cat:
            states = {c['claim_id']:_State(c,self.n,expected) for c in self.claims}
        for g in self.groups[:group_limit]:
            ev = measure(g['setting'],shots,g['group_id']); events.append({**ev,'group':g})
            if self.cat:
                for t in g['terms']:
                    est[t] = parity_expectation(ev['counts'],ev['shots'],t)
                    radii[t] = hoeffding_radius(ev['shots'],alpha)
            else:
                for cid in g['claims']: states[cid].add(ev['counts'],ev['shots'],alpha)
        if self.cat:
            lo, hi = bounds(self.cat,est,radii)
            tol = self.contract.fidelity_tolerance
            return {'loss_interval':[(1-hi)/tol,(1-lo)/tol],
                'point_loss':(1-point_estimate(self.cat,est))/tol,
                'claims':[{'claim_id':'target:fidelity','status':decide(lo,hi,self.contract.threshold),
                           'interval':[lo,hi],'threshold':self.contract.threshold}],
                'events':events,'terms_measured':len(est),'terms_total':len(self.cat['terms']),
                'expectations':{t:{'estimate':est[t],'radius':radii[t]} for t in est}}
        lows, highs, points = [], [], []
        for s in states.values():
            if s.estimate is None:
                lows.append(0); highs.append(2/s.claim['tolerance']); points.append(1); continue
            d = abs(s.estimate-s.claim['expected']) if isinstance(self.contract,PauliContract) else s.estimate
            tol = s.claim['tolerance']
            lows.append(max(0,d-s.radius)/tol); highs.append((d+s.radius)/tol); points.append(d/tol)
        return {'loss_interval':[max(lows),max(highs)],'point_loss':max(points),
                'claims':[s.report() for s in states.values()],'events':events}
