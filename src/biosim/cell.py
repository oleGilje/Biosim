# -*- coding: utf-8 -*-
__author__ = 'Herman Ellingsen, Ole Gilje Gunnarshaug'
__email__ = 'hermane@nmbu.no, ole.gilje.gunnarshaug@nmbu.no'
"""The cell module"""

from .animal import Herbivore, Carnivore
import random


class Lowland:
    """
    Class that will provide attributes to cell class
    """
    f_max = 800
    @classmethod
    def set_attr(cls, dicto):
        setattr(cls, "f_max", dicto["f_max"])


class Highland:
    """
    Class that will provide attributes to cell class
    """
    f_max = 300
    @classmethod
    def set_attr(cls, dicto):
        setattr(cls, "f_max", dicto["f_max"])


class Desert:
    """
    Class that will provide attributes to cell class
    """
    f_max = 0

    @classmethod
    def set_attr(cls, dicto):
        setattr(cls, "f_max", dicto["f_max"])


class Water:
    """
    Class that will provide attributes to cell class
    """
    f_max = 0

    @classmethod
    def set_attr(cls, dicto):
        setattr(cls, "f_max", dicto["f_max"])


fmax_dicto = {"H": Highland.f_max,
              "L": Lowland.f_max,
              "W": Water.f_max,
              "D": Desert.f_max}


class Cell:
    """
    Cell class
    """
    def __init__(self, landtype, location, animals=[]):
        """
        This initializes a cell instance.

        :param landtype: String describing the type of land for the cell
        :type landtype: string
        :param location: Tuple with the location of the cell
        :type location: tuple
        :param animals: List of the animals that are in the cell
        :type animals: list
        :param habitable: Boolean value describing if the cell is habitable or not
        :type habitable: bool
        :param f_max: Maximum amount of fodder in the cell
        :type: f_max: int
        """
        self.landtype = landtype
        self.animals = animals
        self.herbivore = []
        self.carnivore = []
        self.location = location

        if self.landtype == "L":
            self.fodder = fmax_dicto["L"]
            self.habitable = True
        elif self.landtype == "H":
            self.fodder = fmax_dicto["H"]
            self.habitable = True
        elif self.landtype == "D":
            self.fodder = fmax_dicto["D"]
            self.habitable = True
        elif self.landtype == "W":
            self.fodder = fmax_dicto["W"]
            self.habitable = False

    @property
    def number_of_herbivores(self):
        """
        :return: number of herbivores in cell.
        :rtype: int
        """
        return len(self.herbivore)

    @property
    def number_of_carnivores(self):
        """
        :return: number of carnivores in cell.
        :rtype: int
        """
        return len(self.carnivore)

    def update_fodder_year(self):
        """
        Function updates fodder in cell depending on type of land
        """
        if self.landtype == "L":
            self.fodder = 800
        elif self.landtype == "H":
            self.fodder = 300

    def animals_to_migrate(self, population):
        """
        :param population: list of animals in one species
        :type population: list
        :return: Animals that want to migrate, and animals that want to stay
        :rtype: list
        """
        migrate = []
        stay = []
        for x in population:
            if x.want_to_migrate() and not x.has_moved:
                x.has_moved = True
                migrate.append(x)
            else:
                stay.append(x)
        return migrate, stay

    def divide_population(self, list_of_animals):
        """
        Function divides species by doing:

        1. First, a function that will return animal from a given species in a population
        is created.

        2. Then this function is used to extract the different species into their own list.

        :param list_of_animals: List of animals in the cell.
        :type list_of_animals: list
        """
        def extract_species(population, species):
            return [animal for animal in population if type(animal).__name__ == species.__name__]
        self.herbivore.extend(extract_species(list_of_animals, Herbivore))
        self.carnivore.extend(extract_species(list_of_animals, Carnivore))

    @staticmethod
    def migrate(animal, destination, cells):
        """
        This function moves animals to their destination cell.

        :param animal: Class instance of a given species
        :type animal: Class instance
        :param destination: Tuple with the coordinates of the cell the animals migrate to
        :type destination: tuple
        :param cells: Dictionary containing the different cells on the island
        :type cells: dict

        """
        if type(animal) is Herbivore:
            cells[destination].herbivore.append(animal)
        elif type(animal) is Carnivore:
            cells[destination].carnivore.append(animal)

    @staticmethod
    def get_target_destination(cell_coord):
        """
        Function makes a list of the surrounding cells and randomly returns one of these.

        :param cell_coord: Tuple of the coordinates of the cell the animal is in before migration
        :type cell_coord: tuple
        :return: Coordinate for the animal to move to
        :rtype: tuple
        """
        surr_cells = [(cell_coord[0]+n, cell_coord[1]) for n in
                      [-1, 1]] + [(cell_coord[0], cell_coord[1]+m) for m in [-1, 1]]
        destination = random.choice(surr_cells)
        return destination

    def update_fitness(self, species):
        """
        This list iterates through every animal in given species list and updates their fitness

        :param species: List of all the animals of a species in the given cell.
        :type species: list
        """
        [ani.fitness_update() for ani in species]

    def herbivores_eat(self):
        """
        This function if so that herbivores eat:

        1. First, it updates the fitness for all herbivores.

        2. Then it sorts the list of herbivores in regard to their fitness. To make sure the
            fittest eat first.

        3. Then it iterates through all the herbivores. If available fodder, it will eat according
            to their F value. If fodder below this, it will eat what is left, if anything.
        """
        self.update_fitness(self.herbivore)
        self.herbivore.sort(key=lambda x: x.fitness, reverse=True)
        for herb in self.herbivore:
            if self.fodder >= herb.params["F"]:
                herb.feed(herb.params["F"])
                self.fodder -= herb.params["F"]
            else:
                amount_left = self.fodder
                herb.feed(amount_left)
                self.fodder = 0

    def carnivores_eat(self):
        """
        This function is so that carnivores eat.

        1. First, we update the fitness for the carnivores, to make sure it updates ######

        2. Then we sort the herbivores' fitness in ascending order, so that it will start
            with the weakest first.

        3. Then we will go through every carnivore in self.carnivore. Then we will check how
        much it will eat, and update self.herbivore to only contain the survivors.
        """
        self.update_fitness(self.carnivore)
        self.update_fitness(self.herbivore)
        self.herbivore.sort(key=lambda x: x.fitness)
        for carni in self.carnivore:
            self.herbivore = [herb for herb in self.herbivore if not carni.kill(herb)]

    def create_newborns(self, species_pop):
        """
        This function returns newborn to add in species list. Newborn is created if animal.birth
        results in new class instance of the species.

        :param species_pop: List of all the animals in a given species
        :type species_pop: list
        :return: Newborn to add in species list
        :rtype: list
        """
        N = len(species_pop)
        return [newborn for animal in species_pop if (newborn := animal.birth(N))]

    def add_newborns(self):
        """
        This function extends population lists with newborns.
        """
        self.update_fitness(self.herbivore)
        self.update_fitness(self.carnivore)
        self.herbivore.extend(self.create_newborns(self.herbivore))
        self.carnivore.extend(self.create_newborns(self.carnivore))

    def updating_age_for_entire_population(self):
        """
        This function updates annual age for all animals in a cell, regardless of species.
        """
        [animal.age_update() for animal in self.herbivore + self.carnivore]

    def updating_weight_loss_for_entire_population(self):
        """
        This function updates annual weight loss for all animals in a cell, regardless of species.
        """
        [animal.annual_weight_loss() for animal in self.herbivore + self.carnivore]

    def check_for_random_death(self):
        """
        This function checks if animals dies. Updates list to only contain survivors.
        """
        self.herbivore = [herb for herb in self.herbivore if not herb.animal_dies()]
        self.carnivore = [carn for carn in self.carnivore if not carn.animal_dies()]

    def reset_attributes(self):
        """
        This function resets alle the attributes listed in "reset_amount()" for all animals in
        given cell.
        """
        [i.reset_amount() for i in self.carnivore + self.herbivore]


