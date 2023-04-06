"""The start menu for the puzzle game"""
import os
import itertools
import utils
import pygame
import tkinter
from tkinter import filedialog, messagebox

GREEN = (0, 153, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BG_PREFIX = "../res/background"
PREVIEW_PREFIX = "../res/preview"
ARROW_LEFT_PREFIX = "../res/arrow_left_grey"
ARROW_RIGHT_PREFIX = "../res/arrow_right_grey"
PLAY_PREFIX = "../res/play_grey"
PNG_SUFFIX = ".png"
SOUND_CONFIRMED_FILE_NAME = "../res/Confirmed.wav"
FPS = 30
# The following menu item sizes work well on a 2560x1440 screen, so I use them as a benchmark for scaling.
ARROW_SIZE = (90, 90)
PLAY_BUTTON_SIZE = (315, 135)
PREVIEW_IMG_SIZE = (400, 300)
PREVIEW_IMG_SIZE_SQUARE = (300, 300)
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
		self.open_dialog_text = "Choose your own puzzle image"
		self.difficulty_font = pygame.font.Font(None, int(DIFFICULTY_FONT_SIZE * self.scaling_factor))
		self.title_font = pygame.font.Font(None, int(TITLE_FONT_SIZE * self.scaling_factor))
		self.msg_font = self.difficulty_font
		self.title_rendered = self.title_font.render("Puzzle Hustle", True, BLUE)
		self.msg_rendered = self.msg_font.render("Opening puzzle box, please wait ...", True, BLUE)
		self.chosen_image_id = None
		self.chosen_difficulty = 0
		self.puzzle_is_starting = False
		self.chosen_directory = None
		self.title_center = (self.main_surface.get_rect().center[0], HEIGHT_FOR_TITLE * self.main_surface.get_height())
		self.image_center = (self.main_surface.get_rect().center[0], HEIGHT_FOR_IMAGE * self.main_surface.get_height())
		self.difficulty_center = (self.image_center[0], HEIGHT_FOR_DIFFICULTY * self.main_surface.get_height())
		self.play_button_center = (self.difficulty_center[0], HEIGHT_FOR_PLAY_BUTTON * self.main_surface.get_height())
		self.msg_center = (self.play_button_center[0], HEIGHT_FOR_OPEN_BOX_MSG * self.main_surface.get_height())
		self.clock = pygame.time.Clock()
		self.sound_confirmed = pygame.mixer.Sound(SOUND_CONFIRMED_FILE_NAME)
		# Initialize buttons
		self.difficulty_buttons = ClickableGroup()
		self.non_diff_buttons = ClickableGroup()
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
			if i == 0:
				self.non_diff_buttons.add(cur_button)
			else:
				self.difficulty_buttons.add(cur_button)
		# Play button
		cur_image = pygame.image.load(PLAY_PREFIX + PNG_SUFFIX).convert_alpha()
		cur_image = pygame.transform.scale(cur_image, utils.mult_tuple_to_int(PLAY_BUTTON_SIZE, self.scaling_factor))
		play_button = Clickable(cur_image, cur_image.get_rect(center=self.play_button_center), self.start_puzzle)
		self.non_diff_buttons.add(play_button)
		self.all_buttons = ClickableGroup(self.difficulty_buttons.sprites() + self.non_diff_buttons.sprites())
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
			if i == 0:
				image = pygame.transform.scale(image, utils.mult_tuple_to_int(PREVIEW_IMG_SIZE_SQUARE, self.scaling_factor))
			else:
				image = pygame.transform.scale(image, utils.mult_tuple_to_int(PREVIEW_IMG_SIZE, self.scaling_factor))
			self.preview_images.append(image)
			i += 1
		self.chosen_image_id = min(1, i)

	def update_menu(self):
		"""Redraw the start menu"""
		# Background
		self.main_surface.blit(self.bg_image, (0, 0))
		# Preview image
		cur_image = self.preview_images[self.chosen_image_id]
		self.main_surface.blit(cur_image, cur_image.get_rect(center=self.image_center))
		# Difficulty
		if self.chosen_image_id > 0:
			cur_difficulty_font = self.difficulty_font.render(self.difficulty_texts[self.chosen_difficulty], True, RED)
		else:
			cur_difficulty_font = self.difficulty_font.render(self.open_dialog_text, True, RED)
		self.main_surface.blit(cur_difficulty_font, cur_difficulty_font.get_rect(center=self.difficulty_center))
		# Buttons
		if not self.puzzle_is_starting and self.chosen_image_id > 0:
			self.all_buttons.draw(self.main_surface)
		elif not self.puzzle_is_starting:
			self.non_diff_buttons.draw(self.main_surface)
		else:
			# Message (puzzle is starting)
			self.main_surface.blit(self.msg_rendered, self.msg_rendered.get_rect(center=self.msg_center))
		pygame.display.update()

	def handle_events(self) -> (bool, int, int, str):
		"""Handle the events in the start menu.
		Returns a tuple containing
		[0] a bool to indicate if the puzzle shall start,
		[1] the chosen image id,
		[2] the chosen difficulty and
		[3] the chosen directory (if user wants to select their own puzzle image)"""
		has_quit = False
		root = None
		while not self.puzzle_is_starting and not has_quit:
			for event in pygame.event.get():
				if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					# Quit
					has_quit = True
				elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					# Click
					self.all_buttons.collide_click(event.pos)
					if self.puzzle_is_starting and self.chosen_image_id == 0:
						if root is None:
							root = tkinter.Tk()
							root.withdraw()
						self.chosen_directory = filedialog.askdirectory()
						if not self.chosen_directory or not self.check_own_puzzle_dir_and_adjust_difficulty(self.chosen_directory):
							self.puzzle_is_starting = False
					self.update_menu()
				self.clock.tick(FPS)
		# Start the puzzle
		if self.puzzle_is_starting:
			self.sound_confirmed.play()
		return self.puzzle_is_starting, self.chosen_image_id, self.chosen_difficulty, self.chosen_directory

	def check_own_puzzle_dir_and_adjust_difficulty(self, directory: str) -> bool:
		"""Checks if the files in the given directory match the requirements for Puzzle Hustle"""
		num_pieces = [48, 108, 192, 300]
		num_rows = [6, 9, 12, 15]
		num_cols = [8, 12, 16, 20]
		filenames = os.listdir(directory)
		title_error = "Error"
		readme_msg = "See README file for details."
		if len(filenames) not in num_pieces:
			# Invalid number of files in directory
			messagebox.showerror(title_error, "Invalid number of files in directory: Supported numbers are 48, 108, 192 or 300." + readme_msg)
			return False
		filenames.sort()
		folder_name = os.path.basename(directory)
		trg_rows = num_rows[num_pieces.index(len(filenames))]
		trg_cols = num_cols[num_pieces.index(len(filenames))]
		trg_filenames = [folder_name + "_" + str(i) + "_" + str(j) + ".png" for i, j in itertools.product(range(trg_rows), range(trg_cols))]
		trg_filenames.sort()
		invalid_names = [name for name in filenames if name not in trg_filenames]
		if invalid_names:
			# Some file/s don't match the expected pattern
			messagebox.showerror(title_error, "The following filename/s don't match the expected pattern. " + readme_msg + os.linesep * 2 + os.linesep.join(invalid_names))
			return False
		self.chosen_difficulty = num_pieces.index(len(filenames))
		return True

	def start_puzzle(self):
		"""Start the puzzle"""
		self.puzzle_is_starting = True

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
