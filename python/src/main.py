import json
from pathlib import Path
from argparse import ArgumentParser
from dimacs_parser import DimacsParser
from model_timer import Timer
from sat_instance import SATInstance
from collections import deque

def propagate_literal(instance, literal, unit_queue):
    # First check if the literal is already assigned to False
    if instance.lit_value(literal) is False:
        return False
    elif instance.lit_value(literal) is True:
        return True

    instance.assign(literal)
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


def unit_propagation(instance, unit_queue):
    ''' Returns: True if no conflict found, False if conflict found'''
    while unit_queue:
        literal = unit_queue.popleft()
        if not propagate_literal(instance, literal, unit_queue):
            return False 
    return True 


def pure_literal_elimination(instance, unit_queue):
    ''' Returns: True if no conflict found, False if conflict found'''
    solution = dict()

    cur_literals = set.union(*instance.clauses) if instance.clauses else set()
    one_polarity_literals = {lit for lit in cur_literals if -lit not in cur_literals}
    while one_polarity_literals:
        literal = one_polarity_literals.pop()
        # Assign the literal to True and remove clauses satisfied by this literal
        instance.clauses = [clause for clause in instance.clauses if literal not in clause]
        instance.vars.remove(abs(literal)) 

        solution[abs(literal)] = literal > 0

        if not one_polarity_literals:
            # Recompute the set of literals and one-polarity literals after simplification
            cur_literals = set.union(*instance.clauses) if instance.clauses else set()
            one_polarity_literals = {lit for lit in cur_literals if -lit not in cur_literals}

    return instance, None, solution


def sat_solver(instance):
    solution = dict() # TODO: add a stack for backtracing support
    if len(instance.clauses) == 0:
        return "SAT", solution

    # Run UP and PLE while possible
    unit_literals = find_init_unit_literals(instance)
    while True: 
        instance, result, up_solution = unit_propagation(instance, unit_literals)
        unit_literals = None # Don't reuse the same set after the first round
        if result == "UNSAT":
            return "UNSAT", None
        solution.update(up_solution)
        if len(instance.clauses) == 0:
            return "SAT", solution
        
        instance, result, ple_solution = pure_literal_elimination(instance)
        solution.update(ple_solution)
        if len(instance.clauses) == 0:
            return "SAT", solution
         
        if not up_solution and not ple_solution:
            break
        

    # Search for a variable to assign and backtrack if necessary
    
    orig_instance = instance
    var = instance.vars.pop()

    for lit, value in ((var, True), (-var, False)):
        reduced, result, _ = reduce_with_literal(orig_instance, lit)
        if result == "UNSAT":
            continue

        sub_result, sub_sol = sat_solver(reduced)
        if sub_result == "SAT":
            solution[var] = value
            solution.update(sub_sol)
            return "SAT", solution

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
        "Solution": solution,
    }
    
    print(json.dumps(printSol))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_file", type=str)
    args = parser.parse_args()
    main(args)
