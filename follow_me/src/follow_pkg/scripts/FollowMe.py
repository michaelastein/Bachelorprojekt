#!/usr/bin/python
# -*- coding:utf-8 -*-

import rospy
from sensor_msgs.msg import NavSatFix, Imu
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion

import numpy as np



class FollowMe:
	def __init__(self):
		rospy.init_node('FollowMe', anonymous=True)
		self.pub_twist = rospy.Publisher('FollowMe', Twist, queue_size=10)
		self.sub_roboter_gps = rospy.Subscriber('/navsat/fix', NavSatFix,
                                                self.set_actual_pos)
		self.sub_roboter_imu = rospy.Subscriber('/imu/data', Imu,
                                                self.set_actual_orientation)
        	# self.sub_handy_gps = rospy.Subscriber('smartphone_gps', NavSatFix,
        	#                                      self.set_target_pos)
        	self.rate = rospy.Rate(10)  # 10Hz
        	self.orientation = 0  # 0° entspricht norden
        	self.actual_pos = [0, 0]  # [latitude,longitude]
        	self.target_pos = [53.833995, 10.702391]  # [0, 0]  # [latitude,longitude]
        	self.SmartphoneLatitudes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        	self.SmartphoneLongitudes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


    	# the position of the robot
    	def set_actual_pos(self, data):
        	self.actual_pos[0] = data.latitude
        	self.actual_pos[1] = data.longitude
        
	
	# the orientation of the robot
	def set_actual_orientation(self, data):
		euler_angles = euler_from_quaternion((data.orientation.x,data.orientation.y,data.orientation.z,data.orientation.w))
		self.orientation = euler_angles[2]
		
 


	# calculates the distance between robot and smartphone in km
	def get_distance(self):
	    return (np.sqrt(((self.target_pos[0] - self.actual_pos[0]) * 111.3) ** 2
                    + ((self.target_pos[1] - self.actual_pos[1]) * 71.5) ** 2))


	# calculates the angle the robot has to turn to drive to the smartphone
	def get_angle(self):
		latitude = self.target_pos[0] - self.actual_pos[0]
		longitude = self.target_pos[1] - self.actual_pos[1]
		angle = -(self.orientation + np.arctan2(longitude, latitude))
		if 2* np.pi - abs(angle) < abs(angle):
			angle = -1* np.sign(angle)*(2* np.pi - abs(angle))
		return angle

	# calculate rotate velocity
	def get_angular_vel(self):
	    angle = self.get_angle()
	    if angle == 0:
		return 0
	    vel = angle * 0.6
	    if abs(vel) > 1.5:
		vel = 1.5 * np.sign(vel)
	    return vel


	def calculate_speed(self, distance):
	    # speed in m/s
	    if distance > 2:  # max speed of jackal is 2m/s
	        speed = 2
	    elif distance < 0.0015:
	        speed = 0
		print("Ziel erreicht!")
	    else:
		speed = 2
	        #speed = np.abs(distance) * 10
	    #print("vel lin",speed)
	    return speed


	def run(self):
	    msg = Twist()
	    msg.linear.y = 0
	    msg.linear.z = 0
	    msg.angular.x = 0
	    msg.angular.y = 0
	    while not rospy.is_shutdown():
	        msg.angular.z = self.get_angular_vel()
	        msg.linear.x = self.calculate_speed(self.get_distance())
	        self.pub_twist.publish(msg)
		print("---------------------------------")
		print("pos", self.actual_pos[0], self.actual_pos[1])
		print("dis,ang", self.get_distance(),np.rad2deg(self.get_angle()))
	        rospy.on_shutdown(self.stop)
	        self.rate.sleep()


	# stop robot when node is stopped
	def stop(self):
	    Twist().linear.x = 0
	    Twist().linear.y = 0
	    Twist().linear.z = 0
	    Twist().angular.x = 0
	    Twist().angular.y = 0
	    Twist().angular.z = 0
	    self.pub_twist.publish(Twist())



if __name__ == '__main__':
	try:
		FollowMe().run()
	except rospy.ROSInterruptException:
		pass

    	# the position of the smartphone

"""
    	def set_target_pos(self, data):
        	# bildet Mittwelwert
        	for i in range(0, 9):
            		self.SmartphoneLatitudes[i+1] = self.SmartphoneLatitudes[i]
            		self.SmartphoneLongitudes[i+1] = self.SmartphoneLongitudes[i]
        	self.SmartphoneLatitudes[0] = data.latitude
        	self.SmartphoneLongitudes[0] = data.longitude
        	self.target_pos[0] = np.sum(self.SmartphoneLatitudes)/10
        	self.target_pos[1] = np.sum(self.SmartphoneLongitudes)/10
"""