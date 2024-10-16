from typing import Any, Dict

import pygame
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core import IContainerLikeInterface

from state_stack import StackInterface
from ui import Selections, create_title, SelectItem
from ui.layout import Layout


class ItemMenuState:
    def __init__(self, parent: StackInterface, manager: pygame_gui.UIManager, display: pygame.Surface):
        from ingame_menu_state import InGameMenuState
        assert isinstance(parent, InGameMenuState)
        self.parent = parent
        self.manager = manager
        self.display = display
        self.layout = None
        self.category_menu = None
        self.category_menu_options = ["Use", "Key Items", "Exit"]
        self.title = None
        self.item_menus = None

    def _create_layout(self):
        self.layout = Layout(self.manager)
        self.layout.contract("screen", 120, 60)
        self.layout.split_horz("screen", "top", "bottom", 0.2)
        self.layout.split_vert("top", "title", "category", 0.6)
        self.layout.split_horz("bottom", "mid", "inv", 0.2)
        self._create_category_menu()

    def _create_category_menu(self):
        category_pos = (self.layout.left("category"), self.layout.top("category"))
        self.category_menu = Selections(
            container=self.layout,
            title="Select an option",
            options=self.category_menu_options,
            position=category_pos,
            width=self.layout.panels["category"].width,
            columns=1,
            manager=self.manager,
            end_callback=self._on_category_selection
        )

        top_size = (self.layout.panels["title"].width, self.layout.panels["title"].height)
        self.title = create_title(
            html_text="Items",
            pos=(self.layout.left("title") + top_size[0] * 0.02, self.layout.mid_y("title") - 20),
            size=top_size,
            manager=self.manager,
            container=self.layout,
        )

    def _render_data_item(
            self, item: Dict[str, Any], x: float, y: float, manager: UIManager, container: IContainerLikeInterface
    ) -> SelectItem:
        return self.parent.world.draw_item(item, x, y, manager, container)

    def _create_use_item_menu(self):
        inv_pos = (self.layout.left("inv"), self.layout.top("inv"))
        self.item_menus = Selections(
            title="Activated Items",
            data=self.parent.world.items,
            render_data_item=self._render_data_item,
            position=inv_pos,
            width=self.layout.panels["inv"].width,
            columns=1,
            manager=self.manager,
            container=self.layout,
            end_callback=self._on_item_selection
        )

    def _create_key_item_menu(self):
        inv_pos = (self.layout.left("inv"), self.layout.top("inv"))
        self.item_menus = Selections(
            title="Key's in pocket",
            data=self.parent.world.key_items,
            render_data_item=self._render_data_item,
            position=inv_pos,
            width=self.layout.panels["inv"].width,
            columns=1,
            manager=self.manager,
            container=self.layout,
            end_callback=self._on_item_selection
        )

    def _on_item_selection(self, selection: str) -> None:
        if selection == "Exit":
            self.close_menu()
        print(f"Selected Item {selection}")

    def _on_category_selection(self, selection: str) -> None:
        assert selection in self.category_menu_options, f"Invalid selection {selection}"
        if selection == "Exit":
            self.close_menu()
        elif selection == "Use":
            self._create_use_item_menu()
        elif selection == "Key Items":
            self._create_key_item_menu()

        self.category_menu.kill()
        self.category_menu = None

    def close_menu(self) -> None:
        self.layout.kill_layout()
        self.parent.state_machine.change("front")

    def enter(self) -> None:
        self._create_layout()

    def exit(self) -> None:
        self.layout.kill_layout()

    def render(self) -> None:
        self.layout.render()

    def update(self, dt) -> None:
        pass

    def process_event(self, event: pygame.event.Event):
        if self.category_menu is not None:
            self.category_menu.process_event(event)
        if self.item_menus is not None:
            self.item_menus.process_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.category_menu is not None:
                    self.close_menu()
                else:
                    self._create_category_menu()
                    self.item_menus.kill()
                    self.item_menus = None
