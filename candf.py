import os
import pygame
import sys
import math

pygame.init()
pygame.font.init()
size = WIDTH, HEIGHT = 1280, 720
SIZE = 80
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def level_init(name):
    with open(os.path.join('levels/' + name, name) + '.txt', 'r', encoding='utf-8') as f:
        lvl = f.read().split('\n')
    with open(os.path.join('levels/' + name, name + '_textures') + '.txt', 'r', encoding='utf-8') as f:
        lvl_textures = f.read().split('\n')

    width = max(map(len, lvl))
    return width, len(lvl), lvl, lvl_textures


def terminate():
    pygame.quit()
    sys.exit()


class Level:
    sprite_image = {'.': load_image('floor.png'), '#': load_image('wall.png'), 'c': load_image('chest.png'),
                    'N': load_image('door.png'), 'p': load_image('police.png', -1), ' ': load_image('empty.png'),
                    'b': load_image('body.png'), 'w': load_image('window.png'), 'k': load_image('blood.png')}

    def __init__(self, name, screen):
        self.width, self.height, self.board, self.textures = level_init(name)
        self.screen = screen
        self.name = name
        self.level_sprites = pygame.sprite.Group()
        self.dialogs = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.chests = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

    def render(self):
        p_x, p_y = None, None
        for x in range(self.width):
            for y in range(self.height):
                if self.board[y][x] == '@':
                    p_x, p_y = x, y
                if self.board[y][x] == 'd':
                    cella = pygame.sprite.Sprite(self.level_sprites)
                    cella.image = self.sprite_image['.']
                    cella.rect = cella.image.get_rect()
                    cella.rect.x = x * SIZE
                    cella.rect.y = y * SIZE
                    cell = Dialog(self.name, (x, y), self.level_sprites, self.dialogs)
                elif self.board[y][x] == '#':
                    cell = pygame.sprite.Sprite(self.level_sprites, self.walls)
                elif self.board[y][x] == 'c':
                    cell = Chest(self.name, (x, y), self.level_sprites, self.chests)
                elif self.board[y][x] == 'N':
                    cell = Door(self.name, (x, y), self.level_sprites, self.doors)
                else:
                    cell = pygame.sprite.Sprite(self.level_sprites)
                cell.image = self.sprite_image[self.textures[y][x]]
                cell.rect = cell.image.get_rect()
                cell.rect.x = x * SIZE
                cell.rect.y = y * SIZE
        return p_x, p_y

    def update(self):
        self.level_sprites.draw(self.screen)
        if len(self.bullets) > 0:
            for b in self.bullets:
                b.update()
            self.bullets.draw(self.screen)

    def fire(self, pos):
        x, y = pos
        x, y = x - WIDTH // 2, HEIGHT // 2 - y
        # по четвертям
        if x > 0 and y > 0:
            angle = math.atan(x / y) - 2 * math.pi
        elif x < 0 and y > 0:
            angle = math.atan(x / y)
        elif x < 0 and y < 0:
            angle = math.atan(x / y) - math.pi
        else:
            angle = math.atan(x / y) - math.pi
        angle -= math.pi / 2
        Bullet(angle, self.bullets)


class Player(pygame.sprite.Sprite):
    def __init__(self, group, pos):
        x, y = pos
        super().__init__(group)
        self.image = load_image('player.png', -1)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = x * SIZE, y * SIZE
        self.angle = 90

    def change_dir(self, dir):
        if dir == 'up':
            self.image = pygame.transform.rotate(self.image, -self.angle)
            self.image = pygame.transform.rotate(self.image, 180)
            self.angle = 180

        elif dir == 'down':
            self.image = pygame.transform.rotate(self.image, -self.angle)
            self.image = pygame.transform.rotate(self.image, 0)
            self.angle = 0

        elif dir == 'left':
            self.image = pygame.transform.rotate(self.image, -self.angle)
            self.image = pygame.transform.rotate(self.image, -90)
            self.angle = -90

        elif dir == 'right':
            self.image = pygame.transform.rotate(self.image, -self.angle)
            self.image = pygame.transform.rotate(self.image, 90)
            self.angle = 90

    def check_walls(self, walls):
        for wall in walls:
            if pygame.sprite.collide_mask(self, wall):
                return True
        return False

    def wts(self, all_sprites):
        ans = []
        for sprite in all_sprites:
            if pygame.sprite.collide_mask(self, sprite):
                ans.append(sprite)
        return ans

    def render(self, pos):
        x, y = pos
        self.rect.x, self.rect.y = x * SIZE, y * SIZE


class Dialog(pygame.sprite.Sprite):
    def __init__(self, lvl_name, pos, *groap):
        super().__init__(groap)
        self.font = pygame.font.SysFont('Segoe Print', 20, False, False)
        self.dia = self.load_dia(lvl_name, pos)
        self.face = None

    def load_dia(self, lvl_name, pos):
        with open(os.path.join('levels/' + lvl_name,
                               'dia' + f'{pos[0] + 1}_{pos[1] + 1}') + '.txt',
                  'r', encoding='utf-8') as f:
            dia = f.read().split('\n')
        return dia

    def show_dialog(self, screen):
        for text in self.dia:
            if text.split(':')[0] == 'image':
                self.face = load_image(text.split(':')[1])
                continue
            pygame.draw.rect(screen, pygame.color.Color('brown'), (0, HEIGHT - 100, 1000, 100))
            image = self.font.render(text, 1, pygame.color.Color('white'))
            if self.face is not None:
                screen.blit(self.face, (1000, HEIGHT - 100))
            screen.blit(image, (100, HEIGHT - 100))

            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.K_ESCAPE:
                        running = False
                    if event.type == pygame.QUIT:
                        terminate()
                pygame.display.flip()


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Inventory:
    def __init__(self, player):
        self.screen = pygame.display.set_mode(size, pygame.SRCALPHA)
        self.player = player
        self.backpack = []
        self.prop = {'hp': 100, 'ammo': 0}
        self.active_tool = 0

    def render(self, game_screen, click=False):
        if not click:
            """ Здоровье """
            font = pygame.font.SysFont(None, 40)
            image = font.render('HP ' + str(self.prop['hp']), 1, pygame.color.Color('red'))
            game_screen.blit(image, (10, 10))
            game_screen.blit(self.screen, (0, 0))
            """ Рюкзак """
            board = Board(self.backpack)
            board.render(self.active_tool)
        else:
            board = Board(self.backpack)
            self.active_tool = board.get_click(click)
            board.render(self.active_tool)

    def update_inv(self, tools):
        self.backpack.extend(tools)

    def on_click(self, screen, pos):
        self.render(screen, pos)


class Chest(pygame.sprite.Sprite):
    def __init__(self, lvl_name, pos, *group):
        super().__init__(group)
        self.tools = self.load_inv(lvl_name, pos)

    def load_inv(self, lvl_name, pos):
        with open(os.path.join('levels/' + lvl_name,
                               'chest' + f'{pos[0] + 1}_{pos[1] + 1}') + '.txt',
                  'r', encoding='utf-8') as f:
            tools = f.read().split('\n')
        new_tools = []
        for tool in tools:
            if tool.split(':')[0] == 'weapon':
                new_tools.append(Weapon(tool.split(':')[1].split(',')))
            elif tool.split(':')[0] == 'key':
                new_tools.append(Key(tool.split(':')))

        return new_tools


class Door(pygame.sprite.Sprite):
    def __init__(self, lvl_name, pos, *group):
        super().__init__(group)
        self.code = self.load_code(lvl_name, pos)

    def load_code(self, lvl_name, pos):
        with open(os.path.join('levels/' + lvl_name,
                               'door' + f'{pos[0] + 1}_{pos[1] + 1}') + '.txt',
                  'r', encoding='utf-8') as f:
            code = f.read().split('\n')
        return code[0]

    def check_code(self, key):
        if self.code == key.code:
            return True
        return False


class Weapon:
    def __init__(self, tmp):
        damage, code = tmp[0], tmp[1]
        self.damage = damage
        self.image = load_image('wep' + code + '.png', -1)
        self.bullets = pygame.sprite.Group()

    def get_image(self):
        return self.image

    def type(self):
        return 'weapon'


class Bullet(pygame.sprite.Sprite):
    def __init__(self, angle, *groap):
        super().__init__(groap)
        self.angle = angle
        self.image = load_image('bullet.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2
        self.speed = 10

    def update(self):
        self.rect.x += int(self.speed * math.cos(self.angle))
        self.rect.y += int(self.speed * math.sin(self.angle))


class Key:
    def __init__(self, tmp):
        self.code = tmp[1]
        self.image = load_image('key' + '.png', -1)

    def get_image(self):
        return self.image

    def type(self):
        return 'key'


class Board:
    # создание поля
    def __init__(self, backpack):
        self.width = len(backpack)
        self.board = backpack
        self.left = 100
        self.top = 650
        self.cell_size = 50

    def render(self, at):
        self.at = at
        for cell in range(len(self.board)):
            clr = (255, 255, 255, 50)
            if cell == self.at:
                tmp = 4
            else:
                tmp = 2
            screen.blit(self.board[cell].get_image(), (self.left + cell * self.cell_size, self.top))
            pygame.draw.rect(screen, clr,
                             (self.left + cell * self.cell_size, self.top,
                              self.cell_size, self.cell_size), tmp)

    def get_cell(self, mouse_pos):
        x, y = mouse_pos[0] - self.left, mouse_pos[1] - self.top
        x_ans = int(x / self.cell_size)
        y_ans = int(y / self.cell_size)
        if x_ans >= self.width or y_ans >= 1 or x < 0 or y < 0:
            return None
        return x_ans, y_ans

    def on_click(self, cell_coords):
        return cell_coords[0]

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell is not None:
            return self.on_click(cell)
