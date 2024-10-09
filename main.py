import sys

import pygame
import pygame_gui

from explore_state import ExploreState
from fade_state import FadeState
from globals import FPS, NATURAL_SIZE, ASSETS_PATH, DATA_PATH
from map_definitions import small_room_map_def
from state_stack import StateStack
from ui import DialoguePanel, Textbox


def main():
    pygame.init()
    pygame.display.set_caption("Venatorum")
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN, vsync=1)
    display = pygame.surface.Surface(NATURAL_SIZE)

    # Add avatar, hero name, text and action buttons
    hero_image_path = ASSETS_PATH + "hero_portrait.png"
    message = '''A nation can survive its fools, and even the ambitious.
    But it cannot survive treason from within. An enemy at the gates is less formidable, for he is
    known and carries his banner openly. But the traitor moves amongst those
    within the gate freely, his sly whispers rustling through all the alleys, heard
    in the very halls of government itself.'''

    stack = StateStack(pygame_gui.UIManager(screen.get_size(), DATA_PATH + "themes/theme.json"))
    explore_state = ExploreState(
        stack=stack,
        map_def=small_room_map_def,
        start_tile_pos=(8, 9),
        display=display,
        manager=stack.manager
    )

    hero_pos = explore_state.game.get_hero_pos_for_ui()
    hero_pos = (hero_pos[0], hero_pos[1] - 32)


    stack.push(explore_state)

    stack.push(DialoguePanel(
                                hero_image=hero_image_path,
                                hero_name="Hero",
                                message=message,
                                manager=stack.manager,
                                end_callback=lambda: print("Dialogue ended")
                            )
    )

    
    stack.push(FadeState({"duration": 2, "alpha_start": 255, "alpha_finish": 0}, display))
    
    

    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            stack.process_event(event)

            if event.type == pygame.KEYDOWN:
                        
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update
        stack.update(dt)

        # Render
        stack.render(screen, display)
        pygame.display.flip()


if __name__ == '__main__':
    main()
