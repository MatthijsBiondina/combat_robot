from multiprocessing import Process
import imu.imu_publisher as imu


def run_imu_publisher():
    imu.main()


if __name__ == "__main__":
    p_imu = Process(target=run_imu_publisher, daemon=True)
    p_imu.start()

    p_imu.join()  # This will wait indefinitely for the process unless a timeout is specified.
