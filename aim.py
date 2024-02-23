import pygame, random, math

pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Aim Trainer")
black = 0, 0, 0
white = 255, 255, 255
aimColor = 0, 0, 255
font = pygame.font.SysFont("Arial", 32)
target_radius = 30
target_speed = 0.1
target_limit = 5
target_spawn_rate = 0.01
score = 0
time_limit = 30
start_time = pygame.time.get_ticks()
game_over = False
cheat_detected = False
targets = []


class Target:
    def __init__(self, x, y, dx, dy, color, target_radius):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.target_radius = target_radius

    def posX(self):
        return self.x

    def posY(self):
        return self.y

    def move(self):
        self.x += self.dx
        if self.x < target_radius or self.x > screen_width - target_radius:
            self.dx = -self.dx
        self.y += self.dy
        if self.y < target_radius or self.y > screen_height - target_radius:
            self.dy = -self.dy
        for other in targets:
            if other is not self:
                distance = math.hypot(self.x - other.x, self.y - other.y)
                if distance <= target_radius * 2:
                    angle = math.atan2(other.y - self.y, other.x - self.x)
                    sin = math.sin(angle)
                    cos = math.cos(angle)
                    vx1 = self.dx * cos + self.dy * sin
                    vy1 = -self.dx * sin + self.dy * cos
                    vx2 = other.dx * cos + other.dy * sin
                    vy2 = -other.dx * sin + other.dy * cos
                    vx1, vx2 = vx2, vx1
                    self.dx = vx1 * cos - vy1 * sin
                    self.dy = vx1 * sin + vy1 * cos
                    other.dx = vx2 * cos - vy2 * sin
                    other.dy = vx2 * sin + vy2 * cos
                    self.x += self.dx + 2
                    self.y += self.dy + 2
                    other.x += other.dx + 2
                    other.y += other.dy + 2
        if self.dx > 0.2:
            self.color = white
            print(self.dx)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), target_radius)

    def hit(self, x, y):
        return math.hypot(self.x - x, self.y - y) <= target_radius


def create_target():
    x = random.randint(target_radius, screen_width - target_radius)
    y = random.randint(target_radius, screen_height - target_radius)
    dx = random.choice([-target_speed, target_speed])
    dy = random.choice([-target_speed, target_speed])
    color = aimColor
    return Target(x, y, dx, dy, color, target_radius)


def init_game():
    global score, time_limit, start_time, game_over, cheat_detected, targets
    score = 0
    time_limit = 30
    start_time = pygame.time.get_ticks()
    game_over = False
    cheat_detected = False
    targets = []


init_game()
restart_text = font.render("Заново", True, (235, 76, 66))
restart_rect = restart_text.get_rect()
restart_rect.center = screen_width // 2, screen_height // 2 + 50
clicks = []
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for target in targets:
                if target.hit(mouse_x, mouse_y):
                    score += 1
                    targets.remove(target)
                    break
            if restart_rect.collidepoint(mouse_x, mouse_y):
                if game_over:
                    print(1)
                    init_game()
                    screen.fill(white)
                    current_time = pygame.time.get_ticks()
                    elapsed_time = (current_time - start_time) / 1000
                    remaining_time = remaining_time - elapsed_time
        for target in targets:
            if target.posX() > screen_width:
                targets.remove(target)
                if target in targets:
                    targets.remove(target)
                
            if target.posY() > screen_height:
                if target in targets:
                    targets.remove(target)
                
                
    screen.fill(white)
    current_time = pygame.time.get_ticks()
    elapsed_time = (current_time - start_time) / 1000
    remaining_time = time_limit - elapsed_time
    if remaining_time <= 0:
        game_over = True
    if cheat_detected:
        game_over = True
    if not game_over:
        if random.random() < target_spawn_rate and len(targets) < target_limit:
            targets.append(create_target())
        for target in targets:
            target.move()
            target.draw()
        score_text = font.render(f"Счет: {score}", True, black)
        screen.blit(score_text, (10, 10))
        time_text = font.render(f"Время: {int(remaining_time)}", True, black)
        screen.blit(time_text, (screen_width - 150, 10))
        speed_text = font.render(
            f"Скорость: {int(score/(time_limit-remaining_time+1))}", True, black
        )
        screen.blit(time_text, (screen_width / 2, 10))
    else:
        result_text = font.render(f"Игра окончена! Ваш счет: {score}", True, black)
        restart_text = font.render("Заново", True, (235, 76, 66))
        screen.blit(
            result_text,
            (
                screen_width // 2 - result_text.get_width() // 2,
                screen_height // 2 - result_text.get_height() // 2,
            ),
        )
        screen.blit(
            restart_text,
            (
                screen_width // 2 - restart_text.get_width() // 2,
                screen_height // 2 - result_text.get_height() // 2 + 50,
            ),
        )
    pygame.display.update()