"""A simple button class """
import pygame


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
KEY_MAIN = "main"
KEY_CLICKED = "clicked"
KEY_HOVERED = "hovered"


class PygameButton:
	def __init__(self, rect, text, function, bg_color=BLACK, text_font=pygame.font.Font(None, 20), main_text_color=WHITE, clicked_text_color=WHITE, hovered_text_color=WHITE):
		self.rect = pygame.Rect(rect)
		self.text = text
		self.text_colors = {KEY_MAIN: main_text_color, KEY_CLICKED: clicked_text_color, KEY_HOVERED: hovered_text_color}
		self.cur_text_color = main_text_color
		self.rendered_fonts = {KEY_MAIN: text_font.render(self.text, True, main_text_color), KEY_CLICKED: text_font.render(self.text, True, clicked_text_color), KEY_HOVERED: text_font.render(self.text, True, hovered_text_color)}
		self.cur_font = self.rendered_fonts[KEY_MAIN]
		self.function = function
		self.bg_color = bg_color
		self.clicked = False

	def parse_event(self, event: pygame.event.Event):
		"""Handle events that are passed from the main game loop"""
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
			self.clicked = True
			self.cur_text_color = self.text_colors[KEY_CLICKED]
			self.cur_font = self.rendered_fonts[KEY_CLICKED]
			self.function()
		elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			self.clicked = False
			self.cur_text_color = self.text_colors[KEY_MAIN]
			self.cur_font = self.rendered_fonts[KEY_MAIN]

	def blit(self, surface: pygame.Surface):
		"""Blit the button with its current text settings on the given surface"""
		surface.fill(self.bg_color, self.rect)
		surface.blit(self.cur_font, self.cur_font.get_rect(center=self.rect.center))

