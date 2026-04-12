# ASTEROIDES v2.0
# Mundo: spawning, colisões, pontuação, escudo, combo, variantes.

import math
from random import uniform, random

import pygame as pg

import config as C
from sprites import (Asteroid, ExplosiveAsteroid, FrozenAsteroid,
                     Ship, UFO, Bullet, UfoBullet)
from utils import Vec, rand_edge_pos, rand_unit_vec


def _make_asteroid(pos: Vec, vel: Vec, size: str) -> Asteroid:
    """Factory: escolhe normal / explosivo / congelante aleatoriamente."""
    if size in ("L", "M"):
        roll = random()
        if roll < C.EXPLOSIVE_CHANCE:
            return ExplosiveAsteroid(pos, vel, size)
        elif roll < C.EXPLOSIVE_CHANCE + C.FROZEN_CHANCE:
            return FrozenAsteroid(pos, vel, size)
    return Asteroid(pos, vel, size)


class World:
    def __init__(self):
        self.ship = Ship(Vec(C.WIDTH // 2, C.HEIGHT // 2))

        self.bullets     = pg.sprite.Group()
        self.ufo_bullets = pg.sprite.Group()
        self.asteroids   = pg.sprite.Group()
        self.ufos        = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group(self.ship)

        self.score      = 0
        self.lives      = C.START_LIVES
        self.wave       = 0
        self.wave_cool  = C.WAVE_DELAY
        self.safe       = C.SAFE_SPAWN_TIME
        self.ufo_timer  = C.UFO_SPAWN_EVERY

        self.match_time = C.MATCH_DURATION
        self.match_over = False

        # efeito de explosão em cadeia
        self._blast_fx: tuple | None = None

    # ── Ondas ─────────────────────────────────────────────────────────────────

    def start_wave(self):
        self.wave += 1
        count = 3 + self.wave
        for _ in range(count):
            pos = rand_edge_pos()
            while (pos - self.ship.pos).length() < 150:
                pos = rand_edge_pos()
            ang   = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel   = Vec(math.cos(ang), math.sin(ang)) * speed
            self._spawn_asteroid(pos, vel, "L")

    def _spawn_asteroid(self, pos: Vec, vel: Vec, size: str):
        a = _make_asteroid(pos, vel, size)
        self.asteroids.add(a)
        self.all_sprites.add(a)

    def _spawn_ufo(self):
        if self.ufos:
            return
        small = random() < 0.5
        y = uniform(0, C.HEIGHT)
        x = 0 if random() < 0.5 else C.WIDTH
        ufo = UFO(Vec(x, y), small)
        ufo.dir.xy = (1, 0) if x == 0 else (-1, 0)
        self.ufos.add(ufo)
        self.all_sprites.add(ufo)

    # ── Ações do jogador ──────────────────────────────────────────────────────

    def try_fire(self):
        if len(self.bullets) >= C.MAX_BULLETS:
            return
        b = self.ship.fire()
        if b:
            self.bullets.add(b)
            self.all_sprites.add(b)

    def hyperspace(self):
        self.ship.hyperspace()
        self.score = max(0, self.score - C.HYPERSPACE_COST)

    def activate_shield(self):
        self.ship.activate_shield()

    # ── Update principal ──────────────────────────────────────────────────────

    def update(self, dt: float, keys):
        if self.match_over:
            return

        # Timer da partida
        self.match_time -= dt
        if self.match_time <= 0:
            self.match_time = 0
            self.match_over = True
            return

        # Controles da nave
        self.ship.control(keys, dt)
        self.ship.update(dt)
        if self.safe > 0:
            self.ship.invuln = 0.5
            self.safe -= dt

        # OVNIs
        if self.ufos:
            self._ufo_try_fire()
        else:
            self.ufo_timer -= dt
        if not self.ufos and self.ufo_timer <= 0:
            self._spawn_ufo()
            self.ufo_timer = C.UFO_SPAWN_EVERY

        self.bullets.update(dt)
        self.ufo_bullets.update(dt)
        self.asteroids.update(dt)
        self.ufos.update(dt)

        self._handle_collisions()

        # Próxima onda
        if not self.asteroids and self.wave_cool <= 0:
            self.start_wave()
            self.wave_cool = C.WAVE_DELAY
        elif not self.asteroids:
            self.wave_cool -= dt

        # Tick do efeito de explosão
        if self._blast_fx:
            bpos, br, bttl = self._blast_fx
            self._blast_fx = (bpos, br, bttl - dt) if bttl - dt > 0 else None

    def _ufo_try_fire(self):
        for ufo in self.ufos:
            b = ufo.fire_at(self.ship.pos)
            if b:
                self.ufo_bullets.add(b)
                self.all_sprites.add(b)

    # ── Colisões ──────────────────────────────────────────────────────────────

    def _handle_collisions(self):
        # Balas do jogador vs asteroides
        hits = pg.sprite.groupcollide(
            self.asteroids, self.bullets, False, True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast in hits:
            self._split_asteroid(ast)

        # Balas do OVNI vs asteroides (sem pontos)
        ufo_hits = pg.sprite.groupcollide(
            self.asteroids, self.ufo_bullets, False, True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast in ufo_hits:
            self._split_asteroid(ast, award=False)

        # Ameaças vs nave
        if self.ship.invuln <= 0 and self.safe <= 0:
            for ast in list(self.asteroids):
                if (ast.pos - self.ship.pos).length() < (ast.r + self.ship.r):
                    if ast.kind == "frozen":
                        self.ship.frozen = C.FROZEN_DURATION
                    else:
                        if not self.ship.shield_absorb():
                            self._ship_die()
                    break

            for ufo in list(self.ufos):
                if (ufo.pos - self.ship.pos).length() < (ufo.r + self.ship.r):
                    if not self.ship.shield_absorb():
                        self._ship_die()
                    break

            for b in list(self.ufo_bullets):
                if (b.pos - self.ship.pos).length() < (b.r + self.ship.r):
                    b.kill()
                    if not self.ship.shield_absorb():
                        self._ship_die()
                    break

        # Balas do jogador vs OVNIs
        for ufo in list(self.ufos):
            for b in list(self.bullets):
                if (ufo.pos - b.pos).length() < (ufo.r + b.r):
                    pts = C.UFO_SMALL["score"] if ufo.small else C.UFO_BIG["score"]
                    self.score += pts
                    ufo.kill()
                    b.kill()
                    break

    def _split_asteroid(self, ast: Asteroid, award: bool = True,
                         _visited: set = None):
        """Destrói asteroide, concede pontos e aplica efeitos."""
        if _visited is None:
            _visited = set()
        if id(ast) in _visited:
            return
        _visited.add(id(ast))

        if award:
            base  = C.AST_SIZES[ast.size]["score"]
            multi = self.ship.get_multiplier()
            self.ship.register_kill()
            self.ship.add_energy(C.SHIELD_ENERGY_PER_KILL)
            self.score += base * multi

        pos        = Vec(ast.pos)
        split_list = C.AST_SIZES[ast.size]["split"]

        # Mata ANTES de propagar o blast
        ast.kill()

        # Efeitos on_death (explosivo)
        for event in ast.on_death():
            if event[0] == "blast":
                _, blast_pos, blast_r = event
                self._apply_blast(blast_pos, blast_r, _visited)

        # Fragmentos
        for s in split_list:
            dirv  = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * 1.2
            self._spawn_asteroid(pos, dirv * speed, s)

    def _apply_blast(self, center: Vec, radius: float, _visited: set):
        """Destrói asteroides dentro do raio (seguro contra recursão)."""
        self._blast_fx = (center, radius, 0.35)
        for ast in list(self.asteroids):
            if id(ast) in _visited:
                continue
            if (ast.pos - center).length() < radius + ast.r:
                self._split_asteroid(ast, award=True, _visited=_visited)

    def _ship_die(self):
        self.lives -= 1
        # Reseta combo ao morrer
        self.ship.combo       = 1
        self.ship.combo_timer = 0.0
        if self.lives <= 0:
            self.lives      = 0
            self.match_over = True
            return
        self.ship.pos.xy   = (C.WIDTH // 2, C.HEIGHT // 2)
        self.ship.vel.xy   = (0, 0)
        self.ship.angle    = -90.0
        self.ship.invuln   = C.SAFE_SPAWN_TIME
        self.safe          = C.SAFE_SPAWN_TIME

    # ── Desenho ───────────────────────────────────────────────────────────────

    def draw(self, surf: pg.Surface, font: pg.font.Font):
        for ast in self.asteroids:
            ast.draw(surf)
        for ufo in self.ufos:
            ufo.draw(surf)
        for b in self.bullets:
            b.draw(surf)
        for b in self.ufo_bullets:
            b.draw(surf)
        self.ship.draw(surf)

        # Efeito de onda de choque
        if self._blast_fx:
            bpos, br, bttl = self._blast_fx
            alpha = max(0, int(255 * (bttl / 0.35)))
            ring  = pg.Surface((int(br * 2 + 6), int(br * 2 + 6)),
                                pg.SRCALPHA)
            pg.draw.circle(ring, (*C.ORANGE, alpha),
                           (int(br + 3), int(br + 3)), int(br), 3)
            surf.blit(ring, (int(bpos.x - br - 3), int(bpos.y - br - 3)))

        self._draw_hud(surf, font)

    def _draw_hud(self, surf: pg.Surface, font: pg.font.Font):
        pg.draw.line(surf, (60, 60, 60), (0, 50), (C.WIDTH, 50), 1)

        # ── Esquerda: pontuação, vidas, onda ─────────────────────────────
        txt   = f"SCORE {self.score:06d}   VIDAS {self.lives}   ONDA {self.wave}"
        label = font.render(txt, True, C.WHITE)
        surf.blit(label, (10, 14))

        # ── Centro: timer ─────────────────────────────────────────────────
        secs  = int(self.match_time)
        t_col = C.RED if self.match_time < 20 else C.WHITE
        t_str = f"{secs // 60:02d}:{secs % 60:02d}"
        t_surf = font.render(t_str, True, t_col)
        surf.blit(t_surf, (C.WIDTH // 2 - t_surf.get_width() // 2, 14))

        # ── Barra de escudo ───────────────────────────────────────────────
        bx, by, bw, bh = 10, 58, 120, 8
        pg.draw.rect(surf, (40, 40, 40), (bx, by, bw, bh))
        fill = int(bw * (self.ship.shield_energy / C.SHIELD_ENERGY_MAX))
        if fill > 0:
            col = C.CYAN if self.ship.shield_cooldown <= 0 else C.GRAY
            pg.draw.rect(surf, col, (bx, by, fill, bh))
        pg.draw.rect(surf, C.GRAY, (bx, by, bw, bh), 1)
        lbl = font.render("ESCUDO [S]", True, C.GRAY)
        surf.blit(lbl, (bx + bw + 6, by - 2))

        # ── Indicador de combo ────────────────────────────────────────────
        if self.ship.combo > 1:
            col = C.ORANGE if self.ship.combo >= 4 else C.YELLOW
            cs  = font.render(f"x{self.ship.combo} COMBO!", True, col)
            surf.blit(cs, (10, 72))
