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
    def __init__(self, script_path):
        rospy.init_node('talkback')

        rospy.on_shutdown(self.cleanup)

        # Create the sound client object
        self.soundhandle = SoundClient()
        self.name=''
        self.age=''
        self.sex=''
        self.place=0
        self.flag1=False
        self.flag2=False
        self.flag3=True

        # Wait a moment to let the client connect to the
        # sound_play server
        rospy.sleep(1)
        # Make sure any lingering sound_play processes are stopped.
        self.soundhandle.stopAll()

        rospy.loginfo("Say one of the navigation commands...")

        # Subscribe to the recognizer output and set the callback function
        rospy.Subscriber('/farewell_speech',Int32,self.faceCallback)
        rospy.Subscriber('/farewell_age', String, self.ageCallback)
        rospy.Subscriber('/farewell_sex', String, self.sexCallback)
        rospy.Subscriber('/farewell_feature', Int32, self.featureCallback)
        rospy.Subscriber('/farewell_reset', Int32, self.resetCallback)
        rospy.Subscriber('/lm_data', String, self.lmCallback)  # gai lm_data
        self.pub = rospy.Publisher('/farewell_nav', Int32, queue_size=10)

    def faceCallback(self,msg):
        #rospy.loginfo(msg.data)
        if msg.data==1:
            if self.flag3==True:
                self.soundhandle.say("Hello,what is your name" , volume=1.0)
                self.flag1=True
                self.flag3=False

    def ageCallback(self,msg):
        rospy.loginfo(msg.data)
        self.age=msg.data

    def sexCallback(self,msg):
        rospy.loginfo(msg.data)
        if msg.data=='male':
            self.sex = 'man'
        if msg.data=='female':
            self.sex='woman'

    def featureCallback(self,msg):
        rospy.loginfo(msg.data)
        if msg.data==1:
            self.soundhandle.say("We arrived" , volume=1.0)
        if msg.data==2:

            self.soundhandle.say("%s is a %s of %s"%(self.name,self.sex,self.age), volume=1.0)

    def resetCallback(self,msg):
        if msg.data==1:
            self.name = ''
            self.age = ''
            self.sex = ''
            self.place = 0
            self.flag1 = False
            self.flag2 = False
            self.flag3 = True

    def lmCallback(self, msg):
        # Print the recognized words on the screen
        rospy.loginfo(msg.data)

        # Speak the recognized words in the selected voice
        if self.flag1==True:
            self.name=msg.data
            print(self.name)
            self.soundhandle.say("where do you want to go", volume=1.0)
            rospy.sleep(5)
            self.flag1=False
            self.flag2=True

        if self.flag2==True:
            self.place=msg.data
            self.soundhandle.say("please,follow me", volume=1.0)
            rospy.sleep(5)
            if msg.data=='BAR':
                self.place=1
                self.pub.publish(1)
            if msg.data=='SOFA':
                self.place=2
                self.pub.publish(2)
            if msg.data=='TABLE':
                self.place=3
                self.pub.publish(3)
            self.flag2=False





    def cleanup(self):
        self.soundhandle.stopAll()
        rospy.loginfo("Shutting down talkback node...")


if __name__ == "__main__":
    try:
        TalkBack(sys.path[0])
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("Talkback node terminated.")