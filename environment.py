import numpy as np
import pygame
import random

class Environment:
    """
        Manages the environment for fungal growth simulation, including resources, temperature, and humidity.

        Parameters
        ----------
        width : int
            Width of the environment grid (cells).
        height : int
            Height of the environment grid (cells).
        max_resource : float, optional
            Maximum resource level (default is 1.0).
        resource_zero_level : float, optional
            Baseline resource level as a fraction of max_resource (default is 0.08).
        window_size : int, optional
            Size of the moving window for averaging operations (default is 8).
        biomass_threshold : int, optional
            Biomass threshold for critical state (default is 160).
        zone_count : int, optional
            Number of resource-rich zones (default is 20).
        zone_size : int, optional
            Maximum size of each resource zone (default is 200).
        temp_min : int, optional
            Minimum temperature in the environment (default is 20).
        temp_max : int, optional
            Maximum temperature in the environment (default is 30).
        humidity_min : int, optional
            Minimum humidity level (default is 30).
        humidity_max : int, optional
            Maximum humidity level (default is 90).
    """
    def __init__(self, width, height,
                 max_resource = 1.0,
                 resource_zero_level = 0.08,
                 window_size = 8,
                 hyphae_to_window_ratio = 0.5,
                 biomass_threshold = 160,
                 zone_count=20,
                 zone_size=200,
                 temp_min = 20,
                 temp_max = 30,
                 humidity_min=30,
                 humidity_max=90):
        self.width = width
        self.height = height
        self.max_resource = max_resource
        self.biomass_threshold = biomass_threshold
        self.window_size = window_size
        self.hyphae_to_window_ratio = hyphae_to_window_ratio
        self.resource_map = self.__generate_resource_map(zone_count, zone_size, resource_zero_level)
        self.temperature_map = self.generate_temperature_map(temp_min, temp_max)
        self.humidity_map = self.generate_humidity_map(humidity_min, humidity_max)
        self.total_nodes_map = np.zeros((self.height, self.width))
        self.total_biomass_map = np.zeros((self.height, self.width))

    def __generate_resource_map(self, num_zones, max_size, resource_zero_level):
        resource_map = np.zeros((self.width, self.height))
        for _ in range(num_zones):
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            size = random.randint(max_size // 2, max_size)

            initial_resources = random.random() * self.max_resource
            for i in range(-size, size):
                for j in range(-size, size):
                    if 0 <= x + i < self.width and 0 <= y + j < self.height and i ** 2 + j ** 2 < size ** 2:
                        resource_map[x + i, y + j] = initial_resources

        return (resource_map / np.max(resource_map)) * (1-resource_zero_level)*self.max_resource + resource_zero_level*self.max_resource

    def generate_temperature_map(self, temp_min=15, temp_max=35):
        return np.random.uniform(temp_min, temp_max, (self.width, self.height))  # Przykład: 15°C do 35°C

    def generate_humidity_map(self, humidity_min=30, humidity_max=90):
        return np.random.uniform(humidity_min, humidity_max, (self.width, self.height))  # Przykład: 30% do 90%

    def get_temperature(self, position):
        x, y = int(position[0]), int(position[1])
        return self.temperature_map[x, y] if 0 <= x < self.width and 0 <= y < self.height else 0

    def get_resource(self, position):
        x, y = int(position[0]), int(position[1])
        d = self.window_size//2
        res_init = np.sum(self.resource_map[x-d : x+d, y-d : y+d])
        biomass = np.sum(self.total_biomass_map[x-d : x+d, y-d : y+d])

        return res_init - (self.max_resource * self.window_size**2) * (biomass / self.biomass_threshold)

    def add_new_node(self, position, hyphae_length):
        x, y = int(position[0]), int(position[1])
        self.total_biomass_map[x, y] += hyphae_length

    def get_color_based_on_resource(self, resource):
        res = resource / (self.window_size**2)
        if res < 0.05 * self.max_resource:  # Very low resources
            return (173, 216, 230)  # Light Blue (SkyBlue)
        elif res < 0.35 * self.max_resource:  # Low resources
            return (135, 206, 235)  # Lighter Blue (LightSkyBlue)
        elif res < 0.60 * self.max_resource:  # Medium resources
            return (70, 130, 180)  # SteelBlue
        else:  # High resources
            return (30, 144, 255)  # DodgerBlue

    def get_growth_cost(self, position, substrate_concentration):
        (x, y) = position
        x = int(x)
        y = int(y)
        d = self.window_size
        local_biomass = np.sum(self.total_biomass_map[x - d:x + d, y - d:y + d])
        a = 1.0
        l_i = local_biomass
        xi = self.biomass_threshold
        T = self.get_temperature(position)
        b = (T - 9) / 5
        v_i = self.get_resource(position) / (self.window_size**2)

        if v_i <= 0:
            return 1

        cost = (a * (l_i / xi) ** b) * (1 - v_i / self.max_resource)
        return cost

    def get_growth_rate(self, position, substrate_concentration, vmax=2.5, Ks=0.2, Topt=25, Hopt=80, sigma_T=20, sigma_H=40):
        x, y = int(position[0]), int(position[1])
        if 0 <= x < self.width and 0 <= y < self.height:
            T = self.temperature_map[x, y]
            H = self.humidity_map[x, y]
            μ_max = vmax
            # print(f'T:{T}, H:{H}, μ_max:{μ_max}, substrate_concentration:{substrate_concentration}')
            μ = μ_max * (substrate_concentration / (substrate_concentration + Ks)) * \
                np.exp(-((T - Topt) / sigma_T) ** 2) * \
                np.exp(-((H - Hopt) / sigma_H) ** 2)

            return μ * self.hyphae_to_window_ratio * self.window_size
        return 0.0

    def check_in_bounds(self, position):
        x, y = int(position[0]), int(position[1])
        return 0 <= x < self.width and 0 <= y < self.height

    def draw(self, screen):
        for x in range(0, self.width, 10):
            for y in range(0, self.height, 10):
                resource = self.get_resource((x,y))
                color = self.get_color_based_on_resource(resource)
                pygame.draw.rect(screen, color, (x, y, 10, 10))
