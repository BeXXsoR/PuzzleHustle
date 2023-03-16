"""The start menu for the puzzle game"""
import itertools

import pygame
# import pygame_button

GREEN = (0, 153, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PREVIEW_PREFIX = "res/preview"
ARROW_LEFT_PREFIX = "res/arrow_left_grey"
ARROW_RIGHT_PREFIX = "res/arrow_right_grey"
PLAY_PREFIX = "res/play_grey"
PNG_SUFFIX = ".png"
ARROW_SIZE = (90, 90)
PLAY_BUTTON_SIZE = (315, 135)
HEIGHT_FOR_IMAGE = 0.5
HEIGHT_FOR_DIFFICULTY = 0.65
HEIGHT_FOR_PLAY_BUTTON = 0.8
WIDTH_FOR_ARROW_LEFT = 0.35
WIDTH_FOR_ARROW_RIGHT = 1 - WIDTH_FOR_ARROW_LEFT
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


class StartMenu:
	"""The class for everything related to the start menu"""
	def __init__(self, main_surface: pygame.Surface):
		pygame.font.init()
		self.main_surface = main_surface
		self.images = list[pygame.Surface]()
		self.difficulty_texts = ["Easy (48 pieces)", "Medium (108 pieces)", "Hard (192 pieces)"]
		self.difficulty_font = pygame.font.Font(None, 80)
		self.chosen_image_id = None
		self.chosen_difficulty = 0
		self.puzzle_is_starting = False
		self.image_center = (self.main_surface.get_rect().center[0], HEIGHT_FOR_IMAGE * self.main_surface.get_height())
		self.difficulty_center = (self.image_center[0], HEIGHT_FOR_DIFFICULTY * self.main_surface.get_height())
		self.play_button_center = (self.difficulty_center[0], HEIGHT_FOR_PLAY_BUTTON * self.main_surface.get_height())
		self.clock = pygame.time.Clock()
		self.sound_confirmed = pygame.mixer.Sound("res/Confirmed.wav")
		# Initialize buttons
		self.button_group = ClickableGroup()
		on_click_functions = [self.decrement_image_id, self.increment_image_id, self.decrement_difficulty, self.increment_difficulty]
		# Arrow buttons to navigate through the images and difficulties
		for i, j in itertools.product(range(2), range(2)):
			prefix = ARROW_LEFT_PREFIX if j == 0 else ARROW_RIGHT_PREFIX
			cur_image = pygame.image.load(prefix + PNG_SUFFIX).convert_alpha()
			cur_image = pygame.transform.scale(cur_image, ARROW_SIZE)
			cur_center = (
				self.main_surface.get_width() * (WIDTH_FOR_ARROW_LEFT if j == 0 else WIDTH_FOR_ARROW_RIGHT),
				self.image_center[1] if i == 0 else self.difficulty_center[1])
			cur_button = Button(cur_image, cur_image.get_rect(center=cur_center), on_click_functions[2 * i + j])
			self.button_group.add(cur_button)
		# Play button
		cur_image = pygame.image.load(PLAY_PREFIX + PNG_SUFFIX).convert_alpha()
		cur_image = pygame.transform.scale(cur_image, PLAY_BUTTON_SIZE)
		play_button = Button(cur_image, cur_image.get_rect(center=self.play_button_center), self.start_puzzle)
		self.button_group.add(play_button)
		self.prepare_preview_images()
		self.update_menu()

	def prepare_preview_images(self):
		"""Load and scale the images for the preview where the user can choose the puzzle image"""
		preview_size = (400, 300)
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
		"""Redraw the start menu"""
		cur_image = self.images[self.chosen_image_id]
		self.main_surface.fill(GREEN)
		self.main_surface.blit(cur_image, cur_image.get_rect(center=self.image_center))
		cur_difficulty_font = self.difficulty_font.render(self.difficulty_texts[self.chosen_difficulty], True, RED)
		self.main_surface.blit(cur_difficulty_font, cur_difficulty_font.get_rect(center=self.difficulty_center))
		self.button_group.draw(self.main_surface)
		# Game title
		title_font = pygame.font.Font(None, 400).render("Puzzle Hustle", True, BLUE)
		self.main_surface.blit(title_font, title_font.get_rect(center=(self.main_surface.get_rect().center[0], 200)))
		pygame.display.update()

	def handle_events(self) -> (bool, int, int):
		"""Handle the events in the start menu.
		Returns a tuple containing
		[0] a bool to indicate if the puzzle shall start,
		[1] the chosen image id and
		[2] the chosen difficulty"""
		has_quit = False
		while not self.puzzle_is_starting and not has_quit:
			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					# Quit
					has_quit = True
				elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					# Click
					self.button_group.collide_click(event.pos)
					self.update_menu()
				self.clock.tick(FPS)
		return self.puzzle_is_starting, self.chosen_image_id, self.chosen_difficulty

	def start_puzzle(self):
		"""Start the puzzle"""
		self.sound_confirmed.play()
		self.puzzle_is_starting = True

	def increment_image_id(self):
		"""Increment the image id"""
		self.chosen_image_id = (self.chosen_image_id + 1) % len(self.images)

	def decrement_image_id(self):
		"""Decrement the image id"""
		self.chosen_image_id = (self.chosen_image_id - 1) % len(self.images)

	def increment_difficulty(self):
		"""Increment the difficulty"""
		self.chosen_difficulty = (self.chosen_difficulty + 1) % len(self.difficulty_texts)

	def decrement_difficulty(self):
		"""Decrement the difficulty"""
		self.chosen_difficulty = (self.chosen_difficulty - 1) % len(self.difficulty_texts)
