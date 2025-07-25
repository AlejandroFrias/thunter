# Thunter

`thunter` is CLI To Do list with time tracking.

Why the name `thunter`? What do hunters do? They track their prey.
In this case it's tracking your time spent on tasks. A Task Hunter. A T-Hunter, or thunter if you will.
It's a bit of stretch, I know.

I made this tool to help me get better at time estimations on tasks.
I knew I needed to start writing down my time estimates *before* starting the task, track how much time I spent on the task, and then compare the data so I could start to naturally self-correct.
But that was never going to happen if I needed to open a separate app or if it relied on adding a new habit to my existing workflows.

So I made ths CLI tool that I could incorporate into my existing git workflows. See [My git/thunter workflow](#my-gitthunter-workflow) for the aliases I used to achieve a nearly zero effort way to track time spent on each branch, but flexible enough to update to track other tasks that weren't one to one with branches.

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

## My git/thunter workflow

In my regular git workflow, I generally start any work task by making a new branch with the task name or checking out that branch to continue working on it from a previous work session. When I finish a task, I delete the branch.

So with those easy entry points, I made it so checking out or creating a branch with create and start tracking time spent on that branch. And deleting a task will mark it as finished.

I also checkout main when I'm taking a break from a task or at the end of the day. I'm one of those people who also likes to close all their tabs at the end of the day. Weird I know, but it worked out well in this case as an easy way to stop tracking time spent on tasks.

Any time I strayed from these habits, or I wanted to track a task differently, I had the `thunter` CLI at my fingertips (I live on the command line), to quickly edit an existing task (usually to put in a stop time when I forgot to checkout main) or to manually create a separate task, like a research or presentation task.

Below are the git aliases I use with `thunter`.

The key takeaways for updating your own aliases is that the env variable HUNT_SILENT=1 will silence the hunt output (which can get annoying if you're just trying to use git) and `thunter workon` has the `-c` or `--create` flag so you don't need to worry about creating duplicate tasks. `thunter create` will auto prompt you for an estimate, so it also doesn't play nice with scripts like the other commands do.

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
