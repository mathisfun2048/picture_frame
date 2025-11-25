# src/button_handler.py

import RPi.GPIO as GPIO
import time
import logging

logger = logging.getLogger(__name__)


class ButtonHandler:
    """
    Handles button input for the picture frame
    """
    
    def __init__(self, button_pin=18, pull_up=True, debounce_ms=300):
        """
        Initialize button handler
        
        Args:
            button_pin: GPIO pin number (BCM numbering)
            pull_up: True if button connects to GND, False if connects to 3.3V
            debounce_ms: Debounce time in milliseconds
        """
        self.button_pin = button_pin
        self.pull_up = pull_up
        self.debounce_ms = debounce_ms
        self.callback = None
        self.last_press_time = 0
        self.initialized = False
        
        logger.info(f"ButtonHandler created: pin={button_pin}, pull_up={pull_up}")
    
    def setup(self, callback):
        """
        Set up GPIO and register callback
        
        Args:
            callback: Function to call when button is pressed
        """
        try:
            # Disable warnings about channels already in use
            GPIO.setwarnings(False)
            
            # Set up GPIO mode
            GPIO.setmode(GPIO.BCM)
            
            # Clean up any previous configuration on this pin
            try:
                GPIO.cleanup(self.button_pin)
            except:
                pass  # Ignore if nothing to clean up
            
            # Configure pull resistor
            pull_mode = GPIO.PUD_UP if self.pull_up else GPIO.PUD_DOWN
            GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=pull_mode)
            
            # Register callback with edge detection
            # If pull_up=True, button press pulls LOW (falling edge)
            # If pull_up=False, button press pulls HIGH (rising edge)
            edge = GPIO.FALLING if self.pull_up else GPIO.RISING
            
            self.callback = callback
            GPIO.add_event_detect(
                self.button_pin,
                edge,
                callback=self._button_callback,
                bouncetime=self.debounce_ms
            )
            
            self.initialized = True
            logger.info("Button handler initialized and ready")
            
        except Exception as e:
            logger.error(f"Failed to setup button: {e}")
            raise
    
    def _button_callback(self, channel):
        """
        Internal callback for GPIO event
        Handles debouncing and calls user callback
        """
        current_time = time.time()

        # Additional software debouncing
        if current_time - self.last_press_time < (self.debounce_ms / 1000.0):
            logger.debug("Button press ignored (debounce)")
            return

        self.last_press_time = current_time
        logger.info("Button pressed!")

        # Call user callback directly - it should be lightweight
        if self.callback:
            self.callback()
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.initialized:
            try:
                GPIO.remove_event_detect(self.button_pin)
                GPIO.cleanup(self.button_pin)
                self.initialized = False
                logger.info("Button handler cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up button: {e}")