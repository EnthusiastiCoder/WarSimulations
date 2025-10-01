import arcade
import math
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Battle Simulation"


class Troop(arcade.Sprite):
    def __init__(self, animations, x, y, health, speed, attack_range, damage, is_ranged):
        # Start with idle animation
        super().__init__(animations["idle"][0], scale=2)
        self.animations = animations
        self.current_state = "idle"
        self.cur_frame = 0
        self.frame_timer = 0

        self.center_x = x
        self.center_y = y
        self.health = health
        self.max_health = health
        self.speed = speed
        self.attack_range = attack_range
        self.damage = damage
        self.is_ranged = is_ranged
        self.target = None

        # Attack timing
        self.attack_cooldown = 1.0
        self.cooldown_timer = 0

    def set_state(self, state):
        if state != self.current_state:
            self.current_state = state
            self.cur_frame = 0
            self.frame_timer = 0

    def update_animation(self, delta_time: float = 1/60):
        frames = self.animations[self.current_state]
        self.frame_timer += delta_time
        if self.frame_timer > 0.15:  # frame speed
            self.frame_timer = 0
            self.cur_frame = (self.cur_frame + 1) % len(frames)
            self.texture = frames[self.cur_frame]

    def update_logic(self, enemies, projectiles, delta_time):
        if self.health <= 0:
            self.set_state("dead")
            return

        self.cooldown_timer -= delta_time

        # Find living enemies
        living_enemies = [e for e in enemies if e.health > 0]
        if not living_enemies:
            self.set_state("idle")
            return

        # Pick closest target
        self.target = min(living_enemies, key=lambda e: arcade.get_distance_between_sprites(self, e))
        dist = arcade.get_distance_between_sprites(self, self.target)

        if dist <= self.attack_range:
            # Attack
            if self.cooldown_timer <= 0:
                self.set_state("attack")
                self.cooldown_timer = self.attack_cooldown

                if self.is_ranged:
                    # Shoot arrow
                    arrow = Projectile("arrow.png", 0.5,
                                       self.center_x, self.center_y,
                                       self.target, self.damage)
                    projectiles.append(arrow)
                else:
                    # Melee damage
                    self.target.health -= self.damage
            else:
                self.set_state("idle")
        else:
            # Move closer
            self.set_state("walk")
            dx, dy = self.target.center_x - self.center_x, self.target.center_y - self.center_y
            length = math.hypot(dx, dy)
            if length > 0:
                self.center_x += (dx / length) * self.speed
                self.center_y += (dy / length) * self.speed

    def draw(self):
        super().draw()
        if self.health > 0:
            # Draw health bar
            health_ratio = self.health / self.max_health
            arcade.draw_rectangle_filled(self.center_x, self.center_y + 25, 30, 5, arcade.color.RED)
            arcade.draw_rectangle_filled(self.center_x - 15 + health_ratio * 30 / 2,
                                         self.center_y + 25,
                                         health_ratio * 30, 5, arcade.color.GREEN)


class Projectile(arcade.Sprite):
    def __init__(self, texture, scale, x, y, target, damage):
        super().__init__(texture, scale)
        self.center_x = x
        self.center_y = y
        self.target = target
        self.damage = damage
        self.speed = 5

    def update(self):
        if not self.target or self.target.health <= 0:
            return
        dx, dy = self.target.center_x - self.center_x, self.target.center_y - self.center_y
        dist = math.hypot(dx, dy)
        if dist < 10:
            self.target.health -= self.damage
            self.remove_from_sprite_lists()
        else:
            self.center_x += (dx / dist) * self.speed
            self.center_y += (dy / dist) * self.speed


class BattleGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.barbarians = arcade.SpriteList()
        self.archers = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()

    def load_animations(self, prefix):
        # Normally you'd load real sprite sheets here
        return {
            "idle": [arcade.load_texture(f"{prefix}_idle.png")],
            "walk": [arcade.load_texture(f"{prefix}_walk.png")],
            "attack": [arcade.load_texture(f"{prefix}_attack.png")],
            "dead": [arcade.load_texture(f"{prefix}_dead.png")],
        }

    def setup(self):
        barbarian_anim = self.load_animations("barbarian")
        archer_anim = self.load_animations("archer")

        for i in range(5):
            b = Troop(barbarian_anim, 100, 100 + i * 80, 120, 1.5, 20, 15, False)
            self.barbarians.append(b)

        for i in range(5):
            a = Troop(archer_anim, 700, 100 + i * 80, 80, 1.2, 200, 8, True)
            self.archers.append(a)

    def on_draw(self):
        arcade.start_render()
        self.barbarians.draw()
        self.archers.draw()
        self.projectiles.draw()

        for b in self.barbarians:
            b.draw()
        for a in self.archers:
            a.draw()

    def on_update(self, delta_time):
        for b in self.barbarians:
            b.update_logic(self.archers, self.projectiles, delta_time)
            b.update_animation(delta_time)
        for a in self.archers:
            a.update_logic(self.barbarians, self.projectiles, delta_time)
            a.update_animation(delta_time)

        self.projectiles.update()


if __name__ == "__main__":
    game = BattleGame()
    game.setup()
    arcade.run()
