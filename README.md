# Thunter

`thunter`, or task hunter, is a CLI To Do list with time tracking.

The purpose of `thunter` is to get better at time estimation, hence why you cannot create a task without a time estimate.

I made ths CLI tool so that I could piggy back off my pre-existing git workflows to estimate and track time spent on tasks.
See [git/thunter workflow](#my-gitthunter-workflow) for git hooks and aliases you can use to do the same.

<img src="img/create_task-pauses-removed.gif">

## Installation

Via pip
```
pip install thunter
```

Or via uv
```
uv tool install thunter
```

## Usage


The `thunter` CLI tool has commands for:
* `create` - create a new task and estimate it's length
* `workon` / `stop` to start and stop tracking time spent on a task
    * `thunter workon --create <task_name>` will create the task if needed and then start tracking time on it
* `finish` / `restart` to mark a task as completed or to undo that action and restart it
* `estimate` to update your estimate
* `edit` to edit any aspect of a task, including it's history
* `rm` to delete/remove tasks
* `db` will start a sqlite3 session with the thunter database. `tasks` and `history` are the 2 tables

### Configuration options
Environment variables (see [settings.py](thunter/settings.py)):
- `EDITOR` - editor to use for `thunter edit` command
- `THUNTER_DIRECTORY` - directory to store thunter files, e.g. the sqlite database of tasks
- `THUNTER_DATABASE_NAME` - filename of the database
- `THUNTER_SILENT` - silent all console output. set to true, 1, yes, or y. Useful for scripting. Commands all have the `--silent` option as well for the same effect.
- `DEBUG` - get stack traces on errors. Useful for development


## My git/thunter workflow

With the below hook and aliases:
* checking out a branch will start tracking time spent on it
* checking out `main` will stop tracking time
* deleting a branch will mark the task as finished

### *post-checkout*
```
#!/bin/bash
branch_name=$(git rev-parse --abbrev-ref HEAD)
is_branch_switch=$3
if [[ "$is_branch_switch" == "1" ]]; then
    if [[ "$branch_name" == "main" || "$branch_name" == "master" ]]; then
        # `hash thunter 2>/dev/null` is a check for the existence of thunter before calling it
        hash thunter 2>/dev/null && thunter stop
    else
        # `< /dev/tty` is needed to accept the user's time estimate input
        hash thunter 2>/dev/null && thunter workon --create "$branch_name" < /dev/tty
    fi
fi
```

### Git Aliases

```
## ~/.gitconfig

[alias]
    s = "!git status && hash thunter 2>/dev/null && if [ \"$(git rev-parse --abbrev-ref HEAD)\" = \"main\" ]; then THUNTER_SILENT=1 thunter stop; else THUNTER_SILENT=1 thunter workon --create $(git rev-parse --abbrev-ref HEAD); fi"
    bd = ! git branch -d $1 && hash thunter 2>/dev/null && THUNTER_SILENT=1 thunter finish
    bdd = ! git branch -D $1 && hash thunter 2>/dev/null && THUNTER_SILENT=1 thunter finish
```

# Coming Soon

`thunter analyze` command that will give options for some basic data analysis on how accurate your time estimates are.
