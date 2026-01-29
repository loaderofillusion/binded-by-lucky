from my_game import GameView
import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel, UIDropdown
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
import sqlite3


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = UIManager()
        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)
        self.level_select = None
        self.setup_widgets()

    def setup_widgets(self):
        self.manager.clear()
        self.box_layout.clear()  # Очищаем box_layout

        label = UILabel(text="Binded by lucky", font_size=100, text_color=arcade.color.WHITE,
                        width=300, align="center")
        self.box_layout.add(label)

        label = UILabel(text="Меню", font_size=40, text_color=arcade.color.WHITE,
                        width=300, align="center")
        self.box_layout.add(label)

        btn_play = UIFlatButton(text="Играть", width=200, height=50)
        btn_play.on_click = lambda event: self.goToGame()
        self.box_layout.add(btn_play)

        btn_stats = UIFlatButton(text="Статистика", width=200, height=50)
        btn_stats.on_click = lambda event: self.goToStats()
        self.box_layout.add(btn_stats)

        dropdown = UIDropdown(options=["Обучение", "Уровень 1", "Уровень 2", "Уровень 3", "Уровень 4"], width=200)
        dropdown.on_change = lambda value: self.level_selected(value.new_value)
        self.box_layout.add(dropdown)

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.MODE_BEIGE)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def goToGame(self):
        if self.level_select:
            game_view = GameView()
            game_view.setup(self.level_select)
            self.window.show_view(game_view)

    def goToStats(self):
        stat_view = StatView()
        self.window.show_view(stat_view)

    def level_selected(self, level):
        if level[0] == 'О':
            self.level_select = 'tutorial0'
        else:
            self.level_select = f'lvl{level[-1]}'


class StatView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = UIManager()
        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)
        self.setup_widgets()
        self.window.set_fullscreen(True)  # Включаем fullscreen
        width, height = self.window.get_size()
        self.window.set_viewport(0, width, 0, height)

    def setup_widgets(self):
        self.manager.clear()
        self.box_layout.clear()

        label = UILabel(text="Binded by lucky", font_size=20, text_color=arcade.color.WHITE,
                        width=300, align="center")
        self.box_layout.add(label)

        label = UILabel(text="Статистика", font_size=20, text_color=arcade.color.WHITE,
                        width=300, align="center")
        self.box_layout.add(label)

        con = sqlite3.connect('stats.db')
        cur = con.cursor()
        is_passed = cur.execute(f'''SELECT is_passed FROM info''').fetchall()
        is_passed = list(map(lambda x: x[0], is_passed))
        levels = cur.execute(f'''SELECT lvl FROM info''').fetchall()
        levels = list(map(lambda x: x[0], levels))
        time_total = cur.execute(f'''SELECT time_total FROM info''').fetchall()
        time_total = list(map(lambda x: x[0], time_total))
        death_total = cur.execute(f'''SELECT death_total FROM info''').fetchall()
        death_total = list(map(lambda x: x[0], death_total))
        time_best = cur.execute(f'''SELECT time_best FROM info''').fetchall()
        time_best = list(map(lambda x: x[0], time_best))
        death_best = cur.execute(f'''SELECT death_best FROM info''').fetchall()
        death_best = list(map(lambda x: x[0], death_best))
        for i in range(-1, len(is_passed)):
            if i == -1:
                stats_label = UILabel(
                    text=f"         {'Статус':>55}{'Время':>35}{'Смерти':>25}{'Всего времени':>25}{'Всего смертей':>15}",
                    font_size=20, text_color=arcade.color.WHITE,
                    width=300, align="center")
            passed = 'Пройден'
            if is_passed[i] == 0:
                passed = 'Не пройден'
            if i == 0:
                stats_label = UILabel(
                    text=f"Обучение{passed:>30}{round(time_best[i], 3):>30}{death_best[i]:>30}{round(time_total[i], 3):>30}{death_total[i]:>30}",
                    font_size=20, text_color=arcade.color.WHITE,
                    width=300, align="left")
            elif i > 0:
                stats_label = UILabel(text=f"Уровень{levels[i]:}{passed:>30}{round(time_best[i], 3):>30}{death_best[i]:>30}{round(time_total[i], 3):>30}{death_total[i]:>30}", font_size=20, text_color=arcade.color.WHITE,
                            width=300, align="left")
            self.box_layout.add(stats_label)

        btn_menu = UIFlatButton(text="Меню", width=200, height=50)
        btn_menu.on_click = lambda event: self.goToMenu()
        self.box_layout.add(btn_menu)

        btn_clear = UIFlatButton(text="Стереть сохранения", width=200, height=50)
        btn_clear.on_click = lambda event: self.clear_saves()
        self.box_layout.add(btn_clear)

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.GRAY)
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def goToMenu(self):
        menu_view = MenuView()
        self.window.show_view(menu_view)

    def clear_saves(self):
        con = sqlite3.connect('stats.db')
        cur = con.cursor()
        cur.execute('''UPDATE info SET is_passed=0, time_total=0, time_best=0, death_best=0, death_total=0 WHERE is_passed=1''')
        con.commit()
        con.close()



if __name__ == "__main__":
    window = arcade.Window(fullscreen=True)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()
