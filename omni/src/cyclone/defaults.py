from cyclonedds.qos import Qos, Policy
from cyclonedds.util import duration

QOS = Qos(
    Policy.Reliability.BestEffort,
    Policy.Deadline(duration(milliseconds=10)),
    Policy.History.KeepLast(1),
    Policy.ResourceLimits(max_samples=1, max_instances=1, max_samples_per_instance=1),
)
