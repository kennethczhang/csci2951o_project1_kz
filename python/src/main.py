import json
from pathlib import Path
from argparse import ArgumentParser
from dimacs_parser import DimacsParser
from model_timer import Timer
from sat_instance import SATInstance, Clause
from backtracker import BackTracker
from collections import deque

def propagate_literal(instance, literal, unit_queue, bt, reason=None):
    # First check if the literal is already assigned to False
    if instance.lit_value(literal) is False:
        if reason is not None:
            return False, reason
        return False, -1
    elif instance.lit_value(literal) is True:
        return True, None

    instance.assign(literal)
    if reason == None:
        bt.add_decision(literal)
    else:
        bt.add_propagation(literal, reason)
    clause_check_idxs = list(instance.watch_list.get(-literal, [])) # copy

    for ci in clause_check_idxs:
        # Get literal and value of other watched literal
        clause = instance.clauses[ci]
        if clause.lits[clause.w1] == -literal:
            other_watch_idx = clause.w2
        else:
            other_watch_idx = clause.w1
        other_watch_lit = clause.lits[other_watch_idx]
        other_watch_val = instance.lit_value(other_watch_lit)

        if other_watch_val is True: # clause is already satisfied, no need to move watch
            continue

        new_i = None
        for i, lit in enumerate(clause.lits):
            if i == other_watch_idx:
                continue
            if instance.lit_value(lit) is not False: 
                new_i = i # i != watch_idx by definition of watch_idx
                break

        if new_i is not None: # found new watch
            # Update watched literals + watch list
            clause.w1 = other_watch_idx
            clause.w2 = new_i
            instance.watch_list[-literal].remove(ci)
            instance.watch_list.setdefault(clause.lits[new_i], []).append(ci)
        else:
            # No new watch found
            if other_watch_val is False:  # Conflict
                return False, ci
            unit_queue.append((other_watch_lit, ci)) # Otherwise unit (in place edit)

    return True, None


def find_init_unit_literals(instance):
    unit_queue = deque()
    for idx, clause in enumerate(instance.clauses):
        if len(clause.lits) == 1: 
            unit_queue.append((clause.lits[0], idx))
    return unit_queue


def unit_propagation(instance, unit_queue, bt):
    ''' Returns: True if no conflict found, False if conflict found'''
    while unit_queue:
        literal, idx = unit_queue.popleft()
        valid, reason = propagate_literal(instance, literal, unit_queue, bt, idx)
        if not valid:
            return False, reason
    return True, None


def find_conflict_lits(instance, bt, conflict_clause_idx):
    '''Creates learned conflict clause'''
    conflict_lits = instance.clauses[conflict_clause_idx].lits.copy()
    cur_level = bt.current_level

    def cur_level_lits(lits):
        clause_vars = {abs(l) for l in lits}
        out = []
        for t in reversed(bt.trail):  # t is the assigned literal (with its sign)
            v = abs(t)
            if v in clause_vars and bt.level[v] == cur_level:
                # append the literal as it appears in the clause, not necessarily same sign as trail
                # find that literal in lits:
                for l in lits:
                    if abs(l) == v:
                        out.append(l)
                        break
        return out


    uips = cur_level_lits(conflict_lits)# garuanteed non-empty

    while len(uips) > 1:
        lit_to_resolve = uips[0]
        conflict_lits.remove(lit_to_resolve)

        reason_idx = bt.reason[abs(lit_to_resolve)]
        assert reason_idx is not None

        reason_lits = instance.clauses[reason_idx].lits.copy()
        reason_lits = [l for l in reason_lits if l != -lit_to_resolve]

        conflict_lits.extend(reason_lits)

        # Dedupe with order preservation
        seen = set()
        conflict_lits = [l for l in conflict_lits if not (l in seen or seen.add(l))]

        # Need to recompute because new literals added
        uips = cur_level_lits(conflict_lits)
    
    return conflict_lits


def backtrack(instance, unit_queue, bt, conflict_clause_idx):
    # print(instance)
    # print(unit_queue)
    # print(bt)
    # print("------")
    learned_lits = find_conflict_lits(instance, bt, conflict_clause_idx)
    learned_clause = Clause(learned_lits, learned=True)

    # # VSIDS: bump activities for literals involved in the conflict
    # instance.bump_var_activity(learned_lits)

    # Find backjump level (second highest level bc 1-UIP)
    cur_level = bt.current_level

    def cur_level_lits(lits):
        clause_vars = {abs(l) for l in lits}
        out = []
        for t in reversed(bt.trail):  # t is the assigned literal (with its sign)
            v = abs(t)
            if v in clause_vars and bt.level[v] == cur_level:
                # append the literal as it appears in the clause, not necessarily same sign as trail
                # find that literal in lits:
                for l in lits:
                    if abs(l) == v:
                        out.append(l)
                        break
        return out
    
    cur_lits = cur_level_lits(learned_lits)
    # print(learned_clause)
    # print(cur_lits)
    # print(instance)
    # print(unit_queue)
    # print(bt)
    
    assert len(cur_lits) == 1, f"Expected 1 UIP lit, got {cur_lits}"
    uip_lit = cur_lits[0]

    other_levels = [
        bt.level.get(abs(lit), 0)
        for lit in learned_lits
        if lit != uip_lit
    ]

    backjump_level = max(other_levels) if other_levels else 0

    # Backtrack to the level
    while bt.trail and bt.level[abs(bt.trail[-1])] > backjump_level:
        lit = bt.delete_last()
        instance.unassign(lit)
    bt.current_level = backjump_level

    # Add leanred clause to database
    instance.add_clause(learned_clause)

    # Unit propagate the learned clause
    learned_clause_idx = len(instance.clauses) - 1
    unit_queue.append((uip_lit, learned_clause_idx))

    return


def sat_solver(instance, unit_queue=None, bt=None):
    
    if unit_queue is None:
        unit_queue = find_init_unit_literals(instance)
    if bt is None:
        bt = BackTracker()

    while True:
        # Run UP just once
        valid, reason = unit_propagation(instance, unit_queue, bt)
        if not valid:
            if bt.current_level == 0:
                return "UNSAT", None
            backtrack(instance, unit_queue, bt, reason)
            continue

        if instance.is_satisfied():
            return "SAT", instance.assignment

        # Make next decision
        var = next(iter(instance.unassigned_vars))
        lit = var
        unit_queue.append((lit, None))


def main(args):
    input_file = args.input_file
    
    if not input_file:
        print("Usage: python3 src/main.py <cnf file>")
        return

    path = Path(input_file)
    filename = path.name
    
    timer = Timer()
    timer.start()
    
    try:
        instance = DimacsParser.parse_cnf_file(input_file)
        # if instance:
            # print(instance, end="")
    except Exception as e:
        print(f"Error: {e}")

    result, solution = sat_solver(instance)
    
    timer.stop()

    printSol = {
        "Instance": filename,
        "Time": f"{timer.getTime():.2f}",
        "Result": result,
    }

    if result == "SAT":
        printSol["Solution"] = ' '.join(
            f"{lit} {str(solution[lit]).lower()}"
            for lit in sorted(solution.keys())
        )

    
    print(json.dumps(printSol))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()
    main(args)
