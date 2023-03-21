"""Setup file for cx_Freeze"""

from cx_Freeze import setup, Executable

build_exe_options = {
	"packages": ["pygame"],
	"include_files": ["../res"],
	"includes": ["start_menu", "utils", "animations"],
	"build_exe": "build_win64",
	"silent_level": 1
}

setup(
	name="Puzzle Hustle",
	options={"build_exe": build_exe_options},
	executables=[Executable("puzzle.py")]
)
