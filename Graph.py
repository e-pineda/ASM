import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
import matplotlib.animation as animation
plt.rcParams['axes.grid'] = True
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
    def __init__(self, max_turn, animated_graph_saving, image_graph_saving):
        self.time = 0
        self.max_turn = max_turn
        self.i = 0
        self.animated_graph_save = animated_graph_saving
        self.image_graph_save = image_graph_saving

        self.times = [i for i in range(max_turn)]
        self.time_line = []

        self.FFwriter = FasterFFMpegWriter(fps=15)
        self.other_writer = FFMpegWriter(fps=15)

    @staticmethod
    def save_animated_graph(animation, writer, name):
        print("\nCurrently saving:", name)
        animation.save(name, writer=writer)

    @staticmethod
    def save_image_graph(figure, name):
        figure.savefig(name)

    @staticmethod
    def init_animation(lines):
        for line in lines:
            line.set_data([], [])
        return lines

    @staticmethod
    def clear_axes(axes):
        for ax in axes:
            ax[0].clear()

    @staticmethod
    def set_title(axes):
        for ax in axes:
            ax[0].title.set_text(ax[1])

    @staticmethod
    def add_to_graph_line(graph_lines, args):
        for line, value in zip(graph_lines, args[0]):
            line.append(value)

    @staticmethod
    def plot_animated_data(axes, lines):
        for line in lines:
            for ax in axes:
                graph_lines = ax[2]
                time_line = ax[4]
                line_colors = ax[5]

                try:
                    line_width = ax[6]
                except:
                    line_width = 1

                for graph_line, line_color in zip(graph_lines, line_colors):
                    line, = ax[0].plot(time_line, graph_line, color=line_color, lw=line_width)
                continue

    @staticmethod
    def generate_static_plot(axes, line_amount, time_line):
        for i in range(line_amount):
            for ax in axes:
                graph_lines = ax[3]
                line_colors = ax[5]

                try:
                    line_width = ax[6]
                except:
                    line_width = 1

                for graph_line, line_color in zip(graph_lines, line_colors):
                    ax[0].plot(time_line, graph_line, color=line_color, lw=line_width)
                continue

    @staticmethod
    def record_graph_info(info_lists, values):
        for info_list, value in zip(info_lists, values):
            info_list.append(value)


class MarketGraphs(Graphs):
    def __init__(self, max_turn, animated_graph_save, image_graph_save):
        Graphs.__init__(self, max_turn=max_turn, animated_graph_saving=animated_graph_save, image_graph_saving=image_graph_save)

        # First set up the figure, the axis, and the plot element we want to animate
        self.fig, axes = plt.subplots(nrows=3, ncols=2)
        self.price_ax = axes[0][0]
        self.matches_ax = axes[0][1]
        self.volume_ax = axes[1][0]
        self.ppus_ax = axes[1][1]
        self.bid_ax = axes[2][0]
        self.ask_ax = axes[2][1]
        

        self.prices, self.matches, self.bids, self.asks, self.volumes, self.ppus = [], [], [], [], [], []
        self.price_line, self.matches_line, self.bid_line, self.ask_line, self.volume_line, self.profit_line = [], [], [], [], [], []
        self.fig.tight_layout()

        # In order: graph ax, ax name, animated graph line(excluding time_line), static graph lines, animated_time_line,
        # line colors, line width
        self.axes = [(self.price_ax, "Price History", [self.price_line], [self.prices], self.time_line, ['g']),
                     (self.matches_ax, 'Matches Made', [self.matches_line], [self.matches], self.time_line, ['r']),
                     (self.volume_ax, 'Volume', [self.volume_line], [self.volumes], self.time_line, ['y']),
                     (self.ppus_ax, 'Profit per Unit', [self.profit_line], [self.ppus], self.time_line, ['m']),
                     (self.bid_ax, 'Bid Prices', [self.bid_line], [self.bids], self.time_line, ['b']),
                     (self.ask_ax, 'Ask Prices', [self.ask_line], [self.asks], self.time_line, ['c'])]

        self.graph_lines = [self.price_line, self.matches_line, self.volume_line, self.profit_line, self.bid_line, self.ask_line,
                            self.time_line]
        self.info_lists = [self.prices, self.matches, self.volumes, self.ppus, self.bids, self.asks]

        self.line_1, = self.price_ax.plot(self.time_line, self.price_line, color='g')
        self.line_2, = self.matches_ax.plot(self.time_line, self.matches_line, color='r')
        self.line_3, = self.volume_ax.plot(self.time_line, self.volume_line, color='y')
        self.line_4, = self.ppus_ax.plot(self.time_line, self.profit_line, color='m')
        self.line_5, = self.bid_ax.plot(self.time_line, self.bid_line, color='b')
        self.line_6, = self.ask_ax.plot(self.time_line, self.ask_line, color='c')
        self.lines = [self.line_1, self.line_2, self.line_3, self.line_4, self.line_5, self.line_6]

    # record information to graph
    def record_info(self, curr_price, matches, volume, profit_unit, bid, ask):
        Graphs.record_graph_info(self.info_lists, [curr_price, matches, volume, profit_unit, bid, ask])
        self.time += 1

    def gen_static_plot (self):
        # Generate images
        Graphs.generate_static_plot(self.axes, len(self.graph_lines), self.times)
        Graphs.set_title(self.axes)

        # save graph if necessary
        if self.image_graph_save:
            Graphs.save_image_graph(figure=self.fig, name='Marketgraphs.png')

        # show graph
        self.fig.show()

    # per turn of the simulation, pass in the most updated version of the history
    def visualize(self):
        def frames():
            for self.i in range(self.max_turn):
                if self.i == self.max_turn:
                    break
                yield self.prices[self.i], self.matches[self.i], self.volumes[self.i], self.ppus[self.i], self.bids[self.i], \
                      self.asks[self.i], self.times[self.i]

        # initialization function: plot the background of each frame
        def init():
            return Graphs.init_animation(self.lines)

        # animation function.  This is called sequentially
        def animate(*args):
            # append to graph line
            Graphs.add_to_graph_line(self.graph_lines, args)

            # Clear axes and retitle
            Graphs.clear_axes(self.axes)
            Graphs.set_title(self.axes)

            # Plot data
            Graphs.plot_animated_data(self.axes, self.lines)

            self.i += 1
            return self.lines

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, animate, init_func=init,
                                       frames=frames, interval=200, save_count=self.max_turn, blit=True)

        if self.time == self.max_turn and self.animated_graph_save:
            Graphs.save_animated_graph(animation=anim, writer=self.other_writer, name='Marketgraphs.mp4')


class MAGraphs(Graphs):
    def __init__(self, max_turn, name, animated_graph_save, image_graph_save):
        Graphs.__init__(self, max_turn=max_turn, animated_graph_saving=animated_graph_save, image_graph_saving=image_graph_save)

        # First set up the figure, the axis, and the plot element we want to animate
        self.name = name

        self.fig, ((self.five, self.twenty), (self.hundred, self.five_hundred)) = plt.subplots(nrows=2, ncols=2)
        self.fig.tight_layout()
        

        self.five_ma, self.twenty_ma, self.hundred_ma, self.five_hundred_ma = [], [], [], []
        self.five_line, self.twenty_line, self.hundred_line, self.five_hundred_line = [], [], [], []

        self.axes = [(self.five, "5 Day "+self.name + " Moving Average", [self.five_line], [self.five_ma], self.time_line, ['g']),
                     (self.twenty, "20 Day " + self.name + " Moving Average", [self.twenty_line], [self.twenty_ma], self.time_line, ['r']),
                     (self.hundred, "100 Day " + self.name + " Moving Average", [self.hundred_line], [self.hundred_ma], self.time_line, ['b']),
                     (self.five_hundred, "500 Day " + self.name + " Moving Average", [self.five_hundred_line], [self.five_hundred_ma], self.time_line, ['c'])]

        self.graph_lines = [self.five_line, self.twenty_line, self.hundred_line, self.five_hundred_line, self.time_line]
        self.info_lists = [self.five_ma, self.twenty_ma, self.hundred_ma, self.five_hundred_ma]

        self.line_1, = self.five.plot(self.time_line, self.five_line,  color='g')
        self.line_2, = self.twenty.plot(self.time_line, self.twenty_line,  color='r')
        self.line_3, = self.hundred.plot(self.time_line, self.hundred_line,  color='b')
        self.line_4, = self.five_hundred.plot(self.time_line, self.five_hundred_line, color='c')
        self.lines = [self.line_1, self.line_2, self.line_3, self.line_4]

    def record_info(self, values):
        Graphs.record_graph_info(self.info_lists, [values['five_ma_val'], values['twenty_ma_val'],
                                                   values['hundred_ma_val'], values['five_hundred_ma_val']])
        self.time += 1

    def gen_static_plot(self):
        # Generate images
        Graphs.generate_static_plot(self.axes, len(self.graph_lines), self.times)
        Graphs.set_title(self.axes)

        # save graph if necessary
        if self.image_graph_save:
            Graphs.save_image_graph(figure=self.fig, name=self.name + '_MA_graph.png')

        # show graph
        self.fig.show()

    # per turn of the simulation, pass in the most updated version of the history
    def visualize(self):
        def frames():
            for self.i in range(self.max_turn):
                if self.i == self.max_turn:
                    break
                yield self.five_ma[self.i], self.twenty_ma[self.i], self.hundred_ma[self.i], self.five_hundred_ma[self.i]\
                    , self.times[self.i]

        # initialization function: plot the background of each frame
        def init():
            return Graphs.init_animation(self.lines)

        # animation function.  This is called sequentially
        def animate(*args):
            # append to graph line
            Graphs.add_to_graph_line(self.graph_lines, args)

            # Clear axes and retitle
            Graphs.clear_axes(self.axes)
            Graphs.set_title(self.axes)

            # Plot data
            Graphs.plot_animated_data(self.axes, self.lines)

            self.i += 1
            return self.lines

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, animate, init_func=init,
                                       frames=frames, interval=200, save_count=self.max_turn)

        if self.time == self.max_turn and self.animated_graph_save:
            Graphs.save_animated_graph(animation=anim, writer=self.FFwriter, name=self.name + '_MA_graphs.mp4')


class AgentGraphs(Graphs):
    def __init__(self, max_turn, animated_graph_save, image_graph_save):
        Graphs.__init__(self, max_turn=max_turn, animated_graph_saving=animated_graph_save, image_graph_saving=image_graph_save)

        # First set up the figure, the axis, and the plot element we want to animate
        self.fig, ((self.cash, self.pos), (self.profit, self.wealth)) = plt.subplots(nrows=2, ncols=2)
        self.fig.tight_layout()
        

        self.cash_history, self.pos_history, self.profit_history, self.wealth_history = [], [], [], []
        self.cash_line, self.pos_line, self.profit_line, self.wealth_line = [], [], [], []

        self.axes = [(self.cash, "Average Trader Cash held", [self.cash_line], [self.cash_history], self.time_line, ['g']),
                     (self.pos, "Average Trader Position held", [self.pos_line], [self.pos_history], self.time_line, ['r']),
                     (self.profit, "Average Trader Profit", [self.profit_line], [self.profit_history], self.time_line, ['b']),
                     (self.wealth, "Average Trader Wealth", [self.wealth_line], [self.wealth_history], self.time_line, ['c'])]

        self.info_lists = [self.cash_history, self.pos_history, self.profit_history, self.wealth_history]
        self.graph_lines = [self.cash_line, self.pos_line, self.profit_line, self.wealth_line, self.time_line]

        self.line_1, = self.cash.plot(self.time_line, self.cash_line,  color='g')
        self.line_2, = self.pos.plot(self.time_line, self.pos_line,  color='r')
        self.line_3, = self.profit.plot(self.time_line, self.profit_line, color='b')
        self.line_4, = self.wealth.plot(self.time_line, self.wealth_line, color='c')
        self.lines = [self.line_1, self.line_2, self.line_3, self.line_4]

    def record_info(self, values):
        Graphs.record_graph_info(self.info_lists, [values['avg_cash'], values['avg_pos'], values['avg_profit'], values['avg_wealth']])
        self.time += 1

    def gen_static_plot(self):
        # Generate images
        Graphs.generate_static_plot(self.axes, len(self.graph_lines), self.times)
        Graphs.set_title(self.axes)

        # save graph if necessary
        if self.image_graph_save:
            Graphs.save_image_graph(figure=self.fig, name='Agent_graph.png')

        # show graph
        self.fig.show()

    # per turn of the simulation, pass in the most updated version of the history
    def visualize(self):
        def frames():
            for self.i in range(self.max_turn):
                if self.i == self.max_turn:
                    break
                yield self.cash_history[self.i], self.pos_history[self.i], self.profit_history[self.i], \
                      self.wealth_history[self.i], self.times[self.i]

        # initialization function: plot the background of each frame
        def init():
            return Graphs.init_animation(self.lines)

        # animation function.  This is called sequentially
        def animate(*args):
            # append to graph line
            Graphs.add_to_graph_line(self.graph_lines, args)

            # Clear axes and retitle
            Graphs.clear_axes(self.axes)
            Graphs.set_title(self.axes)

            # Plot data
            Graphs.plot_animated_data(self.axes, self.lines)

            self.i += 1
            return self.lines

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, animate, init_func=init,
                                       frames=frames, interval=200, save_count=self.max_turn)
        plt.close(self.fig)
        if self.time == self.max_turn and self.animated_graph_save:
            Graphs.save_animated_graph(animation=anim, writer=self.FFwriter, name='agent_graphs.mp4')


class AgentPerformance(Graphs):
    def __init__(self, max_turn, animated_graph_save, image_graph_save):
        Graphs.__init__(self, max_turn=max_turn, animated_graph_saving=animated_graph_save, image_graph_saving=image_graph_save)

        # First set up the figure, the axis, and the plot element we want to animate\
        self.fig, self.ax = plt.subplots(3, 1)
        self.performances_ax = self.ax[0]
        self.agents_learned_ax = self.ax[1]
        self.mistakes_ax = self.ax[2]

        self.good_performers, self.bad_performers, self.agents_learned, self.mistakes_amount = [], [], [], []
        self.good_line, self.bad_line, self.learned_line, self.mistakes_line = [], [], [], []
        self.fig.tight_layout()
        self.axes = [(self.performances_ax, "Good vs Bad Performers", [self.good_line, self.bad_line], [self.good_performers, self.bad_performers],
                     self.time_line, ['g', 'r'], .5),
                     (self.agents_learned_ax, 'Amount of Agents that learned', [self.learned_line], [self.agents_learned], self.time_line, ['b']),
                     (self.mistakes_ax, 'Amount of Mistakes made', [self.mistakes_line], [self.mistakes_amount], self.time_line, ['c'])]

        self.info_lists = [self.good_performers, self.bad_performers, self.agents_learned, self.mistakes_amount]
        self.graph_lines = [self.good_line, self.bad_line, self.learned_line, self.mistakes_amount, self.time_line]

        self.line_1, = self.performances_ax.plot(self.time_line, self.good_line, color='g', lw=.5)
        self.line_2, = self.performances_ax.plot(self.time_line, self.bad_line, color='r', lw=.5)
        self.line_3, = self.agents_learned_ax.plot(self.time_line, self.learned_line, color='b')
        self.line_4, = self.mistakes_ax.plot(self.time_line, self.mistakes_line, color='r', lw=.5)
        self.lines = [self.line_1, self.line_2, self.line_3, self.line_4]

        # per turn of the simulation, pass in the most updated version of the history

    def record_info(self, values):
        Graphs.record_graph_info(self.info_lists, [values['g_performers'], values['b_performers'], values['agents_learned'],
                                                   values['mistakes_made']])
        self.time += 1

    def gen_static_plot(self):
        # Generate images
        Graphs.generate_static_plot(self.axes, len(self.graph_lines), self.times)
        Graphs.set_title(self.axes)

        # save graph if necessary
        if self.image_graph_save:
            Graphs.save_image_graph(figure=self.fig, name='Performances.png')

        # show graph
        self.fig.show()

    def visualize(self):
        def frames():
            for self.i in range(self.max_turn):
                if self.i == self.max_turn:
                    break
                yield self.good_performers[self.i], self.bad_performers[self.i], self.agents_learned[self.i], \
                      self.mistakes_amount[self.i], self.times[self.i]

        # initialization function: plot the background of each frame
        def init():
            return Graphs.init_animation(self.lines)

        # animation function.  This is called sequentially
        def animate(*args):
            # append to graph line
            Graphs.add_to_graph_line(self.graph_lines, args)

            # Clear axes and retitle
            Graphs.clear_axes(self.axes)
            Graphs.set_title(self.axes)

            # Plot data
            Graphs.plot_animated_data(self.axes, self.lines)

            self.i += 1
            return self.lines

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, animate, init_func=init,
                                       frames=frames, interval=200, save_count=self.max_turn, blit=True)
        if self.time == self.max_turn and self.animated_graph_save:
            Graphs.save_animated_graph(animation=anim, writer=self.other_writer, name='Performers.mp4')


class InterestRate(Graphs):
    def __init__(self, max_turn, animated_graph_save, image_graph_save):
        Graphs.__init__(self, max_turn=max_turn, animated_graph_saving=animated_graph_save, image_graph_saving=image_graph_save)

        # First set up the figure, the axis, and the plot element we want to animate
        self.fig, self.ax = plt.subplots()

        self.interest_rates = []
        self.interest_line = []
        self.fig.tight_layout()

        self.axes = [(self.ax, 'Interest Rate', [self.interest_line], [self.interest_rates], self.time_line, ['g'])]

        self.info_lists = [self.interest_rates]
        self.graph_lines = [self.interest_line, self.time_line]

        self.line_1, = self.ax.plot(self.time_line, self.interest_line, color='g')
        self.lines = [self.line_1]

    def record_info(self, interest):
        Graphs.record_graph_info(self.info_lists, [interest])
        self.time += 1

    def gen_static_plot(self):
        # Generate images
        Graphs.generate_static_plot(self.axes, len(self.graph_lines), self.times)
        Graphs.set_title(self.axes)

        # save graph if necessary
        if self.image_graph_save:
            Graphs.save_image_graph(figure=self.fig, name='Performances.png')

        # show graph
        self.fig.show()

    # per turn of the simulation, pass in the most updated version of the history
    def visualize(self):
        def frames():
            for self.i in range(self.max_turn):
                if self.i == self.max_turn:
                    break
                yield self.interest_rates[self.i], self.times[self.i]

        # initialization function: plot the background of each frame
        def init():
            return Graphs.init_animation(self.lines)

        # animation function.  This is called sequentially
        def animate(*args):
            # append to graph line
            Graphs.add_to_graph_line(self.graph_lines, args)

            # Clear axes and retitle
            Graphs.clear_axes(self.axes)
            Graphs.set_title(self.axes)

            # Plot data
            Graphs.plot_animated_data(self.axes, self.lines)

            self.i += 1
            return self.lines

        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, animate, init_func=init,
                                       frames=frames, interval=200, save_count=self.max_turn, blit=True)
        if self.time == self.max_turn and self.animated_graph_save:
            Graphs.save_animated_graph(animation=anim, writer=self.other_writer, name='InterestGraphs.mp4')



def generate_animated_graphs(graphs):
    for graph in graphs:
        graph.visualize()


def generate_static_graphs(graphs):
    for graph in graphs:
        graph.gen_static_plot()
