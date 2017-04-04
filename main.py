import sys
import time
import numpy as np
import math
import time
sys.path.append("documents/grad-master/")
from svmutil import *

def setPlatform():
    if sys.platform == "darwin":
        print("Using universal Darwin Libraries")
        sys.path.append("./Libraries/LeapMotion/darwin/")

    elif sys.platform == "win32":
        if sys.maxsize > 2**32:
            print("Using 32-bit Windows Libraries")
            sys.path.append("./Libraries/LeapMotion/win64/")
        else:
            print("Using 64-bit Windows Libraries")
            sys.path.append("./Libraries/LeapMotion/win32/")

    elif sys.platform == "linux":
        if sys.maxsize > 2**32:
            print("Using 32-bit Linux Libraries")
            sys.path.append("./Libraries/LeapMotion/linux64/")
        else:
            print("Using 64-bit Linux Libraries")
            sys.path.append("./Libraries/LeapMotion/linux32/")

setPlatform()
import Leap


def getUnitVector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def getAngle(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> getAngle((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> getAngle((1, 0, 0), (1, 0, 0))
            0.0
            >>> getAngle((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = getUnitVector(v1)
    v2_u = getUnitVector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def main():
    target=open("check.txt","w")
    print("Connecting to controller")

    controller = Leap.Controller()
    count=0
    check=-1;
    param=1
    label=0
    target.write("\n")
    target.write(str(label)+" ")
    while not controller.is_connected:
        pass

    print("Connected to controller")

    previousID = controller.frame().id

    while controller.is_connected:
        time.sleep(0.011)
        if(count==100):
            sys.exit()
        frame = controller.frame()

        if frame.id != previousID:
            previousID = frame.id
            hands = frame.hands

            for hand in hands:
                confidence=hand.confidence
                if(confidence > 0.2):
                    check=0
                    print(confidence)
                    if hand.is_left:
                        print("left")
                    elif hand.is_right:
                        print("right")
                    fingers=frame.fingers
                    '''roll=hand.palm_position.yaw
                    print((roll*180)/math.pi)'''
                    for finger in fingers:
                        print(finger.type)
                        for i in range(0,3):
                            print(finger.tip_position[i]-hand.palm_position[i])
                            target.write(str(param)+":"+str(finger.tip_position[i]-hand.palm_position[i])+" ")
                            param=param+1
                        print((finger.tip_position.angle_to(hand.palm_normal)*180)/math.pi)
                        target.write(str(param)+":"+str((finger.tip_position.angle_to(hand.palm_normal)*180)/math.pi)+" ")
                        param=param+1
                        for i in range(0,4):
                            for j in range(0,3):
                                print(finger.joint_position(i)[j]-hand.palm_position[j])
                                target.write(str(param)+":"+str(finger.joint_position(i)[j]-hand.palm_position[j])+" ")
                                param=param+1
                            print((finger.joint_position(i).angle_to(hand.palm_normal)*180)/math.pi)
                            target.write(str(param)+":"+str((finger.joint_position(i).angle_to(hand.palm_normal)*180)/math.pi)+" ")
                            param=param+1
        if check == 0:
            count=count+1
            check=-1
            print("count "+str(count))
    target.write("\n")
    target.close()



if __name__ == '__main__':
    main()
