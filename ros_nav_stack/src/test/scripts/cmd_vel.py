#!/usr/bin/env python3
import rospy
import rospkg
from std_msgs.msg import String
# from geometry_msgs import msg


def talker():
    pup = rospy.Publisher('cmd_vel', String, queue_size=10)
    rospy.init_node('cmd_vel', anonymous=True)
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        hello_str = "hello world %s" % rospy.get_time()
        rospy.loginfo(hello_str)
        pup.publish(hello_str)
        rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass