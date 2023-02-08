from random import randint


class Dot:          # Создаем класс для точек на поле,для каждой точки координаты по осьям x и y
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # применяем метод __eq__ чтобы эффективно проверять равенство для точек
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):  # Создаем классы для отлова ошибок
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Координата не существует,пожалуйста сделайте еще один ход!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Эта координата ужа была использована,попробуйте другую!"


class BoardWrongShipException(BoardException):
    pass


class Ship:   # Класс описывающий корабль(Длина,направление,количество точек)
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):  # Метод Dots возвращающая список всех точек корабля
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shoten(self, shot):
        return shot in self.dots


class Board: # Класс описывающий игровую доску
    def __init__(self, hid=False, size=6):  # Двумерный список(матрица) хранящая состояние каждой из клеток.
        self.size = size
        self.hid = hid  # для того чтобы скрыть корабль противника

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):  # функция add_ship, который ставит корабль на доску

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):  # функция contour, который обводит корабль по контуру,занимая соседние с кораблем клетки.
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d): # Функция которая для точки возвращает True, если точка за пределами поля
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):  # делает выстрел по доске и выводит исключение если координаты неверные
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "Т"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:  # Описывает игроков,является родительским классом для обоих играющих сторон
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self): # Создаем функцию, не даем ей значение, так как необходима разная реализация для классов игроков.
        raise NotImplementedError()

    def move(self): # Делаем ход в игре
        while True:
            try:   # отлавливаем исключения
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):  # Класс соперника, необходимо определить функцию ask на выбор случайной точки
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):  # Класс игрока, необходимо определить ask на ввод координат из консоли
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:   # Класс описывающий игру.
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self): # генерирует случайную доску
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self): # Случайным образом расставляет кораблики на досках
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self): # Вывод приветствия и правил игры
        print("-------------------")
        print()
        print("  Игра морской бой   ")
        print()
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self): # метод с самим игровым циклом. Проверяем сколько не пробитых кораблей осталось,завершаем игру.
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):   # Для запуска игры. Сначала вызываем приветствие потом доски
        self.greet()
        self.loop()


g = Game()    # Присваиваем класс game
g.start()     # Вызываем ее методом старт
