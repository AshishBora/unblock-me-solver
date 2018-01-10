# pylint: disable = C0103, C0111, C0301, R0913, R0903, R0914

"""Some data structures"""

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
