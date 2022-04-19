class State:
    def __init__(self, name) -> None:
        self.name = name
        self.start = False
        self.final = False
        self.transition_rules = dict()

    #maps a state to a symbol. Can map multiple states and stack data to same symbol
    def add_rule(self, reading_symbol, transition_action):
        if reading_symbol in self.transition_rules:
            self.transition_rules[reading_symbol].append(transition_action)
        else:
            self.transition_rules[reading_symbol] = [transition_action]

    #return next symbol if transition rule exists
    def read_symbol(self, reading_symbol, stack_symbol="@"):
        if reading_symbol in self.transition_rules:
            transition_actions = self.transition_rules[reading_symbol]
            result = []
            for ta in transition_actions:
                if (ta["stack_read"] == "@" or ta["stack_read"] == stack_symbol):
                    result.append(ta)
            print(result)
            if result: return result
        return [None]

    def set_final(self, isFinal):
        self.final = isFinal

    def set_start(self, isStart):
        self.start = isStart

    def is_final(self):
        return self.final

    def __str__(self) -> str:
        return ', '.join(['Name: ' + self.name, 
            'Start: ' + str(self.start), 
            'Final: ' + str(self.final),
            'Transition Rules: ' + ', '.join([r + ':' + ','.join(v.name for v in self.read_symbol(r)) for r in self.transition_rules])])


class NFA:
    def __init__(self) -> None:
        self.states = {}
        self.alphabet = set()
        self.start = None
        self.accepts = False
        self.new()
        self.stack = list()

    #creates a new NFA as specified by input NFA file.
    def new(self, nfa_file_name='dpda.txt'):
        self.states = {}
        self.alphabet = set()
        self.start = None
        self.accepts = False
        with open(nfa_file_name) as nfa_file:
            #read states
            state_name_list = nfa_file.readline().rstrip().split(',')
            for state_name in state_name_list: self.states[state_name] = State(state_name)
            #read alphabet (empty string @ always included)
            self.alphabet.add('@')
            letters = nfa_file.readline().rstrip().split(',')
            for l in letters: self.alphabet.add(l)
            #ignore stack alphabet
            stack_alphabet = nfa_file.readline().rstrip()
            #set start state
            start_state = nfa_file.readline().rstrip()
            self.states[start_state].set_start(True)
            self.start = self.states[start_state]
            #set final state(s)
            final_states = nfa_file.readline().rstrip().split(',')
            for final_state in final_states: self.states[final_state].set_final(True)
            #read in all transition rules
            line = nfa_file.readline()
            while line:
                rule = line.rstrip().split(',')
                transition_action = {"symbol_read" : rule[1], 
                                     "stack_read" : rule[2], 
                                     "next_state" : self.states[rule[3]],
                                     "stack_push" : rule[4]}
                print(transition_action)
                self.states[rule[0]].add_rule(rule[1], transition_action)
                line = nfa_file.readline()
            nfa_file.close()

    #simulates NFA for every string in input file and writes results to output file.
    def run(self, input_file_name='input.txt', output_file_name='output.txt'):
        #clear output file
        with open(output_file_name, 'w') as out:
                    out.truncate(0)
                    out.close()
        #read input file, follow transition rules for each string in file and write result to output.
        with open(input_file_name) as input_file:
            with open(output_file_name, 'w') as out:
                for string in input_file:
                    self.accepts = False
                    #sim function
                    self.simulate(self.start, string.rstrip(), self.stack)
                    if self.accepts:
                        out.write('accept\n')
                    else:
                        out.write('reject\n')
                out.close()
            input_file.close()


    #recursively simulate string on NFA
    def simulate(self, current, string, stack, stack_push="@", empty_cycle=set(), iter=0):
        #kills path if no transition rule for previous symbol or path is @ cycle.
        if current == None or current in empty_cycle: return
        
        
        if stack_push != "@": stack.append(stack_push)
        #if in valid state and not in cycle try and read @. Keep track of states visited to prevent cycles.
        empty_string_stack = stack.copy()
        stack_top = ""
        if stack: stack_top = empty_string_stack.pop()
        empty_next = current.read_symbol('@', stack_top)
        new_empty_cycle = empty_cycle.copy()
        new_empty_cycle.add(current)
        print("stack: ", stack)
        print(iter)
        iter += 1
        for s in empty_next:
            if s and s["stack_read"] == "@":
                print("@, @ stack sim :", s)
                self.simulate(
                    s["next_state"], 
                    string, 
                    stack.copy(), 
                    s["stack_push"], 
                    new_empty_cycle,
                    iter)
            else:
                if s: 
                    print("@, r stack sim :", s)
                    self.simulate(
                    s["next_state"], 
                    string, 
                    empty_string_stack.copy(), 
                    s["stack_push"], 
                    new_empty_cycle,
                    iter)

        #if input string is empty and current state is accept state set accepts var to true
        if not string:
            if current.is_final() and not self.accepts: self.accepts = True
            return

        #if input string not empty read leading character and check if any path from it is valid
        next_stack = stack.copy()
        stack_top = ""
        if stack: stack_top = next_stack.pop()
        next_states = current.read_symbol(string[0], stack_top)
        for s in next_states: 
            if s and s["stack_read"] == "@":
                print("r, @ stack sim :", s)
                self.simulate(
                    s["next_state"], 
                    string[1:], 
                    stack.copy(), 
                    s["stack_push"])
            elif s: 
                print("r, r stack sim :", s)
                self.simulate(
                    s["next_state"], 
                    string[1:], 
                    next_stack.copy(), 
                    s["stack_push"])


    def __str__(self) -> str:
        return 'States:\n' + '\n'.join(['  ' + '\n  '.join([str(self.states[s]) for s in self.states]), 
            'Alphabet: {' + ', '.join([s for s in self.alphabet]) + '}'])


def main():
    test_NFA = NFA()
    test_NFA.run()


if __name__ == '__main__':
    main()
