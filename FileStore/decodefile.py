import cv2
import numpy as np
import zlib
import math

def decode_avi_to_csv(avi_path, csv_path, frame_width=256, frame_height=256):
    cap = cv2.VideoCapture(avi_path)
    byte_list = []
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if frame.shape != (frame_height, frame_width, 3):
            raise ValueError(f"Unexpected frame shape: {frame.shape}")
        byte_list.append(frame.flatten())
    cap.release()
    if frame_count == 0:
        raise ValueError("No frames found in video. Please check your input file and codec.")
    all_bytes = np.concatenate(byte_list).astype(np.uint8)
    print("Raw bytes header:", all_bytes[:16])
    try:
        decompressed_data = zlib.decompress(all_bytes.tobytes())
    except Exception as e:
        trimmed_bytes = all_bytes.tobytes().rstrip(b'\x00')
        decompressed_data = zlib.decompress(trimmed_bytes)
    with open(csv_path, 'wb') as f:
        f.write(decompressed_data)
    print(f"Decoded {avi_path} back to {csv_path} (lossless FFV1).")


def decode_avi_to_csv_file():
    mp4_path = "./video/encoded_compressed_avi.avi"
    csv_path = "./csv/output.csv"
    decode_avi_to_csv(mp4_path, csv_path)


if __name__ == "__main__":
    decode_avi_to_csv_file()

