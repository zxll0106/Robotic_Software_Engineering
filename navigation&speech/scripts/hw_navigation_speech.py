#!/usr/bin/env python

"""
    talkback.py - Version 1.1 2013-12-20

    Use the sound_play client to say back what is heard by the pocketsphinx recognizer.

"""

import rospy, os, sys
from std_msgs.msg import String
from std_msgs.msg import Int32
from sound_play.libsoundplay import SoundClient


class TalkBack:
    def __init__(self):
        rospy.init_node('talkback')

        rospy.on_shutdown(self.cleanup)

        # Create the sound client object


        # Wait a moment to let the client connect to the
        # sound_play server
        rospy.sleep(1)

        # Make sure any lingering sound_play processes are stopped.
        print(0)

        rospy.loginfo("Say one of the navigation commands...")

        # Subscribe to the recognizer output and set the callback function
        rospy.Subscriber('/lm_data', String, self.talkback)  # gai lm_data
        self.pub = rospy.Publisher('/navigation', Int32, queue_size=10)

    def talkback(self, msg):
        # Print the recognized words on the screen
        rospy.loginfo(msg.data)
        if msg.data=='GO TO THE BAR':
            self.pub.publish(1)
        if msg.data=='GO TO THE SOFA':
            self.pub.publish(2)
        if msg.data=='GO TO THE TABLE':
            self.pub.publish(3)
        if msg.data=='GO BACK HOME':
            self.pub.publish(4)

    def cleanup(self):
        self.soundhandle.stopAll()
        rospy.loginfo("Shutting down talkback node...")


if __name__ == "__main__":
    try:
        TalkBack()
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("Talkback node terminated.")