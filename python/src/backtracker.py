from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class BackTracker:
    trail: List[int] = field(default_factory=list)
    level: Dict[int, int] = field(default_factory=dict)
    reason: Dict[int, Optional[int]] = field(default_factory=dict)
    current_level: int = 0

    def add_decision(self, lit: int):
        self.current_level += 1
        self.trail.append(lit)
        self.level[abs(lit)] = self.current_level
        self.reason[abs(lit)] = None

    def add_propagation(self, lit: int, reason_clause_idx: int):
        self.trail.append(lit)
        self.level[abs(lit)] = self.current_level
        self.reason[abs(lit)] = reason_clause_idx

    def __str__(self):
        return f"BackTracker(trail={self.trail}, level={self.level}, reason={self.reason})"
