from argparse import ArgumentParser

import Aurora.tools.display_tools as c
from Aurora.tools.__global__ import config as cf, ifttt

allKeyword = "All"


class RezArguments:
    themes: list[str]
    cleanUp: bool
    iconPack: bool

    def __init__(self, themes: list[str], cleanUp=False, iconPack=False):
        self.themes = themes
        self.cleanUp = cleanUp
        self.iconPack = iconPack


def parseStringEx(s: str, valid: list[str], wantsAll=allKeyword):
    res = set([x.strip() for x in s.split(",")])
    if len(res) == 1 and list(res)[0] == wantsAll:
        return valid
    if not res <= set(valid):
        raise ValueError(f"{res} is not in {valid}")
    return list(res)


class RezParser(ArgumentParser):
    rezVariants: list[str]

    def __init__(self, variants: list[str]):
        self.rezVariants = variants
        super().__init__(
            prog="Aurora",
            description="Aurora, an elegant and easy on the eyes MuOS theme.",
            allow_abbrev=False,
        )

        self.register("type", "ThemesList", lambda s: parseStringEx(s, self.rezVariants))

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
            "-p",
            "--iconpack",
            help="generates the icon pack and exits",
            action="store_true",
            dest="iconPackFlag",
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
            help="removes the build folder and exits",
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
            res = RezArguments(args.theme, args.cleanFlag, args.iconPackFlag)
        c.info(f"Got ({res.themes}, {res.cleanUp}, {res.iconPack})")
        return res

    def startInteractivePrompt(self) -> RezArguments:
        wantsThemes = c.ask("Which theme variants do you want?", [allKeyword] + self.rezVariants)
        themes = ifttt(
            wantsThemes == 0,
            self.rezVariants,
            [self.rezVariants[wantsThemes - 1]]
        )

        return RezArguments(themes)
