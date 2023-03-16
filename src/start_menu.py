"""The start menu for the puzzle game"""
import itertools

import pygame
# import pygame_button

GREEN = (0, 153, 0)
PREVIEW_PREFIX = "res/preview"
ARROW_LEFT_PREFIX = "res/arrow_left_grey"
ARROW_RIGHT_PREFIX = "res/arrow_right_grey"
PLAY_PREFIX = "res/play_grey"
PNG_SUFFIX = ".png"
ARROW_SIZE = (43, 69)
FPS = 30


class Button(pygame.sprite.Sprite):
	"""Sprite subclass for the buttons in the start menu"""
	def __init__(self, image: pygame.Surface, rect: pygame.Rect, on_click_function):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = rect
		self.on_click_function = on_click_function

	def on_click(self):
		self.on_click_function()


class ClickableGroup(pygame.sprite.Group):
	"""The sprites group for the arrows with which the user navigates through the image previews and difficulties"""
	def __init__(self):
		pygame.sprite.Group.__init__(self)

	def collide_click(self, point: (int, int)):
		"""Call the on click method of the sprites that collide with the given point"""
		for sprite in self.sprites():
			if sprite.rect.collidepoint(point):
				try:
					sprite.on_click()
				except AttributeError:
					continue


class Arrow(pygame.sprite.Sprite):
	"""The sprite for the arrows with which the user navigates through the image previews and difficulties"""
	def __init__(self, points_to_right: bool, is_for_image: bool, rect: pygame.Rect):
		pygame.sprite.Sprite.__init__(self)
		self.points_to_right = points_to_right
		self.is_for_image = is_for_image
		prefix = ARROW_RIGHT_PREFIX if points_to_right else ARROW_LEFT_PREFIX
		self.image = pygame.image.load(prefix + PNG_SUFFIX).convert_alpha()
		self.rect = rect


class ArrowGroup(pygame.sprite.Group):
	"""The sprites group for the arrows with which the user navigates through the image previews and difficulties"""
	def __init__(self):
		pygame.sprite.Group.__init__(self)

	def collide_point(self, point: tuple):
		"""Return all arrows in the group that collide with the given point"""
		return [arrow for arrow in self.sprites() if arrow.rect.collidepoint(point) and type(arrow) is Arrow]


class StartMenu:
	"""The class for everything related to the start menu"""
	def __init__(self, main_surface: pygame.Surface):
		# self.button_play = pygame_button.PygameButton(main_surface.get_rect(), "Play", self.start_puzzle)
		# self.button_choose_image = pygame_button.PygameButton(main_surface.get_rect(), "Choose image", self.choose_image)
		self.main_surface = main_surface
		self.images = []
		self.difficulty_texts = ["Easy (48 pieces)", "Medium (108 pieces)", "Hard (192 pieces)"]
		self.chosen_image_id = None
		self.chosen_difficulty = 0
		self.puzzle_is_starting = False
		self.clock = pygame.time.Clock()
		# Initialize buttons
		self.button_group = ClickableGroup()
		on_click_functions = [self.decrement_image_id, self.increment_image_id, self.decrement_difficulty, self.increment_difficulty]
		# Arrow buttons to navigate through the images and difficulties
		for i, j in itertools.product(range(2), range(2)):
			prefix = ARROW_RIGHT_PREFIX if j == 1 else ARROW_LEFT_PREFIX
			cur_image = pygame.image.load(prefix + PNG_SUFFIX).convert_alpha()
			cur_button = Button(cur_image, pygame.Rect((400 + j * 700, 750 + i * 600), cur_image.get_size()), on_click_functions[2 * i + j])
			self.button_group.add(cur_button)
		# Play button
		image = pygame.image.load(PLAY_PREFIX + PNG_SUFFIX).convert_alpha()
		play_button = Button(image, pygame.Rect((1000, 900), image.get_size()), self.start_puzzle)
		self.button_group.add(play_button)
		self.prepare_preview_images()
		self.update_menu()

	def prepare_preview_images(self):
		preview_size = (500, 500)
		i = 0
		while True:
			try:
				image = pygame.image.load(PREVIEW_PREFIX + str(i) + PNG_SUFFIX).convert_alpha()
			except FileNotFoundError:
				break
			image = pygame.transform.scale(image, preview_size)
			self.images.append(image)
			i += 1
		self.chosen_image_id = 0

	def update_menu(self):
		self.main_surface.fill(GREEN)
		self.main_surface.blit(self.images[self.chosen_image_id], (500, 500))
		self.button_group.draw(self.main_surface)
		pygame.display.update()

	def handle_events(self) -> (bool, int, int):
		"""Handle the events in the start menu.
		Returns a tuple containing
		[0] a bool to indicate if the puzzle shall start,
		[1] the chosen image id and
		[2] the chosen difficulty"""
		while not self.puzzle_is_starting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					# Quit
					break
				elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					# Click
					self.button_group.collide_click(event.pos)
					self.update_menu()
				self.clock.tick(FPS)
		return self.puzzle_is_starting, self.chosen_image_id, self.chosen_difficulty

	def start_puzzle(self):
		self.puzzle_is_starting = True

	def increment_image_id(self):
		self.chosen_image_id = (self.chosen_image_id + 1) % len(self.images)

	def decrement_image_id(self):
		self.chosen_image_id = (self.chosen_image_id - 1) % len(self.images)

	def increment_difficulty(self):
		self.chosen_difficulty = (self.chosen_difficulty + 1) % len(self.difficulty_texts)

	def decrement_difficulty(self):
		self.chosen_difficulty = (self.chosen_difficulty - 1) % len(self.difficulty_texts)
