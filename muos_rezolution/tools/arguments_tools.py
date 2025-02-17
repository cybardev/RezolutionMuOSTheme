from argparse import ArgumentParser
from enum import Enum

import muos_rezolution.tools.display_tools as c
from muos_rezolution.tools.__global__ import config as cf

allKeyword = "All"


class GridEnabler(Enum):
    ON = "on"
    OFF = "off"
    BOTH = "both"

    def accepted(self):
        return self != GridEnabler.OFF

    def declined(self):
        return self != GridEnabler.ON


class RezArguments:
    themes: list[str]
    grid: GridEnabler
    cleanUp: bool

    def __init__(self, themes: list[str], grid: GridEnabler, cleanUp=False):
        self.themes = themes
        self.grid = grid
        self.cleanUp = cleanUp


def parseStringEx(s: str, valid: list[str], wantsAll=allKeyword):
    res = set([x.strip() for x in s.split(",")])
    if len(res) == 1 and list(res)[0] == wantsAll:
        return valid
    if not res <= set(valid):
        raise ValueError(f"{res} is not in {valid}")
    return list(res)


def ifttt(cond: bool, then, otherwise=None):
    if cond:
        return then
    else:
        return otherwise


class RezParser(ArgumentParser):
    rezVariants: list[str]

    def __init__(self, variants: list[str]):
        self.rezVariants = variants
        super().__init__(
            prog="muos_rezolution",
            description="Rezolution, an elegant and easy on the eyes MuOS theme.",
            allow_abbrev=False,
        )

        self.register("type", "ThemesList", lambda s: parseStringEx(s, self.rezVariants))
        self.register("type", "GridEnabler", lambda s: GridEnabler(s))

        self.add_argument(
            "-t",
            "--theme",
            help=f"generates one or multiple themes ([{', '.join(self.rezVariants)}], default : All)",
            metavar="THEME[,THEME,...]",
            type='ThemesList',
            dest="theme",
            default=self.rezVariants,
        )
        self.add_argument(
            "-g",
            "--grid",
            help=f"adds grid support ([{', '.join([x.value for x in GridEnabler])}], default : Both)",
            metavar="GRID",
            type="GridEnabler",
            dest="gridStyle",
            default=GridEnabler.BOTH,
        )
        self.add_argument(
            "-i",
            "--interactive",
            help="runs the program in interactive mode",
            action="store_true",
            dest="interactiveFlag",
        )
        self.add_argument(
            "-v",
            "--verbose",
            help="displays debug info",
            action="store_true",
            dest="verboseFlag",
        )
        self.add_argument(
            "-c",
            "--clean",
            help="removes the build folder",
            action="store_true",
            dest="cleanFlag",
        )

    def parseArgs(self) -> RezArguments:
        args = self.parse_args()
        if args.verboseFlag:
            cf.VERBOSE = True
        if args.interactiveFlag:
            res = self.startInteractivePrompt()
        else:
            res = RezArguments(args.theme, args.gridStyle, args.cleanFlag)
        c.info(f"Got ({res.themes}, {res.grid}, {res.cleanUp})")
        return res

    def startInteractivePrompt(self) -> RezArguments:
        wantsGrid = c.ask("Do you want to generate the theme with grid support ?", ["Both", "No", "Yes"])
        grid = GridEnabler(("both", "off", "on")[wantsGrid])

        wantsThemes = c.ask("Which theme variants do you want?", [allKeyword] + self.rezVariants)
        themes = ifttt(
            wantsThemes == 0,
            self.rezVariants,
            [self.rezVariants[wantsThemes - 1]]
        )

        return RezArguments(themes, grid)
