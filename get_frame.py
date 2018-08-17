import cv2


def get_frame(frame_num_list, save_file, video_path):
    cap = cv2.VideoCapture(video_path)
    for frame_num in frame_num_list:
        cap.set(1, frame_num)
        ret, frame = cap.read()
        cv2.imwrite(save_file.format(str(frame_num).zfill(6)) + '.png', frame)
