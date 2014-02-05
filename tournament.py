import imp
import os
import sys
import random


WIN_POINTS = 3
LOSE_POINTS = 1
DRAW_POINTS = 0


def beats(a_move, b_move):
    """
    Check if `a_move` beats `b_move`.
    A move should be one of "R" (rock), "P" (paper), or "S" (scissors).
    Returns 'W' for a win, 'L' for a loss, and 'D' for a draw.
    """
    assert a_move in "RPS" and b_move in "RPS"
    if ((a_move == "R" and b_move == "S") or
            (a_move == "S" and b_move == "P") or
            (a_move == "P" and b_move == "R")):
        return "W"
    elif ((b_move == "R" and a_move == "S") or
            (b_move == "S" and a_move == "P") or
            (b_move == "P" and a_move == "R")):
        return "L"
    else:
        return "D"


def battle(player_a, player_b, num_rounds=1000):
    """
    Returns 2-tuple (a_points, b_points) giving the points gained by each
    player.
    """
    a_moves = []
    b_moves = []
    a_points = 0
    b_points = 0

    for _ in xrange(num_rounds):
        if random.randint(0, 1):
            a_move = player_a.move(a_moves, b_moves)
            b_move = player_b.move(b_moves, a_moves)
        else:
            b_move = player_b.move(b_moves, a_moves)
            a_move = player_a.move(a_moves, b_moves)

        outcome = beats(a_move, b_move)
        if outcome == "W":
            a_points += WIN_POINTS
            b_points += LOSE_POINTS
        elif outcome == "L":
            a_points += LOSE_POINTS
            b_points += WIN_POINTS
        elif outcome =="D":
            a_points += DRAW_POINTS
            b_points += DRAW_POINTS

        a_moves.append(a_move)
        b_moves.append(b_move)

    return (a_points, b_points)


def load_bots(dir_fpath):
    """
    Load all Python scripts in the given directory as modules.
    Returns a list of Python modules.
    """
    fnames = os.listdir(dir_fpath)
    fnames = filter(lambda f: f.endswith('.py'), fnames)

    bot_modules = []
    for fname in fnames:
        fpath = os.path.join(dir_fpath, fname)
        module_name = fname.replace('.py','')
        bot = imp.load_source(module_name, fpath)
        bot_modules.append(bot)
    return bot_modules


if __name__ == "__main__":
    assert len(sys.argv) == 2
    bots_dir = sys.argv[1]
    assert os.path.isdir(bots_dir)

    #
    # Load modules contained in bots directory as RPS bots
    bots = load_bots(bots_dir)
    num_bots = len(bots)

    #
    # Bots battle each other once
    print
    for i1 in xrange(num_bots):
        bot1 = bots[i1]
        for i2 in xrange(i1+1, num_bots):
            bot2 = bots[i2]

            bot1_name = bot1.name()
            bot2_name = bot2.name()
            print "'%s' vs '%s'" % (bot1_name, bot2_name)
            (bot1_points, bot2_points) = battle(bot1, bot2)
            print "\t%d points for '%s'" % (bot1_points, bot1_name)
            print "\t%d points for '%s'" % (bot2_points, bot2_name)
            print

