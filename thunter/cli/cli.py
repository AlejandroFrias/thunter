import re
import sys
from typing_extensions import Annotated

import typer.core
from rich.console import Console

from thunter import settings
from thunter.cli.create import app as create_app
from thunter.cli.db import app as db_app
from thunter.cli.edit import app as edit_app
from thunter.cli.estimate import app as estimate_app
from thunter.cli.finish import app as finish_app
from thunter.cli.init import app as init_app, init
from thunter.cli.ls import app as ls_app
from thunter.cli.restart import app as restart_app
from thunter.cli.rm import app as rm_app
from thunter.cli.show import app as show_app
from thunter.cli.stop import app as stop_app
from thunter.cli.workon import app as workon_app
from thunter.constants import ThunterError


class AliasGroup(typer.core.TyperGroup):
    """Custom override of TyperGroup to support command aliases.

    Watch this issue for possible native support in Typer for aliases:
    https://github.com/fastapi/typer/issues/1242
    """

    _CMD_SPLIT_P = re.compile(r" ?[,|] ?")

    def get_command(self, ctx, cmd_name):
        cmd_name = self._group_cmd_name(cmd_name)
        return super().get_command(ctx, cmd_name)

    def _group_cmd_name(self, default_name):
        for cmd in self.commands.values():
            name = cmd.name
            if name and default_name in self._CMD_SPLIT_P.split(name):
                return name
        return default_name


thunter_cli_app = typer.Typer(
    name="thunter",
    no_args_is_help=True,
    cls=AliasGroup,
)
# Add all subcommands to the main CLI app
thunter_cli_app.add_typer(init_app)
thunter_cli_app.add_typer(ls_app)
thunter_cli_app.add_typer(show_app)
thunter_cli_app.add_typer(workon_app)
thunter_cli_app.add_typer(create_app)
thunter_cli_app.add_typer(restart_app)
thunter_cli_app.add_typer(stop_app)
thunter_cli_app.add_typer(finish_app)
thunter_cli_app.add_typer(estimate_app)
thunter_cli_app.add_typer(edit_app)
thunter_cli_app.add_typer(rm_app)
thunter_cli_app.add_typer(db_app)


@thunter_cli_app.callback()
def main_callback(
    ctx: typer.Context,
    silent: Annotated[
        bool,
        typer.Option(
            "--silent",
            "--quite",
            "-s",
            help="Run thunter in silent mode, no output to console.",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-d",
            help="Run thunter in debug mode, printing out full exceptions and traces.",
        ),
    ] = False,
):
    """THunter - your task hunter, tracking time spent on your TODO list!"""
    settings.print_config["silent"] = silent or settings.THUNTER_SILENT
    settings.print_config["debug"] = debug or settings.DEBUG
    if ctx.invoked_subcommand != "init" and settings.needs_init():
        ctx.invoke(init)


def main():
    try:
        thunter_cli_app()
    except KeyboardInterrupt:
        sys.exit(1)
    except ThunterError as thunter_error:
        console = Console()
        if settings.print_config["debug"]:
            console.print_exception(show_locals=True)
        console.print(str(thunter_error))
        sys.exit(thunter_error.exit_status)


if __name__ == "__main__":
    main()
