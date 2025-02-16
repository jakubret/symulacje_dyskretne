import math
import random
import pygame

from . import utils as utils

class FungusGraph:
    """
        Represents a graph structure for simulating fungal growth, with nodes representing fungal components.

        Attributes
        ----------
        nodes : list
            A list of nodes in the fungal graph, where each node represents a fungal structure.
    """
    def __init__(self):
        self.nodes = []

    def add_node(self, position, angle, age=0, growth_rate=1.0):
        node = utils.Node(position, angle, age)
        node.growth_rate = growth_rate
        self.nodes.append(node)
        return node

    def calculate_growth_angle(self, start_pos, end_pos):
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        return angle

    def extend_hypha(self, node, angle, length, env_instance):
            angle_rad = math.radians(angle + random.uniform(-15, 15))
            new_position = (
                node.position[0] + length * math.cos(angle_rad),
                node.position[1] + length * math.sin(angle_rad)
            )

            if env_instance.check_in_bounds(new_position):
                env_instance.add_new_node(new_position, length)
                new_node = self.add_node(new_position, angle=angle, age=node.age + 1, growth_rate=node.growth_rate)
                node.connect(new_node)
                return new_node
            else:
                return None

    def grow(self, active_nodes, env_instance, substrate_concentration=1.0):
        next_active_nodes = []
        for node in active_nodes:

            node.active = False

            growth_cost = env_instance.get_growth_cost(node.position, substrate_concentration)
            growth_rate = env_instance.get_growth_rate(node.position, substrate_concentration)

            print(growth_cost, growth_rate)
            v_max = 1.0

            if growth_cost < 0.05 * v_max:
                print("Rozgałęzienie 3")
                extensions = 3
            elif growth_cost < 0.35 * v_max:
                print("Rozgałęzienie 2")
                extensions = 2
            elif growth_cost < 0.60 * v_max:
                print("Wydłużenie")
                extensions = 1
            else:
                print("Obumarcie")
                node.active = False
                continue

            if extensions == 3:
                angle = random.uniform(22.5, 45)
                angles = [angle + node.angle, -angle + node.angle]
            elif extensions == 2:
                adjustment = random.uniform(30, 60)
                angle = random.choice([-1, 1]) * adjustment
                angles = [node.angle, node.angle + angle]
            else:
                angles = [node.angle]

            for angle in angles:
                new_node = self.extend_hypha(node, angle, growth_rate/len(angles), env_instance)
                if new_node:
                    next_active_nodes.append(new_node)

        return next_active_nodes


    def get_color_based_on_cost(self, cost):
        if cost < 0.05:
            return (0, 255, 0)  # Green
        elif cost < 0.35:
            return (255, 255, 0)  # Yellow
        elif cost < 0.60:
            return (255, 165, 0)  # Orange
        else:
            return (255, 0, 0)  # Red
        
    def draw(self, screen, env_instance, substrate_concentration):
        for node in self.nodes:
            cost = env_instance.get_growth_cost(node.position, substrate_concentration)
            color = self.get_color_based_on_cost(cost)
            pygame.draw.circle(screen, color, (int(node.position[0]), int(node.position[1])), 0.7)
            for connection in node.connections:
                pygame.draw.line(screen, color, node.position, connection.position, 1)

        font = pygame.font.SysFont(None, 24)

        active_count = sum(1 for node in self.nodes if node.active)
        text = font.render(f"Active Nodes: {active_count}, Total Nodes: {len(self.nodes)}", True, (0, 0, 0))
        screen.blit(text, (10, 10))
