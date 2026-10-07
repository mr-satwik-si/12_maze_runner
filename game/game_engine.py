    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_h:
                    self.show_hint = not self.show_hint

        return True

    def update(self):
        if self.won:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)
        self.elapsed = time.time() - self.start_time

        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

    def draw_maze(self):
        wall_w = 3
        for r in range(ROWS):
            for c in range(COLS):
                x, y = c * CELL, r * CELL
                w = self.walls[r][c]

                if w[0]:
                    pygame.draw.line(
                        self.screen, WALL_COLOR,
                        (x, y), (x + CELL, y), wall_w
                    )
                if w[1]:
                    pygame.draw.line(
                        self.screen, WALL_COLOR,
                        (x, y + CELL), (x + CELL, y + CELL), wall_w
                    )
                if w[2]:
                    pygame.draw.line(
                        self.screen, WALL_COLOR,
                        (x + CELL, y), (x + CELL, y + CELL), wall_w
                    )
                if w[3]:
                    pygame.draw.line(
                        self.screen, WALL_COLOR,
                        (x, y), (x, y + CELL), wall_w
                    )

    def draw_hint(self):
        if not self.show_hint:
            return

        for r, c in self.shortest_path:
            path_rect = pygame.Rect(
                c * CELL + 7,
                r * CELL + 7,
                CELL - 14,
                CELL - 14
            )
            pygame.draw.rect(self.screen, PATH_COLOR, path_rect, border_radius=5)

    def draw(self):
        self.screen.fill(BG)
        self.draw_maze()
        self.draw_hint()

        pygame.draw.rect(
            self.screen, EXIT_COLOR, self.exit_rect, border_radius=4
        )
        ex_label = self.font.render("EXIT", True, (20, 80, 20))
        self.screen.blit(
            ex_label,
            (self.exit_rect.x + 2, self.exit_rect.y + 4)
        )

        self.player.draw(self.screen)

        hud = pygame.Rect(0, ROWS * CELL, WIDTH, 60)
        pygame.draw.rect(self.screen, (30, 30, 50), hud)
        time_surf = self.font.render(
            f"Time: {self.elapsed:.1f}s   R = New Maze   H = Hint",
            True,
            (200, 200, 200)
        )
        self.screen.blit(time_surf, (10, ROWS * CELL + 18))

        if self.won:
            overlay = pygame.Surface((WIDTH, ROWS * CELL), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))
            msg = self.big_font.render(
                f"Solved in {self.elapsed:.1f}s!",
                True,
                (80, 240, 80)
            )
            sub = self.font.render(
                "Press R for a new maze",
                True,
                (200, 200, 200)
            )
            self.screen.blit(
                msg,
                (WIDTH // 2 - msg.get_width() // 2, ROWS * CELL // 2 - 30)
            )
            self.screen.blit(
                sub,
                (WIDTH // 2 - sub.get_width() // 2, ROWS * CELL // 2 + 20)
            )

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
