from lib.log_setup import logger

# GPIO mode constants
BCM = 11
BOARD = 10
OUT = 0
IN = 1
HIGH = 1
LOW = 0
PUD_UP = 22
PUD_DOWN = 21
RISING = 31
FALLING = 32
BOTH = 33

# Dictionary to store current pin states
_pin_states = {}

# Dictionary to store event callbacks
_event_callbacks = {}


def setmode(mode):
    """Set the pin numbering mode."""
    logger.info(f"GPIO Emulator: Set mode to {mode}")
    return


def setup(channel, direction, pull_up_down=PUD_UP, initial=None):
    """Set up a GPIO channel."""
    if isinstance(channel, list):
        for ch in channel:
            _pin_states[ch] = LOW if initial is None else initial
            logger.info(f"GPIO Emulator: Set up channel {ch} as {'input' if direction == IN else 'output'}")
    else:
        _pin_states[channel] = LOW if initial is None else initial
        logger.info(f"GPIO Emulator: Set up channel {channel} as {'input' if direction == IN else 'output'}")
    return


def output(channel, state):
    """Set the output state of a GPIO channel."""
    if isinstance(channel, list):
        for ch, st in zip(channel, state if isinstance(state, list) else [state] * len(channel)):
            _pin_states[ch] = st
            logger.info(f"GPIO Emulator: Set channel {ch} to {st}")
    else:
        _pin_states[channel] = state
        logger.info(f"GPIO Emulator: Set channel {channel} to {state}")
    return


def input(channel):
    """Read the current value of a GPIO channel."""
    state = _pin_states.get(channel, LOW)
    logger.info(f"GPIO Emulator: Read channel {channel} as {state}")
    return state


def add_event_detect(channel, edge, callback=None, bouncetime=None):
    """Add event detection to a GPIO channel."""
    _event_callbacks[channel] = callback
    logger.info(f"GPIO Emulator: Added event detection to channel {channel}")
    return


def add_event_callback(channel, callback):
    """Add a callback for an event already defined using add_event_detect()."""
    _event_callbacks[channel] = callback
    logger.info(f"GPIO Emulator: Added event callback to channel {channel}")
    return


def remove_event_detect(channel):
    """Remove event detection from a GPIO channel."""
    if channel in _event_callbacks:
        del _event_callbacks[channel]
    logger.info(f"GPIO Emulator: Removed event detection from channel {channel}")
    return


def cleanup(channel=None):
    """Clean up GPIO channels."""
    global _pin_states, _event_callbacks
    
    if channel is None:
        _pin_states = {}
        _event_callbacks = {}
        logger.info("GPIO Emulator: Cleaned up all channels")
    else:
        if isinstance(channel, list):
            for ch in channel:
                if ch in _pin_states:
                    del _pin_states[ch]
                if ch in _event_callbacks:
                    del _event_callbacks[ch]
            logger.info(f"GPIO Emulator: Cleaned up channels {channel}")
        else:
            if channel in _pin_states:
                del _pin_states[channel]
            if channel in _event_callbacks:
                del _event_callbacks[channel]
            logger.info(f"GPIO Emulator: Cleaned up channel {channel}")
    return


def setwarnings(state):
    """Enable or disable GPIO warnings."""
    logger.info(f"GPIO Emulator: Set warnings to {state}")
    return


def trigger_event(channel):
    """
    Simulate a GPIO event (for testing purposes).
    This function is not part of the actual RPi.GPIO API.
    """
    if channel in _event_callbacks and callable(_event_callbacks[channel]):
        callback = _event_callbacks[channel]
        callback(channel)
        logger.info(f"GPIO Emulator: Triggered event on channel {channel}")
    return 