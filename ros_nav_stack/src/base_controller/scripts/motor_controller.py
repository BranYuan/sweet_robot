#!/usr/bin/python
import rospy
import rospkg
from std_msgs.msg import String


def callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)


def listener():
    rospy.init_node('motor_controller', anonymous=True)
    rospy.Subscriber('cmd_vel', String, callback)
    rospy.spin()


if __name__ == '__main__':
    while True:
        try:
            listener()
        except:
            pass
