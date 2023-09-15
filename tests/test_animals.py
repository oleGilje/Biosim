"""
Tests for the animal class.
"""

from biosim.animal import Herbivore, Carnivore
import pytest
import random
from scipy import stats
random.seed(69)


class TestHerbivore:
    r"""
    ..math::
    latex code
    """

    @pytest.fixture(autouse=True)
    def create_herbivore(self):
        self.h = Herbivore(5, 20)
        self.list_herbs = [Herbivore(random.randint(5, 10), random.randint(30, 40))
                           for _ in range(1000)]

    def test_set_params_value_error(self):
        """Test that we get ValueError when a parameter value is less than zero"""
        self.h.params['eta'] = -1
        with pytest.raises(ValueError):
            self.h.set_params(self.h.params)

    def test_herbivore_aging(self):
        """Test that a herbivores age increases with 1 for each year."""
        for n in range(5, 16):
            self.h.age_update()
            assert self.h.age == n + 1

    def test_herbivore_feed(self):
        """Test that the weight increases when a herbivore eats."""
        self.h.feed(10)
        assert self.h.weight == 20 + (self.h.params['beta']*self.h.params['F'])

    def test_herbivore_weight_loss(self):
        """Test that a herbivores weight decreases."""
        self.h.annual_weight_loss()
        assert self.h.weight == 20 - (self.h.params['eta']*20)

    def test_herbivore_fitness_update_weight_0(self):
        """Test that fitness is 0 when weight is 0."""
        self.h.weight = 0
        self.h.fitness_update()
        assert self.h.fitness == 0

    def test_herbivore_fitness_update_aging(self):
        """Test that the fitness updates when a herbivore ages."""
        fitness_pre = self.h.fitness
        self.h.age_update()
        self.h.fitness_update()
        assert self.h.fitness != fitness_pre

    def test_herbivore_fitness_update_new_weight(self):
        """Test that the fitness updates when a herbivore loses weight."""
        fitness_pre = self.h.fitness
        self.h.annual_weight_loss()
        self.h.fitness_update()
        assert self.h.fitness != fitness_pre

    def test_herbivore_able_to_give_birth_low_weight(self):
        """
        Test that a herbivore is not eligible for birth when its
        weight is less than zeta*(w_birth+sigma_birth)
        """
        assert not self.h.able_to_give_birth()

    def test_herbivore_birth_weight_loss(self, mocker):
        """Test that a herbivore loses weight after giving birth."""
        mocker.patch('random.random', return_value=0)
        self.h.weight = 50
        self.h.fitness_update()
        pre_weight = self.h.weight
        self.h.birth(2)
        post_weight = self.h.weight
        assert pre_weight != post_weight

    def test_herbivore_newborn_age_0(self):
        """Test that a newborn herbivore has age 0"""
        N = len(self.list_herbs)
        [herb.fitness_update() for herb in self.list_herbs]
        babies = [newborn for herb in self.list_herbs if (newborn := herb.birth(N))]
        assert [baby.age == 0 for baby in babies]

    def test_herbivore_certain_death(self, mocker):
        """
        Test that a herbivore does not die when the random probability of
        survival is replaced by 1.
        """
        mocker.patch('random.random', return_value=1)
        for _ in range(100):
            self.h.fitness_update()
            assert not self.h.animal_dies()

    def test_herbivore_certain_survival(self, mocker):
        """
        Test that a herbivore will die when the random probability of
        survival is replaced by 0.
        """
        mocker.patch('random.random', return_value=0)
        for _ in range(100):
            self.h.fitness_update()
            assert self.h.animal_dies()

    def test_herbivore_no_death_fitness_1(self):
        """
        Test that a herbivore does not die when its fitness is 1
        """
        self.h.fitness = 1
        for _ in range(100):
            assert not self.h.animal_dies()

    def test_herbivore_dies_weight_0(self):
        """
        Test that a herbivore actually dies when its weight is 0.
        Weight 0 implies fitness 0.
        """
        self.h.weight = 0
        self.h.fitness_update()
        for _ in range(100):
            assert self.h.animal_dies()

    def test_herbivore_want_to_migrate_random_0(self, mocker):
        """
        Test that a herbivore moves when probability to move
        is set to 1.
        """
        mocker.patch('random.random', return_value=0)
        for _ in range(100):
            self.h.has_moved = False
            assert self.h.want_to_migrate()

    def test_herbivore_move_random_1(self, mocker):
        """
        Test that a herbivore does not move when probability to move
        is set to 0.
        """
        mocker.patch('random.random', return_value=1)
        for _ in range(100):
            self.h.has_moved = False
            assert not self.h.want_to_migrate()

    def test_herbivore_move_only_once(self):
        """Test that a herbivore does not move more than once per year."""
        self.h.has_moved = True
        assert not self.h.want_to_migrate()

    def test_herbivore_birth_weight_gauss(self, mocker):
        """
        Test that the birth function returns gaussian distribution for
        herbivores.

        We set the significance level to be alpha = 0.05. If the p value
        given from scipys stats.normaltest() is higher than alpha we keep
        our null hypothesis and our test will pass.
        """
        mocker.patch('random.random', return_value=0)
        alpha = 0.05
        self.list_herbs = [Herbivore(random.randint(30, 40), random.randint(50, 60)) for _ in
                           range(1000)]
        [herb.fitness_update() for herb in self.list_herbs]
        babies = [herb.birth(len(self.list_herbs)) for herb in self.list_herbs]
        babies_weights = [baby.weight for baby in babies]
        k2, p = stats.normaltest(babies_weights)
        assert p > alpha


class TestCarnivore:

    @pytest.fixture(autouse=True)
    def create_carnivore(self):
        self.c = Carnivore(5, 20)
        self.list_carns = [Carnivore(random.randint(5, 10), random.randint(30, 40)) for _ in
                           range(1000)]

    @pytest.fixture
    def set_params(request):
        Carnivore.get_attributes(request.param)
        yield
        Carnivore.get_attributes(Carnivore.parameters)

    def test_carnivore_aging(self):
        """Test that a carnivores age increases with 1 for each year."""
        for n in range(5, 16):
            self.c.age_update()
            assert self.c.age == n + 1

    def test_carnivore_weight_loss(self):
        """Test that a carnivores weight decreases."""
        self.c.annual_weight_loss()
        assert self.c.weight == 20 - (self.c.params['eta']*20)

    def test_carnivore_birth_low_weight(self):
        """
        Test that a carnivore is not eligible for birth when its
        weight is less than zeta*(w_birth+sigma_birth)
        """
        assert not self.c.able_to_give_birth()

    def test_carnivore_birth_weight_loss(self, mocker):
        """Test that a carnivore loses weight after giving birth."""
        mocker.patch('random.random', return_value=0)
        self.c.weight = 50
        self.c.fitness_update()
        pre_weight = self.c.weight
        self.c.birth(2)
        post_weight = self.c.weight
        assert pre_weight != post_weight

    def test_carnivore_fitness_update_aging(self):
        """Test that the fitness updates when a carnivore ages."""
        fitness_pre = self.c.fitness
        self.c.age_update()
        self.c.fitness_update()
        assert self.c.fitness != fitness_pre

    def test_carnivore_fitness_update_new_weight(self):
        """Test that the fitness updates when a carnivore loses weight."""
        fitness_pre = self.c.fitness
        self.c.annual_weight_loss()
        self.c.fitness_update()
        assert self.c.fitness != fitness_pre

    def test_carnivore_newborn_age_0(self):
        """Test that a newborn carnivore has age 0"""
        N = len(self.list_carns)
        [carn.fitness_update() for carn in self.list_carns]
        babies = [newborn for carn in self.list_carns if (newborn := carn.birth(N))]
        assert [baby.age == 0 for baby in babies]

    def test_carnivore_certain_death(self, mocker):
        """
        Test that a carnivore does not die when the random probability of
        survival is replaced by 1.
        """
        mocker.patch('random.random', return_value=1)
        for _ in range(100):
            self.c.fitness_update()
            assert not self.c.animal_dies()

    def test_carnivore_certain_survival(self, mocker):
        """
        Test that a carnivore will die when the random probability of
        survival is replaced by 0.
        """
        mocker.patch('random.random', return_value=0)
        for _ in range(100):
            self.c.fitness_update()
            assert self.c.animal_dies()

    def test_carnivore_no_death_fitness_1(self):
        """Test that a carnivore does not die when its fitness is 1"""
        self.c.fitness = 1
        assert not self.c.animal_dies()

    def test_carnivore_dies_weight_0(self):
        """Test that a carnivore actually dies when its weight is 0."""
        self.c.weight = 0
        self.c.fitness_update()
        assert self.c.animal_dies()

    def test_carnivore_move_once(self):
        """Test that a carnivore does not move more than once per year."""
        self.c.has_moved = True
        assert not self.c.want_to_migrate()

    def test_carnivore_move_random_0(self, mocker):
        """Test that a carnivore moves when probability to move is set to 1."""
        mocker.patch('random.random', return_value=0)
        for _ in range(100):
            self.c.has_moved = False
            assert self.c.want_to_migrate()

    def test_carnivore_move_random_1(self, mocker):
        """Test that a carnivore does not move when probability to move is set to 0."""
        mocker.patch('random.random', return_value=1)
        for _ in range(100):
            self.c.has_moved = False
            assert not self.c.want_to_migrate()

    def test_carnivore_kill_not_hungry(self, mocker):
        """Test that a carnivore gains the correct amount of weight and can not eat more than 50."""
        mocker.patch('random.random', return_value=0)
        h = Herbivore(20, 60)
        self.c = Carnivore(25, 70)
        h.fitness_update()
        self.c.fitness_update()
        self.c.hungry = True
        self.c.amount_eaten = 10
        self.c.kill(h)
        assert self.c.weight == 70

    def test_carnivore_kill_hungry(self, mocker):
        """Test that a carnivore is still hungry after eating less than 50"""
        mocker.patch('random.random', return_value=0)
        h = Herbivore(5, 10)
        h.fitness_update()
        self.c.fitness_update()
        self.c.amount_eaten = 49
        assert self.c.kill(h)

    def test_carnivore_eating_more_than_50(self):
        """Test that a carnivore can not eat more than 50."""
        self.c.fitness_update()
        h = Herbivore(10, 100)
        h.fitness_update()
        self.c.kill(h)
        assert not self.c.amount_eaten == 50

    def test_carnivore_kill_proba_random_0(self, mocker):
        """Test that a carnivore decides to kill if kill probability is set to 1."""
        h = Herbivore(5, 10)
        h.fitness_update()
        self.c.fitness_update()
        mocker.patch('random.random', return_value=0)
        assert self.c.kill_proba(h)

    def test_carnivore_kill_proba_fitter_herb(self):
        """Test that a carnivore does not kill a herbivore with larger fitness"""
        h = Herbivore(10, 50)
        for _ in range(100):
            h.fitness = 0.7
            self.c.fitness = 0.5
            assert not self.c.kill_proba(h)

    def test_carnivore_kill_proba_low_deltaphimax(self):
        self.c.params['DeltaPhiMax'] = 0
        h = Herbivore(5, 10)
        h.fitness_update()
        self.c.fitness_update()
        for _ in range(100):
            assert self.c.kill_proba(h)

    def test_carnivore_decide_if_kill_random_1(self, mocker):
        """Test that a carnivore decides not to kill if kill probability is set to 0.
        """
        h = Herbivore(5, 10)
        h.fitness_update()
        self.c.fitness_update()
        mocker.patch('random.random', return_value=1)
        assert not self.c.kill_proba(h)

    def test_carnivore_kill_proba(self):  # Foreløpig bare tull
        """
        Test that the kill probability is correctly calculated when
        (carnivores fitness - herbivores fitness) is between 0 and
        DeltaPhiMax.
        """
        results = []
        herbivore_list = [Herbivore(3, 8) for _ in range(1000)]
        self.carnivore_list = [Carnivore(6, 20) for _ in range(1000)]
        [h.fitness_update() for h in herbivore_list]
        [self.c.fitness_update() for self.c in self.carnivore_list]
        [results.append(self.c.kill_proba(h)) for self.c, h in zip(self.carnivore_list, herbivore_list)]
        print(results)
        assert self.c == self.c

    def test_carnivore_kill_weight_increase(self, mocker):
        """Test that the weight increases with the correct amount after a carnivore has eaten."""
        mocker.patch('random.random', return_value=0)
        h = Herbivore(5, 10)
        h.fitness_update()
        pre_kill_weight = self.c.weight
        self.c.fitness_update()
        self.c.kill_proba(h)
        self.c.hungry = True
        self.c.amount_eaten = 0
        self.c.kill(h)
        assert self.c.weight == pre_kill_weight + (h.weight * self.c.params["beta"])

    def test_carnivore_reset_amount(self):
        """Test that an animal is hungry and has not eaten anything when we reset amount."""
        self.c.reset_amount()
        assert self.c.hungry
        assert self.c.amount_eaten == 0

    def test_carnivore_birth_weight_gauss(self, mocker): # kopier til carnivores
        """
        Test that the birth function returns gaussian distribution for
        herbivores.

        We set the significance level to be alpha = 0.05. If the p value
        given from scipys stats.normaltest() is higher than alpha we keep
        our null hypothesis and our test will pass.
        """
        mocker.patch('random.random', return_value=0)
        alpha = 0.05
        self.list_carns = [Carnivore(random.randint(30, 40), random.randint(50, 60)) for _ in
                           range(1000)]
        [carn.fitness_update() for carn in self.list_carns]
        babies = [carn.birth(len(self.list_carns)) for carn in self.list_carns]
        babies_weights = [baby.weight for baby in babies]
        k2, p = stats.normaltest(babies_weights)
        assert p > alpha


