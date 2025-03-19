# Posner

This is an implementation of the Posner attention cueing task [^1] implemented using the PsychoPy software package.

## Installation
It is recommended to install the package into a new environment using Python version 3.10 (this package does not require a specific version but it depends on PsychoPy which does).

For example, using conda
```sh
conda create -n posner python=3.10
conda activate posner
```

The experiment can be installed using `pip`
```sh
pip install git+https://github.com/OleBialas/posner_task.git
```

If you are experiencing any issues this is most likely due to the installation of PsychoPy - consult their [install documentation](https://www.psychopy.org/download.html)

## Run experiment

You can run the experiment from the command line.
You have to pass the path to a JSON file that contains the parameters.
For example, with the `parameters.json` file from this repo:

```sh
posner parameters.json
```

### Data storage

Data are stored in a `data` subfolder in the root directory defined in the configuration file.
A new folder is created for every subject

## Leaderboard

To generate a leaderboard that lists the performance of all subjects run
```sh
python leaderboard.py
```
This program will continuously monitor the `data` folder an update the leaderboard whenever new data is written.
It outputs a `leaderboard.html` file which can be displayed in the browser.

## Footnotes
[^1]:Posner, M. I. (1980). Orienting of attention. Quarterly journal of experimental psychology, 32(1), 3-25.
