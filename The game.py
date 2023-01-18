import pygame
import os
import sys
import random

pygame.init()
size = width, height = 1600, 900
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Spy vs Sniper')
clock = pygame.time.Clock()

FPS = 20
STEP = 5
Is_time_end = False

spy_group = pygame.sprite.Group()
bot_group = pygame.sprite.Group()
patron_group = pygame.sprite.Group()
case_group = pygame.sprite.Group()
smoke_group = pygame.sprite.Group()

winner = None
spy_score = 0
sniper_score = 0


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением {fullname} не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Scheduler:
    def __init__(self):
        self.functions = list()

    def add_task(self, func, frames):
        self.functions.append([func, frames])

    def do_tick(self):
        for i in range(len(self.functions) - 1, -1, -1):
            func = self.functions[i][0]
            frames = self.functions[i][1]
            if frames == 1:
                func()
                self.functions.pop(i)
                continue
            self.functions[i][1] -= 1


class Spy(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        skin = ["body1.png", "body2.png", "body3.png", "body4.png"]
        self.image = load_image(random.choice(skin))
        self.rect = self.image.get_rect()
        while True:
            self.rect.x = random.randint(1, 1600)
            self.rect.y = random.randint(1, 900)
            if self.rect.x < 1515 and self.rect.x > 0 and self.rect.y < 730 and self.rect.y > -10:
                if self.rect.x < 396 or self.rect.x > 1208 or self.rect.y < 56 or self.rect.y > 460:
                    if self.rect.x < 1100 or self.rect.y < 640:
                        if self.rect.x < 1288 or self.rect.y < 565:
                            break
        self.vx = 0
        self.vy = 0

    def update(self):
        self.vx = 0
        self.vy = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] or key[pygame.K_a]:
            self.vx = -STEP
        elif key[pygame.K_RIGHT] or key[pygame.K_d]:
            self.vx = STEP
        if key[pygame.K_UP] or key[pygame.K_w]:
            self.vy = -STEP
        elif key[pygame.K_DOWN] or key[pygame.K_s]:
            self.vy = STEP
        x = self.rect.x + self.vx
        y = self.rect.y + self.vy
        if x < 1515 and x > 0 and y < 730 and y > -10:  # ограничение по карте
            if x < 396 or x > 1208 or y < 56 or y > 460:  # ограничение по бассейну
                if x < 1100 or y < 640:  # ограничение по часам
                    if x < 1288 or y < 565:  # ограничение по пулям
                        self.rect.x += self.vx
                        self.rect.y += self.vy


class Bot(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        skin = ["body1.png", "body2.png", "body3.png", "body4.png"]
        self.image = load_image(random.choice(skin))
        self.rect = self.image.get_rect()
        while True:
            self.rect.x = random.randint(1, 1600)
            self.rect.y = random.randint(1, 900)
            if self.rect.x < 1515 and self.rect.x > 0 and self.rect.y < 730 and self.rect.y > -10:
                if self.rect.x < 396 or self.rect.x > 1208 or self.rect.y < 56 or self.rect.y > 460:
                    if self.rect.x < 1100 or self.rect.y < 640:
                        if self.rect.x < 1288 or self.rect.y < 565:
                            break
        self.vx = 0
        self.vy = 0
        self.Flag = True

    def update(self):
        x = self.rect.x + self.vx
        y = self.rect.y + self.vy
        if x < 1515 and x > 0 and y < 730 and y > -10:  # ограничение по карте
            if x < 396 or x > 1208 or y < 56 or y > 460:  # ограничение по бассейну
                if x < 1100 or y < 640:  # ограничение по часам
                    if x < 1288 or y < 565:  # ограничение по пулям
                        self.rect.x += self.vx
                        self.rect.y += self.vy
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.kill()
        if self.Flag:
            self.Flag = False
            scheduler.add_task(self.change_move, FPS * (random.randint(0, 3) + random.choice([1, 0.5])))

    def change_move(self):
        self.Flag = True
        steps = ["up", "down", "left", "right", "stop"]
        step = random.choice(steps)
        if step == "left":
            self.vx = -STEP
            self.vy = 0
        elif step == "right":
            self.vx = STEP
            self.vy = 0
        elif step == "up":
            self.vx = 0
            self.vy = -STEP
        elif step == "down":
            self.vx = 0
            self.vy = STEP
        elif step == "stop":
            self.vx = 0
            self.vy = 0


class Smoke(pygame.sprite.Sprite):
    def __init__(self, group, smoke_x, smoke_y):
        super().__init__(group)
        self.image = load_image("smoke.png")
        self.rect = self.image.get_rect()
        self.rect.x = smoke_x - 450
        self.rect.y = smoke_y - 450
        scheduler.add_task(lambda: smoke_group.remove(self), FPS * 6)


class Patron(pygame.sprite.Sprite):
    def __init__(self, group, patron_x, patron_y):
        super().__init__(group)
        self.image = load_image("patron.png")
        self.rect = self.image.get_rect()
        self.rect.x = patron_x
        self.rect.y = patron_y


class Case(pygame.sprite.Sprite):

    def __init__(self, group, case_x, case_y):
        super().__init__(group)
        self.image = load_image("case.png")
        self.rect = self.image.get_rect()
        self.rect.x = case_x
        self.rect.y = case_y
        self.removed = False

    def update(self):
        if not self.removed and pygame.sprite.spritecollideany(self, spy_group):
            self.removed = True
            scheduler.add_task(lambda: case_group.remove(self), FPS * 5)


def terminate():
    pygame.quit()
    sys.exit()


def clear():
    global spy_group, patron_group, case_group, bot_group, smoke_group
    spy_group = pygame.sprite.Group()
    bot_group = pygame.sprite.Group()
    patron_group = pygame.sprite.Group()
    case_group = pygame.sprite.Group()
    smoke_group = pygame.sprite.Group()


def game_time():
    global Is_time_end
    Is_time_end = True


def start_screen():
    background = pygame.transform.scale(load_image('start_screen.png'), (1600, 900))
    screen.blit(background, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                elif event.key == pygame.K_SPACE:
                    return
        pygame.display.flip()
        clock.tick(FPS)


def main_screen():
    global scheduler, winner, sniper_score, spy_score
    background = pygame.transform.scale(load_image('main_map.png'), (1600, 900))
    pygame.mouse.set_visible(False)
    aim_cursor = load_image("aim.png")
    spy = Spy(spy_group)
    for i in range(60):
        Bot(bot_group)
    smoke_flag = True
    Case(case_group, 40, 100)
    Case(case_group, 1450, 600)
    Case(case_group, 40, 660)
    Case(case_group, 1450, 25)
    Case(case_group, 550, 20)
    Case(case_group, 850, 750)
    patron1 = Patron(patron_group, 1505, 760)
    patron2 = Patron(patron_group, 1435, 760)
    patron3 = Patron(patron_group, 1365, 760)
    scheduler = Scheduler()
    scheduler.add_task(game_time, FPS * 180)
    while True:
        scheduler.do_tick()
        mouse_cord = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                if event.key == pygame.K_SPACE:
                    if smoke_flag:
                        Smoke(smoke_group, spy.rect.x, spy.rect.y)
                        smoke_flag = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if len(patron_group) == 3:
                    patron_group.remove(patron3)
                elif len(patron_group) == 2:
                    patron_group.remove(patron2)
                elif len(patron_group) == 1:
                    patron_group.remove(patron1)
                if [i for i in spy_group if i.rect.collidepoint(mouse_cord)]:
                    winner = "sniper"
                    sniper_score += 1
                    clear()
                    return
        if not case_group or not patron_group:
            winner = "spy"
            spy_score += 1
            clear()
            return
        if Is_time_end:
            winner = "sniper"
            sniper_score += 1
            clear()
            return
        screen.blit(background, (0, 0))
        spy_group.update()
        spy_group.draw(screen)
        bot_group.update()
        bot_group.draw(screen)
        case_group.update()
        case_group.draw(screen)
        smoke_group.draw(screen)
        patron_group.update()
        patron_group.draw(screen)
        time = scheduler.functions[0][-1]
        font = pygame.font.Font(None, 90)
        time_txt = font.render(f"0{time // FPS // 60}:{time // FPS % 60}", True, pygame.Color('white'))
        screen.blit(time_txt, (1182, 820))
        screen.blit(aim_cursor, (mouse_cord[0] - 90, mouse_cord[1] - 90))
        pygame.display.flip()
        clock.tick(FPS)


def spy_win_screen():
    background = pygame.transform.scale(load_image('spy_win.png'), (1600, 900))
    screen.blit(background, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                elif event.key == pygame.K_SPACE:
                    return
        pygame.display.flip()
        clock.tick(FPS)


def sniper_win_screen():
    background = pygame.transform.scale(load_image('sniper_win.png'), (1600, 900))
    screen.blit(background, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                elif event.key == pygame.K_SPACE:
                    return
        pygame.display.flip()
        clock.tick(FPS)


def tutorial_screen():
    background = pygame.transform.scale(load_image('tutorial_screen.png'), (1600, 900))
    screen.blit(background, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                elif event.key == pygame.K_SPACE:
                    return
        pygame.display.flip()
        clock.tick(FPS)


def score_screen():
    background = pygame.transform.scale(load_image('score_screen.png'), (1600, 900))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 1000)
    sniper_score_txt = font.render(f"{sniper_score}", True, pygame.Color('white'))
    screen.blit(sniper_score_txt, (1125, 225))
    spy_score_txt = font.render(f"{spy_score}", True, pygame.Color('white'))
    screen.blit(spy_score_txt, (100, 225))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                elif event.key == pygame.K_SPACE:
                    return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
tutorial_screen()
while True:
    main_screen()
    if winner == "spy":
        spy_win_screen()
        winner = None
    if winner == "sniper":
        sniper_win_screen()
        winner = None
    score_screen()
