# ASTEROIDES v2.0
# Loop principal, cenas e input.

import sys

import pygame as pg
pg.init()
pg.font.init()

import config as C
from systems import World
from utils import text, text_center


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Asteroides v2.0")
        self.clock = pg.time.Clock()
        self.font  = pg.font.Font(None, 26)
        self.big   = pg.font.Font(None, 72)
        self.med   = pg.font.Font(None, 42)
        self.scene = "menu"   # "menu" | "play" | "over"
        self.world: World | None = None

    def run(self):
        while True:
            dt   = self.clock.tick(C.FPS) / 1000.0
            keys = pg.key.get_pressed()

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit(); sys.exit()
                if e.type == pg.KEYDOWN:
                    self._on_key(e.key)

            self.screen.fill(C.BLACK)

            if self.scene == "menu":
                self._draw_menu()
            elif self.scene == "play":
                self.world.update(dt, keys)
                self.world.draw(self.screen, self.font)
                if self.world.match_over:
                    self.scene = "over"
            elif self.scene == "over":
                self._draw_over()

            pg.display.flip()

    def _on_key(self, key):
        if key == pg.K_ESCAPE:
            if self.scene in ("play", "over"):
                self.scene = "menu"
                self.world = None
            else:
                pg.quit(); sys.exit()

        elif self.scene == "menu":
            self._start()

        elif self.scene == "play":
            if key == pg.K_SPACE:
                self.world.try_fire()
            elif key == pg.K_LSHIFT:
                self.world.hyperspace()
            elif key == pg.K_s:
                self.world.activate_shield()

        elif self.scene == "over":
            if key == pg.K_r:
                self._start()
            else:
                self.scene = "menu"
                self.world = None

    def _start(self):
        self.world = World()
        self.scene = "play"

    # ── Telas ─────────────────────────────────────────────────────────────────

    def _draw_menu(self):
        text_center(self.screen, self.big,  "ASTEROIDES",  C.WIDTH // 2, 120)
        text_center(self.screen, self.med,  "v 2.0",       C.WIDTH // 2, 185, C.GRAY)
        text_center(self.screen, self.font,
                    "Pressione qualquer tecla para jogar",
                    C.WIDTH // 2, 235, C.WHITE)

        # ── Controles ────────────────────────────────────────────────────────
        controles_titulo = self.font.render("CONTROLES", True, C.WHITE)
        self.screen.blit(controles_titulo, (40, 285))

        controles = [
            ("<-  ->    Virar",       C.GRAY),
            ("[^]       Acelerar",    C.GRAY),
            ("ESPACO    Atirar",      C.GRAY),
            ("S         Escudo",      C.GRAY),
            ("SHIFT     Hiperespaco", C.GRAY),
            ("ESC       Sair/Menu",   C.GRAY),
        ]
        y = 315
        for txt, col in controles:
            lbl = self.font.render(txt, True, col)
            self.screen.blit(lbl, (40, y))
            y += 28

        # ── Mecânicas ─────────────────────────────────────────────────────────
        mec_titulo = self.font.render("MECANICAS ESPECIAIS", True, C.WHITE)
        self.screen.blit(mec_titulo, (C.WIDTH - mec_titulo.get_width() - 40, 285))

        mecanicas = [
            ("[EXP] Explosivo  — reacao em cadeia",    C.RED),
            ("[GEL] Congelante — trava os controles",  C.CYAN),
            ("[CMB] Combo x1-x6 — mata em sequencia",  C.ORANGE),
            ("[ESC] Escudo     — absorve 1 impacto",   C.CYAN),
            ("[MET] Metalico   — tiro triplo",         C.YELLOW),
            ("[TMP] Temporal   — para o tempo",        C.PURPLE),
        ]
        y2 = 315
        for txt, col in mecanicas:
            lbl = self.font.render(txt, True, col)
            self.screen.blit(lbl, (C.WIDTH - lbl.get_width() - 40, y2))
            y2 += 28

    def _draw_over(self):
        text_center(self.screen, self.big,
                    "FIM DE JOGO", C.WIDTH // 2, 180)
        text_center(self.screen, self.med,
                    f"PONTUACAO FINAL:  {self.world.score:06d}",
                    C.WIDTH // 2, 270, C.WHITE)
        text_center(self.screen, self.font,
                    "Pressione 'R' para reiniciar a partida",
                    C.WIDTH // 2, C.HEIGHT - 90, C.WHITE)
        text_center(self.screen, self.font,
                    "Pressione qualquer outra tecla para voltar ao menu",
                    C.WIDTH // 2, C.HEIGHT - 60, C.GRAY)