import logging

from src.nodes.ESCs.bbb_beetleweight_single_brushed_esc_v3 import ESC

logger = logging.getLogger(__name__)


class BBBBeetleweightSingleBrushedESCv3(ESC):
    def __init__(self):
        super().__init__()

        logger.log(logging.DEBUG, "Hello World")


if __name__ == "__main__":
    node = BBBBeetleweightSingleBrushedESCv3()
