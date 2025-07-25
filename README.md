# HUNT

HUNT is yet another CLI To Do list with time tracking.

Why the name HUNT? Tracking. Hunting. Get it? It's a bit of stretch, I know.

I made this tool to help me get better at time estimations on tasks.
I knew I needed to start writing down my time estimates *before* starting the task, track how much time I spent on the task, and then compare the data so I could start to naturally self-correct.

To do this I made ths CLI tool that I could incorporate into my existing git workflows. See [My git/huntworkflow](#my-githunt-workflow) for the aliases I used to achieve this.





## Features

TODO

Just try it. I'll finish this before putting it up on pypi

TODO: add created at time stamp and display that somewhere...

## Installation

```
git clone https://github.com/AlejandroFrias/hunt
cd hunt
make install
```

## My git/hunt workflow

```
## ~/.gitconfig

[alias]
    s = "!HUNT_SILENT=1 git status && hash hunt 2>/dev/null && if [ \"$(git rev-parse --abbrev-ref HEAD)\" = \"main\" ]; then hunt stop; else hunt workon $(git rev-parse --abbrev-ref HEAD); fi"
    chb = ! git checkout -b $1 && hash hunt 2>/dev/null && read -er -p 'Estimate '$1' (hrs): ' estimate && hunt --silent workon --create --estimate ${estimate:-0}
    ch = "!git checkout $1 && hash hunt 2>/dev/null && if [ \"$(git rev-parse --abbrev-ref HEAD)\" = \"master\" ]; then hunt --silent stop; else hunt --silent workon --create $(git rev-parse --abbrev-ref HEAD); fi && echo 1>/dev/null"
    chm = ! git checkout master && hash hunt 2>/dev/null && hunt --silent stop
    pushc = ! git push --set-upstream origin $(git rev-parse --abbrev-ref HEAD) && hash hunt 2>/dev/null && hunt --silent stop
    bd = ! git branch -d $1 && hash hunt 2>/dev/null && hunt --silent finish
    bdd = ! git branch -D $1 && hash hunt 2>/dev/null && hunt --silent finish

```

`g s` checks the git status and starts work on the current branch.

`git chb <branch>` creates a new branch and creates a new task with the branch name.
This will prompt to you to enter an estimate (default to 0).

`git ch <branch>` will start working on a task named after the current branch.
Swithcing to master, however, will stop working on the current task.

`git chm` switches to master and stops work on the current task.

`git pushc` pushes your changes and stops work on the task.

`git bd` and `git bdd` are used to delete the branch and finish the task.

Checking out the branch or checking the status of the branch is often how I start my work sessions, so I have hunt start working on the ticket with current branch name.

I end my work session by either checking out master or pushing my changes, so I stop working on the current task whenever I do that.

Deleting my branches is what I do after I've merged to master, so I finish my tasks as part of branch deletion.

I use `hunt edit` to fix tasks, like editing the start/stop times or updating an estimate or even adding a description to the task.

I use `hunt ls` to check my unfinished tasks.
