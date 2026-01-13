import arcade
from pyglet.graphics import Batch
from arcade.gui import UIManager, UIFlatButton, UITextureButton, UILabel, UIInputText, UITextArea, UISlider, UIDropdown, \
    UIMessageBox  # Это разные виджеты
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout  # А это менеджеры компоновки, как в pyQT
import sqlite3

class WinView(arcade.View):
    def __init__(self, deaths, time, level):
        super().__init__()
        arcade.set_background_color(arcade.color.GRAY)
        deaths -= 1
        self.deaths = deaths
        self.time = time
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
        self.level_select = None
        # заносим результаты в базу данных
        con = sqlite3.connect('stats.db')
        cur = con.cursor()
        is_passed = cur.execute(f'''SELECT is_passed FROM info WHERE lvl={level[-1]}''').fetchall()[0][0]
        time_total = cur.execute(f'''SELECT time_total FROM info WHERE lvl={level[-1]}''').fetchall()[0][0]
        death_total = cur.execute(f'''SELECT death_total FROM info WHERE lvl={level[-1]}''').fetchall()[0][0]
        time_best = cur.execute(f'''SELECT time_best FROM info WHERE lvl={level[-1]}''').fetchall()[0][0]
        death_best = cur.execute(f'''SELECT death_best FROM info WHERE lvl={level[-1]}''').fetchall()[0][0]
        if is_passed == 0:
            cur.execute(f'''UPDATE info SET is_passed = 1 WHERE lvl={level[-1]}''')
            cur.execute(f'''UPDATE info SET death_best = {deaths} WHERE lvl={level[-1]}''')
            cur.execute(f'''UPDATE info SET time_best = {time} WHERE lvl={level[-1]}''')

        cur.execute(f'''UPDATE info SET death_total = {death_total + deaths} WHERE lvl={level[-1]}''')
        cur.execute(f'''UPDATE info SET time_total = {time_total + time} WHERE lvl={level[-1]}''')
        if time_best > time:
            cur.execute(f'''UPDATE info SET time_best = {time} WHERE lvl={level[-1]}''')
        if death_best > deaths:
            cur.execute(f'''UPDATE info SET death_best = {deaths} WHERE lvl={level[-1]}''')


        con.commit()
        con.close()

    def setup_widgets(self):
        label = UILabel(text="Вы прошли уровень!",
                        font_size=20,
                        text_color=arcade.color.WHITE,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        label = UILabel(text=f"Время: {round(self.time, 3)} Cмерти: {self.deaths}",
                        font_size=20,
                        text_color=arcade.color.WHITE,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        flat_button = UIFlatButton(text="В меню", width=200, height=50, color=arcade.color.BLUE)
        flat_button.on_click = lambda event: self.goToMenu()
        self.box_layout.add(flat_button)



    def on_draw(self):
        self.clear()
        self.manager.draw()

    def goToMenu(self):
        from main import MenuView
        menu_view = MenuView()  # Создаём игровой вид
        self.window.show_view(menu_view)


