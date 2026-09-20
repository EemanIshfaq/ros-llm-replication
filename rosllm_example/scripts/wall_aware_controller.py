#!/usr/bin/env python3

import rospy
import math
from collections import deque
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

WALL_MIN = 1.5
WALL_MAX = 9.5

SAFE_MIN = 2.5
SAFE_MAX = 8.5

MOVE_SPEED = 2.0
TURN_SPEED = 1.57

class SmartController:

    def __init__(self):
        rospy.init_node('wall_aware_controller')

        self.pose = None
        self.pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
        rospy.Subscriber('/turtle1/pose', Pose, self.pose_cb)

        self.memory = deque(maxlen=20)

        # 🔥 NEW FIXES
        self.is_escaping = False
        self.last_escape_time = rospy.Time.now()

        rospy.loginfo("🚀 FIXED Controller Started")

        while self.pose is None:
            rospy.sleep(0.1)

        self.loop()

    def pose_cb(self, msg):
        self.pose = msg

    # ---------------- WALL ----------------
    def near_wall(self):
        return (self.pose.x < WALL_MIN or self.pose.x > WALL_MAX or
                self.pose.y < WALL_MIN or self.pose.y > WALL_MAX)

    def safe_zone(self):
        return (SAFE_MIN < self.pose.x < SAFE_MAX and
                SAFE_MIN < self.pose.y < SAFE_MAX)

    def wall_dir(self):
        d = {
            "left": self.pose.x,
            "right": WALL_MAX - self.pose.x,
            "bottom": self.pose.y,
            "top": WALL_MAX - self.pose.y
        }
        return min(d, key=d.get)

    # ---------------- MOVE ----------------
    def move(self, lin=0, ang=0, t=1.0):
        twist = Twist()
        twist.linear.x = lin
        twist.angular.z = ang

        end = rospy.Time.now() + rospy.Duration(t)
        while rospy.Time.now() < end:
            self.pub.publish(twist)
            rospy.sleep(0.05)

        self.pub.publish(Twist())

    # ---------------- ESCAPE ----------------
    def escape(self):

        # 🔥 STOP LOOPING
        if self.is_escaping:
            return

        # 🔥 COOLDOWN
        if (rospy.Time.now() - self.last_escape_time).to_sec() < 2:
            return

        self.is_escaping = True
        self.last_escape_time = rospy.Time.now()

        wall = self.wall_dir()
        rospy.logwarn(f"🚨 ESCAPING from {wall}")

        # 🔥 STRONG BACKUP
        for _ in range(8):
            self.move(lin=-2.5, t=0.2)
            if not self.near_wall():
                break

        # 🔥 TURN AWAY PROPERLY
        if wall in ["left", "bottom"]:
            self.move(ang=-TURN_SPEED, t=2.0)
        else:
            self.move(ang=TURN_SPEED, t=2.0)

        # 🔥 MOVE INTO CENTER
        for _ in range(5):
            self.move(lin=2.0, t=0.3)
            if self.safe_zone():
                break

        rospy.loginfo("✅ ESCAPE COMPLETE")

        self.is_escaping = False

    # ---------------- EXECUTE ----------------
    def execute(self, cmd):

        if self.near_wall():
            self.escape()
            return

        if cmd in ["forward", "w"]:
            self.move(lin=MOVE_SPEED)

        elif cmd in ["back", "s"]:
            self.move(lin=-MOVE_SPEED)

        elif cmd in ["left", "a"]:
            self.move(ang=TURN_SPEED)

        elif cmd in ["right", "d"]:
            self.move(ang=-TURN_SPEED)

        elif cmd == "spin":
            self.move(ang=6.28)

        elif cmd == "square":
            for _ in range(4):
                if self.near_wall():
                    self.escape()
                    return
                self.move(lin=2.0, t=1.5)
                self.move(ang=TURN_SPEED)

        elif cmd == "circle":
            self.move(lin=1.5, ang=1.0, t=6)

        else:
            rospy.logwarn("Unknown command")
            return

        self.memory.append(cmd)

    # ---------------- LOOP ----------------
    def loop(self):

        while not rospy.is_shutdown():
            try:
                cmd = input(">> ").strip().lower()
            except:
                break

            if cmd in ["q", "quit"]:
                break

            if cmd in ["repeat", "previous"]:
                if self.memory:
                    cmd = self.memory[-1]
                    rospy.loginfo(f"🔁 Repeating: {cmd}")
                else:
                    continue

            self.execute(cmd)


if __name__ == "__main__":
    SmartController()
