import math
import requests
import sys
from svmutil import *
sys.path.append("documents/grad-master/")


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


def main():
    print("Connecting to controller")
    model = svm_load_model('train2.txt.model')
    controller = Leap.Controller()
    postData = {'access_token': '365e3c7f6d13e7add5d4ae9214f8e36c26c9c0df', 'args': '0'}
    temp = {}
    x = []
    y = [3.0]
    count = 0
    check = -1
    param = 1
    label = 3
    prev = label
    grab = 0
    op = 0
    while not controller.is_connected:
        pass

    print("Connected to controller")

    previousID = controller.frame().id

    while controller.is_connected:
        if count == 100:
            count = 0
            param = 1
            x.append(temp)
            p_labels, p_acc, p_vals = svm_predict(y, x, model)
            valid = False
            if p_labels[0] == 1 and grab == 1 and op == 1:
                print("Hold!")
                valid = True
            if p_labels[0] == -1 and translation_intent_factor > 0.20:
                print("Move!")
                valid = True
            if p_labels[0] == 0 and grab == 1 and op == 1:
                print("Grab!")
                valid = True
            if p_labels[0] == 2 and translation_intent_factor > 0.50:
                print("Hello!")
                valid = True
            prev = p_labels[0]
            op = 0
            grab = 0
            x = []
            temp = {}
            if valid:
                postData['args'] = int(p_labels[0] + 2)
                print(postData['args'])
                requests.post('https://api.particle.io/v1/devices/310021000d47343432313031/led', data=postData)

        frame = controller.frame()
        if count == 0:
            first = frame
        if frame.id != previousID:
            previousID = frame.id
            hands = frame.hands

            for hand in hands:
                confidence = hand.confidence
                if confidence > 0.2:
                    translation_intent_factor = hand.translation_probability(first)
                    check = 0
                    if hand.grab_strength == 1:
                        grab = hand.grab_strength
                    if grab == 1:
                        if hand.grab_strength < 0.55:
                            op = 1
                    fingers = frame.fingers
                    for finger in fingers:
                        '''print(finger.type)'''
                        for i in range(0, 3):
                            temp[param] = finger.tip_position[i] - hand.palm_position[i]
                            param = param + 1
                        temp[param] = ((finger.tip_position.angle_to(hand.palm_normal) * 180) / math.pi)
                        param = param + 1
                        for i in range(0, 4):
                            for j in range(0, 3):
                                temp[param] = finger.joint_position(i)[j] - hand.palm_position[j]
                                param = param + 1
                            temp[param] = ((finger.joint_position(i).angle_to(hand.palm_normal) * 180) / math.pi)
                            param = param + 1
        if check == 0:
            count = count + 1
            check = -1
            '''print("count "+str(count))'''


if __name__ == '__main__':
    main()
