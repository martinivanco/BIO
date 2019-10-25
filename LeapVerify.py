#!/usr/bin/python2

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

GESTURE_NONE = 0
GESTURE_PINCH1 = 1
GESTURE_PINCH2 = 2
GESTURE_PINCH3 = 3
GESTURE_PINCH4 = 4
GESTURE_ERROR = 5
ERROR_THRESHOLD = 20

PASSWORD = [GESTURE_PINCH1, GESTURE_PINCH3, GESTURE_PINCH2, GESTURE_PINCH4]

class VeriListener(Leap.Listener):
    def __init__(self):
        super(VeriListener, self).__init__()
        self.gesture_err = False
        self.password_index = 0

    def on_frame(self, controller):
        # Find the gesture
        frame = controller.frame()
        gesture = self.find_gesture(frame)

        # Print or remove error message
        if gesture == GESTURE_ERROR:
            if not self.gesture_err:
                print 'Please only use one hand.\r',
                sys.stdout.flush()
                self.gesture_err = True
            return
        if self.gesture_err:
            print '                         \r',
            sys.stdout.flush()
            self.gesture_err = False
        
        # No new gesture detected
        if gesture == PASSWORD[self.password_index - 1] or gesture == GESTURE_NONE:
            return
        
        # Check gesture
        if gesture == PASSWORD[self.password_index]:
            self.password_index += 1
            print '*',
            sys.stdout.flush()
            if self.password_index == 4:
                print '\nAuthenticated'
                self.password_index = 0
        else:
            self.password_index = 0
            print '\r    \r',
            sys.stdout.flush()

    def find_gesture(self, frame):
        # Check if exactly one hand is present
        if (len(frame.hands) > 1):
            return GESTURE_ERROR
        if (len(frame.hands) < 1):
            return GESTURE_NONE
        
        # Save the errors of the gestures
        errors = []
        errors.append(self.pinch(frame.hands[0], Leap.Finger.TYPE_INDEX))
        errors.append(self.pinch(frame.hands[0], Leap.Finger.TYPE_MIDDLE))
        errors.append(self.pinch(frame.hands[0], Leap.Finger.TYPE_RING))
        errors.append(self.pinch(frame.hands[0], Leap.Finger.TYPE_PINKY))

        min_error_index = 0
        for i in range(len(errors)):
            if errors[i] < errors[min_error_index]:
                min_error_index = i
        
        if errors[min_error_index] < ERROR_THRESHOLD:
            return min_error_index + 1
        else:
            return GESTURE_NONE
    
    def pinch(self, hand, other_finger):
        thumb = None
        other = None
        for f in hand.fingers:
            if f.type == Leap.Finger.TYPE_THUMB:
                thumb = f.bone(Leap.Bone.TYPE_DISTAL).next_joint
            if f.type == other_finger:
                other = f.bone(Leap.Bone.TYPE_DISTAL).next_joint
        
        if thumb is not None and other is not None:
            return thumb.distance_to(other)
        return 1000

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