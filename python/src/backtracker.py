from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class BackTracker:
    trail: List[int] = field(default_factory=list)
    level: Dict[int, int] = field(default_factory=dict) # 
    reason: Dict[int, Optional[int]] = field(default_factory=dict)
    current_level: int = 0

    # None reason = decision, idx reason = clause index causing UP

    def add_decision(self, lit: int):
        self.current_level += 1
        self.trail.append(lit)
        self.level[abs(lit)] = self.current_level
        self.reason[abs(lit)] = None

    def add_propagation(self, lit: int, reason_clause_idx: int):
        self.trail.append(lit)
        self.level[abs(lit)] = self.current_level
        self.reason[abs(lit)] = reason_clause_idx

    def delete_last(self):
        lit = self.trail.pop()
        del self.level[abs(lit)]
        if self.reason[abs(lit)] == None:
            self.current_level -= 1
        del self.reason[abs(lit)]
        return lit

    def __str__(self):
        return f"BackTracker(trail={self.trail}, level={self.level}, reason={self.reason})"
