import json
from pathlib import Path
from argparse import ArgumentParser
from dimacs_parser import DimacsParser
from model_timer import Timer
from sat_instance import SATInstance
from collections import deque

def propagate_literal(instance, literal, unit_queue, trail):
    # First check if the literal is already assigned to False
    if instance.lit_value(literal) is False:
        return False
    elif instance.lit_value(literal) is True:
        return True

    instance.assign(literal, trail)
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
                return False
            unit_queue.append(other_watch_lit) # Otherwise unit (in place edit)

    return True


def find_init_unit_literals(instance):
    unit_queue = deque()
    for clause in instance.clauses:
        if len(clause.lits) == 1: 
            unit_queue.append(clause.lits[0])
    return unit_queue


def unit_propagation(instance, unit_queue, trail):
    ''' Returns: True if no conflict found, False if conflict found'''
    while unit_queue:
        literal = unit_queue.popleft()
        if not propagate_literal(instance, literal, unit_queue, trail):
            return False 
    return True 


def sat_solver(instance, unit_queue=None, trail=None):
    if instance.is_satisfied():
        return "SAT", instance.assignment
    
    if unit_queue is None:
        unit_queue = find_init_unit_literals(instance)
    if trail is None:
        trail = []
    
    # Run UP just once
    result = unit_propagation(instance, unit_queue, trail)
    if not result:
        return "UNSAT", None
    if instance.is_satisfied():
        return "SAT", instance.assignment

    # If we reach here, we need to make a decision
    # Search for a variable to assign and backtrack if necessary
    var = next(iter(instance.unassigned_vars))
    for lit in (var, -var):
        level = len(trail) # current decision level 
        unit_queue = deque() # reset unit literals for new branch

        if propagate_literal(instance, lit, unit_queue, trail):
            result, sol = sat_solver(instance, unit_queue, trail)
            if result == "SAT":
                return "SAT", sol
        
        # Backtrack because no solution
        while len(trail) > level:
            instance.unassign(trail.pop())

    return "UNSAT", None


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
        if instance:
            print(instance, end="")
    except Exception as e:
        print(f"Error: {e}")

    # TODO: call your solver here and get the result
    result, solution = sat_solver(instance)
    
    timer.stop()
    
    printSol = {
        "Instance": filename,
        "Time": f"{timer.getTime():.2f}",
        "Result": result,
        "Solution": ' '.join(f"{lit} {str(solution[lit]).lower()}" for lit in sorted(solution.keys())),
    }
    
    print(json.dumps(printSol))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()
    main(args)




# def pure_literal_elimination(instance, unit_queue):
#     ''' Returns: True if no conflict found, False if conflict found'''

    
#     solution = dict()

#     cur_literals = set.union(*instance.clauses) if instance.clauses else set()
#     one_polarity_literals = {lit for lit in cur_literals if -lit not in cur_literals}
#     while one_polarity_literals:
#         literal = one_polarity_literals.pop()
#         # Assign the literal to True and remove clauses satisfied by this literal
#         instance.clauses = [clause for clause in instance.clauses if literal not in clause]
#         instance.vars.remove(abs(literal)) 
#         solution[abs(literal)] = literal > 0

#         if not one_polarity_literals:
#             # Recompute the set of literals and one-polarity literals after simplification
#             cur_literals = set.union(*instance.clauses) if instance.clauses else set()
#             one_polarity_literals = {lit for lit in cur_literals if -lit not in cur_literals}

#     return instance, None, solution

        # instance, result, ple_solution = pure_literal_elimination(instance)
        # solution.update(ple_solution)
        # if len(instance.clauses) == 0:
        #     return "SAT", solution
