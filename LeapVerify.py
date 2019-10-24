#!/usr/bin/python2

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class VeriListener(Leap.Listener):
    def __init__(self):
        super(VeriListener, self).__init__()

    def on_frame(self, controller):
        # Find the gesture
        frame = controller.frame()

    def find_gesture(self, parameter_list):
        pass

def main():
    # Create a gesture verification listener and a leap controller
    listener = VeriListener()
    controller = Leap.Controller()

    # Add the listener to controllers listener list
    controller.add_listener(listener)

    # Make sure the user can cancel
    print "Press Enter to quit..."
    try:
        raw_input()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the listener when we're done
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()