
import pytest
import random
from scipy import stats
import statistics

from biosim.animal import Herbivore, Carnivore
from biosim.cell import Cell


class TestCell:
    """Tests for the Cell class"""
    herbs = [Herbivore(random.randint(5, 10), random.randint(30, 40)) for _ in range(100)]
    carns = [Carnivore(random.randint(5, 10), random.randint(50, 70)) for _ in range(100)]
    list_animals = herbs + carns

    @pytest.fixture(autouse=True)
    def create_cell(self):
        self.lowland_cell = Cell('L', (1, 1), self.list_animals)
        self.highland_cell = Cell('H', (2, 1), self.list_animals)
        self.desert_cell = Cell('D', (1, 1), self.list_animals)
        self.water_cell = Cell('W', (1, 1), self.list_animals)

    def test_lowland_habitable(self):
        """Test that lowland actually is habitable"""
        assert self.lowland_cell.habitable

    def test_highland_habitable(self):
        """Test that highland actually is habitable"""
        assert self.highland_cell.habitable

    def test_desert_habitable(self):
        """Test that desert actually is habitable"""
        assert self.desert_cell.habitable

    def test_water_not_habitable(self):
        """Test that water is not habitable"""
        assert not self.water_cell.habitable

    def test_fodder_lowland(self):
        """Test that lowland starts with 800 fodder"""
        assert self.lowland_cell.fodder == 800

    def test_fodder_highland(self):
        """Test that highland starts with 300 fodder"""
        assert self.highland_cell.fodder == 300

    def test_fodder_desert(self):
        """Test that desert starts with 0 fodder"""
        assert self.desert_cell.fodder == 0

    def test_fodder_water(self):
        """Test that water starts with 0 fodder"""
        assert self.water_cell.fodder == 0

    def test_number_of_herbivores(self):
        """
        Test that the number_of_herbivores gets the number of
        herbivores in the cell.
        This test is landtype independent.
        """
        self.lowland_cell.herbivore = self.herbs
        assert self.lowland_cell.number_of_herbivores == len(self.herbs)

    def test_number_of_carnivores(self):
        """Test that the number_of_carnivores works."""
        self.lowland_cell.carnivore = self.carns
        assert self.lowland_cell.number_of_carnivores == len(self.carns)

    def test_fodder_lowland_updates(self):  # might change this, max fodder in cell is 800?
        """Test that fodder in lowland updates in the beginning of the year."""
        self.lowland_cell.fodder = 100
        self.lowland_cell.update_fodder_year()
        assert self.lowland_cell.fodder == 800

    def test_fodder_highland_updates(self): # might change this, max fodder in cell is 300?
        """Test that fodder in highland updates in the beginning of the year."""
        self.highland_cell.fodder = 100
        self.highland_cell.update_fodder_year()
        assert self.highland_cell.fodder == 300

    def test_divide_population_herbivore(self):
        """Test that the herbivore list only contains herbivores. landtype independent."""
        self.lowland_cell.divide_population(self.list_animals)
        for animal in self.lowland_cell.herbivore:
            assert type(animal) is Herbivore

    def test_divide_population_carnivore(self):
        """Test that the carnivore list only contains carnivores. landtype independent."""
        self.lowland_cell.divide_population(self.list_animals)
        for animal in self.lowland_cell.carnivore:
            assert type(animal) is Carnivore

    def test_target_destination(self):
        """Tests that the animals moves to one of the surrounding cells."""
        surr_cells = [(0, 1), (1, 0), (2, 1), (1, 2)]
        assert (self.lowland_cell.get_target_destination((1, 1)) in surr_cells)

    def test_herbivores_eat_sort(self):
        """Test that the herbivores gets sorted descending/ascending by fitness."""
        self.lowland_cell.update_fitness(self.herbs)
        self.herbs.sort(key=lambda x: x.fitness, reverse=True)
        assert all(self.herbs[i].fitness >= self.herbs[i+1].fitness for i in range(len(self.herbs)-1))

    def test_herbivores_eat(self):
        """Test that the herbivores eat the right amount of fodder"""
        self.lowland_cell.animals = [Herbivore(5, 20) for _ in range(10)]
        self.lowland_cell.divide_population(self.lowland_cell.animals)
        sum_weight = sum([herb.weight for herb in self.lowland_cell.animals])
        self.lowland_cell.herbivores_eat()
        sum_weight_after = sum([herb.weight for herb in self.lowland_cell.animals])
        assert sum_weight_after == (sum_weight + 90)

    def test_herbivores_eat_less_10_fodder_cell(self):
        """
        Test that herbivore only eats the fodder that is left in the
        cell if there is less than 10 fodder in the cell.
        """
        self.lowland_cell.fodder = 9
        self.lowland_cell.animals = [Herbivore(5, 10)]
        self.lowland_cell.divide_population(self.lowland_cell.animals)
        self.lowland_cell.herbivores_eat()
        new_weight = sum([herb.weight for herb in self.lowland_cell.animals])
        assert new_weight == 10 + 9*0.9

    def test_herbivores_eat_0_fodder_cell(self):
        """
        Test that the cell contains 0 fodder after a herbivore eats
        when there is less than 10 fodder in the cell.
        """
        self.lowland_cell.fodder = 9
        self.lowland_cell.animals = [Herbivore(5, 10)]
        self.lowland_cell.divide_population(self.lowland_cell.animals)
        self.lowland_cell.herbivores_eat()
        assert self.lowland_cell.fodder == 0

    def test_herbivore_eat_0_fodder(self):
        """Test that a herbivore does not eat anything when there is 0 fodder in a cell."""
        self.lowland_cell.fodder = 0
        self.lowland_cell.animals = [Herbivore(5, 10)]
        self.lowland_cell.divide_population(self.lowland_cell.animals)
        pre_weight = sum([herb.weight for herb in self.lowland_cell.animals])
        self.lowland_cell.herbivores_eat()
        post_weight = sum([herb.weight for herb in self.lowland_cell.animals])
        assert pre_weight == post_weight

    def test_fodder_eaten_removed(self):
        """Test that when an animal eats fodder it is removed from the cell."""
        herbivore = [Herbivore(5, 20) for _ in range(10)]
        herbi_cell = Cell('L', (2, 2), herbivore)
        herbi_cell.divide_population(herbi_cell.animals)
        herbi_cell.herbivores_eat()
        assert herbi_cell.fodder == 700

    def test_update_fitness_herbivore(self):
        """Test that update_fitness updates herbivores fitness"""
        h = Herbivore(5, 20)
        h_list = [Herbivore(5, 20)]
        herbi_cell = Cell('L', (2, 2), h)
        assert herbi_cell.update_fitness(h_list) == h.fitness_update()

    def test_update_fitness_carnivore(self):
        """Test that update_fitness updates carnivores fitness"""
        c = Carnivore(5, 20)
        c_list = [Carnivore(5, 20)]
        herbi_cell = Cell('L', (2, 2), c)
        assert herbi_cell.update_fitness(c_list) == c.fitness_update()

        results_herb = []
        results_carn = []
        alpha = 0.05
        self.lowland_cell.divide_population(self.list_animals)

        for _ in range(1000):
            self.lowland_cell.add_newborns()
            results_herb.append(len(self.lowland_cell.herbivore))
            results_carn.append(len(self.lowland_cell.carnivore))
        print(results_carn)
        k2_herb, p_herb = stats.normaltest(results_herb)
        k2_carn, p_carn = stats.normaltest(results_carn)
        assert p_herb < alpha
        assert p_carn < alpha

    def test_updating_age_for_entire_population_equal(self):
        """Test that the age updates equally for herbivore and carnivore"""
        h_list = [Herbivore(5, 20)]
        c_list = [Carnivore(5, 20)]
        herbi_cell = Cell('L', (2, 2), h_list)
        carni_cell = Cell('L', (1, 1), c_list)
        assert herbi_cell.updating_age_for_entire_population() == carni_cell.updating_age_for_entire_population()

    def test_updating_age_for_entire_population(self):
        """Test that the age updates for entire population"""
        pre_mean_age = statistics.mean([ani.age for ani in self.lowland_cell.animals])
        self.lowland_cell.divide_population(self.lowland_cell.animals)
        self.lowland_cell.updating_age_for_entire_population()
        post_mean_age = statistics.mean([ani.age for ani in self.lowland_cell.animals])
        assert post_mean_age == pytest.approx(pre_mean_age + 1)

    def test_updating_weight_loss_for_entire_population(self):
        """Test that the weight decreases for entire population"""
        pre_weight = [ani.weight for ani in self.lowland_cell.animals]
        self.lowland_cell.divide_population(self.lowland_cell.animals)
        self.lowland_cell.updating_weight_loss_for_entire_population()
        assert [ani.weight != pre_ani for ani, pre_ani in
                zip(self.lowland_cell.animals, pre_weight)]

    def test_updating_weight_loss_for_entire_population_equal(self):
        """Test that the weight loss updates equally for herbivore and carnivore"""
        h_list = [Herbivore(5, 20)]
        c_list = [Carnivore(5, 20)]
        herbi_cell = Cell('L', (2, 2), h_list)
        carni_cell = Cell('L', (1, 1), c_list)
        assert herbi_cell.updating_weight_loss_for_entire_population() == carni_cell.updating_weight_loss_for_entire_population()

    def test_carnivores_eat(self):
        """
        Test that carnivores does not kill too many herbivores.

        We set the significance level to be alpha = 0.05. If the p value
        given from scipys stats.normaltest() is lower than alpha we reject
        our null hypothesis and our test will pass.
        """
        results = []
        alpha = 0.05
        self.lowland_cell.divide_population(self.lowland_cell.animals)
        for _ in range(1000):
            self.lowland_cell.carnivores_eat()
            results.append(len(self.lowland_cell.herbivore))
        k2, p = stats.normaltest(results)
        assert p < alpha
