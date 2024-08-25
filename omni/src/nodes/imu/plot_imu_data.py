import numpy as np

from dds_utils.dds_subscriber import DDSSubscriber
from imu.imu_publisher import IMUSample
import cv2


def quat_to_rot_matrix(quat):
    """Convert a normalized quaternion into a rotation matrix."""
    w, x, y, z = quat / np.linalg.norm(quat)  # Normalize the quaternion
    return np.array(
        [
            [1 - 2 * y * y - 2 * z * z, 2 * x * y - 2 * z * w, 2 * x * z + 2 * y * w],
            [2 * x * y + 2 * z * w, 1 - 2 * x * x - 2 * z * z, 2 * y * z - 2 * x * w],
            [2 * x * z - 2 * y * w, 2 * y * z + 2 * x * w, 1 - 2 * x * x - 2 * y * y],
        ]
    )


def transform_axes(quat):
    """Transforms the standard axes by the rotation matrix derived from quat."""
    rot_matrix = quat_to_rot_matrix(quat)
    axes = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    transformed_axes = rot_matrix @ axes.T  # Matrix multiplication
    return transformed_axes.T  # Transpose back to original shape


def draw_axes(img, origin, axes, accel, scale=100):
    """Draws 3D axes on the image from the given origin."""
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]  # BGR colors for x, y, z axes
    for i, (color, axis) in enumerate(zip(colors, axes)):
        axis_length = scale + 50 * (accel[i] > 0.75) - 50 * (accel[i] < -0.75)
        end_point = origin + (axis_length * axis[:2]).astype(int)
        cv2.line(
            img,
            tuple(origin.astype(int)),
            tuple(end_point.astype(int)),
            color,
            5,
        )
    return img


imu = DDSSubscriber("imu", IMUSample)

# Continuously display the result
while True:
    imu_sample = imu()
    imu_quat = np.array(
        [imu_sample.quat_w, imu_sample.quat_x, imu_sample.quat_y, imu_sample.quat_z]
    )
    transformed_axes = transform_axes(imu_quat)

    # Reinitialize the image to black (to clear old axes)
    image = np.zeros((500, 500, 3), dtype=np.uint8)
    origin = np.array([250, 250])  # Center of the image

    accel = (imu_sample.accel_x, imu_sample.accel_y, imu_sample.accel_z)

    image = draw_axes(image, origin, transformed_axes, accel)

    image = image.transpose(1, 0, 2)

    cv2.imshow("3D Axes", image)
    if cv2.waitKey(10) == ord("q"):
        break

cv2.destroyAllWindows()
