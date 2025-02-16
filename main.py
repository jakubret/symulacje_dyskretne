import pygame
from . import utils as ut
from . import environment as env
from . import graph as graph
import random
import time

def reset_simulation():
    env_instance = env.Environment(
        ut.WIDTH, ut.HEIGHT,
        max_resource = 1.0,
        resource_zero_level = 0.10,
        window_size = 8,
        hyphae_to_window_ratio = 0.3,
        biomass_threshold = 120,
        zone_count = 10,
        zone_size = 100,
        temp_min = 20,
        temp_max = 30,
        humidity_min = 60,
        humidity_max = 90
    )
    my_fungus_graph = graph.FungusGraph()
    start_position = (ut.WIDTH // 2, ut.HEIGHT // 2)

    while (env_instance.get_growth_rate(start_position, 1.0) <= 0 and
           env_instance.get_growth_cost(start_position, 1.0) >= 0.05):
        start_position = (random.randint(0, ut.WIDTH-1), random.randint(0, ut.HEIGHT-1))

    initial_node1 = my_fungus_graph.add_node(start_position, 0)
    initial_node2 = my_fungus_graph.add_node(start_position, 90)
    initial_node3 = my_fungus_graph.add_node(start_position, 180)
    initial_node4 = my_fungus_graph.add_node(start_position, 270)
    active_nodes = [initial_node1, initial_node2, initial_node3, initial_node4]
    # active_nodes = [initial_node1]
    return env_instance, my_fungus_graph, active_nodes

def main():
    pygame.init()
    screen = pygame.display.set_mode((ut.WIDTH, ut.HEIGHT))
    pygame.display.set_caption("Fungus Growth Simulation")
    clock = pygame.time.Clock()

    zone_count = 16
    report_interval = 5
    substrate_concentration = 1

    env_instance, my_fungus_graph, active_nodes = reset_simulation()
    running = True
    paused = False
    last_report_time = time.time()

    while running:
        screen.fill(ut.WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    env_instance, my_fungus_graph, active_nodes = reset_simulation()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    paused = not paused

        if not paused:
            active_nodes = my_fungus_graph.grow(active_nodes, env_instance, substrate_concentration)
            env_instance.draw(screen)
            my_fungus_graph.draw(screen, env_instance, substrate_concentration)

            active_nodes = [node for node in active_nodes if node.active]

            if time.time() - last_report_time >= report_interval:
                print(f"Active Nodes: {len(active_nodes)}, Total Nodes: {len(my_fungus_graph.nodes)}")
                last_report_time = time.time()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

    pygame.quit()

if __name__ == "__main__":
    main()
