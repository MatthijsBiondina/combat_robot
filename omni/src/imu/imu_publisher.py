import board
import busio
import adafruit_bno055
import time

from dataclasses import dataclass, field
from cyclonedds.domain import DomainParticipant
from cyclonedds.pub import DataWriter
from cyclonedds.topic import Topic
from cyclonedds.core import Qos, Policy
from cyclonedds.idl import IdlStruct
from cyclonedds.util import duration

from utils.logger import Logger


# Dataclass for IMU data
@dataclass
class IMUSample(IdlStruct, typename="IMUSample.Msg"):
    """
    A dataclass that defines the structure for IMU data including quaternion components.

    Attributes:
        timestamp (float): The timestamp when the data is recorded.
        quat_w (float): Quaternion component W.
        quat_x (float): Quaternion component X.
        quat_y (float): Quaternion component Y.
        quat_z (float): Quaternion component Z.
        accel_x (float): Accelerometer data along the X-axis.
        accel_y (float): Accelerometer data along the Y-axis.
        accel_z (float): Accelerometer data along the Z-axis.
    """

    timestamp: float = field(metadata={"id": 0})
    quat_w: float = field(default=0.0, metadata={"id": 1})
    quat_x: float = field(default=0.0, metadata={"id": 2})
    quat_y: float = field(default=0.0, metadata={"id": 3})
    quat_z: float = field(default=0.0, metadata={"id": 4})
    accel_x: float = field(default=0.0, metadata={"id": 5})
    accel_y: float = field(default=0.0, metadata={"id": 6})
    accel_z: float = field(default=0.0, metadata={"id": 7})


class IMUPublisher:
    """
    A publisher class for IMU data that includes quaternion and accelerometer readings.
    """

    def __init__(self):
        """Initialize the publisher object, setting up DDS participant, topic, and writer."""
        self.participant = DomainParticipant()

        qos = Qos(
            Policy.Reliability.BestEffort,
            Policy.Durability.Volatile,
            Policy.Deadline(duration(milliseconds=10)),
            Policy.History.KeepLast(1),
            Policy.ResourceLimits(
                max_samples=1, max_instances=1, max_samples_per_instance=1
            ),
        )

        self.topic = Topic(self.participant, "imu", IMUSample, qos=qos)
        self.writer = DataWriter(self.participant, self.topic, qos=qos)
        
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bno055.BNO055_I2C(self.i2c_bus)

    def publish_data(self):
        """Continuously capture data from the IMU and publish it."""
        while True:
            quaternion = self.sensor.quaternion
            accel = self.sensor.linear_acceleration

            if quaternion is None or accel is None:
                continue  # Skip if the data is incomplete

            imu_data = IMUSample(
                timestamp=time.time(),
                quat_w=quaternion[0],
                quat_x=quaternion[1],
                quat_y=quaternion[2],
                quat_z=quaternion[3],
                accel_x=accel[0],
                accel_y=accel[1],
                accel_z=accel[2],
            )

            try:
                self.writer.write(imu_data)  # Publish the data
            except Exception as e:
                print(f"Failed to publish data: {e}", end="\r")


def main():
    """
    Main function to create a publisher and start data publishing.
    """
    logger = Logger()
    publisher = IMUPublisher()
    logger.log("IMU: ready!")
    publisher.publish_data()


if __name__ == "__main__":
    main()
