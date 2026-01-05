import argparse
import string
import json
import random
from pathlib import Path
from unittest.mock import patch
from typing import Literal, Tuple, List, Union, Optional
from pydantic import BaseModel, field_validator, model_validator
import pandas as pd
import numpy as np
from psychopy import visual, core, event
import pygame

KEYMAP = {
    "Keyboard":{
        "left":"left",
        "right":"right",
        "exit":"escape"
    },
    "Controller":{
        "left":"A",
        "right":"Y",
        "exit":"X"
    }
          }

class Pos(BaseModel):
    left: Tuple[float, float]
    right: Tuple[float, float]

    @model_validator(mode="after")
    def sides_are_correct(values):
        assert values.left[0] < values.right[0]
        return values


class Config(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True
    }
    root_dir: Path
    input_method: Literal["Keyboard", "Controller"]
    controller: Optional[pygame.joystick.JoystickType] = None
    max_wait: Union[int, float]
    fix_dur: Union[int, float]
    cue_dur: Union[int, float]
    fix_radius: float
    fix_color: str
    stim_radius: float
    stim_color: str
    n_blocks: int
    n_trials: int
    p_valid: float
    pos: Pos

    @field_validator("root_dir")
    @staticmethod
    def root_dir_exists(value: Path) -> Path:
        assert value.exists()
        return value

    @field_validator("p_valid")
    @staticmethod
    def p_valid_is_percentage(value: float) -> float:
        assert 0 <= value <= 1
        return value

    @field_validator("fix_dur", "cue_dur")
    @staticmethod
    def durations_are_positive(value: Union[int, float]) -> float:
        assert 0 <= value <= 1
        return float(value)

    @model_validator(mode="after")
    def conditions_can_be_divided_into_n_trials(values):
        assert (values.n_trials / 2) * values.p_valid % 1 == 0
        return values

    @model_validator(mode="after")
    def get_controller(values):
        if values.input_method == "Controller":
            pygame.init()
            pygame.joystick.init()
            joystick_count = pygame.joystick.get_count()
            if joystick_count == 0:
                raise ValueError("No joystick detected")
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            values.controller = joystick
        return values


def test_experiment(subject_id: str, config: str, screen: int = 0):

    def mock_waitKeys(keyList):
        return [random.choice(keyList)]

    with patch("posner.experiment.event.waitKeys", side_effect=mock_waitKeys):
        run_experiment(subject_id, config, screen)


def run_experiment(win: visual.Window, config_file: str, overwrite: bool = False):

    config = load_config(config_file)
    clock = core.Clock()

    subject_id = get_text_input(win, "Enter you NAME and press any button to continue")
    subject_dir = make_subject_dir(config, subject_id)
    while subject_dir is None:
        subject_id = get_text_input(win, "The name already exists, pick a DIFFERENT one!", color="red")
        subject_dir = make_subject_dir(config, subject_id)

    display_instruction(win, config, clock)
    
    end = False
    df = []
    while not end:
        df.append(run_block(win, clock, config))
        response = display_break_prompt(win, config, clock)
        if response == "exit":
            end = True
    df = pd.concat(df)
    df.to_csv(subject_dir/f'{subject_id}_data.csv', index=False)
    run_experiment(win, config_file)

def run_block(
    win: visual.Window,
    clock: core.Clock,
    config: Config,
) -> pd.DataFrame:
    
    df = pd.DataFrame()
    for i in range(3):
        side, valid = roll_condition(config.p_valid)
        response, response_time = run_trial(win, clock, side, valid, config)
        row = pd.DataFrame(
            [{"side": side, "valid": valid, "response": response, "response_time": response_time}]
        )
        df = pd.concat([df, row])
    return df


def run_trial(
    win: visual.Window,
    clock: core.Clock,
    side: Literal["left", "right"],
    valid: bool,
    config: Config,
) -> Tuple[bool, float]:

    draw_frames(win, config)
    draw_fixation(win, config)
    win.flip()

    core.wait(config.fix_dur)

    draw_frames(win, config)
    draw_fixation(win, config)
    if (side == "left" and valid) or (side == "right" and not valid):
        draw_frames(win, config, highlight="left")
    else:
        draw_frames(win, config, highlight="right")
    win.flip()

    core.wait(config.cue_dur)

    draw_frames(win, config)
    draw_stimulus(win, config, side)
    win.flip()

    response, response_time = wait_for_response(config, clock, keys=["left", "right"], max_wait=config.max_wait)
    if response == side:
        response = True
    else:
        response = False
    return response, response_time

def roll_condition(p_valid: float) -> Tuple[Literal["left", "right"], bool]:
    side = np.random.choice(["left", "right"])
    valid = np.random.choice([True, False], p=[p_valid, 1-p_valid])
    return side, valid

def wait_for_response(
        config:Config, clock:core.Clock, keys:Union[None, List[str]]=None, max_wait:Union[int, float]=np.inf
) -> Tuple[Union[str,None], float]:
    clock.reset()
    response = None
    if config.input_method == "Keyboard":
        response = _get_response_keyboard(keys, max_wait, config)
    elif isinstance(config.controller, pygame.joystick.JoystickType):
        response = _get_response_controller(keys, max_wait,clock, config)
    else:
        raise ValueError("No valid input method found!")
    response_time = clock.getTime()
    return response, response_time

def _get_response_controller(keys, max_wait, clock, config):
    if keys is not None:
        key_list = [KEYMAP[config.input_method][k] for k in keys]
    else:
        key_list = []
    response = None
    while response is None and clock.getTime().real < max_wait:
        pygame.event.pump()
        button_states = [
            config.controller.get_button(i) for i in range(config.controller.get_numbuttons())
        ]
        if button_states[0]: # A button on 8BitDo
            response = "right"
        elif button_states[4]:
            response = "left" # Y button on 8BitDo
        elif button_states[3]:
            response = "exit" # Y button on 8BitDo
        elif any(button_states):
            response = "random"
        if response in key_list or (keys is None and response == "random"):
            break
    return response

def _get_response_keyboard(keys, max_wait, config) -> str:
    if keys is not None:
        key_list = [KEYMAP[config.input_method][k] for k in keys]
        keys = event.waitKeys(keyList=key_list, maxWait=max_wait)
        response = keys[0]
        return response

def draw_frames(
    win: visual.Window,
    config: Config,
    highlight: Optional[Literal["left", "right"]] = None,
) -> None:
    for side, pos in zip(["left", "right"], [config.pos.left, config.pos.right]):
        if side == highlight:
            color = config.stim_color
        else:
            color = "white"
        frame = visual.Rect(win, lineColor=color, pos=pos)
        frame.draw()


def draw_fixation(win: visual.Window, config: Config) -> None:
    fixation = visual.Circle(
        win, radius=config.fix_radius, size=(1 / win.aspect, 1), fillColor=config.fix_color
    )
    fixation.draw()


def draw_stimulus(
    win: visual.Window, config: Config, side: Literal["left", "right"]
) -> None:
    if side == "left":
        pos = config.pos.left
    elif side == "right":
        pos = config.pos.right
    stimulus = visual.Circle(
        win,
        pos=pos,
        radius=config.stim_radius,
        size=(1 / win.aspect, 1),
        fillColor=config.stim_color,
        lineColor=None,
    )
    stimulus.draw()

def draw_text(win: visual.Window, text: str) -> None:
    text_stim = visual.TextStim(win, text=text)
    text_stim.draw()
    win.flip()
    core.wait(0.5)

def display_instruction(win, config, clock):
    text = f"""Fixate the {config.fix_color.upper()} dot in the middle.
        One of the boxes will be highlighted {config.stim_color.upper()}.
        Then, a {config.stim_color.upper()} dot will appear. \n
        Say whether this dot is on the left or right side by pressing the {KEYMAP[config.input_method]["left"]} or {KEYMAP[config.input_method]["right"]} key.
        Respond as FAST as possible!\n
        Press any key to continue"""
    draw_text(win, text)
    wait_for_response(config, clock)

def display_break_prompt(win, config, clock):
    text = f" Press {KEYMAP[config.input_method]['exit']} if you want to exit. Press any other key to keep going"
    draw_text(win, text)
    response, _ = wait_for_response(config, clock, keys=["left", "right", "exit"])
    return response

def get_text_input( win:visual.Window, header_text:str, footer_text:str="", max_length:int=20, color="white") -> str:
    
    header = visual.TextStim(win, text=header_text, pos=(0, 0.3), color=color)
    text_box = visual.Rect(win, width=0.7, height=0.3, pos=(0,0), fillColor='darkgrey')
    display_text = visual.TextStim(win, text="", pos=(0,0), color='black')
    footer = visual.TextStim(win, text=footer_text, pos=(0, -0.2))
    current_text = ""
    
    while True:
        header.draw()
        text_box.draw()
        display_text.setText(current_text)
        display_text.draw()
        footer.draw()
        win.flip()
        keys = event.waitKeys()
        assert isinstance(keys, list)
        
        if 'return' in keys or 'enter' in keys:
            return current_text  # User confirmed entry
        
        elif 'backspace' in keys:
            current_text = current_text[:-1]
        
        else: # Add the pressed key if it's a valid character and within length limit
            for key in keys:
                if len(key) == 1 and len(current_text) < max_length:
                    if key in string.ascii_letters + string.digits + string.punctuation + ' ':
                        current_text += key


def load_config(config_file: str) -> Config:
    if not Path(config_file).exists():
        raise FileNotFoundError(f"Couldn't find config file at {config_file}")
    config_dict = json.load(open(config_file))
    return Config(**config_dict)


def make_subject_dir(config:Config, subject_id:str) -> Union[None, Path]:
    subject_dir = Path(config.root_dir) / "data" / subject_id
    if subject_dir.exists():
        return None
    else:
        subject_dir.mkdir(parents=True)
        return subject_dir

def main_cli():
    parser = argparse.ArgumentParser(description="A Python implementation of the Posner attention cueing task built on PsychoPy")
    parser.add_argument("config", type=str, help="Path to the JSON file with the experiments configuration")
    parser.add_argument("--screen", type=int, default=0, help="Number of the screen where window is displayed (defaults to 0)")
    parser.add_argument("--test", action="store_true", help="Run an automated test of the experiment")
    args = parser.parse_args()
    win = visual.Window(fullscr=True, screen=args.screen)
    if args.test is False:
        run_experiment(win, args.config)
    else:
        test_experiment(args.subject_id, args.config, args.overwrite, args.screen)

if __name__ == "__main__":
    main_cli()
