import time, atexit, ev3dev

def run_for(motor, power=75, ever=None, seconds=None, degrees=None):
    """ Run motor for specified amount of seconds, degrees, or forever

    Examples:
    run_for(motor, ever=True)
    run_for(motor, seconds=0.5)
    run_for(motor, degrees=270, power=100)

    Power is specified in percents in the range of [-100; 100]. In case the
    motor is in regulation mode, the power value is used to compute
    pulses_per_seconds value. The upper limits for pulses_per_second assumed to
    be 900 and 1200 for tacho and minitacho motors accordingly.
    """

    if motor.regulation_mode == ev3dev.motor.mode_on:
        if motor.type() == 'tacho':
            motor.pulses_per_second_setpoint = int(power * 9)
        elif motor.type() == 'minitacho':
            motor.pulses_per_second_setpoint = int(power * 12)
    else:
        motor.duty_cycle_setpoint = int(power)

    if ever is not None:
        motor.run_mode = ev3dev.motor.run_mode_forever
    elif seconds is not None:
        motor.run_mode = ev3dev.motor.run_mode_time
        motor.time_setpoint = int(seconds * 1000)
    elif degrees is not None:
        motor.run_mode = ev3dev.motor.run_mode_position
        motor.position_mode = ev3dev.motor.position_mode_relative
        motor.position = 0
        motor.position_setpoint = int(degrees)

    motor.run()

def run_until(motor, power=75, degrees=None, check=None, check_interval=0.01):
    """ Run motor until specified position or until check() evaluates to True.

    Examples:
    run_until(motor, degrees=270, power=40)
    run_until(motor, check=lambda: touch_sensor.value())

    Power is specified in percents in the range of [-100; 100]. In case the
    motor is in regulation mode, the power value is used to compute
    pulses_per_seconds value. The upper limits for pulses_per_second assumed to
    be 900 and 1200 for tacho and minitacho motors accordingly.
    """

    if motor.regulation_mode == ev3dev.motor.mode_on:
        if motor.type() == 'tacho':
            motor.pulses_per_second_setpoint = int(power * 9)
        elif motor.type() == 'minitacho':
            motor.pulses_per_second_setpoint = int(power * 12)
    else:
        motor.duty_cycle_setpoint = int(power)

    if degrees is not None:
        motor.run_mode = ev3dev.motor.run_mode_position
        motor.position_mode = ev3dev.motor.position_mode_absolute
        motor.position_setpoint = int(degrees)
    else:
        motor.run_mode = ev3dev.motor.run_mode_forever

    motor.run()

    while True:
        if degrees is not None:
            if not motor.running(): break
        elif check():
            motor.stop()
            break

        time.sleep(check_interval)

def drive_for(left, right, dir=0, power=75, ever=None, seconds=None):
    """ Run both motors for a specified amount of seconds, or forever. The
    dir parameter is in range [-100, 100] and specifies how fast the robot
    should turn.

    dir = -100: turn left as fast as possible,
    dir =    0: drive forward,
    dir =  100: turn right as fast as possible.

    The motor on the outer arc is driven at full power (specified as 'power'
    parameter), and the inner motor power is computed accordingly.
    """

    if (dir >= 0):
        master = left
        slave  = right
    else:
        master = right
        slave  = left

    mpower = power
    spower = power * (50 - abs(dir)) / 50

    run_for(master, mpower, ever, seconds)
    run_for(slave,  spower, ever, seconds)

#----------------------------------------------------------------------------
# Reset any motors attached at program exit
#----------------------------------------------------------------------------
def reset_motors():
    for port in [ev3dev.OUTPUT_A, ev3dev.OUTPUT_B, ev3dev.OUTPUT_C, ev3dev.OUTPUT_C]:
        m = ev3dev.motor(port)
        if m.connected(): m.reset()

atexit.register(reset_motors)
