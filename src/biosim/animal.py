# -*- coding: utf-8 -*-
__author__ = 'Herman Ellingsen, Ole Gilje Gunnarshaug'
__email__ = 'hermane@nmbu.no, ole.gilje.gunnarshaug@nmbu.no'
"""The animal module"""

import random
import math


class Animal:
    """
    Class for animals
    """
    animal_count = 0

    @classmethod
    def set_params(cls, dicto):
        """
        This function sets new parameters as class attributes.
        :param dicto: Dictionary containing parameter values.
        :type dicto: dict
        """

        for key in cls.params:
            if key in dicto:
                if dicto[key] < 0:
                    raise ValueError("Cant be below zero")
                cls.params.update(dicto)

    @classmethod
    def get_params(cls):
        """
        Get parameters.

        :return: Dictionary with parameters
        :rtype: dict
        """
        return cls.params

    def __init__(self, age, weight):
        """
        This initializes an animal instance.

        :param age: Initial age
        :type age: int
        :param weight: Initial weight
        :type weight: int or float
        """
        type(self).animal_count += 1
        self.age = age
        self.weight = weight
        self.has_moved = False
        self.amount_eaten = 0
        self.hungry = True

    def __del__(self):
        """Remove 1 when animal is removed."""
        type(self).animal_count -= 1

    def get_params(self):
        """
        get parameters.
        :return: Dictionary with parameters
        :rtype: dict
        """
        return self.params

    def age_update(self):
        """
        Updates age of animal, and then updates the fitness according to the new age.
        """
        self.age += 1
        self.fitness_update()

    def feed(self, food_to_eat):
        """
        This function feed an animal. It takes amount of food in as parameter.
        Then updates the weight and the amount the animal have eaten.
        Lastly the fitness is updated.

        :param food_to_eat: Amount of food to feed the animal
        :type food_to_eat: int
        """
        self.weight += food_to_eat*self.params["beta"]
        self.amount_eaten += food_to_eat
        self.fitness_update()

    def annual_weight_loss(self):
        """
        Function updates weight of animal according to annual weight loss set
        by given parameters "eta" and its own weight.
        """
        self.weight -= self.params["eta"]*self.weight
        self.fitness_update()

    def fitness_update(self):
        """
        Function updates fitness of animal according to function for fitness.
        The fitness is calculated according to formula below, based on
        its weight and age.

        .. math::

            \\Phi =
            \\begin{cases}
            0 & w\\leq 0\\

            \q^{+}(a, a_{\\frac{1}{2}}, \\phi_{age}) \\times q^{-}(w, w_{\\frac{1}{2}},
            \\phi_{weight}) & \\text{else}
            \\end{cases}

        where

        .. math::
            q^{\\pm} (a, a_{\\frac{1}{2}}, \\phi_{age}) = \\frac{1}{1 + e^{\\pm
            \\phi (x - x_{\\frac{1}{2}})}}

        .. math::
              \\text{Note that: } 0 \\leq  \\Phi \\leq 1
        """
        if self.weight <= 0:
            self.fitness = 0
        else:
            age_part = 1/(1+math.exp(self.params["phi_age"]*(self.age-self.params["a_half"])))
            weight_part = 1/(1+math.exp(-self.params["phi_weight"]*(self.weight-self.params["w_half"])))
            self.fitness = age_part * weight_part

    def want_to_migrate(self):
        """
        Function checks if animal wants to migrate depending on function
        for migration with random draw according to p value. Self.have_moved
        also needs to be False in order to return true.

        :return: True if criteria is met.
        :rtype: bool
        """
        self.fitness_update()
        p = self.params["mu"]*self.fitness
        if p > random.random() and self.has_moved is False:
            return True

    def able_to_give_birth(self):
        """
        Function checks if the weight of the animal is higher than the
        minimum weight in order to give birth. If so, returns "True"

        :return: true criteria is met
        :rtype: bool
        """
        if self.weight > (self.params["zeta"] *
                          (self.params["w_birth"] + self.params["sigma_birth"])):
            return True

    def birth(self, N):
        """
        Function calculates weight of baby and the weight loss of animal giving birth.
        Then it checks the criteria if animal can give birth. If so, it updates weight
        and fitness of animal. The probability of giving birth is calculated with the
        formula below.

        .. math::

            \\text{min}(1, \\gamma \\times \\phi \\times (\\text{N} - 1))


        :param N: Number of animals in population of same species

        :return: Animal of same species when criteria are met.
        """
        baby_weight = random.gauss(self.params["w_birth"], self.params["sigma_birth"])
        weight_loss = self.params["xi"] * baby_weight
        p = min(1, self.params["gamma"] * self.fitness * (N-1))
        if self.weight > weight_loss and p > random.random() and self.able_to_give_birth():
            self.weight -= weight_loss
            self.fitness_update()
            return type(self)(0, baby_weight)

    def animal_dies(self):
        """
        Checks if animal will die, either from weight being zero or less, or from
        randomness according to function below.

        .. math::

            \\omega(1 - \\Phi)

        :return: True if criteria are met
        """
        if self.weight <= 0 or self.params["omega"]*(1-self.fitness) > random.random():
            return True

    def reset_amount(self):
        """
        Resets given attributes to what was initialized when animal was created.
        """
        self.has_moved = False
        self.amount_eaten = 0
        self.hungry = True


class Herbivore(Animal):
    """
    This class creates Herbivore instances. These instances represent animals that can live on the
    island in simulations. This class inherits from the Animal class.
    """
    params = {"eta": 0.05,
              "beta": 0.9,
              "phi_age": 0.6,
              "phi_weight": 0.1,
              "a_half": 40.0,
              "w_half": 10.0,
              "mu": 0.25,
              "omega": 0.4,
              "zeta": 3.5,
              "w_birth": 8,
              "sigma_birth": 1.5,
              "gamma": 0.2,
              "xi": 1.2,
              "F": 10}

    def __init__(self, age=None, weight=None):
        """
        Age and weight are inherited from the Animal class

        :param age: Age of animal
        :param weight: Weight of animal
        """
        super().__init__(age, weight)
        self.fitness = self.fitness_update()


class Carnivore(Animal):
    """
    This class creates Carnivore instances. These instances represent animals that can live on the
    island in simulations. This class inherits from the Animal class
    """
    params = {"eta": 0.125,
                   "beta": 0.75,
                   "phi_age": 0.3,
                   "phi_weight": 0.4,
                   "a_half": 40.0,
                   "w_half": 4.0,
                   "mu": 0.4,
                   "omega": 0.8,
                   "zeta": 3.5,
                   "w_birth": 6.0,
                   "sigma_birth": 1.0,
                   "gamma": 0.8,
                   "xi": 1.1,
                   "DeltaPhiMax": 10,
                   "F": 50}

    def __init__(self, age=None, weight=None):
        """
        Age and weight are inherited from the Animal class.

        :param age: Age of animal
        :param weight: Weight of animal
        """
        super().__init__(age, weight)
        self.fitness = self.fitness_update()
        self.hungry = True
        self.amount_eaten = 0

    def kill_proba(self, herb):
        """
        Function finds probability of killing the herbivore. If probability
        is higher than the random number between 0 and 1, it will return True.
        The probability is calculated with the formula below.

        .. math::

            p =
            \\begin{cases}
            0 & \\text{if } \\phi_{carn} \\leq \\phi_{herb}

            \\frac{\\phi_{carn} - \\phi_{herb}}{\\Delta\\phi_{max}}& \\text{if } 0 <
            \\phi_{carn} - \\phi_{herb} \\leq \\Delta\\phi_{max}

            1 & \\text{otherwise. }
            \\end{cases}

        :param herb: Class instance of type herbivore

        :return: True is criteria are met.

        """
        if self.fitness <= herb.fitness:
            kill_proba = 0
        elif 0 < (self.fitness - herb.fitness) < self.params["DeltaPhiMax"]:
            kill_proba = (self.fitness - herb.fitness)/self.params["DeltaPhiMax"]
        else:
            kill_proba = 1

        if kill_proba > random.random():
            return True
        else:
            return False

    def kill(self, herbi):
        """
        This function decides if the carnivore should kill the herbivore depending
        on how much it already has eaten. It will also track how much it has eaten
        and will feed the animal max F amount of meat.

        :param herbi: Class instance of type herbivore

        :return: True is criteria are met.
        """
        if self.kill_proba(herbi) and self.hungry:
            if (self.amount_eaten + herbi.weight) > 50:
                self.feed(50-self.amount_eaten)
                self.hungry = False
            else:
                self.feed(herbi.weight)
            return True
        else:
            return False


