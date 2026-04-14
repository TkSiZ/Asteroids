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
        text_center(self.screen, self.big,  "ASTEROIDES",  C.WIDTH // 2, 150)
        text_center(self.screen, self.med,  "v 2.0",       C.WIDTH // 2, 210, C.GRAY)

        linhas = [
            ("Pressione qualquer tecla para jogar", C.WHITE),
            ("", C.BLACK),
            ("<- ->   virar        ↑   acelerar", C.GRAY),
            ("ESPAÇO   atirar     S   escudo",   C.GRAY),
            ("SHIFT   hiperespaço  ESC   sair",  C.GRAY),
        ]
        y = 290
        for txt, col in linhas:
            text_center(self.screen, self.font, txt, C.WIDTH // 2, y, col)
            y += 30

        # Legenda das mecânicas
        mecanicas = [
            ("🔴 Explosivo — reação em cadeia",    C.RED),
            ("🔵 Congelante — trava os controles", C.CYAN),
            ("⚡ Combo x1–x6 — mata em sequência", C.ORANGE),
            ("🛡 Escudo — absorve 1 impacto",       C.CYAN),
            ("🟡 Metálico — concede tiro triplo",  C.YELLOW),
            ("🟣 Temporal — para o tempo",         C.PURPLE)
        ]
        y2 = 290
        for txt, col in mecanicas:
            lbl = self.font.render(txt, True, col)
            self.screen.blit(lbl, (C.WIDTH - lbl.get_width() - 20, y2))
            y2 += 30

    def _draw_over(self):
        text_center(self.screen, self.big,
                    "FIM DE JOGO", C.WIDTH // 2, 200)
        text_center(self.screen, self.med,
                    f"PONTUAÇÃO FINAL:  {self.world.score:06d}",
                    C.WIDTH // 2, 290, C.WHITE)
        text_center(self.screen, self.font,
                    "Pressione qualquer tecla para voltar ao menu",
                    C.WIDTH // 2, C.HEIGHT - 70, C.GRAY)
        text_center(self.screen, self.font,
                    "Pressione 'R' para reiniciar a partida",
                    C.WIDTH // 2, C.HEIGHT - 90, C.GRAY)
