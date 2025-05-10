import pygame
import random

# Инициализация
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space hawk")

# Цветове
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Зареждане на изображения
background_image = pygame.image.load('data/background.png')
player_image = pygame.image.load('data/player.png')
bullet_image = pygame.image.load('data/bullet.png')
invader_sprites = [
    pygame.image.load('data/invader1.png'),
    pygame.image.load('data/invader2.png'),
    pygame.image.load('data/invader3.png'),
    pygame.image.load('data/invader4.png')
]
boss_image = pygame.image.load('data/boss.png')
boss_bullet_image = pygame.image.load('data/boss_bullet.png')
boss_gameover_image = pygame.image.load('data/boss_gameover.png')

# Зареждане на звуци
pygame.mixer.music.load("data/background_music.wav")
pygame.mixer.music.play(-1)
shoot_sound = pygame.mixer.Sound("data/shoot.MP3")
death_sound = pygame.mixer.Sound("data/death.wav")

# Параметри
player_width, player_height = 70, 80
bullet_width, bullet_height = 30, 50
invader_width, invader_height = 40, 40
boss_width, boss_height = 200, 160

player_speed = 5
bullet_speed = 5
bullet_delay = 300
invader_speed = 5
boss_speed = 3
boss_bullet_speed = 4
boss_shoot_delay = 1200

font = pygame.font.SysFont("arial", 30)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

class Player:
    def __init__(self):
        self.x = WIDTH // 2 - player_width // 2
        self.y = HEIGHT - 90
        self.image = pygame.transform.scale(player_image, (player_width, player_height))

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= player_speed
        elif direction == "right" and self.x < WIDTH - player_width:
            self.x += player_speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(bullet_image, (bullet_width, bullet_height))

    def move(self):
        self.y -= bullet_speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Invader:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.speed = invader_speed
        self.image = pygame.transform.scale(sprite, (invader_width, invader_height))

    def move(self):
        self.x += self.speed
        if self.x <= 0 or self.x >= WIDTH - invader_width:
            self.speed *= -1
            self.y += 20

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class Boss:
    def __init__(self):
        self.x = WIDTH // 2 - boss_width // 2
        self.y = 50
        self.health = 20
        self.speed = boss_speed
        self.image = pygame.transform.scale(boss_image, (boss_width, boss_height))
        self.last_shot_time = 0

    def move(self):
        self.x += self.speed
        if self.x <= 0 or self.x >= WIDTH - boss_width:
            self.speed *= -1

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def shoot(self, current_time):
        if current_time - self.last_shot_time > boss_shoot_delay:
            self.last_shot_time = current_time
            return BossBullet(self.x + boss_width // 2 - 30, self.y + boss_height)
        return None

class BossBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(boss_bullet_image, (60, 80))

    def move(self):
        self.y += boss_bullet_speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

class SpaceInvaders:
    def __init__(self):
        self.menu_active = True
        self.paused = False
        self.instructions_active = False
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.bullets = []
        self.invaders = []
        self.boss = None
        self.boss_bullets = []
        self.score = 0
        self.level = 1
        self.lives = 3
        self.last_bullet_time = 0
        self.create_invaders()
        self.game_over = False
        self.boss_killed_player = False
        self.paused = False

    def create_invaders(self):
        if self.level % 5 == 0:
            self.boss = Boss()
        else:
            sprite_index = (self.level - 1) % 4
            sprite = invader_sprites[sprite_index]
            self.invaders.clear()
            for i in range(6):
                for j in range(4):
                    self.invaders.append(Invader(50 + i * 100, 50 + j * 50, sprite))

    def handle_collisions(self):
        for bullet in self.bullets[:]:
            if self.boss:
                if bullet.x < self.boss.x + boss_width and bullet.x + bullet_width > self.boss.x and \
                   bullet.y < self.boss.y + boss_height and bullet.y + bullet_height > self.boss.y:
                    self.bullets.remove(bullet)
                    self.boss.health -= 1
                    if self.boss.health <= 0:
                        self.score += 1000
                        self.boss = None
                        self.level += 1
                        self.create_invaders()
            else:
                for invader in self.invaders[:]:
                    if bullet.x < invader.x + invader_width and bullet.x + bullet_width > invader.x and \
                       bullet.y < invader.y + invader_height and bullet.y + bullet_height > invader.y:
                        self.invaders.remove(invader)
                        self.bullets.remove(bullet)
                        self.score += 100
                        break

        for boss_bullet in self.boss_bullets[:]:
            if boss_bullet.x < self.player.x + player_width and boss_bullet.x + 60 > self.player.x and \
               boss_bullet.y < self.player.y + player_height and boss_bullet.y + 80 > self.player.y:
                self.boss_bullets.remove(boss_bullet)
                death_sound.play()
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    self.boss_killed_player = True

        for invader in self.invaders[:]:
            if invader.x < self.player.x + player_width and invader.x + invader_width > self.player.x and \
               invader.y < self.player.y + player_height and invader.y + invader_height > self.player.y:
                self.invaders.remove(invader)
                death_sound.play()
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    self.boss_killed_player = False

    def level_up(self):
        if not self.invaders and not self.boss:
            self.level += 1
            self.create_invaders()

    def show_menu(self):
        screen.blit(pygame.transform.scale(background_image, (WIDTH, HEIGHT)), (0, 0))
        draw_text("Space hawk", font, WHITE, screen, WIDTH // 2, HEIGHT // 3)
        draw_text("Press Enter to Start", font, WHITE, screen, WIDTH // 2, HEIGHT // 2)
        draw_text("Press Q to Quit", font, WHITE, screen, WIDTH // 2, HEIGHT // 1.5)
        draw_text("Press I for Instructions", font, WHITE, screen, WIDTH // 2, HEIGHT // 1.72)
        pygame.display.flip()

    def show_instructions(self):
        screen.blit(pygame.transform.scale(background_image, (WIDTH, HEIGHT)), (0, 0))
        draw_text("INSTRUCTIONS", font, WHITE, screen, WIDTH // 2, HEIGHT // 3)
        draw_text("ESC to Pause", font, WHITE, screen, WIDTH // 2, HEIGHT // 2)
        draw_text("B for Back to Menu", font, WHITE, screen, WIDTH // 2, HEIGHT // 1.5)
        pygame.display.flip()

    def show_pause_screen(self):
        draw_text("PAUSED", font, WHITE, screen, WIDTH // 2, HEIGHT // 3)
        draw_text("Press ESC to Resume", font, WHITE, screen, WIDTH // 2, HEIGHT // 2)
        draw_text("Press B for Main Menu", font, WHITE, screen, WIDTH // 2, HEIGHT // 1.5)

    def run_game(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if not self.menu_active and not self.game_over:
                        if event.key == pygame.K_ESCAPE:
                            self.paused = not self.paused
                        elif event.key == pygame.K_b:
                            self.menu_active = True
                            self.reset_game()
                    elif self.menu_active:
                        if event.key == pygame.K_RETURN:
                            self.menu_active = False
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False
                        elif event.key == pygame.K_i:
                            self.instructions_active = True
                            self.menu_active = False

            keys = pygame.key.get_pressed()

            if self.instructions_active:
                self.show_instructions()
                if keys[pygame.K_b]:
                    self.instructions_active = False
                    self.menu_active = True

            elif self.menu_active:
                self.show_menu()
                if keys[pygame.K_RETURN]:
                    self.menu_active = False
                    self.reset_game()
                elif keys[pygame.K_q]:
                    running = False
            else:
                screen.blit(pygame.transform.scale(background_image, (WIDTH, HEIGHT)), (0, 0))

                if self.paused:
                    self.show_pause_screen()
                elif not self.game_over:
                    if keys[pygame.K_LEFT]:
                        self.player.move("left")
                    if keys[pygame.K_RIGHT]:
                        self.player.move("right")
                    if keys[pygame.K_SPACE]:
                        if current_time - self.last_bullet_time > bullet_delay:
                            self.bullets.append(Bullet(self.player.x + player_width // 2 - bullet_width // 2, self.player.y))
                            self.last_bullet_time = current_time
                            shoot_sound.play()

                    for bullet in self.bullets[:]:
                        bullet.move()
                        if bullet.y < 0:
                            self.bullets.remove(bullet)

                    for invader in self.invaders:
                        invader.move()

                    if self.boss:
                        self.boss.move()
                        new_bullet = self.boss.shoot(current_time)
                        if new_bullet:
                            self.boss_bullets.append(new_bullet)

                    for boss_bullet in self.boss_bullets[:]:
                        boss_bullet.move()
                        if boss_bullet.y > HEIGHT:
                            self.boss_bullets.remove(boss_bullet)

                    self.handle_collisions()
                    self.level_up()

                    self.player.draw()
                    for bullet in self.bullets:
                        bullet.draw()
                    for invader in self.invaders:
                        invader.draw()
                    if self.boss:
                        self.boss.draw()
                    for boss_bullet in self.boss_bullets:
                        boss_bullet.draw()

                    draw_text(f"Score: {self.score}", font, WHITE, screen, WIDTH // 2, 20)
                    draw_text(f"Level: {self.level}", font, WHITE, screen, 100, 20)
                    draw_text(f"Lives: {self.lives}", font, WHITE, screen, WIDTH - 100, 20)

                elif self.game_over:
                    if self.boss_killed_player:
                        screen.blit(pygame.transform.scale(boss_gameover_image, (WIDTH, HEIGHT)), (0, 0))
                        draw_text("Press R for Restart", font, WHITE, screen, WIDTH // 2, HEIGHT - 60)
                    else:
                        draw_text("GAME OVER! Press R for Restart", font, WHITE, screen, WIDTH // 2, HEIGHT // 2)
                    if keys[pygame.K_r]:
                        self.reset_game()
                        self.menu_active = True

                pygame.display.flip()
                clock.tick(60)

        pygame.quit()

# Старт
SpaceInvaders().run_game()
