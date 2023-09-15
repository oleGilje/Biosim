# -*- coding: utf-8 -*-
"""
Graphics used in biosim.

File is based on code found in the "randvis" project by Hans Ekkard Plesser
"""

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os

_FFMPEG_BINARY = 'ffmpeg'
_MAGICK_BINARY = 'magick'


_DEFAULT_GRAPHICS_DIR = os.path.join('..', 'data')
_DEFAULT_GRAPHICS_NAME = 'dv'
_DEFAULT_IMG_FORMAT = 'png'
_DEFAULT_MOVIE_FORMAT = 'mp4'

class Graphics:
    """Provides graphics support for Biosim."""
    def __init__(self, hist_specs, img_fmt=None, ymax_animals=None,
                 cmax_animals=None, img_years=None, img_dir=None, img_base=None):
        """
        :param hist_specs: dictionary of histograms specifications
        :type hist_specs: dict
        :param img_name: beginning of name for image files
        :type img_name: str
        :param img_fmt: image file format suffix
        :type img_fmt: str
        :param ymax_animals: Number specifying y-axis limit for graph showing animal numbers
        :type ymax_animals: int
        :param cmax_animals: dictionary containing values for color scale used in _map_herb_ax
        and _map_carn_ax
        :type cmax_animals: dict
        :param img_years: years between visualizations saved to files (default: vis_years)
        :type img_years: int
        :param img_dir: directory for image files; no images if None
        :type img_dir: str
        :param img_base: String with beginning of file name for figures
        :type img_base: str
        """
        if img_dir is None:
            self._img_dir = _DEFAULT_GRAPHICS_DIR
        else:
            self._img_dir = img_dir
        if img_dir is not None:
            self._img_base = os.path.join(self._img_dir, img_base)
        else:
            self._img_base = img_base
        self._img_fmt = img_fmt if img_fmt is not None else _DEFAULT_IMG_FORMAT
        if hist_specs is None:
            self._hist_specs = {"fitness": {"max": 1.0, "delta": 0.1},
                                "age": {"max": 40.0, "delta": 2.0},
                                "weight": {"max": 40.0, "delta": 2.0}}
        else:
            self._hist_specs = hist_specs

        self._cmax_animals = cmax_animals if cmax_animals is not None else {"Herbivore": 50,
                                                                            "Carnivore": 20}
        self._ymax_animals = ymax_animals
        self._img_years = img_years if img_years is not None else 1
        self._img_ctr = 0
        self._img_step = 1
        self._template = '{:5d}'

        self._fig = None
        self._map_of_island_ax = None
        self._yearcount_ax = None
        self._animal_line_count_ax = None
        self._herbivore_line = None
        self._carnivore_line = None
        self._animal_migration_ax = None
        self._hist_fitness_ax = None
        self._hist_age_ax = None
        self._hist_weight_ax = None
        self._migration_herb_ax = None
        self._migration_carn_ax = None


    def get_bins(self, stat):
        """
        :param stat: age, weight or fitness stat
        :type stat: float or int
        :return: number of bins
        :rtype: int
        """
        return int(self._hist_specs[stat]['max'] / self._hist_specs[stat]['delta'])

    def setup(self, final_step, island_map):
        """
        Prepare graphics.

        Call this before calling :meth:`update()` for the first time after
        the final time step has changed.

        :param final_step: last time step to be visualised (upper limit of x-axis)
        :param island_map: map of the island
        """
        self._island_map_string = island_map

        if self._fig is None:
            self._fig = plt.figure()

        if self._map_of_island_ax is None:
            self._map_of_island_ax = self._fig.add_axes([0.07, 0.60, 0.25, 0.25])
            self._map_of_island_ax.set_title('Island')
            self._plot_island()

        if self._yearcount_ax is None:
            self._yearcount_ax = self._fig.add_axes([0.46, 0.31, 0.08, 0.08])
            self._yearcount_ax.set_title('Year')
            self._yearcount_ax.axis('off')
            self._year_text = self._yearcount_ax.text(0.5, 0.5,
                                                      self._template.format(0),
                                                      fontsize=15,
                                                      horizontalalignment='center',
                                                      verticalalignment='center',
                                                      transform=self._yearcount_ax.transAxes)


        if self._animal_line_count_ax is None:
            self._animal_line_count_ax = self._fig.add_axes([0.65, 0.60, 0.25, 0.25])
            self._animal_line_count_ax.set_title('Total animals on island')

            if self._animal_line_count_ax is not None:
                self._animal_line_count_ax.set_ylim(0, self._ymax_animals)
            self._animal_line_count_ax.set_xlim(0, 300)


        if self._hist_fitness_ax is None:
            self._hist_fitness_ax = self._fig.add_axes([0.10, 0.05, 0.20, 0.1])
            self._hist_fitness_ax.set_title('Fitness')

        if self._hist_age_ax is None:
            self._hist_age_ax = self._fig.add_axes([0.40, 0.05, 0.20, 0.1])
            self._hist_age_ax.set_title('Age')

        if self._hist_weight_ax is None:
            self._hist_weight_ax = self._fig.add_axes([0.75, 0.05, 0.20, 0.1])
            self._hist_weight_ax.set_title('Weight')

        if self._migration_herb_ax is None:
            self._migration_herb_ax = self._fig.add_axes([0.10, 0.25, 0.22, 0.22])
            self._migration_herb_ax.axis('off')
            self._migration_herb_ax.set_title("Herbivore Density")
            self._img_herb_axis = None

        if self._migration_carn_ax is None:
            self._migration_carn_ax = self._fig.add_axes([0.68, 0.25, 0.22, 0.22])
            self._migration_carn_ax.axis('off')
            self._migration_carn_ax.set_title("Carnivore Density")
            self._img_carn_axis = None


        if self._herbivore_line is None:
            herbivore_line_plot = self._animal_line_count_ax.plot(np.arange(0, final_step + 1),
                                                                  np.full(final_step + 1, np.nan),
                                                                  'g-')
            self._herbivore_line = herbivore_line_plot[0]
        else:
            x_data_herb, y_data_herb = self._herbivore_line.get_data()
            x_new_herb = np.arange(x_data_herb[-1] + 1, final_step + 1)
            if len(x_new_herb) > 0:
                y_new_herb = np.full(x_new_herb.shape, np.nan)
                self._herbivore_line.set_data(np.hstack((x_data_herb, x_new_herb),
                                                        (y_data_herb, y_new_herb)))

        # Setup for carnivore line
        if self._carnivore_line is None:
            carnivore_line_plot = self._animal_line_count_ax.plot(np.arange(0, final_step + 1),
                                                                  np.full(final_step + 1, np.nan),
                                                                  'r-')
            self._carnivore_line = carnivore_line_plot[0]
        else:
            x_data_carn, y_data_carn = self._carnivore_line.get_data()
            x_new_carn = np.arange(x_data_carn[-1] + 1, final_step + 1)
            if len(x_new_carn) > 0:
                y_new_carn = np.full(x_new_carn.shape, np.nan)
                self._carnivore_line.set_data(np.hstack((x_data_carn, x_new_carn),
                                                        (y_data_carn, y_new_carn)))

        # Legend:
        self._animal_line_count_ax.legend([self._herbivore_line, self._carnivore_line],
                                          ["Herbivore", "Carnivore"],
                                          fontsize=8)

        self._plt_fig_title = self._fig.add_axes([0.28, 0.85, 0.5, 0.2])  # llx, lly, w, h
        self._plt_fig_title.axis('off')
        self._plt_fig_title_txt = self._plt_fig_title.text(0.5, 0.5, self._template.format(0),
                                                           horizontalalignment='center',
                                                           verticalalignment='center',
                                                           transform=self._plt_fig_title.transAxes,
                                                           fontsize=8,
                                                           fontweight='bold')
        self._plt_fig_title_txt.set_text("BioSim June 2022 Group 19"
                                         "\n Herman Ellingsen and Ole Gilje Gunnarshaug")

    def update(self, year, total_herbivores, total_carnivores,
               map_herbs, map_carns, dicto_hist_herb, dicto_hist_can):
        """
        :param year: year of simulation
        :tyoe year: int
        :param total_herbivores: amount of herbivores on island
        :type total_herbivores: int
        :param total_carnivores: amount of carnivores on island
        :type total_carnivores: int
        :param map_herbs: numpy array showing how many herbivore are in each cell
        :type map_herbs: numpy array
        :param map_carns: numpy array showing how many carnivore are in each cell
        :type map_carn: numpy array
        :param dicto_hist_herb: dictionary containing information for histograms for herbivores
        :type dicto_hist_herb: dict
        :param dicto_hist_carn: dictionary containing information for histograms for carnivores
        :type dicto_hist_carn: dict
        """
        self._update_year_count(year)
        self._update_total_animals(year, total_herbivores, total_carnivores)
        self._update_system_map(map_herbs, map_carns)
        self._fig.canvas.flush_events()
        self._update_age_ax(dicto_hist_herb["age"], dicto_hist_can["age"])
        self._update_weight_ax(dicto_hist_herb["weight"], dicto_hist_can["weight"])
        self._update_fitness_ax(dicto_hist_herb["fitness"], dicto_hist_can["fitness"])
        plt.pause(1e-6)  # 1e-6

        if year % self._img_years == 0:
            self._save_graphics(year)


    def _update_age_ax(self, herb_age, carn_age):
        """
        Updates histogram for age

        :param herb_age: list of all herbivore ages
        :type: herb_age: list
        :param carn_age: list of all herbivore ages
        :type: carn_age: list
        """
        self._hist_age_ax.clear()
        self._hist_age_ax.set_title('Age')
        age_bins = self.get_bins('age')
        self._hist_age_ax.hist((herb_age, carn_age), bins=age_bins,
                               range=(0, self._hist_specs['age']['max']),
                               histtype='step', color=('g', "r"), lw=2)

    def _update_weight_ax(self, herb_weight, carn_weight):
        """
        Updates histogram for weight

        :param herb_weight: list of all herbivore weights
        :tyoe herb_weight: list
        :param carn_weight: list of all carnivore weight
        :type carn_weight: list
        """
        self._hist_weight_ax.clear()
        self._hist_weight_ax.set_title('Weight')
        weight_bins = self.get_bins('weight')
        self._hist_weight_ax.hist((herb_weight, carn_weight), bins=weight_bins,
                                  range=(0, self._hist_specs['weight']['max']),
                                  histtype='step', color=('g', "r"), lw=2)

    def _update_fitness_ax(self, herb_fitness, carn_fitness):
        """
        Updates histogram for fitness

        :param herb_fitness: list of all herbivore fitnesses
        :type: herb_fitness: list
        :param carn_fitness: list of all carnivore fitnesses
        :type: carn_fitness: list
        """
        self._hist_fitness_ax.clear()
        self._hist_fitness_ax.set_title('Fitness')
        fitness_bins = self.get_bins('fitness')
        self._hist_fitness_ax.hist((herb_fitness, carn_fitness), bins=fitness_bins,
                                   range=(0, self._hist_specs['fitness']['max']),
                                   histtype='step', color=('g', "r"), lw=2)

    def _update_total_animals(self, year, herbivores, carnivores):
        """
        Updates line plot for Herbivore and Carnivore

        :param year: year in plot
        :type year: int
        :param herbivores: amount of herbivores in given year
        :type herbivores: int
        :param carnivores: amount of carnivores in given year
        :type carnivores: int
        """
        y_data_herb = self._herbivore_line.get_ydata()
        y_data_herb[year] = herbivores
        self._herbivore_line.set_ydata(y_data_herb)

        y_data_carn = self._carnivore_line.get_ydata()
        y_data_carn[year] = carnivores
        self._carnivore_line.set_ydata(y_data_carn)

        # Updates y_axis automatically if _ymax_animals is not set
        if self._ymax_animals is None:
            y_data_herb[0] = 1
            self._animal_line_count_ax.set_ylim(0, max(y_data_herb)+(max(y_data_herb)*0.20))

    def _update_year_count(self, year):
        """
        Updates year count in _fig

        :param year: year in simulation
        :type year: int
        """
        self._year_text.set_text(self._template.format(year))

    def _plot_island(self):
        """
        Plots island map in _fig
        """
        #                   R    G    B
        rgb_value = {'W': (0.0, 0.0, 1.0),  # blue
                     'L': (0.0, 0.6, 0.0),  # dark green
                     'H': (0.5, 1.0, 0.5),  # light green
                     'D': (1.0, 1.0, 0.5)}  # light yellow

        map_rgb = [[rgb_value[column] for column in row] for row in
                   self._island_map_string.splitlines()]

        self._map_of_island_ax.imshow(map_rgb)

        # Make sure that ticks don't sit on top of each other
        if len(map_rgb[0]) < 10:
            range_number_xticks = 1
        elif 10 < len(map_rgb[0]) < 20:
            range_number_xticks = 2
        else:
            range_number_xticks = 3

        # Make sure that ticks don't sit on top of each other
        if len(map_rgb) < 10:
            range_number_yticks = 1
        elif 10 < len(map_rgb) < 20:
            range_number_yticks = 2
        else:
            range_number_yticks = 3

        self._map_of_island_ax.set_xticks(range(len(map_rgb[0]))[::range_number_xticks])
        self._map_of_island_ax.set_xticklabels(range(1, 1 + len(map_rgb[0]))[::range_number_xticks])
        self._map_of_island_ax.set_yticks(range(len(map_rgb))[::range_number_yticks])
        self._map_of_island_ax.set_yticklabels(range(1, 1 + len(map_rgb))[::range_number_yticks])

        # Adjusts the legend_ax for island_plot according to width
        if len(map_rgb[0]) < 20:
            length = 0.3
        elif 20 < len(map_rgb[0]) < 30:
            length = 0.35
        else:
            length = 0.40

        ax_map_legend = self._fig.add_axes([length, 0.63, 0.08, 0.3])
        ax_map_legend.axis('off')
        for ix, name in enumerate(('Water', 'Lowland',
                                   'Highland', 'Desert')):
            if ix > 1:
                text_color = 'Black'
            else:
                text_color = 'White'
            ax_map_legend.add_patch(plt.Rectangle((0., ix * 0.2), 1.5, 0.1,
                                          edgecolor='none',
                                          facecolor=rgb_value[name[0]]))
            ax_map_legend.text(0., ix * 0.2, name, transform=ax_map_legend.transAxes,
                       color=text_color, fontsize=7, fontweight='bold')

    def _update_system_map(self, map_herbs, map_carns):
        """
        Update the 2D-view of the system.

        :param map_herbs: numpy array showing how many herbivore are in each cell
        :type map_herbs: numpy array
        :param map_carns: numpy array showing how many carnivore are in each cell
        :type map_carns: numpy array
        """
        map_herb = np.transpose(map_herbs)
        if self._img_herb_axis is not None:
            self._img_herb_axis.set_data(map_herb)
        else:
            self._img_herb_axis = self._migration_herb_ax.imshow(map_herb,
                                                                 interpolation='nearest',
                                                                 vmin=0,
                                                                 vmax=self._cmax_animals["Herbivore"],
                                                                 cmap='Greens')
            plt.colorbar(self._img_herb_axis, ax=self._migration_herb_ax,
                         orientation='horizontal')

        map_carn = np.transpose(map_carns)
        if self._img_carn_axis is not None:
            self._img_carn_axis.set_data(map_carn)

        else:
            self._img_carn_axis = self._migration_carn_ax.imshow(map_carn,
                                                                 interpolation='nearest',
                                                                 vmin=0,
                                                                 vmax=self._cmax_animals["Carnivore"],
                                                                 cmap='Reds')
            plt.colorbar(self._img_carn_axis, ax=self._migration_carn_ax,
                         orientation='horizontal')

    def _save_graphics(self, step):
        """
        Saves graphics to file if file name given.

        :param step: step/year in simulation
        :type step: int
        """
        if self._img_base is None or step % self._img_step != 0:
            return

        plt.savefig(f'{os.path.join(self._img_base)}_{step:05d}.{self._img_fmt}')
        self._img_ctr += 1

    def make_movie(self, movie_fmt="mp4"):
        """
        Creates MPEG4 movie from visualization images saved.

        .. :note:
            Requires ffmpeg for MP4 and magick for GIF

        The movie is stored as img_base + movie_fmt

        :param movie_fmt: format for movie
        :type movie_fmt: str
        """

        if self._img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt is None:
            movie_fmt = _DEFAULT_MOVIE_FORMAT

        if movie_fmt == 'mp4':
            try:
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', '{}_%05d.png'.format(self._img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self._img_base),
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: convert failed with: {}'.format(err))
        else:
            raise ValueError('Unknown movie format: ' + movie_fmt)



