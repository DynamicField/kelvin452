self.text_sprite = KelvinSprite(pygame.Surface((0, 0)))
        self.text_sprite.layer = 200
        self.attach_component(self.text_sprite)
        self.text_sprite.image = default_font.render("START GAME", True, (255,255,255))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=True))
