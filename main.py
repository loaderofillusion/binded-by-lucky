import arcade
from pyglet.graphics import Batch
from game import GameView
import arcade
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox  # Это разные виджеты
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout  # А это менеджеры компоновки, как в pyQT

SCREEN_W = 1280
SCREEN_H = 720
class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.GRAY)

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout()  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager    def on_draw(self):
        self.clear()

    def setup_widgets(self):
        label = UILabel(text="Binded by lucky",
                        font_size=20,
                        text_color=arcade.color.WHITE,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        label = UILabel(text="Меню",
                        font_size=20,
                        text_color=arcade.color.WHITE,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        flat_button = UIFlatButton(text="Плоская Кнопка", width=200, height=50, color=arcade.color.BLUE)
        flat_button.on_click = lambda event:self.goToGame()
        self.box_layout.add(flat_button)


        dropdown = UIDropdown(options=["Опция 1", "Опция 2", "Опция 3"], width=200)
        dropdown.on_change = lambda value: print(f"Выбрано: {value}")
        self.box_layout.add(dropdown)
    def on_draw(self):
        self.clear()
        self.manager.draw()

    def goToGame(self):
        game_view = GameView()  # Создаём игровой вид
        game_view.setup('lvl1')
        self.window.show_view(game_view)
window = arcade.Window(SCREEN_W, SCREEN_H, "Учимся ставить на паузу")
menu_view = MenuView()
window.show_view(menu_view)
arcade.run()