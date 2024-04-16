import hashlib
from PIL import Image

# Function to calculate the SHA256 hash value of a image using its path
def calculate_sha256(image_path):
    # sha256_hash = hashlib.sha256()
    image = Image.open(image_path)
    res = str(hashlib.sha256((image).tobytes()).hexdigest())
    return res
    # with open(image_path, "rb") as f:
    #     # Read and update hash string value in blocks of 4K
    #     for byte_block in iter(lambda: f.read(4096), b""):
    #         sha256_hash.update(byte_block)
    # return sha256_hash.hexdigest()




