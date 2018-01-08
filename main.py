# pylint: disable = C0103, C0111, C0301, R0913, R0903, R0914

import os
import time
import cPickle as pickle

import unblock_solver


class Rundata(object):
    def __init__(self, start, swipes,
                 screen_time, init_time, solve_time, run_time):
        self.start = start
        self.swipes = swipes
        self.screen_time = screen_time
        self.init_time = init_time
        self.solve_time = solve_time
        self.run_time = run_time

    def pprint(self):
        print 'time_spent: screen = {:06.2f}, init = {:06.2f}, solve = {:06.2f}, run = {:06.2f}'.format(
            self.screen_time,
            self.init_time,
            self.solve_time,
            self.run_time,
        )


def get_cmd(move, pattern, X_vals, Y_vals):
    j1, i1, j2, i2 = move
    dist = abs(j1 - j2) + abs(i1 - i2)

    x1 = X_vals[i1]
    y1 = Y_vals[j1]
    x2 = X_vals[i2]
    y2 = Y_vals[j2]

    cmd = pattern.format(
        x1, y1, x2, y2, 50*dist
    )
    return cmd


def run_cmds(cmds):
    for cmd in cmds:
        # print cmd
        os.system(cmd)


def solve():

    t0 = time.time()

    # print 'Capturing and transferring screenshot...'
    screen_cmds = [
        './adb shell screencap -p /sdcard/screencap.png',
        './adb pull /sdcard/screencap.png',
    ]
    run_cmds(screen_cmds)
    t1 = time.time()

    # print 'Getting initial configuration...',
    start = unblock_solver.get_start_config()
    # print 'Done'
    t2 = time.time()

    # print 'Computing the moves...',
    swipes = unblock_solver.solve(start)
    if swipes is None:
        print 'Invalid grid'
        raise RuntimeError
    t3 = time.time()

    # print 'Converting to swipe commands...',
    X_vals = [127, 294, 461, 628, 795, 962]
    Y_vals = [633, 800, 967, 1134, 1301, 1468]
    pattern = 'input swipe {} {} {} {} {}; '
    move_cmds = [get_cmd(swipe, pattern, X_vals, Y_vals) for swipe in swipes]
    solution_cmd = './adb shell "{}"'.format('\n'.join(move_cmds))
    # print 'Done'

    # print 'Solving the puzzle...',
    run_cmds([solution_cmd])
    # print 'Done\n'
    t4 = time.time()

    rundata = Rundata(start, swipes,
                      t1 - t0,
                      t2 - t1,
                      t3 - t2,
                      t4 - t3)
    rundata.pprint()

    return rundata


def save_to_pickle(log, pkl_filepath):
    with open(pkl_filepath, 'wb') as pkl_file:
        pickle.dump(log, pkl_file)


def load_if_pickled(pkl_filepath):
    """Load if the pickle file exists. Else return empty list"""
    if os.path.isfile(pkl_filepath):
        with open(pkl_filepath, 'rb') as pkl_file:
            log = pickle.load(pkl_file)
    else:
        log = []
    return log


def main():
    transition_cmds = [
        './adb shell input tap 383 1203',  # click on next (Challenge mode)
        './adb shell input tap 549 156',  # tap outside to remove touch artifacts (example: developer options)
    ]

    # Thrice so that even if click on ads by mistake, we go back to the game
    back_cmds = ['./adb shell input keyevent 4' for _ in range(3)]

    pkl_filepath = './unblock_log.pkl'
    log = load_if_pickled(pkl_filepath)

    new_in_log = 0
    while True:
        if new_in_log >= 5:
            save_to_pickle(log, pkl_filepath)
            new_in_log = 0

        try:
            run_cmds(transition_cmds)
            rundata = solve()
            log.append(rundata)
            new_in_log += 1
            time.sleep(4) # Time in seconds.
        except unblock_solver.BFSError:
            run_cmds(back_cmds)
        except unblock_solver.HashError:
            run_cmds(back_cmds)

if __name__ == '__main__':
    main()
