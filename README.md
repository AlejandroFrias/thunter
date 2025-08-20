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

### Configuration options
Environment variables (see [settings.py](thunter/settings.py)):
- `EDITOR` - editor to use for `thunter edit` command
- `THUNTER_DIRECTORY` - directory to store thunter files, e.g. the sqlite database of tasks
- `THUNTER_DATABASE_NAME` - filename of the database
- `THUNTER_SILENT` - silent all console output. set to true, 1, yes, or y. Useful for scripting. Commands all have the `--silent` option as well for the same effect.
- `DEBUG` - get stack traces on errors. Useful for development


## My git/thunter workflow

Many of us already have our git workflows.
Below are 2 ways to integrate `thunter` into your existing workflows: git-hooks and aliases


### Git Hooks

* `post-checkout` - handles creating and tracking time spent on tasks
* `post-merge` - handles marking tasks as finished

####  *post-checkout*

Switching to the `main` branch will stop tracking time.

Switching to any other branch will start tracking time on a task with the same name, possibly creating the task if it didn't exist and prompting you for a time estimate.


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

#### *post-merge*

TODO write and figure out how the merge hook works

### Git Aliases

If you are consistent with your usage of aliases, this can be another way to integrate the 2 together.
I prefer git-hooks because they work even when I don't use my aliases, like when using a GUI tool or some other git wrapper like graphite.

You can use a combination of both. I use just the `git status` alias below and the 2 hooks above.

```
## ~/.gitconfig

[alias]
    s = "!git status && hash thunter 2>/dev/null && if [ \"$(git rev-parse --abbrev-ref HEAD)\" = \"main\" ]; then THUNTER_SILENT=1 thunter stop; else THUNTER_SILENT=1 thunter workon --create $(git rev-parse --abbrev-ref HEAD); fi"
    ch = "!git checkout $1 && hash thunter 2>/dev/null && if [ \"$(git rev-parse --abbrev-ref HEAD)\" = \"master\" ]; then THUNTER_SILENT=1 thunter stop; else THUNTER_SILENT=1 thunter workon --create $(git rev-parse --abbrev-ref HEAD); fi"
    chb = !git checkout -b $1 && hash thunter 2>/dev/null && thunter workon --create $(git rev-parse --abbrev-ref HEAD)
    chm = ! git checkout main && hash thunter 2>/dev/null && THUNTER_SILENT=1 thunter stop
    bd = ! git branch -d $1 && hash thunter 2>/dev/null && THUNTER_SILENT=1 thunter finish
    bdd = ! git branch -D $1 && hash thunter 2>/dev/null && THUNTER_SILENT=1 thunter finish
```
