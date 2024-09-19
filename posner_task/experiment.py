from psychopy import visual, core, event
import numpy as np

resolution = (1920, 1080)
width_scaling = resolution[1] / resolution[0]
win = visual.Window(size=resolution, fullscr=False)
clock = core.Clock()

arrow_vertices = np.array(
    [
        [-0.06, 0.01],
        [-0.06, -0.01],
        [-0.02, -0.01],
        [-0.02, -0.03],
        [0.02, 0],
        [-0.02, 0.03],
        [-0.02, 0.01],
    ]
)
fixation_dur = 0.25
cue_dur = 0.5


def run_block(sequence):
    for position, valid in sequence:
        response, response_time = run_trial(position, valid)


def run_trial(position, valid):
    """
    Run a single trial of the Posner cueing task
    Arguments:
        position (str): Stimulus position, can be "left" or "right".
        valid (bool): Whether the cue is valid (i.e. points to the target).
    Returns:
        response (str): Subject's response, can be "left" or "right".
        response_times (float): Time passed between stimulus presentation and response.
    """
    draw_frames()
    draw_fixation()
    win.flip()

    core.wait(fixation_dur)

    draw_frames()
    if (position == "left" and valid) or (position == "right" and not valid):
        draw_arrow("left")
    else:
        draw_arrow("right")
    win.flip()

    core.wait(cue_dur)

    draw_frames()
    draw_stimulus(position)
    win.flip()
    clock.reset()

    keys = event.waitKeys(keyList=["left", "right", "escape"])
    response = keys[0]
    response_time = clock.getTime()

    return response, response_time


def draw_frames():
    for x_pos in [-0.5, 0.5]:  # draw frames where stimulus may appear
        frame = visual.Rect(win, lineColor="white", pos=(x_pos, 0))
        frame.draw()


def draw_fixation():
    fixation = visual.Circle(  # size adjusts scaling for screen size
        win, radius=0.01, size=(1 * width_scaling, 1), fillColor="white"
    )
    fixation.draw()
    pass


def draw_arrow(point):
    if point == "left":
        cue = visual.ShapeStim(win, vertices=arrow_vertices * -1, lineColor="red")
    else:
        cue = visual.ShapeStim(win, vertices=arrow_vertices * 1, lineColor="red")
    cue.draw()
    pass


def draw_stimulus(side):
    if side == "left":
        x_pos = -0.5
    elif side == "right":
        x_pos = 0.5
    else:
        raise ValueError("Side must be 'left' or 'right'!")
    stimulus = visual.Circle(
        win,
        pos=[x_pos, 0],
        radius=0.02,
        size=(1 * width_scaling, 1),
        fillColor="black",
        lineColor=None,
    )
    stimulus.draw()


if __name__ == "__main__":
    response, response_time = run_trial("left", True)
    print(response, response_time)
    win.close()
