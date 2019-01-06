#!/usr/bin/python
import rospy
import rospkg
from std_msgs.msg import String
# from geometry_msgs import msg


def cmd_vel():
    pup = rospy.Publisher('cmd_vel', String, queue_size=10)
    rospy.init_node('vel_generate', anonymous=True)
    rate = rospy.Rate(2)
    while not rospy.is_shutdown():
        hello_str = "hello world %s" % rospy.get_time()
        rospy.loginfo(hello_str)
        pup.publish(hello_str)
        rate.sleep()


if __name__ == '__main__':
    try:
        cmd_vel()
    except rospy.ROSInterruptException:
        pass