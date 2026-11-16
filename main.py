import re
import socket
import ipaddress
import sqlite3
import webbrowser
from urllib.parse import quote
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.utils import platform

KV = r"""
#:kivy 2.3.0
<NavButton@Button>:
    background_normal: ''
    background_color: (0.10, 0.16, 0.22, 1)
    color: (0.83, 0.90, 0.97, 1)
    font_size: '13sp'
<PrimaryButton@Button>:
    background_normal: ''
    background_color: (0.04, 0.42, 0.34, 1)
    color: (0.96, 1, 1, 1)
    size_hint_y: None
    height: '48dp'
    font_size: '14sp'
<DarkInput@TextInput>:
    multiline: False
    size_hint_y: None
    height: '48dp'
    background_normal: ''
    background_active: ''
    background_color: (0.08, 0.12, 0.17, 1)
    foreground_color: (0.92, 0.95, 1, 1)
    cursor_color: (0.2, 0.8, 0.65, 1)
    padding: '12dp', '14dp'
BoxLayout:
    orientation: 'vertical'
    padding: '14dp'
    spacing: '10dp'
    canvas.before:
        Color:
            rgba: (0.035, 0.05, 0.075, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        size_hint_y: None
        height: '54dp'
        orientation: 'vertical'
        Label:
            text: '[b]GEOSINT X[/b]'
            markup: True
            color: (0.25, 0.9, 0.7, 1)
            font_size: '24sp'
            halign: 'left'
            text_size: self.size
        Label:
            text: 'MOBILE INTELLIGENCE WORKSPACE'
            color: (0.45, 0.56, 0.68, 1)
            font_size: '9sp'
            halign: 'left'
            text_size: self.size
    BoxLayout:
        size_hint_y: None
        height: '42dp'
        spacing: '6dp'
        NavButton:
            text: 'ПОИСК'
            on_release: app.show_tab('search')
        NavButton:
            text: 'ИСТОРИЯ'
            on_release: app.show_tab('history')
        NavButton:
            text: 'БАЗА'
            on_release: app.show_tab('database')
    ScreenManager:
        id: screens
        Screen:
            name: 'search'
            BoxLayout:
                orientation: 'vertical'
                spacing: '10dp'
                Spinner:
                    id: mode
                    text: 'Проверка домена'
                    values: ['Проверка домена', 'Анализ IP', 'Проверка email', 'Проверка телефона', 'Поиск публичного ника']
                    size_hint_y: None
                    height: '48dp'
                    background_normal: ''
                    background_color: (0.09, 0.14, 0.2, 1)
                    color: (0.9, 0.94, 1, 1)
                DarkInput:
                    id: query
                    hint_text: 'Введите значение'
                PrimaryButton:
                    text: 'ЗАПУСТИТЬ АНАЛИЗ'
                    on_release: app.analyze()
                BoxLayout:
                    size_hint_y: None
                    height: '38dp'
                    spacing: '6dp'
                    NavButton:
                        text: 'КОПИРОВАТЬ'
                        on_release: app.copy_result()
                    NavButton:
                        text: 'ОТКРЫТЬ ССЫЛКУ'
                        on_release: app.open_result_link()
                Label:
                    text: 'РЕЗУЛЬТАТ'
                    size_hint_y: None
                    height: '22dp'
                    color: (0.25, 0.9, 0.7, 1)
                    halign: 'left'
                    text_size: self.size
                ScrollView:
                    do_scroll_x: False
                    Label:
                        id: output
                        text: 'выбери модуль и введи данные.'
                        size_hint_y: None
                        height: max(self.texture_size[1] + dp(24), dp(130))
                        text_size: self.width - dp(16), None
                        halign: 'left'
                        valign: 'top'
                        color: (0.78, 0.84, 0.91, 1)
                        padding: '8dp', '8dp'
        Screen:
            name: 'history'
            BoxLayout:
                orientation: 'vertical'
                spacing: '8dp'
                Label:
                    text: '[b]ИСТОРИЯ ЗАПРОСОВ[/b]'
                    markup: True
                    size_hint_y: None
                    height: '32dp'
                    color: (0.25, 0.9, 0.7, 1)
                    halign: 'left'
                    text_size: self.size
                BoxLayout:
                    size_hint_y: None
                    height: '42dp'
                    spacing: '6dp'
                    NavButton:
                        text: 'ОБНОВИТЬ'
                        on_release: app.refresh_history()
                    NavButton:
                        text: 'ОЧИСТИТЬ'
                        on_release: app.clear_history()
                ScrollView:
                    do_scroll_x: False
                    Label:
                        id: history_text
                        text: 'история пока пуста.'
                        size_hint_y: None
                        height: max(self.texture_size[1] + dp(24), dp(120))
                        text_size: self.width - dp(16), None
                        halign: 'left'
                        valign: 'top'
                        color: (0.78, 0.84, 0.91, 1)
                        padding: '8dp', '8dp'
        Screen:
            name: 'database'
            BoxLayout:
                orientation: 'vertical'
                spacing: '8dp'
                Label:
                    text: '[b]ЛОКАЛЬНАЯ БАЗА РЕЗУЛЬТАТОВ[/b]'
                    markup: True
                    size_hint_y: None
                    height: '32dp'
                    color: (0.25, 0.9, 0.7, 1)
                    halign: 'left'
                    text_size: self.size
                Label:
                    id: db_stats
                    text: 'загрузка...'
                    size_hint_y: None
                    height: '30dp'
                    color: (0.78, 0.84, 0.91, 1)
                    halign: 'left'
                    text_size: self.size
                NavButton:
                    text: 'ОБНОВИТЬ СТАТИСТИКУ'
                    size_hint_y: None
                    height: '44dp'
                    on_release: app.refresh_database()
                Label:
                    text: 'данные хранятся локально на устройстве. экспорт и синхронизация не включены.'
                    color: (0.45, 0.56, 0.68, 1)
                    font_size: '12sp'
                    halign: 'left'
                    valign: 'top'
                    text_size: self.size
"""

class GeosintApp(App):
    def build(self):
        self.title = "GEOSINT X"
        self.last_link = None
        self.db = None
        self.db_path = None
        return Builder.load_string(KV)

    def on_start(self):
        self.init_db()
        self.refresh_history()
        self.refresh_database()

    def init_db(self):
        if platform == "android":
            self.db_path = self.user_data_dir + "/geosint_x.db"
        else:
            self.db_path = "geosint_x.db"
        self.db = sqlite3.connect(self.db_path)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                module TEXT NOT NULL,
                query TEXT NOT NULL,
                result TEXT NOT NULL
            )
        """)
        self.db.commit()

    def show_tab(self, name):
        self.root.ids.screens.current = name
        if name == "history":
            self.refresh_history()
        elif name == "database":
            self.refresh_database()

    def set_output(self, value, link=None):
        self.root.ids.output.text = value
        self.last_link = link

    def save_record(self, module, query, result):
        self.db.execute(
            "INSERT INTO searches(created_at,module,query,result) VALUES(?,?,?,?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), module, query, result)
        )
        self.db.commit()
        self.refresh_database()

    def analyze(self):
        mode = self.root.ids.mode.text
        value = self.root.ids.query.text.strip()
        if not value:
            self.set_output("ошибка: сначала введи значение.")
            return
        self.last_link = None
        try:
            if mode == "Проверка домена":
                result, link = self.domain_check(value)
            elif mode == "Анализ IP":
                result, link = self.ip_check(value)
            elif mode == "Проверка email":
                result, link = self.email_check(value)
            elif mode == "Проверка телефона":
                result, link = self.phone_check(value)
            else:
                result, link = self.username_check(value)
            self.set_output(result, link)
            self.save_record(mode, value, result)
        except Exception as exc:
            self.set_output(f"ошибка анализа: {exc}")

    def domain_check(self, value):
        domain = value.lower().strip().rstrip(".")
        if "://" in domain:
            domain = domain.split("://", 1)[1].split("/", 1)[0]
        if "/" in domain:
            domain = domain.split("/", 1)[0]
        if not re.fullmatch(r"(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", domain):
            return "домен имеет некорректный формат.", None
        lines = [f"ДОМЕН: {domain}"]
        try:
            infos = socket.getaddrinfo(domain, None)
            addresses = sorted({x[4][0] for x in infos})
            lines.append("DNS A/AAAA:")
            lines.extend(f"  • {a}" for a in addresses)
        except socket.gaierror:
            lines.append("DNS: записи не найдены или сеть недоступна.")
        link = f"https://rdap.org/domain/{quote(domain)}"
        lines.append(f"RDAP: {link}")
        lines.append(f"DNS: https://dns.google/resolve?name={quote(domain)}")
        return "\n".join(lines), link

    def ip_check(self, value):
        try:
            addr = ipaddress.ip_address(value)
        except ValueError:
            return "некорректный IPv4/IPv6 адрес.", None
        link = f"https://rdap.org/ip/{quote(str(addr))}"
        lines = [
            f"IP: {addr}", f"ВЕРСИЯ: IPv{addr.version}",
            f"ГЛОБАЛЬНЫЙ: {'да' if addr.is_global else 'нет'}",
            f"ЧАСТНЫЙ: {'да' if addr.is_private else 'нет'}",
            f"LOOPBACK: {'да' if addr.is_loopback else 'нет'}",
            f"ЗАРЕЗЕРВИРОВАН: {'да' if addr.is_reserved else 'нет'}",
            f"RDAP: {link}"
        ]
        return "\n".join(lines), link

    def email_check(self, value):
        email = value.strip()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            return "формат email некорректен.", None
        domain = email.rsplit("@", 1)[1].lower()
        link = f"https://dns.google/resolve?name={quote(domain)}&type=MX"
        lines = [f"EMAIL: {email}", "ФОРМАТ: корректный"]
        try:
            socket.getaddrinfo(domain, 25)
            lines.append("ДОМЕН: разрешается через DNS")
        except socket.gaierror:
            lines.append("ДОМЕН: DNS-запись не найдена или сеть недоступна")
        lines.extend([
            "ПОЧТОВЫЙ ЯЩИК: существование не подтверждено.",
            f"MX LOOKUP: {link}"
        ])
        return "\n".join(lines), link

    def phone_check(self, value):
        cleaned = re.sub(r"[\s().-]", "", value)
        if not re.fullmatch(r"\+?[0-9]{7,15}", cleaned):
            return "номер должен содержать 7–15 цифр; допускается начальный +.", None
        result = (
            f"ВВОД: {value}\nНОРМАЛИЗОВАНО: {cleaned}\n"
            "ФОРМАТ: допустимый по длине\n"
            "ВЛАДЕЛЕЦ И ТОЧНАЯ ГЕОЛОКАЦИЯ: не определяются."
        )
        return result, None

    def username_check(self, value):
        name = value.strip().lstrip("@")
        if not re.fullmatch(r"[A-Za-z0-9._-]{2,64}", name):
            return "допустимы 2–64 символа: латиница, цифры, точка, дефис, подчёркивание.", None
        link = f"https://www.google.com/search?q={quote(chr(34)+name+chr(34))}"
        result = (
            f"НИК: {name}\nНОРМАЛИЗОВАНО: {name.lower()}\n"
            "ПУБЛИЧНЫЙ ПОИСК:\n"
            f"Google: {link}\n"
            f"GitHub: https://github.com/{quote(name)}\n"
            f"Reddit: https://www.reddit.com/user/{quote(name)}/\n"
            "наличие аккаунта автоматически не подтверждается."
        )
        return result, link

    def copy_result(self):
        Clipboard.copy(self.root.ids.output.text)
        Popup(title="GEOSINT X", content=Label(text="результат скопирован"),
              size_hint=(.75, .22)).open()

    def open_result_link(self):
        if self.last_link:
            webbrowser.open(self.last_link)
        else:
            Popup(title="GEOSINT X", content=Label(text="для этого результата нет внешней ссылки"),
                  size_hint=(.82, .22)).open()

    def refresh_history(self):
        if not self.db:
            return
        rows = self.db.execute(
            "SELECT created_at,module,query FROM searches ORDER BY id DESC LIMIT 100"
        ).fetchall()
        if not rows:
            value = "история пока пуста."
        else:
            value = "\n\n".join(
                f"{r[0]}\n[{r[1]}] {r[2]}" for r in rows
            )
        self.root.ids.history_text.text = value

    def clear_history(self):
        self.db.execute("DELETE FROM searches")
        self.db.commit()
        self.refresh_history()
        self.refresh_database()

    def refresh_database(self):
        if not self.db:
            return
        total = self.db.execute("SELECT COUNT(*) FROM searches").fetchone()[0]
        modules = self.db.execute(
            "SELECT module,COUNT(*) FROM searches GROUP BY module ORDER BY module"
        ).fetchall()
        lines = [f"ВСЕГО СОХРАНЕНО: {total}"]
        lines.extend(f"{name}: {count}" for name, count in modules)
        self.root.ids.db_stats.text = "\n".join(lines)

if __name__ == "__main__":
    GeosintApp().run()
