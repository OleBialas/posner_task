# Posner

This is an implementation of the Posner attention cueing task [^1] implemented using the PsychoPy software package.

## Installation
It is recommended to install the package into a new environment using Python version 3.10 (this package does not require a specific version but it depends on PsychoPy which does).

For example, using conda
```sh
conda create -n posner python=3.8
conda activate posner
```

The experiment can be installed using `pip`
```sh
pip install git+https://github.com/OleBialas/posner_task.git
```

If you are experiencing any issues this is most likely due to the installation of PsychoPy - consult their [install documentation](https://www.psychopy.org/download.html)

## Run experiment

The experiment can be run from the command line.
You have top specify the subject's ID and path to a configuration file.
For example, if the subject's ID is 3 and the configuration is a file called `config.json` in the current directory, run:

```sh
posner 3 config.json
```

### Configuration
The configuration file is written in the JSON format and looks like this:
```json
{
    "root_dir": "",
    "fix_dur": 0.5,
    "cue_dur": 0.5,
    "fix_radius": 0.025,
    "fix_color": "white",
    "stim_radius": 0.05,
    "stim_color": "red",
    "n_blocks": 2,
    "n_trials": 10,
    "p_valid": 0.8,
    "pos": {"left":  [-0.5, 0], "right": [0.5, 0]}
}

```
- `root `is the directory where the experimental results are saved (a data new subdirectory `data` will be created
- `fix_dur` is the duration the fixation point is displayed (in seconds)
- `cue_dur` is the duration the cue before the stimulus is displayed (in seconds)
- `fix_radius`: is the radius of the fixation point
- `fix_color` is the color of the fixation point
- `stim_radius` is the radius of the stimulus point
- `stim_color` is the color of the stimulus
- `n_trials` is the number of trials per block
- `n_blocks` is the number of blocks
- `p_valid` is the percentage of trials where the cue is valid (i.e. correctly indicates the stimulus' location)
- `pos` contains the x and y coordinates for visual elements on the left and right side

Positions and sizes are defined in PsychoPy's [normlaized units](https://www.psychopy.org/general/units.html#normalised-units)

### Data storage
The program will create a folder for the given subject ID in the root directory and store the results using one CSV file per block.
If the respective subject folder already exists, the program will throw an error.
You can use the `--overwrite` flag to ignore this and overwrite existing data:

```sh
posner 3 config.json --overwrite
```

### Testing
To make sure the experiment runs without error, you can run an automated test using the `--test` flag:

```sh
posner 7 config.json --test
```
This will run the whole experiment and randomly select whenever a response is being prompted.
The data generated by the test is deleted afterwards




## Footnotes
[^1]:Posner, M. I. (1980). Orienting of attention. Quarterly journal of experimental psychology, 32(1), 3-25.
