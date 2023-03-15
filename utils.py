import itertools


def add_tuples(tuple1: tuple, tuple2: tuple) -> tuple:
	"""Add tuples itemwise"""
	return tuple([a + b for a, b in itertools.zip_longest(tuple1, tuple2, fillvalue=0)])


def subtract_tuples(tuple1: tuple, tuple2: tuple) -> tuple:
	"""Subtract tuples itemwise"""
	return tuple([a - b for a, b in itertools.zip_longest(tuple1, tuple2, fillvalue=0)])


def multiply_tuple(tuple1: tuple, scalar: float) -> tuple:
	"""Multiply tuple with a scalar itemwise"""
	return tuple([a * scalar for a in tuple1])


def mult_tuple_to_int(tuple1: tuple, scalar: float) -> tuple:
	"""Multiply tuple with a scalar itemwise and cast the result to integer"""
	return tuple([int(a * scalar) for a in tuple1])

