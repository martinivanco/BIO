#!/usr/bin/python2

import Leap, sys, thread, time, threading, signal

HOLD_ERR_TRESH = 10
VERIFY_ERR_TRESH = 30

class VeriGesture():
    def __init__(self, hand):
        self.fingers = [None] * 5
        self.tips = [None] * 5
        self.distances = []

        for f in hand.fingers:
            self.fingers[f.type] = f
            self.tips[f.type] = f.bone(Leap.Bone.TYPE_DISTAL).next_joint
        for f in self.fingers:
            if f is None:
                print "Well, I did not expect that."
        
        for i in range(4):
            for j in range(4 - i):
                self.distances.append(self.tips[i].distance_to(self.tips[i + 1 + j]))
    
    def compare(self, gesture, treshold):
        for i in range(10):
            if abs(self.distances[i] - gesture.distances[i]) > treshold:
                return False
        return True

class VeriPassword():
    def __init__(self, gestures):
        self.gestures = gestures if gestures is not None else []
        self.index = 0
        self.mode = 0 if gestures is None else 2
        self.temp_gestures = [None] * 61
        self.temp_index = 0
        self.verified = threading.Event()

    def frame(self, hand):
        if self.verified.is_set():
            return

        if self.mode == 0:
            self.gesture_set(hand)
        if self.mode == 1:
            pass
        if self.mode == 2:
            self.gesture_verify(hand)

    def gesture_reset(self):
        self.temp_gestures[0] = self.temp_gestures[self.temp_index]
        self.temp_index = 1

    def gesture_hold(self, frame_count, hand):
        self.temp_gestures[self.temp_index] = VeriGesture(hand)
        if self.temp_index == 0:
            self.temp_index += 1
            return False

        if not self.temp_gestures[self.temp_index].compare(self.temp_gestures[self.temp_index - 1], HOLD_ERR_TRESH):
            self.gesture_reset()
            return False
        if self.temp_index % 10 != 0:
            self.temp_index += 1
            return False
        
        if not self.temp_gestures[self.temp_index].compare(self.temp_gestures[self.temp_index - 10], HOLD_ERR_TRESH):
            self.gesture_reset()
            return False
        if self.temp_index != frame_count:
            self.temp_index += 1
            return False

        if not self.temp_gestures[self.temp_index].compare(self.temp_gestures[self.temp_index - frame_count], HOLD_ERR_TRESH):
            self.gesture_reset()
            return False
        return True

    def gesture_set(self, hand):
        if not self.gesture_hold(60, hand):
            return

        self.gestures.append(self.temp_gestures[55])
        self.temp_index = 0
        print "*",
        sys.stdout.flush()

    def gesture_verify(self, hand):
        if not self.gesture_hold(40, hand):
            return
        self.temp_index = 0

        if self.gestures[self.index].compare(self.temp_gestures[25], VERIFY_ERR_TRESH):
            self.index += 1
            print "*",
            sys.stdout.flush()
        else:
            self.index = 0
            print "\r                                \r",
            sys.stdout.flush()
            return
        
        if self.index >= len(self.gestures):
            self.verified.set()
            self.index = 0

    def save(self):
        if len(self.gestures) == 0:
            print "Error: Empty password."
            return False
        print "Password successfully set."
        self.mode = 2
        return True

class VeriListener(Leap.Listener):
    def __init__(self):
        super(VeriListener, self).__init__()
        self.callback = None
        self.callback_lock = threading.Lock()
        self.err_msg = False

    def set_callback(self, callback):
        self.callback_lock.acquire()
        self.callback = callback
        self.callback_lock.release()

    def on_frame(self, controller):
        # Get recent frame and check there is a valid gesture
        frame = controller.frame()
        if not self.single_hand(frame):
            return
        if self.no_gesture(frame):
            return

        # If there is one, pass it to the callback object
        if self.callback is not None:
            self.callback.frame(frame.hands[0])

    def single_hand(self, frame):
        if (len(frame.hands) > 1):
            if not self.err_msg:
                print "\rPlease only use one hand.",
                sys.stdout.flush()
                self.err_msg = True
            return False

        if self.err_msg == True:
            print "\r                         \r",
            sys.stdout.flush()
            self.err_msg = False

        if (len(frame.hands) < 1):
            return False

        return True

    def no_gesture(self, frame):
        for f in frame.hands[0].fingers:
            angle_sum = 0
            for i in range(3):
                angle_sum += f.bone(i).direction.angle_to(f.bone(i+1).direction)

            if f.type == Leap.Finger.TYPE_THUMB and angle_sum > 1.0:
                return False
            if angle_sum > 2.0:
                return False
            
        return True


def set_password(password):
    try:
        input("Gesture your password and type Enter.\n")
    except KeyboardInterrupt:
        print "\nRemoving listener. Bye."
        return False
    except SyntaxError:
        return password.save()
    return False

def check_password(password):
    print "Please input your password."
    try:
        while not password.verified.wait(1000):
            pass
    except:
        print "\nRemoving listener. Bye."
        return False
    return True

def main():
    # Create a gesture listener and a leap controller
    listener = VeriListener()
    controller = Leap.Controller()
    controller.add_listener(listener)

    # Create password verifier and assign it to listener
    password = VeriPassword(None)
    listener.set_callback(password)

    # Set password
    if not set_password(password):
        controller.remove_listener(listener)
        return

    # Check password
    if check_password(password):
        print "\nSuccessfully verified"
    
    # Remove the listener when we're done
    controller.remove_listener(listener)

if __name__ == "__main__":
    main()