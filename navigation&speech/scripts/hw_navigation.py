#!/usr/bin/env python

"""

    RoboCup@Home Education | oc@robocupathomeedu.org
    navi.py - enable turtlebot to navigate to predefined waypoint location

"""

import rospy

import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, PoseWithCovarianceStamped, Point, Quaternion, Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from std_msgs.msg import Int32
from tf.transformations import quaternion_from_euler

original = 0
start = 1


class NavToPoint:
    def __init__(self):
        #rospy.on_shutdown(self.cleanup)

        # Subscribe to the move_base action server
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)

        rospy.loginfo("Waiting for move_base action server...")

        # Wait for the action server to become available
        self.move_base.wait_for_server(rospy.Duration(120))
        rospy.loginfo("Connected to move base server")

        # A variable to hold the initial pose of the robot to be set by the user in RViz
        initial_pose = PoseWithCovarianceStamped()
        rospy.Subscriber('initialpose', PoseWithCovarianceStamped, self.update_initial_pose)
        rospy.Subscriber('/navigation',Int32,self.navCallback)

        # Get the initial pose from the user
        rospy.loginfo("*** Click the 2D Pose Estimate button in RViz to set the robot's initial pose...")
        rospy.wait_for_message('initialpose', PoseWithCovarianceStamped)

        # Make sure we have the initial pose
        while initial_pose.header.stamp == "":
            rospy.sleep(1)

        rospy.loginfo("Ready to go")
        rospy.sleep(1)

        self.locations = dict()

        # Location bar
        A_x = -2.62
        A_y = -1.16
        A_theta = -0.00143

        quaternion = quaternion_from_euler(0.0, 0.0, A_theta)
        self.locations['A'] = Pose(Point(A_x, A_y, 0.000),
                              Quaternion(quaternion[0], quaternion[1], quaternion[2], quaternion[3]))

        #Location sofa
        B_x = 1.24
        B_y = -2.45
        B_theta = -0.00143

        quaternion = quaternion_from_euler(0.0, 0.0, B_theta)
        self.locations['B'] = Pose(Point(B_x, B_y, 0.000),
                                   Quaternion(quaternion[0], quaternion[1], quaternion[2], quaternion[3]))

        #Location tabel
        C_x = 0.96
        C_y = -0.159
        C_theta = -0.00143

        quaternion = quaternion_from_euler(0.0, 0.0, C_theta)
        self.locations['C'] = Pose(Point(C_x, C_y, 0.000),
                                   Quaternion(quaternion[0], quaternion[1], quaternion[2], quaternion[3]))

        # self.goal = MoveBaseGoal()
        # rospy.loginfo("Starting navigation test")


        # self.goal.target_pose.header.frame_id = 'map'
        # self.goal.target_pose.header.stamp = rospy.Time.now()

            #Robot will go to point A
            # if start == 1:
            #     rospy.loginfo("Going to point A")
            #     rospy.sleep(2)
            #     self.goal.target_pose.pose = self.locations['A']
            #     self.move_base.send_goal(self.goal)
            #     waiting = self.move_base.wait_for_result(rospy.Duration(300))
            #     if waiting == 1:
            #         rospy.loginfo("Reached point A")
            #         rospy.sleep(2)
            #         rospy.loginfo("Ready to go back")
            #         rospy.sleep(2)
            #         global start
            #         start = 0
            #
            # # After reached point A, robot will go back to initial position
            # elif start == 0:
            #     rospy.loginfo("Going back home")
            #     rospy.sleep(2)
            #     self.goal.target_pose.pose = self.origin
            #     self.move_base.send_goal(self.goal)
            #     waiting = self.move_base.wait_for_result(rospy.Duration(300))
            #     if waiting == 1:
            #         rospy.loginfo("Reached home")
            #         rospy.sleep(2)
            #         global start
            #         start = 2
            #
            # rospy.Rate(5).sleep()

    def navCallback(self,data):

        if original==1:
            rospy.loginfo(data.data)
            self.goal = MoveBaseGoal()
            self.goal.target_pose.header.frame_id = 'map'
            self.goal.target_pose.header.stamp = rospy.Time.now()
            if data.data == 1:
                rospy.loginfo("Going to the bar")
                rospy.sleep(2)
                self.goal.target_pose.pose = self.locations['A']
                self.move_base.send_goal(self.goal)
                waiting = self.move_base.wait_for_result(rospy.Duration(300))
                if waiting == 1:
                    rospy.loginfo("Reached the bar")
                    rospy.sleep(2)

            if data.data == 2:
                rospy.loginfo("Going to the sofa")
                rospy.sleep(2)
                self.goal.target_pose.pose = self.locations['B']
                self.move_base.send_goal(self.goal)
                waiting = self.move_base.wait_for_result(rospy.Duration(300))
                if waiting == 1:
                    rospy.loginfo("Reached the sofa")
                    rospy.sleep(2)

            if data.data== 3:
                rospy.loginfo("Going to the tabel")
                rospy.sleep(2)
                self.goal.target_pose.pose = self.locations['C']
                self.move_base.send_goal(self.goal)
                waiting = self.move_base.wait_for_result(rospy.Duration(300))
                if waiting == 1:
                    rospy.loginfo("Reached the tabel")
                    rospy.sleep(2)

            if data.data==4:
                rospy.loginfo("Going back home")
                rospy.sleep(2)
                self.goal.target_pose.pose = self.origin
                self.move_base.send_goal(self.goal)
                waiting = self.move_base.wait_for_result(rospy.Duration(300))
                if waiting == 1:
                    rospy.loginfo("Reached home")
                    rospy.sleep(2)






    def update_initial_pose(self, initial_pose):
        self.initial_pose = initial_pose
        if original == 0:
            self.origin = self.initial_pose.pose.pose
            global original
            original = 1

    def cleanup(self):
        rospy.loginfo("Shutting down navigation	....")
        self.move_base.cancel_goal()


if __name__ == "__main__":
    rospy.init_node('navi_point')
    try:
        NavToPoint()
        rospy.spin()
    except:
        pass

