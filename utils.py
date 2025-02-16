from . import environment as env
from . import graph as graph

WIDTH, HEIGHT = 800, 800
WHITE, LIGHT_SKY_BLUE, BLACK, LIGHT_GRAY, BROWN = (255, 255, 255), (135, 206, 250), (0, 0, 0), (211, 211, 211), (139, 69, 19)

import time

class Node:
    """
        Represents a node in the fungal growth network, which can connect to other nodes and track its state over time.

        Attributes
        ----------
        position : tuple
            The position of the node in the environment (e.g., (x, y)).
        age : int, optional
            The age of the node (default is 0).
        active : bool
            Whether the node is active or not.
        birth_time : float
            The timestamp when the node was created.
        connections : list
            A list of other nodes this node is connected to.
        angle : float
            The angle at which the node is oriented.

        Methods
        -------
        is_alive()
            Checks if the node is still active based on its age or environmental conditions.
        connect(other_node)
            Connects this node to another node, establishing a link between them.
    """
    def __init__(self, position, angle, age=0):
        self.position = position
        self.age = age
        self.active = True
        self.birth_time = time.time()
        self.connections = []
        self.angle = angle

    def is_alive(self):
        # Sprawdzenie, czy węzeł żyje, także biorąc pod uwagę strefy
        if time.time()  > 1:
            self.active = False
        return self.active

    def connect(self, other_node):
        self.connections.append(other_node)


def get_fungus_color(age):
    age = min(age, 100)
    if age < 20:
        return (255, 0, 0)
    elif age < 40:
        return (255, 165, 0)
    elif age < 60:
        return (204, 204, 0)
    elif age < 80:
        return (0, 255, 0)
    else:
        return (0, 0, 255)

def get_fungus_color_status(self):
    if self.active:
        return LIGHT_SKY_BLUE
    else:
        return LIGHT_GRAY

def reset_simulation(zone_count=32):
    env_instance = env.Environment(WIDTH, HEIGHT, zone_count=zone_count, zone_size=120)
    my_fungus_graph = graph.FungusGraph()
    start_position = (WIDTH // 2, HEIGHT // 2)
    while env_instance.get_growth_rate(start_position, 1.0) <= 0:
        start_position = (WIDTH // 2, HEIGHT // 2)
    initial_node = my_fungus_graph.add_node(start_position)
    active_nodes = [initial_node]
    return env_instance, my_fungus_graph, active_nodes



