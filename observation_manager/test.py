import rospy
from rosllm_srvs.srv import AtomicAction, AtomicActionResponse, AtomicActionRequest

rospy.init_node("test_node")

req = AtomicActionRequest()
req.input = '{"vel": 1.0}'

handle = rospy.ServiceProxy("/forward", AtomicAction)
resp = handle(req)

print("Goodbye")
