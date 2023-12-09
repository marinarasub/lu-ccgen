from sys import exit, argv, stdout, stderr
import os
import platform
import traceback
from datetime import datetime
import argparse
import logging

import fpdf
from fpdf import FPDF

import ccgen_util as util


# TODO
# - add more grid options
# - size, align and paper layout options
# - add more logging
# - windows font find
# - JSON configuration

OSNAME = platform.system()
CWD = os.getcwd()
HOMEDIR = os.path.expanduser('~')
MODULEDIR = os.path.dirname(os.path.abspath(__file__))

WINDOWS_FONTDIR = "C:\Windows\fonts"
LINUX_FONTDIR1 = "/usr/share/fonts"
LINUX_FONTDIR2 = "/usr/local/share/fonts"
LINUX_FONTDIR3 = os.path.join(HOMEDIR, ".local/share/fonts")

PDF_EXT = ".pdf"
FONT_EXTS = [".ttf", ".otf"]
GRID_DIRNAME = os.path.join(MODULEDIR, "grids")

CONST_SIZE_UNIT = "mm"
BOX_VALIGN_OFFSET = -0.6 # characters don't seem to be vertically centered so add offset for now - seems to differ b/t fonts so add as option?

DEFAULT_NCHAR = 0
DEFAULT_NBOX = 0
DEFAULT_FONTSIZE = 54
DEFAULT_TITLEFONTSIZE = 32
DEFAULT_TEXTFONTSIZE = 16
DEFAULT_FOOTERFONTSIZE = 10
DEFAULT_FONT = "Arial"
DEFAULT_OUTPUT_FILEPATH = "out" + PDF_EXT
DEFAULT_MARGIN = util.in_to_mm(1)
DEFAULT_PAPERSIZE = "letter"
DEFAULT_ORIENTATION = "portrait"
DEFAULT_INTERCHAR_VSPACE = 4 # mm
DEFAULT_GRID_IMG = "mi-grid.png"
DEFAULT_CHARPAD = 2 # mm
DEFAULT_BOXSPACE = 1 # mm

LOGFORMAT = "%(asctime)s [%(levelname)s] %(message)s"


logging.getLogger(fpdf.__name__).setLevel(logging.WARNING)

log = None


class run_config:
    def __init__(self):
        self.font_name: str = ""
        self.title: str = ""
        self.chars: 'list[str]' = []
        self.output_path: str = ""
        self.nchar: int = 0
        self.nbox: int = 0
        self.round: bool = False
        self.font_size: int = 0


def iswindows() -> bool:
    return OSNAME == "Windows"


def islinux() -> bool:
    return OSNAME == "Linux"


def find_font_windows(fname: str) -> str:
    # TODO
    return ""


def find_font_linux(font_fname: str) -> str:
    check_dirs = [
        CWD,
        LINUX_FONTDIR1,
        LINUX_FONTDIR2,
        LINUX_FONTDIR3,
    ]

    for dir in check_dirs:
        log.debug(f"looking for font in {dir} ...")
        for root, dnames, fnames in os.walk(dir):
            for fname in fnames:
                log.debug(f"checking file {fname}")
                # if not ext, try all font exts
                if os.path.splitext(font_fname)[1] == "":
                    for ext in FONT_EXTS:
                        if fname == font_fname + ext:
                            log.debug(f"found file {fname}")
                            return os.path.join(root, fname)
                else:
                    if fname == font_fname:
                        log.debug(f"found file {fname}")
                        return os.path.join(root, fname)

    return ""


def find_font(fname: str) -> str:
    if iswindows():
        return find_font_windows(fname)
    elif islinux():
        return find_font_linux(fname)
    else:
        pass
    return ""

class ccgen_pdf(FPDF):
    def __init__(
            self,
            config: run_config,
            orientation = DEFAULT_ORIENTATION,
            format = DEFAULT_PAPERSIZE
        ) -> None:
        super().__init__(orientation=orientation, unit=CONST_SIZE_UNIT, format=format)
        self.config = config

    def setup_pdf_fonts(self):
        font_path = find_font(self.config.font_name)
        if font_path:
            log.debug(f"found font {font_path}")
            self.add_font(family=self.config.font_name, fname=font_path)


    def setup_pdf_metadata(self):
        self.set_creator("ccgen")
        self.set_creation_date


    def setup_pdf_page_layout(self):
        self.set_margins(left=DEFAULT_MARGIN, top=DEFAULT_MARGIN, right=DEFAULT_MARGIN)
        self.set_auto_page_break(False, margin=DEFAULT_MARGIN)


    def set_pdf_font_for_characters(self):
        self.set_font(family=self.config.font_name)
        self.set_font_size(size=self.config.font_size)


    def set_pdf_font_for_title(self):
        self.set_font(family=self.config.font_name)
        self.set_font_size(size=DEFAULT_TITLEFONTSIZE)


    def set_pdf_font_for_text(self):
        self.set_font(family=self.config.font_name)
        self.set_font_size(size=DEFAULT_TEXTFONTSIZE)


    def set_pdf_font_for_footer(self):
        self.set_font(family=self.config.font_name)
        self.set_font_size(size=DEFAULT_FOOTERFONTSIZE)


    def footer(self): # override
        self.set_pdf_font_for_footer()
        self.set_y(-self.b_margin)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', border=0, align='C')
        self.ln()


    def header(self): # override
        if self.config.title:
            self.set_pdf_font_for_title()
            self.cell(w=0, h=0, text=self.config.title, border=0, align='C')
            self.ln()


    def add_name_date(self):
        self.set_pdf_font_for_text()
        self.cell(w=0, h=0, text="Name:", border=0, align='L')
        self.ln()
        self.cell(w=0, h=0, text="Date:", border=0, align='L')
        self.ln()
        self.ln()
    

    def add_box(self, box_size: float, c: str):
        x = self.get_x()
        y = self.get_y()

        self.image(
            x=x + DEFAULT_BOXSPACE / 2,
            y=y + DEFAULT_BOXSPACE / 2 + BOX_VALIGN_OFFSET,
            w=box_size - DEFAULT_BOXSPACE,
            h=box_size - DEFAULT_BOXSPACE,
            name=os.path.join(GRID_DIRNAME, DEFAULT_GRID_IMG)
        )
        
        self.set_xy(x, y)

        self.cell(w=box_size, h=box_size, text=c, border=0, align='C')
    

    def write_output(self):
        output_path = self.config.output_path
        if os.path.splitext(output_path)[1] == "":
            output_path += PDF_EXT
        self.output(output_path)
        log.info(f"Output written to {output_path}")


    def make_pdf(self) -> None:
        self.setup_pdf_metadata()
        self.setup_pdf_fonts()
        self.setup_pdf_page_layout()

        pn = 0 # page num
        i = 0 # ith character
        k = 0 # kth box per character

        while i < len(self.config.chars):
            self.add_page()
            pn += 1

            if pn == 1:
                self.add_name_date()

            box_size = util.pt_to_mm(self.config.font_size) + 2 * DEFAULT_CHARPAD
            content_width = self.w - self.l_margin - self.r_margin
            content_height = self.h - self.get_y() - self.b_margin
            max_x = self.w - self.r_margin
            max_y = self.h - self.b_margin

            max_k = self.config.nchar + self.config.nbox
            
            # max_per_line = int(content_width // box_size)
            # max_lines = int(content_height // box_size)
            # max_boxes_per_line = int(content_width // box_size)
            # char_boxes_per_line = int(max_boxes_per_line // 2)

            # add chars to page while they fit
            self.set_pdf_font_for_characters()
            while self.get_y() + box_size < max_y and i < len(self.config.chars):
                while self.get_x() + box_size < max_x and i < len(self.config.chars):
                    c = self.config.chars[i]
                    if k >= self.config.nchar:
                        c =  ''
                    
                    self.add_box(box_size, c)
                    
                    # update i, k
                    k += 1
                    if k >= max_k:
                        # if round, add boxes until line is filled
                        if self.config.round and self.get_x() + box_size < max_x:
                            continue

                        self.ln(DEFAULT_INTERCHAR_VSPACE)
                        i += 1
                        k = 0
                        break
                
                self.ln()
           
        self.write_output()


def run(config: run_config) -> None: 
    for c in config.chars:
        if len(c) != 1 or not c.isprintable() or c.isspace():
            log.error(f"'{c}' is not a single character or is an invalid character")
            return
        else:
            log.info(f"using character '{c}'")

    pdf = ccgen_pdf(config)
    pdf.make_pdf()


def log_level_from_arg(arg: str) -> int:
    if arg == "DEBUG":
        return logging.DEBUG
    elif arg == "INFO":
        return logging.INFO
    elif arg == "WARNING":
        return logging.WARNING
    elif arg == "ERROR":
        return logging.ERROR
    else:
        try:
            return int(arg)
        except ValueError as e:
            pass
        print("invalid log level, returning default")
        return logging.WARN


def setup_logger(log_level: int):
    global log
    handler = logging.StreamHandler(stderr)
    formatter = logging.Formatter(fmt=LOGFORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logging.getLogger(__name__).setLevel(log_level)
    logging.getLogger(__name__).addHandler(handler)
    log = logging.getLogger(__name__)


def config_from_args(args) -> run_config:
    config = run_config()
    config.font_name = args.font
    config.title = args.title
    config.chars = [c for c in args.chars]
    if args.output:
        config.output_path = args.output
    elif args.title:
        config.output_path = args.title + PDF_EXT
    else:
        config.output_path = DEFAULT_OUTPUT_FILEPATH
    config.nchar = args.nchar
    config.nbox = args.nbox
    config.round = not args.no_round
    config.font_size = args.size
    return config


def main(argv: 'list[str]') -> int:
    parser = argparse.ArgumentParser(description="Chinese character worksheet generator (田字格字帖产生器/田字格字帖產生器)")
    parser.add_argument("-l", "--log", help="set log level", default="INFO")
    parser.add_argument("-f", "--font", help="which font to use", default=DEFAULT_FONT)
    parser.add_argument("-t", "--title", help="title of page", default="")
    parser.add_argument("chars", help="which characters to use")
    parser.add_argument("--nchar", type=int, help="how many copies per character, 0 is fit page width", default=DEFAULT_NCHAR)
    parser.add_argument("--nbox", type=int, help="how many blank boxes for each character, 0 is fit page width", default=DEFAULT_NBOX)
    parser.add_argument("--no-round", action="store_true", help="don't round up nbox to fit line", default=False)
    parser.add_argument("--size", type=int, help="font size (pt)", default=DEFAULT_FONTSIZE)
    parser.add_argument("-o", "--output", help="name of output file")

    try:
        args = parser.parse_args(argv[1:])

        setup_logger(log_level_from_arg(args.log))

        config = config_from_args(args)

        run(config)
    except Exception as e:
        print(traceback.format_exc())
        return 1

    return 0


if __name__ == "__main__":
    exit(main(argv))
else:
    print("ccgen should only be run as main!")
    exit(1)