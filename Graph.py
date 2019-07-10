import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import matplotlib.animation as animation
plt.rcParams['animation.ffmpeg_path'] = "C:/FFmpeg/bin/ffmpeg"


class FasterFFMpegWriter(FFMpegWriter):
    '''FFMpeg-pipe writer bypassing figure.savefig.'''
    def __init__(self, **kwargs):
        '''Initialize the Writer object and sets the default frame_format.'''
        super().__init__(**kwargs)
        self.frame_format = 'argb'

    def grab_frame(self, **savefig_kwargs):
        '''Grab the image information from the figure and save as a movie frame.

        Doesn't use savefig to be faster: savefig_kwargs will be ignored.
        '''
        try:
            # re-adjust the figure size and dpi in case it has been changed by the
            # user.  We must ensure that every frame is the same size or
            # the movie will not save correctly.
            self.fig.set_size_inches(self._w, self._h)
            self.fig.set_dpi(self.dpi)
            # Draw and save the frame as an argb string to the pipe sink
            self.fig.canvas.draw()
            self._frame_sink().write(self.fig.canvas.tostring_argb())
        except (RuntimeError, IOError) as e:
            out, err = self._proc.communicate()
            raise IOError('Error saving animation to file (cause: {0}) '
                      'Stdout: {1} StdError: {2}. It may help to re-run '
                      'with --verbose-debug.'.format(e, out, err))


class Graphs(object):
    def __init__(self, max_turn, graph_saving):
        self.time = 0
        self.max_turn = max_turn-1
        self.i = 0
        self.graph_save = graph_saving

        self.times = [i for i in range(max_turn - 1)]
        self.time_line = []

        self.FFwriter = FasterFFMpegWriter(fps=15)
        self.other_writer = FFMpegWriter(fps=15)


class MarketGraphs(Graphs):
    def __init__(self, max_turn, graph_save):
        Graphs.__init__(self, max_turn=max_turn, graph_saving=graph_save)

        # First set up the figure, the axis, and the plot element we want to animate
        self.fig, ((self.price_ax, self.volume_ax), (self.matches_ax, self.bid_ask_ax)) = plt.subplots(nrows=2, ncols=2)

        self.prices, self.matches, self.bids, self.asks, self.volumes = [], [], [], [], []
        self.price_line, self.matches_line, self.bid_line, self.ask_line, self.volume_line = [], [], [], [], []
        self.fig.tight_layout()

        self.line_1, = self.price_ax.plot(self.time_line, self.price_line, color='g')
        self.line_2, = self.matches_ax.plot(self.time_line, self.matches_line, color='r')
        self.line_3, = self.bid_ask_ax.plot(self.time_line, self.bid_line, color='b', lw=.5)
        self.line_4, = self.bid_ask_ax.plot(self.time_line, self.ask_line, color='k', lw=.5)
        self.line_5, = self.volume_ax.plot(self.time_line, self.volume_line, color='y')
        self.lines = [self.line_1, self.line_2, self.line_3, self.line_4, self.line_5]

    # per turn of the simulation, pass in the most updated version of the history
    def graph_data(self, curr_price, matches, bid, ask, volume):

        self.prices.append(curr_price)
        self.matches.append(matches)
        self.bids.append(bid)
        self.asks.append(ask)
        self.volumes.append(volume)
        self.time += 1
        self.plot_cont()

    def plot_cont(self):
        def frames():
            for self.i in range(self.max_turn):
                if self.i == self.max_turn:
                    break
                yield self.prices[self.i], self.matches[self.i], self.bids[self.i], self.asks[self.i], \
                      self.volumes[self.i], self.times[self.i]

        # initialization function: plot the background of each frame
        def init():
            self.lines[0].set_data([], [])
            self.lines[1].set_data([], [])
            self.lines[2].set_data([], [])
            self.lines[3].set_data([], [])
            return self.lines

        # animation function.  This is called sequentially
        def animate(*args):
            self.price_line.append(args[0][0])
            self.matches_line.append(args[0][1])
            self.bid_line.append(args[0][2])
            self.ask_line.append(args[0][3])
            self.volume_line.append(args[0][4])
            self.time_line.append(args[0][5])

            self.price_ax.clear()
            self.matches_ax.clear()
            self.bid_ask_ax.clear()
            self.volume_ax.clear()

            self.price_ax.title.set_text("Price History")
            self.matches_ax.title.set_text("Matches Made")
            self.bid_ask_ax.title.set_text('Bid vs Ask')
            self.volume_ax.title.set_text('Volume')
            self.lines[0], = self.price_ax.plot(self.time_line, self.price_line, color='g')
            self.lines[1], = self.matches_ax.plot(self.time_line, self.matches_line, color='r')
            self.lines[2], = self.bid_ask_ax.plot(self.time_line, self.bid_line, color='b', lw=.5)
            self.lines[3], = self.bid_ask_ax.plot(self.time_line, self.ask_line, color='m', lw=.5)
            self.lines[4], = self.volume_ax.plot(self.time_line, self.volume_line, color='y')

            self.i += 1
            return self.lines

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, animate, init_func=init,
                                       frames=frames, interval=200, save_count=self.max_turn, blit=True)
        if self.time == self.max_turn and self.graph_save:
            anim.save('Marketgraphs.mp4', writer=self.other_writer)


class MAGraphs(Graphs):
    def __init__(self, max_turn, name, graph_save):
        Graphs.__init__(self, max_turn=max_turn, graph_saving=graph_save)

        # First set up the figure, the axis, and the plot element we want to animate
        self.name = name

        self.fig, ((self.five, self.twenty), (self.hundred, self.five_hundred)) = plt.subplots(nrows=2, ncols=2)
        self.fig.tight_layout()

        self.five_ma, self.twenty_ma, self.hundred_ma, self.five_hundred_ma = [], [], [], []
        self.five_line, self.twenty_line, self.hundred_line, self.five_hundred_line = [], [], [], []

        self.line_1, = self.five.plot(self.time_line, self.five_line,  color='g')
        self.line_2, = self.twenty.plot(self.time_line, self.twenty_line,  color='r')
        self.line_3, = self.hundred.plot(self.time_line, self.hundred_line,  color='b')
        self.line_4, = self.five_hundred.plot(self.time_line, self.five_hundred_line, color='c')
        self.lines = [self.line_1, self.line_2, self.line_3, self.line_4]

    # per turn of the simulation, pass in the most updated version of the history
    def graph_data(self, values):
        self.five_ma.append(values['five_ma_val'])
        self.twenty_ma.append(values['twenty_ma_val'])
        self.hundred_ma.append(values['hundred_ma_val'])
        self.five_hundred_ma.append(values['five_hundred_ma_val'])

        self.time += 1
        self.plot_cont()

    def plot_cont(self):
        def frames():
            for self.i in range(self.max_turn):
                if self.i == self.max_turn:
                    break
                yield self.five_ma[self.i], self.twenty_ma[self.i], self.hundred_ma[self.i], self.five_hundred_ma[self.i]\
                    , self.times[self.i]

        # initialization function: plot the background of each frame
        def init():
            self.lines[0].set_data([], [])
            self.lines[1].set_data([], [])
            self.lines[2].set_data([], [])
            self.lines[3].set_data([], [])
            return self.lines

        # animation function.  This is called sequentially
        def animate(*args):
            self.five_line.append(args[0][0])
            self.twenty_line.append(args[0][1])
            self.hundred_line.append(args[0][2])
            self.five_hundred_line.append(args[0][3])
            self.time_line.append(args[0][4])
            self.five.clear()
            self.twenty.clear()
            self.hundred.clear()
            self.five_hundred.clear()

            self.lines[0], = self.five.plot(self.time_line, self.five_line,  color='g')
            self.lines[1], = self.twenty.plot(self.time_line, self.twenty_line,  color='r')
            self.lines[2], = self.hundred.plot(self.time_line, self.hundred_line,  color='b')
            self.lines[3], = self.five_hundred.plot(self.time_line, self.five_hundred_line, color='c')

            self.five.title.set_text("5 Day " + self.name + " Moving Average")
            self.twenty.title.set_text("20 Day " + self.name + " Moving Average")
            self.hundred.title.set_text("100 Day " + self.name + " Moving Average")
            self.five_hundred.title.set_text("500 Day " + self.name + " Moving Average")

            self.i += 1
            return self.lines

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, animate, init_func=init,
                                       frames=frames, interval=200, save_count=self.max_turn)

        if self.time == self.max_turn and self.graph_save:
            anim.save(self.name + '_MA_graphs.mp4', writer=self.FFwriter)


class AgentGraphs(Graphs):
    def __init__(self, max_turn, graph_save):
        Graphs.__init__(self, max_turn=max_turn, graph_saving=graph_save)

        # First set up the figure, the axis, and the plot element we want to animate
        self.fig, ((self.cash, self.pos), (self.profit, self.wealth)) = plt.subplots(nrows=2, ncols=2)
        self.fig.tight_layout()

        self.cash_history, self.pos_history, self.profit_history, self.wealth_history = [], [], [], []
        self.cash_line, self.pos_line, self.profit_line, self.wealth_line = [], [], [], []

        self.line_1, = self.cash.plot(self.time_line, self.cash_line,  color='g')
        self.line_2, = self.pos.plot(self.time_line, self.pos_line,  color='r')
        self.line_3, = self.profit.plot(self.time_line, self.profit_line, color='b')
        self.line_4, = self.wealth.plot(self.time_line, self.wealth_line, color='c')
        self.lines = [self.line_1, self.line_2, self.line_3, self.line_4]

    # per turn of the simulation, pass in the most updated version of the history
    def graph_data(self, values):
        self.cash_history.append(values['avg_cash'])
        self.pos_history.append(values['avg_pos'])
        self.profit_history.append(values['avg_profit'])
        self.wealth_history.append(values['avg_wealth'])

        self.time += 1
        self.plot_cont()

    def plot_cont(self):
        def frames():
            for self.i in range(self.max_turn):
                if self.i == self.max_turn:
                    break
                yield self.cash_history[self.i], self.pos_history[self.i], self.profit_history[self.i], self.wealth_history[self.i]\
                    , self.times[self.i]

        # initialization function: plot the background of each frame
        def init():
            self.lines[0].set_data([], [])
            self.lines[1].set_data([], [])
            self.lines[2].set_data([], [])
            self.lines[3].set_data([], [])
            return self.lines

        # animation function.  This is called sequentially
        def animate(*args):
            self.cash_line.append(args[0][0])
            self.pos_line.append(args[0][1])
            self.profit_line.append(args[0][2])
            self.wealth_line.append(args[0][3])
            self.time_line.append(args[0][4])

            self.cash.clear()
            self.pos.clear()
            self.profit.clear()
            self.wealth.clear()

            self.lines[0], = self.cash.plot(self.time_line, self.cash_line, color='g')
            self.lines[1], = self.pos.plot(self.time_line, self.pos_line,  color='r')
            self.lines[2], = self.profit.plot(self.time_line, self.profit_line,  color='b')
            self.lines[3], = self.wealth.plot(self.time_line, self.wealth_line,  color='c')

            self.cash.title.set_text("Average Trader Cash held")
            self.pos.title.set_text("Average Trader Position held")
            self.profit.title.set_text("Average Trader Profit")
            self.wealth.title.set_text("Average Trader Wealth")

            self.i += 1
            return self.lines

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, animate, init_func=init,
                                       frames=frames, interval=200, save_count=self.max_turn)
        plt.close(self.fig)
        if self.time == self.max_turn and self.graph_save:
            anim.save('agent_graphs.mp4', writer=self.FFwriter)


class AgentPerformance(Graphs):
    def __init__(self, max_turn, graph_save):
        Graphs.__init__(self, max_turn=max_turn, graph_saving=graph_save)

        # First set up the figure, the axis, and the plot element we want to animate\
        self.fig, self.ax = plt.subplots()

        self.good_performers, self.bad_performers = [], []
        self.good_line, self.bad_line, = [], []
        self.fig.tight_layout()

        self.line_1, = self.ax.plot(self.time_line, self.good_line, color='g', lw=.5)
        self.line_2, = self.ax.plot(self.time_line, self.bad_line, color='r', lw=.5)
        self.lines = [self.line_1, self.line_2]

        # per turn of the simulation, pass in the most updated version of the history

    def graph_data(self, values):
        self.good_performers.append(values['g_performers'])
        self.bad_performers.append(values['b_performers'])
        self.time += 1
        self.plot_cont()

    def plot_cont(self):
        def frames():
            for self.i in range(self.max_turn):
                if self.i == self.max_turn:
                    break
                yield self.good_performers[self.i], self.bad_performers[self.i], self.times[self.i]

        # initialization function: plot the background of each frame
        def init():
            self.lines[0].set_data([], [])
            self.lines[1].set_data([], [])
            return self.lines

        # animation function.  This is called sequentially
        def animate(*args):
            self.good_line.append(args[0][0])
            self.bad_line.append(args[0][1])
            self.time_line.append(args[0][2])

            self.ax.clear()

            self.ax.title.set_text("Good Performers")

            self.lines[0], = self.ax.plot(self.time_line, self.good_line, color='g')
            self.lines[1], = self.ax.plot(self.time_line, self.bad_line, color='r')

            self.i += 1
            return self.lines

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, animate, init_func=init,
                                       frames=frames, interval=200, save_count=self.max_turn, blit=True)
        if self.time == self.max_turn and self.graph_save:
            anim.save('Performers.mp4', writer=self.other_writer)


class InterestRate(Graphs):
    def __init__(self, max_turn, graph_save):
        Graphs.__init__(self, max_turn=max_turn, graph_saving=graph_save)

        # First set up the figure, the axis, and the plot element we want to animate
        self.fig, self.ax = plt.subplots()

        self.interest_rates = []
        self.interest_line = []
        self.fig.tight_layout()

        self.line_1, = self.ax.plot(self.time_line, self.interest_line, color='g')

    # per turn of the simulation, pass in the most updated version of the history
    def graph_data(self, interest):
        self.interest_rates.append(interest)
        self.time += 1
        self.plot_cont()

    def plot_cont(self):
        def frames():
            for self.i in range(self.max_turn):
                if self.i == self.max_turn:
                    break
                yield self.interest_rates[self.i], self.times[self.i]

        # initialization function: plot the background of each frame
        def init():
            self.line_1.set_data([], [])
            return self.line_1,

        # animation function.  This is called sequentially
        def animate(*args):
            self.interest_line.append(args[0][0])
            self.time_line.append(args[0][1])

            self.ax.clear()

            self.ax.title.set_text('Interest Rate')
            self.line_1, = self.ax.plot(self.time_line, self.interest_line, color='g')

            self.i += 1
            return self.line_1,

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, animate, init_func=init,
                                       frames=frames, interval=200, save_count=self.max_turn, blit=True)
        if self.time == self.max_turn and self.graph_save:
            anim.save('InterestGraphs.mp4', writer=self.other_writer)
