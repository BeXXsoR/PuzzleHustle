"""The start menu for the puzzle game"""
import itertools
import utils
import pygame

GREEN = (0, 153, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BG_PREFIX = "res/background"
PREVIEW_PREFIX = "res/preview"
ARROW_LEFT_PREFIX = "res/arrow_left_grey"
ARROW_RIGHT_PREFIX = "res/arrow_right_grey"
PLAY_PREFIX = "res/play_grey"
PNG_SUFFIX = ".png"
FPS = 30
# The following menu item sizes work well on a 2560x1440 screen, so I use them as a benchmark for scaling.
ARROW_SIZE = (90, 90)
PLAY_BUTTON_SIZE = (315, 135)
PREVIEW_IMG_SIZE = (400, 300)
BENCHMARK_HEIGHT = 1440
DIFFICULTY_FONT_SIZE = 80
TITLE_FONT_SIZE = 400
HEIGHT_FOR_TITLE = 0.1
HEIGHT_FOR_IMAGE = 0.5
HEIGHT_FOR_DIFFICULTY = 0.65
HEIGHT_FOR_PLAY_BUTTON = 0.8
HEIGHT_FOR_OPEN_BOX_MSG = 0.8
WIDTH_FOR_ARROW_LEFT = 0.35
WIDTH_FOR_ARROW_RIGHT = 1 - WIDTH_FOR_ARROW_LEFT


class Clickable(pygame.sprite.Sprite):
	"""Sprite subclass for the buttons in the start menu"""
	def __init__(self, image: pygame.Surface, rect: pygame.Rect, on_click_function):
		super().__init__()
		self.image = image
		self.rect = rect
		self.on_click_function = on_click_function

	def on_click(self):
		self.on_click_function()


class ClickableGroup(pygame.sprite.Group):
	"""Sprites group for the buttons in the start menu"""
	def __init__(self, *sprites):
		super().__init__(*sprites)

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
	def __init__(self, main_surface: pygame.Surface, bg_image: pygame.Surface = None):
		pygame.font.init()
		self.main_surface = main_surface
		self.scaling_factor = main_surface.get_height() / BENCHMARK_HEIGHT
		self.bg_image = bg_image
		self.preview_images = list[pygame.Surface]()
		self.difficulty_texts = ["Easy (48 pieces)", "Medium (108 pieces)", "Hard (192 pieces)"]
		self.difficulty_font = pygame.font.Font(None, int(DIFFICULTY_FONT_SIZE * self.scaling_factor))
		self.title_font = pygame.font.Font(None, int(TITLE_FONT_SIZE * self.scaling_factor))
		self.msg_font = self.difficulty_font
		self.title_rendered = self.title_font.render("Puzzle Hustle", True, BLUE)
		self.msg_rendered = self.msg_font.render("Opening puzzle box, please wait ...", True, BLUE)
		self.chosen_image_id = None
		self.chosen_difficulty = 0
		self.puzzle_is_starting = False
		self.title_center = (self.main_surface.get_rect().center[0], HEIGHT_FOR_TITLE * self.main_surface.get_height())
		self.image_center = (self.main_surface.get_rect().center[0], HEIGHT_FOR_IMAGE * self.main_surface.get_height())
		self.difficulty_center = (self.image_center[0], HEIGHT_FOR_DIFFICULTY * self.main_surface.get_height())
		self.play_button_center = (self.difficulty_center[0], HEIGHT_FOR_PLAY_BUTTON * self.main_surface.get_height())
		self.msg_center = (self.play_button_center[0], HEIGHT_FOR_OPEN_BOX_MSG * self.main_surface.get_height())
		self.clock = pygame.time.Clock()
		self.sound_confirmed = pygame.mixer.Sound("res/Confirmed.wav")
		# Initialize buttons
		self.button_group = ClickableGroup()
		on_click_functions = [self.decrement_image_id, self.increment_image_id, self.decrement_difficulty, self.increment_difficulty]
		# Arrow buttons to navigate through the images and difficulties
		for i, j in itertools.product(range(2), range(2)):
			prefix = ARROW_LEFT_PREFIX if j == 0 else ARROW_RIGHT_PREFIX
			cur_image = pygame.image.load(prefix + PNG_SUFFIX).convert_alpha()
			cur_image = pygame.transform.scale(cur_image, utils.mult_tuple_to_int(ARROW_SIZE, self.scaling_factor))
			cur_center = (
				self.main_surface.get_width() * (WIDTH_FOR_ARROW_LEFT if j == 0 else WIDTH_FOR_ARROW_RIGHT),
				self.image_center[1] if i == 0 else self.difficulty_center[1])
			cur_button = Clickable(cur_image, cur_image.get_rect(center=cur_center), on_click_functions[2 * i + j])
			self.button_group.add(cur_button)
		# Play button
		cur_image = pygame.image.load(PLAY_PREFIX + PNG_SUFFIX).convert_alpha()
		cur_image = pygame.transform.scale(cur_image, utils.mult_tuple_to_int(PLAY_BUTTON_SIZE, self.scaling_factor))
		play_button = Clickable(cur_image, cur_image.get_rect(center=self.play_button_center), self.start_puzzle)
		self.button_group.add(play_button)
		# self.play_button_group = pygame.sprite.LayeredDirty(play_button)
		self.prepare_images()
		self.update_menu()

	def prepare_images(self):
		"""Load and scale the images for the start menu"""
		# Background image (if necessary)
		if not self.bg_image:
			self.bg_image = pygame.image.load(BG_PREFIX + PNG_SUFFIX).convert_alpha()
			self.bg_image = pygame.transform.scale(self.bg_image, self.main_surface.get_size())
		# Preview images
		i = 0
		while True:
			try:
				image = pygame.image.load(PREVIEW_PREFIX + str(i) + PNG_SUFFIX).convert_alpha()
			except FileNotFoundError:
				break
			image = pygame.transform.scale(image, utils.mult_tuple_to_int(PREVIEW_IMG_SIZE, self.scaling_factor))
			self.preview_images.append(image)
			i += 1
		self.chosen_image_id = 0

	def update_menu(self):
		"""Redraw the start menu"""
		# Background
		self.main_surface.blit(self.bg_image, (0, 0))
		# Preview image
		cur_image = self.preview_images[self.chosen_image_id]
		self.main_surface.blit(cur_image, cur_image.get_rect(center=self.image_center))
		# Difficulty
		cur_difficulty_font = self.difficulty_font.render(self.difficulty_texts[self.chosen_difficulty], True, RED)
		self.main_surface.blit(cur_difficulty_font, cur_difficulty_font.get_rect(center=self.difficulty_center))
		# Buttons
		self.button_group.draw(self.main_surface)
		# Game title
		# self.main_surface.blit(self.title_rendered, self.title_rendered.get_rect(center=self.title_center))
		# Message (puzzle is starting)
		if self.puzzle_is_starting:
			self.main_surface.blit(self.msg_rendered, self.msg_rendered.get_rect(center=self.msg_center))
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
		# Adjust the start menu to show that the puzzle will start shortly
		self.button_group.empty()

	def increment_image_id(self):
		"""Increment the image id"""
		self.chosen_image_id = (self.chosen_image_id + 1) % len(self.preview_images)

	def decrement_image_id(self):
		"""Decrement the image id"""
		self.chosen_image_id = (self.chosen_image_id - 1) % len(self.preview_images)

	def increment_difficulty(self):
		"""Increment the difficulty"""
		self.chosen_difficulty = (self.chosen_difficulty + 1) % len(self.difficulty_texts)

	def decrement_difficulty(self):
		"""Decrement the difficulty"""
		self.chosen_difficulty = (self.chosen_difficulty - 1) % len(self.difficulty_texts)
