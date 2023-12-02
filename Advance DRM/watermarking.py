import cv2
from scipy.fftpack import dct, idct
import numpy as np

def dct2(a):
    return dct(dct(a.T, norm='ortho').T, norm='ortho')
def idct2(a):
    return idct(idct(a.T, norm='ortho').T, norm='ortho')

def apply_watermark(cover_image_path, watermark_image_path):
    img = cv2.imread(cover_image_path, 0)
    watermark = cv2.imread(watermark_image_path, 0)
    img = cv2.resize(img, (512, 512))
    watermark = cv2.resize(watermark, (512, 512))
    dct_img = dct2(img)    # DCT of cover image
    dct_watermark = dct2(watermark)   # DCT of watermark image
    alpha = 0.009
    dct_watermarked = dct_img + alpha * dct_watermark  
    watermarked = idct2(dct_watermarked)
    watermarked = np.uint8(np.clip(watermarked, 0, 255))
    cv2.imshow('Watermarked', watermarked)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def extract_watermark(cover_image_path, watermarked_image_path):
    img = cv2.imread(cover_image_path, 0)
    watermarked = cv2.imread(watermarked_image_path, 0)
    img = cv2.resize(img, (512, 512))
    watermarked = cv2.resize(watermarked, (512, 512))
    dct_img = dct2(img)    # DCT of cover image
    dct_watermarked = dct2(watermarked)   # DCT of watermarked image
    beta = 0.1
    extracted_watermark = (dct_watermarked - dct_img) / beta
    extracted_watermark = idct2(extracted_watermark)
    extracted_watermark = np.uint8(np.clip(extracted_watermark, 0, 255))  # Convert to uint8
    cv2.imshow('Extracted Watermark', extracted_watermark)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


