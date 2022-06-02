class Piece10Entity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.reward = 2
        self.position = Vector2(x, y)
        self.pre_shake_position = self.position
        self.compteurProj = random.randint(1, 2)
        self.compteurProjRes = self.compteurProj
        a = random.randint(32, 64)
        p10ed = pygame.transform.scale(assets.sprite("p10ed.png"), (a, a))
        self.__sprite = self.attach_component(make_sprite(p10ed, (x, y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        if self.position.x >= 575:
            self.compteurProj -= game.delta_time
            if self.compteurProj <= 0:
                proj_entity = ProjEntity(self.position.x, self.position.y - random.randint(0, 19))
                game.world.spawn_entity(proj_entity)
                self.compteurProj = 1.0
                self.position = self.pre_shake_position.copy()
        self.position.x += 200 * game.delta_time
        if self.position.x > 580:
            self.position.x = 580

        # Le mage va trembler parce que c'est la concentration tout ça
        if self.compteurProj < 0.5 and game.time_factor != 0:
            self.position.x = self.pre_shake_position.x + random.randint(-4, 4)
            self.position.y = self.pre_shake_position.y + random.randint(-4, 4)
        else:
            self.pre_shake_position = self.position.copy()


class ProjEntity(Entity, ReactsToCollisions):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        self.__launched = False
        proj = pygame.transform.scale(assets.sprite("projectile.png"), (94, 38))
        self.__sprite = self.attach_component(make_sprite(proj, (x, y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        self.position.x += 600 * game.delta_time
        if self.position.x > 1200:
            game.world.destroy_entity(self)
            end_game()

    def _on_collide(self, other: Entity):
        if isinstance(other, FireEntity):
            game.world.destroy_entity(self)

