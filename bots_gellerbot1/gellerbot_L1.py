import inspect
import types
import sys
import random


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


def move(my_moves, opp_moves):
    curr_frame = inspect.currentframe()

    #
    # Find the opponent's module
    battle_frame = find_battle_frame(curr_frame)
    if battle_frame is None:
        return random.choice(('R', 'P', 'S'))

    bots = get_local_bot_modules(battle_frame)

    this_bot = sys.modules[__name__]
    bots.remove(this_bot)

    opponent = bots.pop()

    #
    # See what the opponent will throw and beat them
    opp_move = opponent.move(opp_moves, my_moves)

    if opp_move == 'R':
        return 'P'
    elif opp_move == 'P':
        return 'S'
    else:
        return 'R'
        
        
def name():
    return "Uri Geller"