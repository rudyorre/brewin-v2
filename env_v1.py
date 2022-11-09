class EnvironmentManager:
    '''
    The EnvironmentManager class keeps a mapping between each global variable (aka symbol)
    in a brewin program and the value of that variable - the value that's passed in can be
    anything you like. In our implementation we pass in a Value object which holds a type
    and a value (e.g., Int, 10).

    To implement lexical scoping, the environment will lose it's O(1) look-up times, since it's
    transitioning from a single dictionary object to a list of dictionaries. Each dictionary
    represents a new scope. So when looking up a variable, it will start with the most recent
    scope dictionary and will move down from there. This means that if there are `n` variables and
    `m` scopes initializing these variables, then it will take O(m) time complexity for standard-look up
    and O(n) space complexity.
    '''
    def __init__(self):
        '''
        dwandwadawd

        self.environment starts with two scopes because the 0th scope is for global variables like resulti, whereas
        the 1st scope is where the first declared variables will be stored.
        '''
        self.environment = [{}, {}]
        self.prev_environments = []

    def exists(self, symbol):
        '''Returns true if the variable exists.'''
        for scope in reversed(self.environment):
            if symbol in scope:
                return True
        return False

    def exists_scope(self, symbol):
        '''Returns true if the variable exists within the same scope.'''
        return symbol in self.environment[-1]

    def get(self, symbol):
        '''
        Gets the data associated a variable name from the first occurrence
        when traversing from the most recent scope to the least recent.
        '''
        for scope in reversed(self.environment):
            if symbol in scope:
                return scope[symbol]
        return None

    def add(self, symbol, value):
        '''Adds new variable the current scope.'''
        self.environment[-1][symbol] = value

    def set(self, symbol, value):
        '''Sets the data associated with a variable name.'''
        # self.print_env(types=True)
        # Assign value to most recent occurrence of the variable
        for scope in reversed(self.environment):
            if symbol in scope:
                # scope[symbol] = scope
                scope[symbol].v = value.v
                return

        # If the variable doesn't already exist, add it to the most recent scope
        self.environment[-1][symbol] = value

    def set_return(self, symbol, value):
        '''
        Sets the global return value (based by type eventually). To make it
        global, this will be in the top-level scope.
        '''
        self.environment[0][symbol] = value

    def push_scope(self):
        '''Creates a new scope.'''
        self.environment.append(dict())
    
    def pop_scope(self):
        '''
        Deletes the most recent scope, and all references to the
        variables defined within this scope.
        '''
        self.environment.pop()

    def print_env(self, values=True, types=False):
        print('[')
        for scope in self.environment:
            print(' { ', end='')
            for (name, value) in scope.items():
                print(f'{name}: {value.type()} {value.value()}', end=', ')
            print('}')
        print(']')
                


  


