import time

from src.cyclone.writer import Writer
from src.idl.base_types.float_pod import FloatPOD

writer0 = Writer("ESC0_pulsewidth", FloatPOD)
writer1 = Writer("ESC1_pulsewidth", FloatPOD)
writer2 = Writer("ESC2_pulsewidth", FloatPOD)

t0 = time.time()
while time.time() < t0 + 2:
    writer0.publish(FloatPOD(timestamp=time.time(), float_=1400))
    # writer1.publish(FloatPOD(timestamp=time.time(), float_=1400))
    # writer2.publish(FloatPOD(timestamp=time.time(), float_=1400))
    writer0.sleep()
