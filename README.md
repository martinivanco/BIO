# Leap Motion for Verification
Project made as a part of the course Biometric Systems at Brno University of Technology. The task was to create an application that would use [Leap Motion](https://developer.leapmotion.com/) device and its framework as a verification tool. The application is just a *proof of concept*. The user sets a password using a sequence of gestures, repeats it to check it has been set correctly and then is asked to authenticate (again using the same gesture sequence). The application **does not** save the password anywhere.

## How to use
1. Clone this repo using `git clone https://github.com/photohunter9/BIO.git`
2. Run the app using `python2 LeapVerify.py`
3. ???
4. Profit!

## Dependencies
Python 2.7
LeapMotion - I have used SDK version 2 since it supports all major operating systems and many different languages including Python. Sadly, only Python 2 is supported. The SDK can be downloaded directly from Leap Motion website for your platform. If you use macOS, you just need to install the main Leap Motion controller app, the libraries are included in the code. If you use some other system, check out the documentation or create an issue, I might be able to help you. Obviously, you also need the Leap Motion device itself.