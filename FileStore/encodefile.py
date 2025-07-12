import cv2
import numpy as np
import zlib
import math


def encode_csv_to_avi(csv_path, avi_path, frame_width=256, frame_height=256, fps=1):
    with open(csv_path, 'rb') as f:
        original_data = f.read()
    compressed_data = zlib.compress(original_data, level=9)
    print("Compressed data header:", compressed_data[:16])

    total_bytes = len(compressed_data)
    bytes_per_frame = frame_width * frame_height * 3
    num_frames = math.ceil(total_bytes / bytes_per_frame)
    padded_data = compressed_data + b'\x00' * (num_frames * bytes_per_frame - total_bytes)

    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    out = cv2.VideoWriter(avi_path, fourcc, fps, (frame_width, frame_height), isColor=True)
    for i in range(num_frames):
        start = i * bytes_per_frame
        end = start + bytes_per_frame
        frame_bytes = np.frombuffer(padded_data[start:end], dtype=np.uint8)
        frame = frame_bytes.reshape((frame_height, frame_width, 3))
        out.write(frame)
    out.release()
    print(f"Encoded {csv_path} into {avi_path} using {num_frames} frames (lossless FFV1).")

def encode_input_csv():
    csv_path = "./csv/input.csv"
    mp4_path = "./video/encoded_compressed_avi.avi"
    encode_csv_to_avi(csv_path, mp4_path)


if __name__ == "__main__":
    encode_input_csv()
