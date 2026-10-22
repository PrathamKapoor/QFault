"""Deterministic one-edit program interventions. No state or evaluator access."""
from itertools import permutations
from math import pi
from typing import Annotated, Literal
from pydantic import Field
from .quantum import Strict, Gate, resources
from .lab import CustomCircuit


class EditRestrictions(Strict):
    operators: tuple[Literal['remove','replace','angle','reassign','insert'], ...] = Field(default=('remove','replace','angle','reassign'), max_length=5)
    positions: tuple[Annotated[int, Field(strict=True)], ...] | None = Field(default=None, max_length=33)
    palette: tuple[Literal['h','x','z','s','rx','ry','rz','cx','cz','cp','swap'], ...] = Field(default=('h','x','z','cx','cz'), max_length=11)
    angles: tuple[Annotated[float, Field(strict=True)], ...] = Field(default=(0., pi/2, -pi/2, pi), max_length=8)
    max_depth: int = Field(default=32, ge=1, le=37, strict=True)


def generate(original: CustomCircuit, restrictions: EditRestrictions, limit: int):
    """Declared order; at most 4096 proposals inspected, 48 accepted; no hidden priority."""
    if not 1 <= limit <= 48:
        raise ValueError('candidate limit must be 1..48')
    if restrictions.positions is not None and any(p < 0 or p > len(original.gates) for p in restrictions.positions):
        raise ValueError('edit position outside circuit')
    if any(abs(a) > 8*pi for a in restrictions.angles):
        raise ValueError('angle outside gate bounds')
    candidates, excluded = [], []
    seen = {original.circuit_id:None}
    gates = original.gates
    old_resources = resources(original.subject())

    def proposals():
        for op in restrictions.operators:
            for i in range(len(gates) + (op == 'insert')):
                if restrictions.positions is not None and i not in restrictions.positions:
                    continue
                before = gates[i] if i < len(gates) and op != 'insert' else None
                if op == 'remove':
                    yield op, i, before, None
                elif op == 'angle' and before.angle is not None:
                    for a in restrictions.angles:
                        yield op, i, before, Gate(name=before.name, qubits=before.qubits, angle=a)
                elif op == 'reassign':
                    for qs in permutations(range(original.n_qubits),len(before.qubits)):
                        yield op, i, before, Gate(name=before.name,qubits=qs,angle=before.angle)
                elif op in ('replace','insert'):
                    for name in restrictions.palette:
                        arity = 2 if name in ('cx','cz','cp','swap') else 1
                        assignments = [before.qubits] if before and len(before.qubits)==arity else permutations(range(original.n_qubits),arity)
                        for qs in assignments:
                            for a in (restrictions.angles if name in ('rx','ry','rz','cp') else (None,)):
                                yield op, i, before, Gate(name=name,qubits=qs,angle=a)

    inspected = 0
    for op, i, before, after in proposals():
        inspected += 1
        if inspected > 4096: break
        edit = {'operator':op,'index':i,'before':before.model_dump(mode='json') if before else None,
                'after':after.model_dump(mode='json') if after else None}
        changed = gates[:i] + (() if after is None else (after,)) + gates[i+(op!='insert'):]
        if before == after or (after and after.angle == 0 and op == 'insert'):
            excluded.append({**edit,'reason':'NO_OP'}); continue
        try:
            c = CustomCircuit.model_validate({**original.model_dump(),'gates':changed})
            res = resources(c.subject())
            if res['depth'] > restrictions.max_depth: raise ValueError('depth limit')
        except ValueError:
            excluded.append({**edit,'reason':'STRUCTURAL_LIMIT'}); continue
        if c.circuit_id in seen:
            earlier=seen[c.circuit_id]
            duplicate={**edit,'reason':'DUPLICATE_OR_ORIGINAL','equivalent_circuit_id':c.circuit_id}
            excluded.append(duplicate)
            if earlier is not None: earlier['equivalent_edits'].append(edit)
            continue
        candidates.append({'candidate_id':c.circuit_id,'circuit_id':c.circuit_id,
            'original_circuit_id':original.circuit_id,'circuit':c.model_dump(mode='json'),'edit':edit,
            'equivalent_edits':[],
            'resources':res,'resource_delta':{k:res[k]-old_resources[k] for k in ('gates','depth','two_qubit_gates')},
            'eligibility':'Validated one-edit circuit within declared restrictions',
            'provenance':'deterministic declared operator / position / palette order'})
        seen[c.circuit_id]=candidates[-1]
        if len(candidates) == limit: break
    return {'candidates':candidates,'excluded':excluded,'proposals_inspected':min(inspected,4096),
            'truncated':len(candidates)==limit or inspected>4096,'search_ceiling':limit}
