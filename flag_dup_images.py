from dotenv import load_dotenv
load_dotenv()

import os
import io
import imagehash
import datetime
from PIL import Image
from fastapi import FastAPI
from typing import List

# Load folder paths from .env
SOURCE_FOLDER = os.getenv("SOURCE_FOLDER")
DEST_FOLDER = os.getenv("DEST_FOLDER")


import os
import io
import imagehash
import datetime
from PIL import Image
from fastapi import FastAPI
from typing import List

app = FastAPI()


# Get all image files from a local folder
def list_images(folder_path):
    images = []
    for file_name in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            timestamp = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            size = os.path.getsize(file_path)
            images.append((file_path, timestamp, size))
    return images


# Find min and max timestamps
def get_time_range(folder_path):
    images = list_images(folder_path)
    if images:
        return images[0][1], images[-1][1]
    return None, None


# Compute hash of an image
def compute_hash(image_path):
    image = Image.open(image_path)
    return imagehash.phash(image)


# Identify similar images within 60 seconds and preserve the highest resolution
def find_and_filter_duplicates(folder_path):
    images = list_images(folder_path)
    duplicates = []
    image_groups = {}

    for file_path, timestamp, size in images:
        img_hash = compute_hash(file_path)
        print(img_hash)
        # Group by hash
        if img_hash in image_groups:
            image_groups[img_hash].append((file_path, timestamp, size))
        else:
            image_groups[img_hash] = [(file_path, timestamp, size)]
    print(image_groups)
    for img_hash, group in image_groups.items():
        group.sort(key=lambda x: (-x[2], x[1]))  # Sort by size (desc), then timestamp (asc)
        preserved_image = group[0]  # Keep the highest resolution image
        duplicates.extend([img[0] for img in group[1:]])  # Mark others as duplicates

    return duplicates


# Move duplicates to another folder
def move_duplicates(source_folder, dest_folder):
    #duplicates = find_and_filter_duplicates(source_folder)
    x=0;
    duplicates = find_similar_images(source_folder)
    print(duplicates)
    os.makedirs(dest_folder, exist_ok=True)
    for dup_file in duplicates:
        file_name = os.path.basename(dup_file[1])
        print("file_name",file_name)
        if os.path.exists(os.path.join(source_folder, file_name)):
            dest_path = os.path.join(dest_folder, file_name)
            os.rename(dup_file[1], dest_path)
    return len(duplicates)


def compute_phash(img_path):
    img = Image.open(img_path).convert("RGB")
    return imagehash.phash(img)


def find_similar_images(folder_path):
    images = list_images(folder_path)
    similar_images = []

    hashes = {img[0]: compute_phash(img[0]) for img in images}

    for img1, hash1 in hashes.items():
        for img2, hash2 in hashes.items():
            if img1 != img2 and hash1 - hash2 < 5:  # Threshold for similarity
                similar_images.append((img1, img2, hash1 - hash2))

    return similar_images


# def find_similar_images(folder_path,x):
#     images = list_images(folder_path)
#     similar_images = []
#
#     for i in range(len(images)):
#         for j in range(i + 1, len(images)):
#             similarity = compute_similarity(images[i][0], images[j][0])  # Pass only file paths
#             if similarity > 0.90:
#                 similar_images.append((images[i][0], images[j][0], similarity))
#
#     return similar_images
# curl -X GET "http://localhost:8000/process?folder_path=C:/Users/vipul/Downloads/wetransfer_images-over-1000_2025-04-02_1930&dest_folder=C:/Users/vipul/Downloads/destination"
# {"min_time":"2025-04-02 19:35:00","max_time":"2025-04-02 19:35:00","duplicates_moved":256}

@app.get("/process")
def process_images(folder_path: str, dest_folder: str):
    #folder_path="C:/Users/vipul/Downloads/sample"
    folder_path="C:/Users/vipul/Downloads/wetransfer_images-over-1000_2025-04-02_1930"

    dest_folder="C:/Users/vipul/Downloads/wetransfer_images-over-1000_2025-04-02_1930/moved_files"
    min_time, max_time = get_time_range(folder_path)
    duplicate_count = move_duplicates(folder_path, dest_folder)
    print("done")
    return {
        "min_time": str(min_time),
        "max_time": str(max_time),
        "duplicates_moved": duplicate_count,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
