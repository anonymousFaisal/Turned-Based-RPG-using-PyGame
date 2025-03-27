import random
import pygame
import button

# Initial setup
pygame.init()
clock = pygame.time.Clock()

# Constants
FPS = 60
BOTTOM_PANEL = 150
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400 + BOTTOM_PANEL

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Game window setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Battle')

# Game state variables
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
clicked = False
game_over = 0

# Load fonts
font1 = pygame.font.Font("font/BreatheFire.ttf", 26)

# Load images
BACKGROUND_IMG = pygame.image.load('image/background/background.png').convert_alpha()
PANEL_IMG = pygame.image.load('image/Icons/panel.png').convert_alpha()
POTION_IMG = pygame.image.load('image/Icons/potion.png').convert_alpha()
RESTART_IMG = pygame.image.load('image/Icons/restart.png').convert_alpha()
VICTORY_IMG = pygame.image.load('image/Icons/victory.png').convert_alpha()
DEFEAT_IMG = pygame.image.load('image/Icons/defeat.png').convert_alpha()
SWORD_IMG = pygame.image.load('image/Icons/sword.png').convert_alpha()


# Draw functions
def draw_text(text, font, text_col, x, y):
    """Render and draw text on the screen."""
    image = font.render(text, True, text_col)
    screen.blit(image, (x, y))


def draw_bg():
    """Draw the background image."""
    screen.blit(BACKGROUND_IMG, (0, 0))


def draw_panel():
    """Draw the bottom panel with player and enemy information."""
    screen.blit(PANEL_IMG, (0, SCREEN_HEIGHT - BOTTOM_PANEL))
    draw_text(f'{knight.name} HP: {knight.hp}', font1, WHITE, 100, SCREEN_HEIGHT - BOTTOM_PANEL + 10)
    for enemy_count, enemy in enumerate(bandit_list):
        draw_text(f'{enemy.name} HP: {enemy.hp}', font1, WHITE, 550, (SCREEN_HEIGHT - BOTTOM_PANEL + 10) + enemy_count * 60)


# Fighter class
class Fighter:
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0=Idle; 1=Action; 2=Hurt; 3=Dead
        self.update_time = pygame.time.get_ticks()
        # Load idle images
        temp_list = []
        for i in range(8):
            image = pygame.image.load(f'image/{self.name}/Idle/{i}.png')
            image = pygame.transform.scale(image, (image.get_width() * 3, image.get_height() * 3))
            temp_list.append(image)
        self.animation_list.append(temp_list)
        # Load attack images
        temp_list = []
        for i in range(8):
            image = pygame.image.load(f'image/{self.name}/Attack/{i}.png')
            image = pygame.transform.scale(image, (image.get_width() * 3, image.get_height() * 3))
            temp_list.append(image)
        self.animation_list.append(temp_list)
        # Load hurt images
        temp_list = []
        for i in range(3):
            image = pygame.image.load(f'image/{self.name}/Hurt/{i}.png')
            image = pygame.transform.scale(image, (image.get_width() * 3, image.get_height() * 3))
            temp_list.append(image)
        self.animation_list.append(temp_list)
        # Load death images
        temp_list = []
        for i in range(10):
            image = pygame.image.load(f'image/{self.name}/Death/{i}.png')
            image = pygame.transform.scale(image, (image.get_width() * 3, image.get_height() * 3))
            temp_list.append(image)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 100
        # Handle animation
        # Update image
        self.image = self.animation_list[self.action][self.frame_index]
        # Check if the time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # If the animation has run out then reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        # Set variables to idle animation
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        # Deal damage to enemy
        rand = random.randint(-5, 5)
        damage = self.strength + rand
        target.hp -= damage
        # Run enemy hurt animation
        target.hurt()
        # Check if the target has died
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), RED)
        damage_text_group.add(damage_text)
        # Set variables to attack animation
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        # Set variables to hurt animation
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        # Set variables to death animation
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def reset(self):
        self.alive = True
        self.potions = self.start_potions
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)


# Health Bar Class
class HealthBar:
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        # Update with new health
        self.hp = hp
        # Calculate health ratio
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


# Damage text class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font1.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # Move damage text up
        self.rect.y -= 1
        # Delete the text after a few seconds
        self.counter += 1
        if self.counter > 30:
            self.kill()


# Sprite Groups
damage_text_group = pygame.sprite.Group()

# Create fighters
knight = Fighter(200, 260, 'Knight', 30, 10, 3)
bandit1 = Fighter(550, 270, 'Bandit', 20, 6, 1)
bandit2 = Fighter(700, 270, 'Bandit', 20, 6, 1)
bandit_list = [bandit1, bandit2]

# Create Health Bars
knight_health_bar = HealthBar(100, SCREEN_HEIGHT - BOTTOM_PANEL + 40, knight.hp, knight.max_hp)
bandit1_health_bar = HealthBar(550, SCREEN_HEIGHT - BOTTOM_PANEL + 40, bandit1.hp, bandit1.max_hp)
bandit2_health_bar = HealthBar(550, SCREEN_HEIGHT - BOTTOM_PANEL + 100, bandit2.hp, bandit2.max_hp)

# Create buttons
potion_button = button.Button(screen, 100, SCREEN_HEIGHT - BOTTOM_PANEL + 70, POTION_IMG, 64, 64)
restart_button = button.Button(screen, 330, 120, RESTART_IMG, 120, 30)

# Main game loop
run = True
while run:
    clock.tick(FPS)

    # Draw background
    draw_bg()

    # Draw panel
    draw_panel()
    knight_health_bar.draw(knight.hp)
    bandit1_health_bar.draw(bandit1.hp)
    bandit2_health_bar.draw(bandit2.hp)

    # Draw fighters
    knight.update()
    knight.draw()
    for bandit in bandit_list:
        bandit.update()
        bandit.draw()

    # Draw the damage text
    damage_text_group.update()
    damage_text_group.draw(screen)

    # Control player actions
    # Reset action variables
    attack = False
    potion = False
    target = None
    # Make sure mouse is visible
    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos):
            # Hide mouse
            pygame.mouse.set_visible(False)
            # Show sword in place of mouse cursor
            screen.blit(SWORD_IMG, pos)
            if clicked is True and bandit.alive is True:
                attack = True
                target = bandit_list[count]
    if potion_button.draw():
        potion = True
    # Show number of potions remaining
    draw_text(str(knight.potions), font1, WHITE, 150, SCREEN_HEIGHT - BOTTOM_PANEL + 70)

    if game_over == 0:
        # PLayer action
        if knight.alive:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    # Look for player action
                    # Attack
                    if attack is True and target is not None:
                        knight.attack(target)
                        current_fighter += 1
                        action_cooldown = 0
                    # Potion
                    if potion:
                        if knight.potions > 0:
                            # Check if the potion would heal the player beyond max health
                            if knight.max_hp - knight.hp > potion_effect:
                                heal_amount = potion_effect
                            else:
                                heal_amount = knight.max_hp - knight.hp
                            knight.hp += heal_amount
                            knight.potions -= 1
                            damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), GREEN)
                            damage_text_group.add(damage_text)
                            current_fighter += 1
                            action_cooldown = 0
        else:
            game_over = -1

        # Enemy action
        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        # Check if bandit need to heal first
                        if (bandit.hp / bandit.max_hp) < 0.5 and bandit.potions > 0:
                            # Check if the potion would heal the bandit beyond max health
                            if bandit.max_hp - bandit.hp > potion_effect:
                                heal_amount = potion_effect
                            else:
                                heal_amount = bandit.max_hp - bandit.hp
                            bandit.hp += heal_amount
                            bandit.potions -= 1
                            damage_text = DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), GREEN)
                            damage_text_group.add(damage_text)
                            current_fighter += 1
                            action_cooldown = 0
                        # Attack
                        else:
                            bandit.attack(knight)
                            current_fighter += 1
                            action_cooldown = 0
                else:
                    current_fighter += 1
        # If all fighters have had a turn then reset
        if current_fighter > total_fighters:
            current_fighter = 1

    # Check if all bandits are dead
    alive_bandits = 0
    for bandit in bandit_list:
        if bandit.alive:
            alive_bandits += 1
    if alive_bandits == 0:
        game_over = 1

    # Check if game is over
    if game_over != 0:
        if game_over == 1:
            screen.blit(VICTORY_IMG, (250, 50))
        if game_over == -1:
            screen.blit(DEFEAT_IMG, (290, 50))
        if restart_button.draw():
            knight.reset()
            for bandit in bandit_list:
                bandit.reset()
                current_fighter = 1
                action_cooldown = 0
                game_over = 0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False

    pygame.display.update()

pygame.quit()
