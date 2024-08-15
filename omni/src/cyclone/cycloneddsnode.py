import time


class CycloneDDSNode:
    """
    A class to manage rate-controlled loops, similar to ROS's Rate, for CycloneDDS applications.
    """

    def __init__(self, rate_hz: int = 50):
        """
        Initializes the CycloneDDSNode with a specified loop rate.

        Args:
            rate_hz (int): The desired loop rate in Hertz.
        """
        self.__period = 1.0 / rate_hz  # Time period for each loop iteration in seconds.
        self.__last_sleep = time.time()  # Timestamp of the last sleep call.

    def sleep(self):
        """
        Sleeps for the necessary duration to maintain the loop rate.

        This method calculates the time elapsed since the last sleep, determines the remaining
        time to maintain the desired loop period, and sleeps for that duration. It then updates
        the timestamp for the next iteration.

        If the processing time exceeds the desired period, it doesn't sleep, ensuring that the loop
        doesn't run slower than intended.
        """
        elapsed_time = (
            time.time() - self.__last_sleep
        )  # Time taken since the last sleep.
        sleep_time = max(0.0, self.__period - elapsed_time)  # Remaining time to sleep.
        time.sleep(sleep_time)  # Sleep for the calculated duration.
        self.__last_sleep = time.time()  # Update the timestamp for the next iteration.
