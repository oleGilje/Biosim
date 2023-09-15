# -*- coding: utf-8 -*-
"""
BioSim class. Based on template provided by Hans Ekkard Plesser in INF200 2022.
"""
__author__ = 'Herman Ellingsen, Ole Gilje Gunnarshaug'
__email__ = 'hermane@nmbu.no, ole.gilje.gunnarshaug@nmbu.no'

from .animal import Herbivore, Carnivore
from .island import Island
from .cell import Water, Lowland, Highland, Desert
from .graphics import Graphics
import random
import numpy as np
import csv

species_population = {'Herbivore': Herbivore, "Carnivore": Carnivore}
landscapes_types = {'L': Lowland, 'H': Highland,
                    'W': Water, 'D': Desert}


class BioSim:
    """
    Biosim class
    """
    def __init__(self,
                 island_map=None,
                 ini_pop=None,
                 seed=None,
                 vis_years=None,
                 ymax_animals=None,
                 cmax_animals=None,
                 hist_specs=None,
                 img_dir=None,
                 img_base=None,
                 img_fmt=None,
                 img_years=None,
                 log_file=None):
        """
               :param island_map: Multi-line string specifying island geography
               :param ini_pop: List of dictionaries specifying initial population
               :param seed: Integer used as random number seed
               :param ymax_animals: Number specifying y-axis limit for graph showing animal numbers
               :param cmax_animals: Dict specifying color-code limits for animal densities
               :param hist_specs: Specifications for histograms, see below
               :param vis_years: years between visualization updates (if 0, disable graphics)
               :param img_dir: String with path to directory for figures
               :param img_base: String with beginning of file name for figures
               :param img_fmt: String with file type for figures, e.g. 'png'
               :param img_years: years between visualizations saved to files (default: vis_years)
               :param log_file: If given, write animal counts to this file

                Sjekk ut dette:
               If img_dir is None, no figures are written to file. Filenames are formed as
                   f'{os.path.join(img_dir, img_base}_{img_number:05d}.{img_fmt}'
               where img_number are consecutive image numbers starting from 0.
               img_dir and img_base must either be both None or both strings.
               """
        if seed is None:
            seed = 12
        random.seed(seed)

        self._year = 0
        self._num_animals = 0
        Herbivore.animal_count = 0
        Carnivore.animal_count = 0
        self._population_history = {}
        self.log_file = log_file

        if self.check_map(island_map):
            self.island_map = island_map
        self.ini_cells()

        if ini_pop:
            self.add_population(ini_pop)
        self.create_array()

        if vis_years != 0:
            self.vis_years = vis_years

            self.graph = Graphics(
                                  hist_specs=hist_specs,
                                  img_fmt=img_fmt,
                                  ymax_animals=ymax_animals,
                                  cmax_animals=cmax_animals,
                                  img_years=img_years,
                                  img_dir=img_dir,
                                  img_base=img_base)
            self.graph.setup(400,
                             self.island_map)
        else:
            self.vis_years = vis_years
            self.graph = None

    @staticmethod
    def set_animal_parameters(species, params):
        """
        Set parameters for animal species.

        :param species: String, name of animal species
        :param params: Dict with valid parameter specification for species
        """
        species_population[species].set_params(params)

    @staticmethod
    def set_landscape_parameters(cell_type, parameters):
        """
        Set parameters for landscape type.

        :param landscape: String, code letter for landscape
        :param params: Dict with valid parameter specification for landscape
        """
        if cell_type not in ["W", "L", "H", "D"]:
            raise ValueError("No cell type:", cell_type)
        else:
            landscapes_types[cell_type].set_attr(parameters)

    def ini_cells(self):
        """
        Initialize cells from map.
        """
        self.cells = Island.make_map(self.island_map)

    def create_array(self):
        """
        Create array for herbivores and carnivores to be used to track amount in each cell.
        """
        n_columns = len(self.island_map.split()[0])
        n_rows = len(self.island_map.split())
        self.herb_array = np.zeros(shape=(n_columns, n_rows))
        self.carn_array = np.zeros(shape=(n_columns, n_rows))

    @staticmethod
    def check_map(map):
        """
        This method makes the following checks, to make sure map is in right format:
        -That map is not empty
        -That map only contains approved landtypes, which is ["W", "L", "H", "D"]
        -That all rows have equal length
        -That all borders is of landtype "W"

        :param map: string containing letters that make up the map
        :type map: str
        :return: True, if no errors are raised
        :rtype: bool
        """
        if not map:
            raise ValueError("Landscape string cannot be empty")

        landscape_cells = [landscape_type for line in map.split() for landscape_type in line]
        if not all(landscape_type in ["W", "L", "H", "D"] for landscape_type in landscape_cells):
            raise ValueError("Landscape string cannot be empty, and can only contain:")

        length_of_rows = [len(line) for line in map.split()]
        row_length = length_of_rows[0] - 1

        if not all(len(line) == length_of_rows[0] for line in map.split()):
            raise ValueError("Rows must have equal length")

        for n, line in enumerate(map.split()):
            if line[0] and line[row_length] != "W":
                raise ValueError("Not water")
            if n == 0 and not all(l == "W" for l in line):
                raise ValueError("Not Water")
            if n == len(map.split()) - 1 and not all(l == "W" for l in line):
                raise ValueError("Not Water")
        return True

    def assign_herbs_and_carns_in_array(self):
        """
        Function assigns herbivores and carnivores into numpy array to show how many of each
        species are in each cell.
        """
        for coord in self.cells:
            self.herb_array[coord[0]-1][coord[1]-1] = len(self.cells[coord].herbivore)
            self.carn_array[coord[0]-1][coord[1]-1] = len(self.cells[coord].carnivore)

    def simulate(self, num_years):
        """
        Run simulation while visualizing the result.

        :param num_years: number of years to simulate
        :type num_years: int
        """
        for n in range(num_years):

            dicto_hist_herb = {"age": [],
                          "weight": [],
                          "fitness": []}

            dicto_hist_can = {"age": [],
                          "weight": [],
                          "fitness": []}

            Island.yearly_cycle_phase_1(self)

            Island.migration_herbivores(self)
            Island.migration_carnivores(self)

            Island.yearly_cycle_phase_2(self)
            Island.yearly_cycle_phase_3(self)

            self._population_history[self._year] = {"Herbivore": self.num_animals_per_species["Herbivore"],
                                                    "Carnivore": self.num_animals_per_species["Carnivore"]}

            self.assign_herbs_and_carns_in_array()
            for i in self.cells:
                for j in self.cells[i].herbivore:
                    dicto_hist_herb["age"].append(j.age)
                    dicto_hist_herb["weight"].append(j.weight)
                    dicto_hist_herb["fitness"].append(j.fitness)

                for carn in self.cells[i].carnivore:
                    dicto_hist_can["age"].append(carn.age)
                    dicto_hist_can["weight"].append(carn.weight)
                    dicto_hist_can["fitness"].append(carn.fitness)

            if self.graph:
                self.graph.update(self._year,
                                  self.num_animals_per_species["Herbivore"],
                                  self.num_animals_per_species["Carnivore"],
                                  self.herb_array,
                                  self.carn_array,
                                  dicto_hist_herb,
                                  dicto_hist_can)
            self.save_log_file()
            self._year += 1

    def return_animal(self, params):
        """
        Returns correct species of animal

        :param params: dictionary containing species, age and weight
        :type params: dict
        :return: Class instance of Carnivore or Herbivore
        :rtype: Herbivore class og Carnivore class
        """
        if params["species"] == "Herbivore":
            return Herbivore(params["age"],
                             params["weight"])
        elif params["species"] == "Carnivore":
            return Carnivore(params["age"],
                             params["weight"])
        else:
            raise ValueError("Species needs to be Herbivore or Carnivore")

    def add_population(self, population):
        """
        Add a population to the island

        :param population: List of dictionaries specifying population
        """
        for i in population:
            location = i["loc"]
            animal_population = i["pop"]
            animals = [self.return_animal(i) for i in animal_population]
            Island.add_animals(self, self.cells, location=location, animals=animals)

    def save_log_file(self):
        """
        Creates log file if given file name.
        """
        if self.log_file is None:
            return
        else:
            with open(self.log_filen + ".csv", mode="w") as log_csv:
                headers = ["Year", "Herbivore", "Carnivore"]
                writer = csv.writer(log_csv)
                writer.writerow(headers)
                for key, value in self._population_history.items():
                    writer.writerow([key, value["Herbivore"], value["Carnivore"]])

    @property
    def year(self):
        """Last year simulated."""
        return self._year

    @property
    def num_animals(self):
        """Total number of animals on island."""
        return Carnivore.animal_count + Herbivore.animal_count

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""
        return {"Herbivore": Herbivore.animal_count, "Carnivore": Carnivore.animal_count}

