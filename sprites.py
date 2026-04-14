# ASTEROIDES v2.0
# Entidades do jogo: nave, asteroides variantes, balas, OVNI.

import math
import random as _rnd
from random import uniform

import pygame as pg

import config as C
from utils import Vec, angle_to_vec, draw_circle, draw_poly, wrap_pos


# ---------------------------------------------------------------------------
# Balas
# ---------------------------------------------------------------------------

class Bullet(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec):
        super().__init__()
        self.pos  = Vec(pos)
        self.vel  = Vec(vel)
        self.ttl  = C.BULLET_TTL
        self.r    = C.BULLET_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos  = wrap_pos(self.pos)
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        draw_circle(surf, self.pos, self.r)


class UfoBullet(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec):
        super().__init__()
        self.pos  = Vec(pos)
        self.vel  = Vec(vel)
        self.ttl  = C.UFO_BULLET_TTL
        self.r    = C.BULLET_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos  = wrap_pos(self.pos)
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        draw_circle(surf, self.pos, self.r, C.RED)


# ---------------------------------------------------------------------------
# Asteroides
# ---------------------------------------------------------------------------

class Asteroid(pg.sprite.Sprite):
    kind = "normal"

    def __init__(self, pos: Vec, vel: Vec, size: str):
        super().__init__()
        self.pos      = Vec(pos)
        self.vel      = Vec(vel)
        self.size     = size
        self.r        = C.AST_SIZES[size]["r"]
        self.poly_seed = _rnd.randint(0, 2**31)
        self.poly     = self._make_poly()
        self.rect     = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def _make_poly(self):
        rng   = _rnd.Random(self.poly_seed)
        steps = 12 if self.size == "L" else 10 if self.size == "M" else 8
        pts   = []
        for i in range(steps):
            ang    = i * (360 / steps)
            jitter = rng.uniform(0.75, 1.2)
            r      = self.r * jitter
            v      = Vec(math.cos(math.radians(ang)),
                         math.sin(math.radians(ang)))
            pts.append(v * r)
        return pts

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos  = wrap_pos(self.pos)
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        pts = [(self.pos + p) for p in self.poly]
        pg.draw.polygon(surf, C.WHITE, pts, width=1)

    def on_death(self) -> list:
        """Retorna lista de efeitos ao morrer."""
        return []


class ExplosiveAsteroid(Asteroid):
    """Vermelho — explode ao morrer, destruindo asteroides próximos."""
    kind = "explosive"

    def draw(self, surf: pg.Surface):
        pts = [(self.pos + p) for p in self.poly]
        pg.draw.polygon(surf, C.RED, pts, width=2)
        draw_circle(surf, self.pos, max(4, self.r // 3), C.ORANGE)

    def on_death(self) -> list:
        return [("blast", Vec(self.pos), C.EXPLOSIVE_RADIUS)]


class FrozenAsteroid(Asteroid):
    """Ciano — congela os controles da nave ao colidir."""
    kind = "frozen"

    def draw(self, surf: pg.Surface):
        pts = [(self.pos + p) for p in self.poly]
        pg.draw.polygon(surf, C.CYAN, pts, width=2)
        draw_circle(surf, self.pos, self.r + 3, (40, 160, 200))


class SpreadAsteroid(Asteroid):
    """Amarelo — concede tiro triplo ao ser destruído."""
    kind = "spread"

    def draw(self, surf: pg.Surface):
        pts = [(self.pos + p) for p in self.poly]
        pg.draw.polygon(surf, C.YELLOW, pts, width=2)
        draw_circle(surf, self.pos, max(4, self.r // 3), C.YELLOW)

    def on_death(self) -> list:
        return [("spread",)]


class TimeAsteroid(Asteroid):
    """Roxo — congela o tempo dos inimigos ao ser destruído."""
    kind = "time"

    def draw(self, surf: pg.Surface):
        pts = [(self.pos + p) for p in self.poly]
        pg.draw.polygon(surf, (200, 100, 255), pts, width=2) # Cor Roxa
        # Desenha uma pequena ampulheta minimalista no centro
        draw_poly(surf, [
            self.pos + Vec(-4, -4), self.pos + Vec(4, -4),
            self.pos + Vec(-4, 4),  self.pos + Vec(4, 4)
        ], C.PURPLE)

    def on_death(self) -> list:
        return [("freeze_time",)]


# ---------------------------------------------------------------------------
# Nave
# ---------------------------------------------------------------------------

class Ship(pg.sprite.Sprite):
    def __init__(self, pos: Vec):
        super().__init__()
        self.pos   = Vec(pos)
        self.vel   = Vec(0, 0)
        self.angle = -90.0
        self.cool  = 0.0
        self.invuln = 0.0
        self.r     = C.SHIP_RADIUS
        self.rect  = pg.Rect(0, 0, self.r * 2, self.r * 2)

        # Congelamento
        self.frozen = 0.0

        # Escudo
        self.shield_energy   = 0.0
        self.shield_active   = False
        self.shield_timer    = 0.0
        self.shield_cooldown = 0.0

        # Combo
        self.combo       = 1
        self.combo_timer = 0.0

        # Timers Powerups
        self.spread_timer = 0.0
        self.freeze_timer = 0.0

    # ── Controles ─────────────────────────────────────────────────────────

    def control(self, keys: pg.key.ScancodeWrapper, dt: float):
        if self.frozen > 0:
            self.frozen -= dt
            return
        if keys[pg.K_LEFT]:
            self.angle -= C.SHIP_TURN_SPEED * dt
        if keys[pg.K_RIGHT]:
            self.angle += C.SHIP_TURN_SPEED * dt
        if keys[pg.K_UP]:
            self.vel += angle_to_vec(self.angle) * C.SHIP_THRUST * dt
        self.vel *= C.SHIP_FRICTION


    def fire(self) -> list["Bullet"]:
        if self.cool > 0:
            return []
        
        dirv = angle_to_vec(self.angle)
        pos  = self.pos + dirv * (self.r + 6)
        vel  = self.vel + dirv * C.SHIP_BULLET_SPEED
        self.cool = C.SHIP_FIRE_RATE
        
        bullets = [Bullet(pos, vel)]
        
        # Tiro triplo ativo se o timer for maior que 0
        if self.spread_timer > 0:
            dir_l = angle_to_vec(self.angle - C.SPREAD_ANGLE)
            dir_r = angle_to_vec(self.angle + C.SPREAD_ANGLE)
            
            bullets.append(Bullet(self.pos + dir_l * (self.r + 6), self.vel + dir_l * C.SHIP_BULLET_SPEED))
            bullets.append(Bullet(self.pos + dir_r * (self.r + 6), self.vel + dir_r * C.SHIP_BULLET_SPEED))
            
        return bullets

    def hyperspace(self):
        self.pos    = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))
        self.vel.xy = (0, 0)
        self.invuln = 1.0

    # ── Escudo ────────────────────────────────────────────────────────────

    def activate_shield(self):
        if (self.shield_energy >= C.SHIELD_ENERGY_MAX
                and self.shield_cooldown <= 0
                and not self.shield_active):
            self.shield_active   = True
            self.shield_timer    = C.SHIELD_DURATION
            self.shield_energy   = 0.0

    def add_energy(self, amount: float):
        self.shield_energy = min(C.SHIELD_ENERGY_MAX,
                                 self.shield_energy + amount)

    def shield_absorb(self) -> bool:
        """Retorna True se o escudo absorveu o impacto."""
        if self.shield_active:
            self.shield_active   = False
            self.shield_timer    = 0.0
            self.shield_cooldown = C.SHIELD_COOLDOWN
            return True
        return False

    # ── Combo ─────────────────────────────────────────────────────────────

    def register_kill(self):
        self.combo       = min(C.COMBO_MAX, self.combo + 1)
        self.combo_timer = C.COMBO_WINDOW

    def get_multiplier(self) -> int:
        return self.combo

    # ── Update / Draw ──────────────────────────────────────────────────────

    def update(self, dt: float):
        # Timers dos efeitos
        if self.spread_timer > 0:
            self.spread_timer -= dt
        if self.freeze_timer > 0:
            self.freeze_timer -= dt 
        if self.cool > 0:
            self.cool -= dt
        if self.invuln > 0:
            self.invuln -= dt

        # timers do escudo
        if self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active   = False
                self.shield_cooldown = C.SHIELD_COOLDOWN
        if self.shield_cooldown > 0:
            self.shield_cooldown -= dt

        # decaimento do combo
        if self.combo_timer > 0:
            self.combo_timer -= dt
        else:
            self.combo = 1

        self.pos += self.vel * dt
        self.pos  = wrap_pos(self.pos)
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        dirv  = angle_to_vec(self.angle)
        left  = angle_to_vec(self.angle + 140)
        right = angle_to_vec(self.angle - 140)
        p1 = self.pos + dirv  * self.r
        p2 = self.pos + left  * self.r * 0.9
        p3 = self.pos + right * self.r * 0.9
        draw_poly(surf, [p1, p2, p3])

        # piscada de invulnerabilidade
        if self.invuln > 0 and int(self.invuln * 10) % 2 == 0:
            draw_circle(surf, self.pos, self.r + 6)

        # indicador de congelamento
        if self.frozen > 0:
            draw_circle(surf, self.pos, self.r + 4, C.CYAN)

        # bolha do escudo
        if self.shield_active:
            pulse = int(self.shield_timer * 8) % 2
            r_off = 10 + pulse * 3
            cx, cy = int(self.pos.x), int(self.pos.y)
            pg.draw.circle(surf, C.CYAN, (cx, cy), self.r + r_off, width=2)
            for i in range(6):
                a1 = math.radians(i * 60)
                a2 = math.radians((i + 1) * 60)
                x1 = cx + math.cos(a1) * (self.r + r_off)
                y1 = cy + math.sin(a1) * (self.r + r_off)
                x2 = cx + math.cos(a2) * (self.r + r_off)
                y2 = cy + math.sin(a2) * (self.r + r_off)
                pg.draw.line(surf, (100, 255, 255), (x1, y1), (x2, y2), 1)


# ---------------------------------------------------------------------------
# OVNI
# ---------------------------------------------------------------------------

class UFO(pg.sprite.Sprite):
    def __init__(self, pos: Vec, small: bool):
        super().__init__()
        self.pos   = Vec(pos)
        self.small = small
        profile    = C.UFO_SMALL if small else C.UFO_BIG
        self.r     = profile["r"]
        self.aim   = profile["aim"]
        self.speed = C.UFO_SPEED
        self.cool  = C.UFO_FIRE_EVERY
        self.rect  = pg.Rect(0, 0, self.r * 2, self.r * 2)
        self.dir   = Vec(1, 0) if uniform(0, 1) < 0.5 else Vec(-1, 0)

    def update(self, dt: float):
        self.pos  += self.dir * self.speed * dt
        self.cool -= dt
        if self.pos.x < -self.r * 2 or self.pos.x > C.WIDTH + self.r * 2:
            self.kill()
        self.rect.center = self.pos

    def fire_at(self, target_pos: Vec) -> "UfoBullet | None":
        if self.cool > 0:
            return None
        aim_vec = Vec(target_pos) - self.pos
        if aim_vec.length_squared() == 0:
            aim_vec = self.dir.normalize()
        else:
            aim_vec = aim_vec.normalize()
        max_error = (1.0 - self.aim) * 60.0
        shot_dir  = aim_vec.rotate(uniform(-max_error, max_error))
        self.cool = C.UFO_FIRE_EVERY
        vel       = shot_dir * C.UFO_BULLET_SPEED
        return UfoBullet(self.pos + shot_dir * (self.r + 6), vel)

    def draw(self, surf: pg.Surface):
        w, h = self.r * 2, self.r
        body = pg.Rect(0, 0, w, h)
        body.center = self.pos
        pg.draw.ellipse(surf, C.WHITE, body, width=1)
        cup = pg.Rect(0, 0, int(w * 0.5), int(h * 0.7))
        cup.center = (int(self.pos.x), int(self.pos.y - h * 0.3))
        pg.draw.ellipse(surf, C.WHITE, cup, width=1)
