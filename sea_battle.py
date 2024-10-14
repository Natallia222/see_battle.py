import random


# Классы исключений
class GameException(Exception):
    """Базовый класс для всех исключений в игре."""
    pass


class ShipPlacementException(GameException):
    """Ошибка размещения корабля на доске (выход за границы или пересечение)."""

    def __init__(self, message="Невозможно разместить корабль: нарушение правил расположения."):
        self.message = message
        super().__init__(self.message)


class ShotException(GameException):
    """Ошибка при выстреле (выстрел за границы или повторный выстрел)."""

    def __init__(self, message="Выстрел невозможен: нарушены правила атаки."):
        self.message = message
        super().__init__(self.message)


# Класс Dot для точек на поле
class Dot:
    """Класс для представления точки на игровом поле."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

    def is_valid(self, size):
        return 0 <= self.x < size and 0 <= self.y < size


# Класс Ship для описания кораблей
class Ship:
    """Класс для описания корабля."""

    def __init__(self, bow, length, orientation):
        self.bow = bow
        self.length = length
        self.orientation = orientation
        self.hits = 0

    def dots(self):
        """Метод для получения всех точек, занимаемых кораблем."""
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orientation == 0:
                cur_x += i  # горизонтально
            elif self.orientation == 1:
                cur_y += i  # вертикально

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def hit(self, shot):
        """Проверка, попали ли по кораблю."""
        return shot in self.dots()


# Класс Board для игрового поля
class Board:
    """Класс для представления игрового поля."""

    def __init__(self, size=6):
        self.size = size
        self.ships = []
        self.shots = []
        self.busy = []

    def add_ship(self, ship):
        """Добавление корабля на доску."""
        for dot in ship.dots():
            if not dot.is_valid(self.size) or dot in self.busy:
                raise ShipPlacementException(f"Невозможно разместить корабль на {dot}.")

        for dot in ship.dots():
            self.busy.append(dot)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship):
        """Добавление контура вокруг корабля."""
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for dot in ship.dots():
            for dx, dy in near:
                cur = Dot(dot.x + dx, dot.y + dy)
                if cur.is_valid(self.size) and cur not in self.busy:
                    self.busy.append(cur)

    def shoot(self, dot):
        """Обработка выстрела на доске."""
        if dot in self.shots:
            raise ShotException(f"Вы уже стреляли по этой точке: {dot}")

        self.shots.append(dot)

        for ship in self.ships:
            if ship.hit(dot):
                ship.hits += 1
                if ship.hits == ship.length:
                    self.ships.remove(ship)
                    self.contour(ship)
                    return "Корабль уничтожен!"
                return "Попадание!"
        return "Мимо!"

    def all_ships_sunk(self):
        """Проверка, потоплены ли все корабли."""
        return len(self.ships) == 0

    def display(self, show_ships=False):
        """Отображение игрового поля."""
        board = [["O"] * self.size for _ in range(self.size)]

        for shot in self.shots:
            board[shot.x][shot.y] = "T" if any(ship.hit(shot) for ship in self.ships) else "."

        if show_ships:
            for ship in self.ships:
                for dot in ship.dots():
                    board[dot.x][dot.y] = "S"

        print("\n".join(" ".join(row) for row in board))


# Класс Game для управления игровым процессом
class Game:
    """Класс для управления игровым процессом."""

    def __init__(self, size=6):
        self.size = size
        self.player_board = self.random_board()
        self.ai_board = self.random_board()
        self.turn = 0  # 0 - ходит игрок, 1 - ИИ

    def random_board(self):
        """Создание доски с случайной расстановкой кораблей."""
        board = Board(self.size)
        attempts = 0
        for length in [3, 2, 2, 1, 1, 1, 1]:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(
                    bow=Dot(random.randint(0, self.size - 1), random.randint(0, self.size - 1)),
                    length=length,
                    orientation=random.randint(0, 1)
                )
                try:
                    board.add_ship(ship)
                    break
                except ShipPlacementException:
                    continue
        return board

    def switch_turn(self):
        """Смена хода."""
        self.turn = 1 - self.turn

    def make_turn(self, dot):
        """Обработка хода игрока или ИИ."""
        if self.turn == 0:
            result = self.ai_board.shoot(dot)
        else:
            result = self.player_board.shoot(dot)
        print(result)
        self.switch_turn()

    def play(self):
        """Основной цикл игры."""
        while True:
            print("\nВаше поле:")
            self.player_board.display(show_ships=True)
            print("\nПоле ИИ:")
            self.ai_board.display()

            if self.turn == 0:
                print("Ваш ход:")
                x = int(input("Введите координату x: "))
                y = int(input("Введите координату y: "))
                dot = Dot(x, y)
            else:
                dot = Dot(random.randint(0, self.size - 1), random.randint(0, self.size - 1))
                print(f"Ход ИИ: {dot}")

            try:
                self.make_turn(dot)
            except ShotException as e:
                print(e)

            if self.ai_board.all_ships_sunk():
                print("Вы победили!")
                break
            elif self.player_board.all_ships_sunk():
                print("ИИ победил!")
                break
game = Game()
game.play()
