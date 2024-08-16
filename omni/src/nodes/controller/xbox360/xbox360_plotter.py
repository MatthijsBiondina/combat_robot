import os
from copy import copy

from src.cyclone.cycloneddsnode import CycloneDDSNode
from src.idl.xbox360_pod import Xbox360POD
from src.nodes.controller.xbox360.xbox360_reader import Xbox360Reader
from src.utils.logger import get_logger
from src.utils.tools import pyout, pretty_string

logger = get_logger()


class Xbox360Plotter(CycloneDDSNode):
    ascii_base = """
      _Lbump_                               _Rbump_
     / _____ \                             / _____ \\
   +.-'     '-.---------------------------.-'     '-.+
  /   l_stick  '.                       .'   but_Y    \\
 /   |       |   \                     /     but_Y     \\
/    |       |    ;  __           __  ;  btX       btB  ;
|    |       |    | back         strt |  btX       btB  |
|    |       |    ;                   ;  btX       btB  ;
|\   |       |   /  _           _______\     but_A     /|
| \   l_stick  .','" "',       |       |'.   but_A   .' |
|  '-.______.-' /   ^   \      |       |  '-._____.-'   |
|               | <   > |------|       |                |
|              /\   v   /      |       |\               |
|             /  '.___.'       |       | \              |
|            /                  '''''''   \             |
 \          /                              \           /
  \________/                                \_________/
     """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.controller = Xbox360Reader()

        self.__run()

    def __run(self):
        while True:
            try:
                state = self.controller.state

                ascii = copy(self.ascii_base)
                ascii = self.__buttons(ascii, state)
                # ascii = self.__joysticks(ascii, state)

                os.system("clear")
                print(ascii)

            except Exception as e:
                logger.exception(f"Er is een onverwachte fout opgetreden: {e}")
            self.sleep()
        pyout()

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

        # Tested and works. Mapping in pygame seems to be incorrect
        r_stick = (
            pretty_string("VVVVVVV", color="CYAN")
            if state.button_right_stick
            else "       "
        )
        ascii = ascii.replace("l_stick", r_stick)

        return ascii

    def __joysticks(self, ascii: str, state: Xbox360POD) -> str:
        lx = min(int((state.axis_left_stick_x + 1) / 2 * 8), 7)

        print(lx)


if __name__ == "__main__":
    node = Xbox360Plotter()
