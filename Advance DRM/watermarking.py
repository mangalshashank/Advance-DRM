import cv2
from scipy.fftpack import dct, idct
import numpy as np

def dct2(a):
    return dct(dct(a.T, norm='ortho').T, norm='ortho')

def idct2(a):
    return idct(idct(a.T, norm='ortho').T, norm='ortho')

def convert_to_same_channels(image, target_channels):
    if len(image.shape) == 2:
        # Convert grayscale image to RGB
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == target_channels:
        # Already has the desired number of channels
        return image
    else:
        # Convert to grayscale and then to RGB
        return cv2.cvtColor(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2RGB)

def apply_watermark(cover_image_np_array, watermark_image_np_array, alpha):
    # Resize images to the same dimensions
    img = cv2.resize(cover_image_np_array, (512, 512))
    watermark = cv2.resize(watermark_image_np_array, (512, 512))

    # Ensure both images have the same number of channels
    img = convert_to_same_channels(img, watermark.shape[2])
    watermark = convert_to_same_channels(watermark, img.shape[2])

    # Convert images to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    watermark = cv2.cvtColor(watermark, cv2.COLOR_BGR2GRAY)

    # Apply DCT to the cover image and watermark image
    dct_img = dct2(img)
    dct_watermark = dct2(watermark)

    # Apply watermark using alpha value
    dct_watermarked = dct_img + alpha * dct_watermark

    # Inverse DCT to get watermarked image
    watermarked = idct2(dct_watermarked)

    # Clip values to valid image range and convert to uint8
    watermarked_image = np.uint8(np.clip(watermarked, 0, 255))

    return watermarked_image

def extract_watermark(cover_image_np_array, watermarked_image_np_array, beta):
    # Resize images to the same dimensions
    img = cv2.resize(cover_image_np_array, (512, 512))
    watermarked = cv2.resize(watermarked_image_np_array, (512, 512))

    # Ensure both images have the same number of channels
    img = convert_to_same_channels(img, watermarked.shape[2])
    watermarked = convert_to_same_channels(watermarked, img.shape[2])

    # Convert images to grayscale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    watermarked = cv2.cvtColor(watermarked, cv2.COLOR_BGR2GRAY)

    # Apply DCT to the cover image and watermarked image
    dct_img = dct2(img)
    dct_watermarked = dct2(watermarked)

    # Extract watermark using beta value
    extracted_watermark = (dct_watermarked - dct_img) / beta

    # Inverse DCT to get the extracted watermark
    extracted_watermark = idct2(extracted_watermark)

    # Clip values to valid image range and convert to uint8
    extracted_watermark = np.uint8(np.clip(extracted_watermark, 0, 255))

    return extracted_watermark

# # Example usage:
# cover_image_path = 'path/to/cover_image.jpg'
# watermark_image_path = 'path/to/watermark_image.jpg'

# # Choose appropriate alpha and beta values
# alpha_value = 0.009
# beta_value = 0.01

# # Apply watermark
# watermarked_image = apply_watermark(cv2.imread(cover_image_path), cv2.imread(watermark_image_path), alpha_value)

# # Save watermarked image
# cv2.imwrite('watermarked_image.jpg', watermarked_image)

# # Extract watermark
# extracted_watermark = extract_watermark(cv2.imread(cover_image_path), cv2.imread('watermarked_image.jpg'), beta_value)

# # Save extracted watermark
# cv2.imwrite('extracted_watermark.jpg', extracted_watermark)
