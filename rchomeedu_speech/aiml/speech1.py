#!/usr/bin/env python

"""
    talkback.py - Version 1.1 2013-12-20

    Use the sound_play client to say back what is heard by the pocketsphinx recognizer.

"""

import rospy, os, sys
import aiml
from std_msgs.msg import String
from sound_play.libsoundplay import SoundClient

kernel = aiml.Kernel()
kernel.learn("/home/zhaixiaolin/catkin_ws/src/rc-home-edu-learn-ros-master/rchomeedu_speech/aiml/std-startup.xml")
kernel.respond("load aiml b")



class TalkBack:
    def __init__(self, script_path):
        rospy.init_node('talkback')

        rospy.on_shutdown(self.cleanup)

        # Create the sound client object
        self.soundhandle = SoundClient()

        # Wait a moment to let the client connect to the
        # sound_play server
        rospy.sleep(1)

        # Make sure any lingering sound_play processes are stopped.
        self.soundhandle.stopAll()

        # Announce that we are ready for input
        # self.soundhandle.playWave('say-beep.wav')
        # rospy.sleep(2)
        # self.soundhandle.say('Ready')

        #rospy.loginfo("Say one of the navigation commands...")

        # Subscribe to the recognizer output and set the callback function
        rospy.Subscriber('/lm_data', String, self.talkback)  # gai lm_data

    def talkback(self, msg):

        # Print the recognized words on the screen
        rospy.loginfo(msg.data)

        # Speak the recognized words in the selected voice
        # self.soundhandle.say("I heard " + msg.data, volume=0.01)
        # rospy.sleep(5)
        if kernel.respond(msg.data)!=None:
	        print(kernel.respond(msg.data))
	        self.soundhandle.say(kernel.respond(msg.data), volume=1.0)

        # if msg.data.find('WHAT IS YOUR NAME') > -1:
        #     self.soundhandle.say("My name is Jack ", volume=0.5)
        #     rospy.sleep(5)
        # elif msg.data.find('HOW OLD ARE YOU')>-1:
        #     self.soundhandle.say("I am 18 years old ", volume=0.5)
        #     rospy.sleep(5)
        # elif msg.data.find('WHERE ARE YOU FROM')>-1:
        #     self.soundhandle.say("I am from NANKAI University,Tainjin,China. ", volume=0.5)
        #     rospy.sleep(5)



    def cleanup(self):
        self.soundhandle.stopAll()
        rospy.loginfo("Shutting down talkback node...")


if __name__ == "__main__":
    
    try:
        TalkBack(sys.path[0])
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("Talkback node terminated.")
