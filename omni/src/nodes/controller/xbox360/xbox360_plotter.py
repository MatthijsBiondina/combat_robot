import os

from src.cyclone.cycloneddsnode import CycloneDDSNode
from src.nodes.controller.xbox360.xbox360_reader import Xbox360Reader
from src.utils.logger import get_logger
from src.utils.tools import pyout

logger = get_logger()


class Xbox360Plotter(CycloneDDSNode):
    ascii = """
      _=====_                               _=====_
     / _____ \                             / _____ \\
   +.-'_____'-.---------------------------.-'_____'-.+
  /   |     |  '.                       .'  |     |   \\
 / ___| /|\ |___ \                     / ___|     |___ \\
/ |      |      | ;  __           __  ; |             | ;
| | <---   ---> | | |__|         |__| | |             | |
| |___   |   ___| ;                   ; |___       ___| ;
|\    | \|/ |    /  _     ___   _______\    |     |    /|
| \   |_____|  .','" "', |___| |       |'.  |_____|  .' |
|  '-.______.-' /   ^   \      |       |  '-._____.-'   |
|               | <   > |------|       |                |
|              /\   v   /      |       |\               |
|             /  '.___.'       |_______| \              |
|            /                            \             |
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

                os.system("clear")
                print(self.ascii)

            except Exception as e:
                logger.exception(f"Er is een onverwachte fout opgetreden: {e}")
            self.sleep()
        pyout()


if __name__ == "__main__":
    node = Xbox360Plotter()
