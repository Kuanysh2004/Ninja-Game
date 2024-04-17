# Ninja Game

`описание проекта` 

2д платформер, то есть пиксельная игра где главный персонаж ниндзя и ему нужно выбраться из подземелья

`реализуемый функционал`

Возможность управления игроком с клавиатуры (wad, потом ещё подумаю на какую клаву поставить возможность атаки). Игра будет в сингл плеере, но с хорошей анимацией

`архитектура`

class Game: будет реализованая считавания нажатии клавиш, и отрисовка экрана

class Editor: вспомогательная структура, чтобы карты я мог создавать нажатием мышкой по полю (для обычного игрока этот класс будет недоступен (скорее всего потом будет run файл в котором этот класс просто не будет запускаться)); В нём использовано больше методов для считывания нажатии, на нажатие g включается режим когда объекты можно ставить по не целым координатам(для декора), кнопка o сохранить построенную карту в json файл, кнопка t для autotile, ну и на левую кнопку мыши поставить объект, а на правую удалить, через прокрутки "шарика по середине мышки" меняются пакеты с рисунками, а с зажатым левым шифтом варианты рисунка

class Tilemap:  def tiles_around(self, pos) - считывает объекты вокруг (оптимизация чтобы не рендерить  
                все объекты на карте, а только те что на экране)
                def save(self, path) - сохранить карту которую нарисовал
                def load(self, path) - загрузить уже существующую карту (json файл должен быть)
                def physics_rects_around(self, pos) - для того чтобы рендерить объекты с физикой которые на экране (тоже оптимизация типа)
                def autotile(self) - смешная штука, работает исключительно для ускорение создания карты (она не под все наборы рисунков работает правильно, потому что для каждого набора своё правило)
                def render(self, surf, offset=(0, 0)) - для рендеринга карты (отрисовка)

в папке utils.py два метода для загрузки картинок и class Animation:
def copy(self) - создает копию объекта данного класса
def update(self) - сама функция анимации, то есть просто меняет фрейм
def img(self) - возвращает текущую картинку из набора, тем самым у нас получается своего рода анимация

class PhysicsEntity находится в файле entities.py:
                def rect(self) - чтобы придать форму объекту
                def set_action(self, action) - метод чтобы для каждого объекта с физикой сделать анимацию, то есть он определяет какое действие сейчас делает объект
                def update(self, tilemap, movement=(0, 0)) - в зависимости от движения обновление нахождение объекта на карте
                def render(self, surf, offset=(0, 0)) - рендеринг

class Player(PhysicsEntity) наследник от PhysicsEntity:
                def update(self, tilemap, movement=(0, 0)) - добавлять логику анимации для игрока (ну там бег, прыжок, флип)

                ещё будет реализован метод для атаки

class NPC/Enemies(PhysicsEntity): ботики на карту чтобы было не скучно

может ещё будет отдельный класс или метод для добавления звуковых эффектов, и для создания главного меню/переключение между уровнями (p.s. если успею создать несколько уровней)
