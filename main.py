import requests
import json
import numpy as np
import pandas as pd
import cv2 
import time

# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# The sample connects to a device-specific MQTT endpoint on your IoT Hub.
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

CONNECTION_STRING = "{Your_IoT_hub_device_connection_string}"
PREDICTION_URL = "{Your_Custom_Vision_Prediction_URL}"
PREDICTION_KEY = "{Your_Custom_Vision_Prediction_Key}"
TAG_LIST = ["person"]
PROBABILITY_THRESHOLD = 0.95
VIDEO_FILE_URL="https://github.com/intel-iot-devkit/sample-videos/raw/master/worker-zone-detection.mp4"
VIDEO_FILE_NAME = VIDEO_FILE_URL[VIDEO_FILE_URL.rfind('/') + 1:]

response = requests.get(VIDEO_FILE_URL)
with open('./input/' + VIDEO_FILE_NAME, 'wb') as saveFile:
    saveFile.write(response.content)

def iothub_client_init():
    # Create an IoT Hub client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    return client

def cv_oj_api(url, key, img_file_path, img, tag_list):
    headers = {
            'content-type':'application/octet-stream',
            'Prediction-Key': key
            }
    response = requests.post(url, data = open(img_file_path, "rb"), headers = headers)
    response.raise_for_status()
    result = response.json()

    tag_grab_dict = {}
    #print(result)
    prob = pd.DataFrame([[tag_i["tagName"], tag_i["probability"]] for tag_i in result["predictions"]], columns=["tagName", "probability"])
    #print(prob.head)
    for tag in tag_list:
        tag_grab_dict[(tag+'_count')] = 0
        if len(prob.query('tagName==@tag')) == 0:
            #tag_grab_dict[(tag+'_px')] = 0
            #tag_grab_dict[(tag+'_py')] = 0
            tag_grab_dict[(tag+'_x')] = 0
            tag_grab_dict[(tag+'_y')] = 0
            continue
        if prob.query('tagName==@tag')['probability'].max() < PROBABILITY_THRESHOLD:
            #tag_grab_dict[(tag+'_px')] = 0
            #tag_grab_dict[(tag+'_py')] = 0
            tag_grab_dict[(tag+'_x')] = 0
            tag_grab_dict[(tag+'_y')] = 0
            continue

        tag_ids = prob.query('tagName==@tag')['probability']
        for i, probability in tag_ids.iteritems():
            if(probability > PROBABILITY_THRESHOLD):
                tag_grab_dict[(tag+'_count')] += 1
                #tag_grab_dict['created'] = result['created']
                tag_grid = result['predictions'][i]['boundingBox']
                y = int(tag_grid['top'] * img.shape[0])
                x = int(tag_grid['left'] * img.shape[1])
                h = int(tag_grid['height'] * img.shape[0])
                w = int(tag_grid['width'] * img.shape[1])
                # position of the highest probability one
                if i == 0:
                    # center of a box
                    tag_x = x + int(w/2)
                    tag_y = y + int(h/2)
                    #tag_grab_dict[(tag + '_px')] = x
                    #tag_grab_dict[(tag + '_py')] = y
                    tag_grab_dict[(tag + '_x')] = tag_x
                    tag_grab_dict[(tag + '_y')] = tag_y                

                cv2.putText(img, tag, (x, y - 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return img, tag_grab_dict


if __name__ == '__main__':
    cap = cv2.VideoCapture('./input/' + VIDEO_FILE_NAME) # Video file name to be predicted
    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out = cv2.VideoWriter(('./output/result.mp4'), fourcc, 2, (cap_width, cap_height)) # Output file name

    count=0
    tag_grab_df = pd.DataFrame([])

    client = iothub_client_init()

    while(cap.isOpened()):
        t1 = time.time()
        ret, frame = cap.read()
        if not ret:
            break
        count += 1

        # 1 frame/sec 
        if count % fps != 0:
            continue

        # img resize
        #height = frame.shape[0]
        #width = frame.shape[1]
        #frame = cv2.resize(frame, (int(width*0.5), int(height*0.5)))

        tmp_file_path = './output/tmp.jpg'
        cv2.imwrite(tmp_file_path, frame)

        # api prediction & masking
        frame, tag_grab_dict = cv_oj_api(PREDICTION_URL, PREDICTION_KEY, tmp_file_path, frame, TAG_LIST)

        # Send message to IoT Hub
        message = Message(json.dumps(tag_grab_dict))
        print( "Sending message: {}".format(message) )
        client.send_message(message)

        tag_grab_dict['time'] = count/fps
        tag_grab_df = tag_grab_df.append([tag_grab_dict])

        # write & show frame
        #print(frame.shape)
        out.write(frame)
        #img_file_path = './output/' + str(count) + '.jpg'
        #cv2.imwrite(img_file_path, frame)
        #cv2_imshow(frame) 
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

        sec = count/fps
        if sec % 10 == 0:
            print(sec,'sec ended.')

        #for short time debug
        #if sec >= 10:
        #    break

    # Release everything if job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    tag_grab_df.to_csv('./output/tag_grab_df.csv', index=False, encoding='shift-JIS')