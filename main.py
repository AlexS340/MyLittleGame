import pygame
import sys
from candf import Level, Player, Camera, Inventory, Dialog

pygame.init()

FPS = 61
BULLETCHECKEVENT = 1
pygame.time.set_timer(BULLETCHECKEVENT, 100)
WALLCHECKEVENT = 2
pygame.time.set_timer(WALLCHECKEVENT, 500)

clock = pygame.time.Clock()
size = WIDTH, HEIGHT = 720, 720
screen = pygame.display.set_mode(size, pygame.SRCALPHA)

screen.fill(pygame.Color('black'))
player_sprite = pygame.sprite.Group()

running = True
lvl_tmp = 1
level = Level('lvl_1', screen)
player = Player(player_sprite, level.render())
inventory = Inventory(player)
camera = Camera()
dy, dx = 0, 0

intro = Dialog('lvl_1', (-1, -1))
intro.show_dialog(screen)


def terminate():
    pygame.quit()
    sys.exit()


def NEXT_FRAME():
    player.rect.x += dx
    player.rect.y += dy
    if player.check_walls(level.walls):
        player.rect.x -= dx
        player.rect.y -= dy

    camera.update(player)
    camera.apply(player)
    for sprite in level.level_sprites:
        camera.apply(sprite)

    level.update()
    inventory.render(screen)
    player_sprite.draw(screen)
    clock.tick(FPS)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()

        if event.type == pygame.KEYDOWN:
            if event.unicode == 'w':
                player.change_dir('up')
                dy = -4
            elif event.unicode == 'd':
                player.change_dir('right')
                dx = 4
            elif event.unicode == 'a':
                player.change_dir('left')
                dx = -4
            elif event.unicode == 's':
                player.change_dir('down')
                dy = 4
            elif event.unicode.isdigit():
                if int(event.unicode) != 0:
                    inventory.active_tool = int(event.unicode) - 1

        if event.type == pygame.KEYUP:
            if str(event.key) in '97 100':
                dx = 0
            if str(event.key) in '115 119':
                dy = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                inventory.on_click(screen, event.pos)
            elif event.button == 1 and len(inventory.backpack) > 0:
                try:
                    tool = inventory.backpack[inventory.active_tool]
                except:
                    print("err")

                if tool.type() == 'weapon':
                    level.fire(event.pos)

        if event.type == BULLETCHECKEVENT:
            for bullet in level.bullets:
                for wall in level.walls:
                    if pygame.sprite.collide_mask(bullet, wall):
                        bullet.kill()

        if event.type == WALLCHECKEVENT:
            active_sprites = player.wts(level.level_sprites)
            for active_sprite in active_sprites:
                for group in active_sprite.groups():
                    if group == level.dialogs:
                        dx, dy = 0, 0
                        active_sprite.show_dialog(screen)
                        active_sprite.remove(level.dialogs)

                    if group == level.chests:
                        inventory.update_inv(active_sprite.tools)
                        active_sprite.remove(level.chests)

                    if group == level.doors and len(inventory.backpack) > 0:
                        if inventory.backpack[inventory.active_tool].type() == 'key' \
                                and active_sprite.check_code(inventory.backpack[inventory.active_tool]):
                            lvl_tmp += 1
                            del level
                            level = Level('lvl_' + str(lvl_tmp), screen)
                            player.render(level.render())
                            print('NEXT LEVEL')
    NEXT_FRAME()
    pygame.display.flip()
    screen.fill((0, 0, 0))
