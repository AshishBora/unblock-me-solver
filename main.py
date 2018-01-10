# pylint: disable = C0103, C0111, C0301, R0913, R0903, R0914

"""Solver for the Unblock Me game"""

import time
import utils
import solver
import classes


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


def solve():

    t0 = time.time()

    # print 'Capturing and transferring screenshot...'
    screen_filename = 'screen.png'
    screen_cmds = [
        './adb shell screencap -p /sdcard/{}'.format(screen_filename),
        './adb pull /sdcard/{}'.format(screen_filename),
    ]
    utils.run_cmds(screen_cmds)
    t1 = time.time()

    # print 'Getting initial configuration...',
    start = solver.get_start_config(screen_filename)
    # print 'Done'
    t2 = time.time()

    # print 'Computing the moves...',
    swipes = solver.solve(start)
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
    utils.run_cmds([solution_cmd])
    # print 'Done\n'
    t4 = time.time()

    rundata = classes.Rundata(start, swipes,
                              t1 - t0,
                              t2 - t1,
                              t3 - t2,
                              t4 - t3)
    rundata.pprint()

    return rundata


def main():
    transition_cmds = [
        # './adb shell input tap 383 1203',  # click on next (Challenge mode)
        './adb shell input tap 549 156',  # tap outside to remove touch artifacts (example: developer options)
    ]

    # Thrice so that even if click on ads by mistake, we go back to the game
    back_cmds = ['./adb shell input keyevent 4' for _ in range(3)]

    pkl_filepath = './log.pkl'
    log = utils.load_if_pickled(pkl_filepath)

    new_in_log = 0
    while True:
        if new_in_log >= 5:
            utils.save_to_pickle(log, pkl_filepath)
            new_in_log = 0

        try:
            utils.run_cmds(transition_cmds)
            rundata = solve()
            log.append(rundata)
            new_in_log += 1
            time.sleep(4)  # Time in seconds.
        except (solver.BFSError, solver.HashError):
            utils.run_cmds(back_cmds)

if __name__ == '__main__':
    main()
