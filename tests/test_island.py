from biosim.island import Island
import pytest


class TestIsland:
    """Tests for Island class"""

    @pytest.fixture(autouse=True)
    def create_island(self):
        self.island = Island()

    def test_make_map(self):
        """Test that a ValueError is raised when the map contains invalid land types"""
        pass

    def test_add_animals_in_water(self):
        """Test that adding animals in water does not work"""
        pass

    def test_migration_herbivores(self):
        """Test that herbivores migrate"""
        pass

