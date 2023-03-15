from PIL import Image, ImageSequence
import pygame
import itertools


class Animation:
	def __init__(self, filename, size: (int, int) = None):
		"""A class to play animated gif files in pygame"""
		if not pygame.get_init():
			pygame.init()
		self.filename = filename
		self.pil_frames = []
		self.pygame_frames = []
		self.clock = pygame.time.Clock()
		self.cur_frame = 0
		with Image.open(self.filename) as anim:
			self.duration = anim.info["duration"]
			self.transparency = anim.info["transparency"] if "transparency" in anim.info else None
			for frame in ImageSequence.Iterator(anim):
				pil_frame = frame.resize(size) if size else frame
				pygame_frame = pygame.image.fromstring(pil_frame.tobytes(), pil_frame.size, pil_frame.mode)
				pygame_frame.set_colorkey(self.transparency)
				self.pygame_frames.append(pygame_frame)
				self.pil_frames.append(pil_frame)
		self.num_frames = len(self.pygame_frames)

	def get_next_frame(self) -> pygame.Surface:
		"""Return the next frame of the animation"""
		frame = self.pygame_frames[self.cur_frame]
		self.cur_frame = (self.cur_frame + 1) % self.num_frames
		return frame

	def play(self, surface: pygame.Surface, position: (int, int), loops: int) -> None:
		"""Play the animated image
		surface is the surface to blit the frames on
		position is the top left position of the frames with respect to the surface
		loops is the number of times that the animation is played"""
		with Image.open(self.filename) as anim:
			duration = anim.info["duration"]
			for i, frame in itertools.product(range(loops), ImageSequence.Iterator(anim)):
				frame.tobytes()
				pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
				surface.blit(pygame_image, position)
				pygame.time.delay(duration)

	def get_frames_and_duration(self) -> (list, int):
		"""Return all frames belonging to the animation as well as its duration"""
		all_frames = []
		with Image.open(self.filename) as anim:
			for frame in ImageSequence.Iterator(anim):
				pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
				all_frames.append(pygame_image)
		return all_frames, anim.info["duration"]

	def resize_all_frames(self, new_size: (int, int)) -> None:
		"""Resize all frames of the animation to the specified size"""
		resized_frames = []
		for frame in self.pil_frames:
			resized_frames.append(frame.resize(new_size))
			self.pil_frames = resized_frames
