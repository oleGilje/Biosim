# -*- coding: utf-8 -*-
__author__ = 'Herman Ellingsen, Ole Gilje Gunnarshaug'
__email__ = 'hermane@nmbu.no, ole.gilje.gunnarshaug@nmbu.no'
"""The island module"""

from .cell import Cell
from .animal import Herbivore, Carnivore

class Island:
    """
    Island class
    """
    def __init__(self):
        self.length_map_x = None
        self.length_map_y = None

    @staticmethod
    def make_map(map):
        """
        Function reads in list of letters and creates dictionary of cells.

        :param map: String of letters describing different landtypes
        :type map: str
        :return: :map_dicto: Dictionary where keys are coordinates(tuple) and values are Cell
        objects.
        :rtype: dict
        """
        map_dicto = {(x + 1, y + 1): Cell(landtype, (x, y)) for y, line in enumerate(map.split())
                     for x, landtype in enumerate(line)}
        return map_dicto

    def add_animals(self, cells, location, animals):
        """
        This function will perform "divide_population()" on animals in a cell with given location.

        :param cells: Dictionary containing the cells in the island
        :type cells: dict
        :param location: Tuple with the given location to perform function on
        :type location: typle
        :param animals: List of animals
        :type animals: list
        """
        cells[location].divide_population(animals)

    def migration_herbivores(self):
        for coord in self.cells:
            herbivores = self.cells[coord].herbivore
            animal_to_migrate, stay = self.cells[coord].animals_to_migrate(herbivores)
            self.cells[coord].herbivore = stay
            for animal in animal_to_migrate:
                target = self.cells[coord].get_target_destination(coord)
                if self.cells[target].habitable:
                    self.cells[coord].migrate(animal, target, self.cells)
                else:
                    self.cells[coord].migrate(animal, coord, self.cells)

    def migration_carnivores(self):
        for coord in self.cells:
            carnivores = self.cells[coord].carnivore
            animal_to_migrate, stay = self.cells[coord].animals_to_migrate(carnivores)
            self.cells[coord].carnivore = stay
            for animal in animal_to_migrate:
                target = self.cells[coord].get_target_destination(coord)
                if self.cells[target].habitable:
                    self.cells[coord].migrate(animal, target, self.cells)
                else:
                    self.cells[coord].migrate(animal, coord, self.cells)


    def yearly_cycle_phase_1(self):
        """
        Phase 1 of the yearly cycle on Island. This will perform the following things:

        1. Update fodder in cell, depending on landtype

        2. Herbivores eat

        3. Carnivores eat

        4. Procreation
        """
        for cell in self.cells.values():
            cell.update_fodder_year()
            cell.herbivores_eat()
            cell.carnivores_eat()
            cell.add_newborns()

    def yearly_cycle_phase_2(self):
        """
        Phase 2 of the yearly cycle on Island. This will perform the following things:

        1. Update the age for all animals

        2. Update weight for all animals according to annual weight loss

        3. Remove all animals that die (not from carnivores eating)
        """

        for cell in self.cells.values():
            cell.updating_age_for_entire_population()
            cell.updating_weight_loss_for_entire_population()
            cell.check_for_random_death()

    def yearly_cycle_phase_3(self):
        """
        Phase 3 of the yearly cycle on Island. This will perform the following thing:

        -Reset the attributes given in "reset_attributes()" for alle animals on island.
        """
        for cell in self.cells.values():
            cell.reset_attributes()
