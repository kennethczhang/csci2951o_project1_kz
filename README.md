# csci2951o_project1_kz

Optimization plans:

- update sat data structure to track var to clauses
    - using watched literals
    - new idea: assign all vars and if no conflict, then SAT
    - did UP

- No PLE in modern solvers??? Slow becuase of learned clauses and bad returns
    - Expensive from global scans, and doable without but complex w minimal return


- backtracing logic

- conflict driven clause learning (part of backtracking)


backtracking later:
- search heuristic can be
    - conflict driven
    - one of the weights he said in beginning
- restart poliicy
- smarter non-chronological back tracking ?




Modern solvers (MiniSAT-style and beyond):
Use watched literals for BCP
Use VSIDS branching
Use clause learning
Often do not use PLE at all during search