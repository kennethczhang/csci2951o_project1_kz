from dataclasses import dataclass, field
from typing import List, Set, Dict


@dataclass
class Clause:
    lits: List[int] = field(default_factory=list)
    w1: int = 0
    w2: int = 1
    learned: bool = False

    def __post_init__(self):
        if len(self.lits) == 1:
            self.w2 = 0

    def __str__(self):
        return f"Clause(w1={self.w1}, w2={self.w2}, lits={self.lits})"


@dataclass
class SATInstance:
    clauses: List[Clause] = field(default_factory=list)
    watch_list: Dict[int, List[int]] = field(default_factory=dict)
    assignment: Dict[int, bool] = field(default_factory=dict)
    unassigned_vars: Set[int] = field(default_factory=set)
    # var_activity: Dict[int, float] = field(default_factory=dict)
    # var_polarity: Dict[int, bool] = field(default_factory=dict)
    # vsids_inc: float = 1.0
    # vsids_decay: float = 0.95
    # lit_count: Dict[int, int] = field(default_factory=dict)

    def add_clause(self, clause: Clause):
        self.clauses.append(clause)
        idx = len(self.clauses) - 1

        l1 = clause.lits[clause.w1]
        l2 = clause.lits[clause.w2]
        self.watch_list.setdefault(l1, []).append(idx)
        if l2 != l1:
            self.watch_list.setdefault(l2, []).append(idx)

        self.unassigned_vars.update(abs(lit) for lit in clause.lits)

        # for lit in clause.lits:
        #     v = abs(lit)
        #     # Initialize VSIDS-related metadata lazily
        #     if v not in self.var_activity:
        #         self.var_activity[v] = 0.0
        #     if v not in self.var_polarity:
        #         self.var_polarity[v] = (lit > 0)

        # for lit in clause.lits:
        #     self.lit_count[lit] = self.lit_count.get(lit, 0) + 1

    def lit_value(self, lit: int):
        v = abs(lit)
        if v not in self.assignment:
            return None
        val = self.assignment[v]
        return val if lit > 0 else not val
    
    def assign(self, lit: int): 
        v = abs(lit)
        self.assignment[v] = (lit > 0)
        # self.var_polarity[v] = (lit > 0)
        self.unassigned_vars.discard(v)

    def unassign(self, lit: int):
        v = abs(lit)
        del self.assignment[v]
        self.unassigned_vars.add(v)

    def is_satisfied(self):
        # return len(self.unassigned_vars) == 0
        # TODO: i thought if len(self.unassigned_vars) == 0 then its T for watched literals
        for clause in self.clauses:
            if not any(self.lit_value(lit) is True for lit in clause.lits):
                return False
        return True


    def __str__(self):
        numVars = len(self.unassigned_vars) + len(self.assignment)
        numClauses = len(self.clauses)
        out = []
        out.append(f"Number of variables: {numVars}")
        out.append(f"Number of clauses: {numClauses}")
        # out.append(f"Variables: {self.vars}")
        for i, clause in enumerate(self.clauses):
            out.append(f"Clause {i}: {clause}")
        out.append(f"Watch list: {self.watch_list}")
        out.append(f"Assignment: {self.assignment}")
        out.append(f"Unassigned vars: {self.unassigned_vars}")

        return "\n".join(out) + "\n"

    # VSIDS helper methods
    def bump_var_activity(self, lits):
        inc = self.vsids_inc
        for lit in lits:
            v = abs(lit)
            self.var_activity[v] = self.var_activity.get(v, 0.0) + inc
            if self.var_activity[v] > 1e100:
                self._rescale_activities()
        # Increase increment geometrically (equivalent to decay of existing activities)
        self.vsids_inc /= self.vsids_decay

    def _rescale_activities(self):
        scale = 1e-100
        for v in self.var_activity:
            self.var_activity[v] *= scale
        self.vsids_inc *= scale
