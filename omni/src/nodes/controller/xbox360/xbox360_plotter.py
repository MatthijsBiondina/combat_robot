import os
import time
from copy import copy

from src.cyclone.cycloneddsnode import CycloneDDSNode
from src.idl.xbox360_pod import Xbox360POD
from src.nodes.controller.xbox360.xbox360_reader import Xbox360Reader
from src.utils.logger import get_logger
from src.utils.tools import pyout, pretty_string

logger = get_logger()


class Xbox360Plotter(CycloneDDSNode):
    ascii_base = """
    
    
    
      L_trigg                               R_trigg
     / Lbump \                             / Rbump \\
   +.-'     '-.---------------------------.-'     '-.+
  /   l_stick  '.                       .'   but_Y    \\
 /   |l_joy_0|   \                     /     but_Y     \\
/    |l_joy_1|    ;  __           __  ;  btX       btB  ;
|    |l_joy_2|    | back         strt |  btX       btB  |
|    |l_joy_3|    ;                   ;  btX       btB  ;
|\   |l_joy_4|   /              r_stick\     but_A     /|
| \   l_stick  .','" "',       |r_joy_0|'.   but_A   .' |
|  '-.______.-' /   ^   \      |r_joy_1|  '-._____.-'   |
|               | <   > |------|r_joy_2|                |
|              /\   v   /      |r_joy_3|\               |
|             /  '.___.'       |r_joy_4| \              |
|            /                  r_stick   \             |
 \          /                              \           /
  \________/                                \_________/
     """

    connection = """
    
    
    
      =======                               =======
     / ===== \                             / ===== \\
   +.-'     '-.---------------------------.-'     '-.+
  /            '.       █████████       .'            \\
 /   |       |   \       ███████       /               \\
/    |       |    ;  __   █████   __  ;                 ;
|    |       |    |        ███        |                 |
|    |       |    ;                   ;                 ;
|\   |       |   /         ███         \               /|
| \            .','" "',   ███ |       |'.           .' |
|  '-.______.-' /   ^   \      |       |  '-._____.-'   |
|               | <   > |------|       |                |
|              /\   v   /      |       |\               |
|             /  '.___.'       |       | \              |
|            /                            \             |
 \          /                              \           /
  \________/                                \_________/
     """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.controller = Xbox360Reader(suppress_warnings=True)

        self.__run()

    def __run(self):
        time.sleep(5)
        os.system("clear")
        while True:
            try:
                state = self.controller.state

                ascii = copy(self.ascii_base)
                ascii = self.__buttons(ascii, state)
                ascii = self.__joysticks(ascii, state)
                ascii = self.__dpad(ascii, state)

                print(ascii)
                nr_of_lines = len(ascii.split("\n"))
                print(f"\033[{nr_of_lines}A", end="\r")
            except AttributeError:
                print(pretty_string(self.connection, color="YELLOW"))
                nr_of_lines = len(self.connection.split("\n"))
                print(f"\033[{nr_of_lines}A", end="\r")

            except Exception as e:
                logger.exception(f"Er is een onverwachte fout opgetreden: {e}")
            self.sleep()

    def __buttons(self, ascii: str, state: Xbox360POD) -> str:
        button_A = pretty_string("#####", color="GREEN") if state.button_A else "     "
        ascii = ascii.replace("but_A", button_A)

        button_B = pretty_string("###", color="RED") if state.button_B else "   "
        ascii = ascii.replace("btB", button_B)

        button_X = pretty_string("###", color="BLUE") if state.button_X else "   "
        ascii = ascii.replace("btX", button_X)

        button_Y = pretty_string("#####", color="YELLOW") if state.button_Y else "     "
        ascii = ascii.replace("but_Y", button_Y)

        l_bump = (
            pretty_string("#####", color="CYAN")
            if state.button_left_bumper
            else "====="
        )
        ascii = ascii.replace("Lbump", l_bump)

        r_bump = (
            pretty_string("#####", color="CYAN")
            if state.button_right_bumper
            else "====="
        )
        ascii = ascii.replace("Rbump", r_bump)

        back = pretty_string("####", color="CYAN") if state.button_back else "    "
        ascii = ascii.replace("back", back)

        strt = pretty_string("####", color="CYAN") if state.button_start else "    "
        ascii = ascii.replace("strt", strt)

        l_stick = (
            pretty_string("VVVVVVV", color="CYAN")
            if state.button_left_stick
            else "       "
        )
        ascii = ascii.replace("l_stick", l_stick)
        r_stick = (
            pretty_string("VVVVVVV", color="CYAN")
            if state.button_right_stick
            else "       "
        )
        ascii = ascii.replace("r_stick", r_stick)

        return ascii

    def __joysticks(self, ascii: str, state: Xbox360POD) -> str:
        ly = min(int((state.axis_left_stick_y + 1) / 2 * 5), 4)
        lx = min(int((state.axis_left_stick_x + 1) / 2 * 7), 6)
        for ii in range(5):
            row_str = list("       ")
            row_str[lx] = "X"
            row_str = "".join(row_str) if ii == ly else "       "
            ascii = ascii.replace(f"l_joy_{ii}", pretty_string(row_str, color="CYAN"))

        ry = min(int((state.axis_right_stick_y + 1) / 2 * 5), 4)
        rx = min(int((state.axis_right_stick_x + 1) / 2 * 7), 6)
        for ii in range(5):
            row_str = list("       ")
            row_str[rx] = "X"
            row_str = "".join(row_str) if ii == ry else "       "
            ascii = ascii.replace(f"r_joy_{ii}", pretty_string(row_str, color="CYAN"))

        l_trigger = min(int((state.axis_left_trigger + 1) / 2 * 7 + 0.5), 7)
        ascii = ascii.replace(
            f"L_trigg",
            pretty_string("#" * l_trigger, color="CYAN") + ("=" * (7 - l_trigger)),
        )

        r_trigger = min(int((state.axis_right_trigger + 1) / 2 * 7 + 0.5), 7)
        ascii = ascii.replace(
            f"R_trigg",
            pretty_string("#" * r_trigger, color="CYAN") + ("=" * (7 - r_trigger)),
        )
        return ascii

    def __dpad(self, ascii: str, state: Xbox360POD) -> str:
        x = state.hat_D_pad_x
        y = state.hat_D_pad_y

        if y == 1:
            ascii = ascii.replace("^", pretty_string("#", color="CYAN"))
        elif y == -1:
            ascii = ascii.replace("v", pretty_string("#", color="CYAN"))

        if x == 1:
            ascii = ascii.replace(">", pretty_string("#", color="CYAN"))
        elif x == -1:
            ascii = ascii.replace("<", pretty_string("#", color="CYAN"))

        return ascii


if __name__ == "__main__":
    node = Xbox360Plotter()
