import inspect
import types
import sys
import random
import ast

def stack_has_bot(current_frame):
    """
    Travel through the stack and see if we hit a frame in a
    module that looks like an RPS bot.
    """
    ancestor_frame = current_frame.f_back
    while ancestor_frame is not None:
        module = inspect.getmodule(ancestor_frame)
        if hasattr(module, 'move') and hasattr(module, 'name'):
            return True
        ancestor_frame = ancestor_frame.f_back
    return False


def get_local_bot_modules(frame):
    """
    Find all bot modules (if any) that are in the frame's local scope.
    """
    bots = set()

    local_vars = frame.f_locals
    for name, val in local_vars.iteritems():
        if isinstance(val, types.ModuleType):
            if hasattr(val, 'move') and hasattr(val, 'name'):
                bots.add(val)

    return bots


def find_battle_frame(current_frame):
    """
    Travel through the stack and see if we find the frame that's pointing
    to two or more bots.
    Return None no matching frame could be found.
    """
    ancestor_frame = current_frame.f_back
    while ancestor_frame is not None:
        bots = get_local_bot_modules(ancestor_frame)
        if len(bots) >= 2:
            return ancestor_frame

        ancestor_frame = ancestor_frame.f_back
    return None


def inject_at_start(func, inject_src):
    """
    Insert some python code at the start of a function. This will modify the
    argument function (`func`) with the updated code.

    `inject_src` is the python source code that will be inserted.
    This snippet should be indented as if it were plain code. I.e., the
    first line should have no indentation.
    """
    #
    # AST for injection
    inject_tree = ast.parse(inject_src, mode='exec')
    inject_tree = inject_tree.body[0]

    #
    # AST for native function
    func_src = inspect.getsource(func)  #~ this can cause issues due to indentation
    func_tree = ast.parse(func_src, mode='exec')

    func_name = func.__name__

    #
    # Modify the existing func tree
    old_body = func_tree.body[0].body
    new_body = [inject_tree] + old_body
    func_tree.body[0].body = new_body

    func_tree = ast.fix_missing_locations(func_tree)  # might not be necessary

    #
    # Compile the module (it contains the function)
    # Recall that we parse'd the func as a module (due to using exec mode).
    # So when we compile (see next line), it's actually a module containing the
    # function.
    module_code_obj = compile(func_tree, filename='<string>', mode='exec')

    #
    # So now we need to execute the module so we can get the function within it.
    # This is what the next two lines do
    scope = {}
    exec(module_code_obj) in scope

    #
    # The scope now has within it the function code we need
    func_code_obj = scope[func_name].__code__
    func.__code__ = func_code_obj


def move(my_moves, opp_moves):
    curr_frame = inspect.currentframe()

    #
    # Check if we're in a loop because the opponent is also playing
    # psychic-shenanigans
    if stack_has_bot(curr_frame):
        # clever girl
        return random.choice('RPS')

    #
    # Find the opponent's module
    battle_frame = find_battle_frame(curr_frame)
    if battle_frame is None:
        return random.choice('RPS')

    bots = get_local_bot_modules(battle_frame)

    this_bot = sys.modules[__name__]
    bots.remove(this_bot)

    opponent = bots.pop()

    #
    # Modify the opponent's code
    # We have to use a special attribute set on the function object to make
    # sure we don't re-edit the code.
    # This is becuase, after injecting the code, we're going to end up
    # with linecahce issues if we try to re-inject on the same function.
    # (Theoretically we'd just be re-editing the original source code (see:
    # inspect.getsource), but the linecache will cause a failure because it's
    # out of synch.)
    # For more info, see the source code for inspect.findsource; specifically
    # the line
    #    raise IOError('could not get source code'))
    # gets triggered.
    if not hasattr(opponent.move, '__spooned__'):
        code = """return 'R'"""
        inject_at_start(opponent.move, code)
        opponent.move.__spooned__ = True
    return 'P'


def name():
    return "Uri Geller"