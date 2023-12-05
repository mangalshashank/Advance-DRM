import numpy as np
import pywt
from PIL import Image
from scipy.fftpack import dct
from scipy.fftpack import idct

model = 'haar'
level = 1

def convert_image(image_name, size):
    img = Image.open( image_name).resize((size, size), 1)
    img = img.convert('L')
    image_array = np.array(img.getdata(), dtype=float).reshape((size, size))
    return image_array

def process_coefficients(imArray, model, level):
    coeffs=pywt.wavedec2(data = imArray, wavelet = model, level = level)
    coeffs_H=list(coeffs) 
    return coeffs_H

def embed_mod2(coeff_image, coeff_watermark, offset=0):
    for i in range(coeff_watermark.__len__()):
        for j in range(coeff_watermark[i].__len__()):
            coeff_image[i*2+offset][j*2+offset] = coeff_watermark[i][j]
    return coeff_image

def embed_mod4(coeff_image, coeff_watermark):
    for i in range(coeff_watermark.__len__()):
        for j in range(coeff_watermark[i].__len__()):
            coeff_image[i*4][j*4] = coeff_watermark[i][j]
    return coeff_image
           
def embed_watermark(watermark_array, orig_image):
    watermark_flat = watermark_array.ravel()
    ind = 0
    for x in range (0, orig_image.__len__(), 8):
        for y in range (0, orig_image.__len__(), 8):
            if ind < watermark_flat.__len__():
                subdct = orig_image[x:x+8, y:y+8]
                subdct[5][5] = watermark_flat[ind]
                orig_image[x:x+8, y:y+8] = subdct
                ind += 1 
    return orig_image
      
def apply_dct(image_array):
    size = image_array[0].__len__()
    all_subdct = np.empty((size, size))
    for i in range (0, size, 8):
        for j in range (0, size, 8):
            subpixels = image_array[i:i+8, j:j+8]
            subdct = dct(dct(subpixels.T, norm="ortho").T, norm="ortho")
            all_subdct[i:i+8, j:j+8] = subdct
    return all_subdct

def inverse_dct(all_subdct):
    size = all_subdct[0].__len__()
    all_subidct = np.empty((size, size))
    for i in range (0, size, 8):
        for j in range (0, size, 8):
            subidct = idct(idct(all_subdct[i:i+8, j:j+8].T, norm="ortho").T, norm="ortho")
            all_subidct[i:i+8, j:j+8] = subidct
    return all_subidct

def get_watermark(dct_watermarked_coeff, watermark_size):
    subwatermarks = []
    for x in range (0, dct_watermarked_coeff.__len__(), 8):
        for y in range (0, dct_watermarked_coeff.__len__(), 8):
            coeff_slice = dct_watermarked_coeff[x:x+8, y:y+8]
            subwatermarks.append(coeff_slice[5][5])
    watermark = np.array(subwatermarks).reshape(watermark_size, watermark_size)
    return watermark

def apply_watermark(image_path, watermark_path):
    image_array = convert_image(image_path, 2048)
    watermark_array = convert_image(watermark_path, 128)
    coeffs_image = process_coefficients(image_array, model, level=level)
    dct_array = apply_dct(coeffs_image[0])
    dct_array = embed_watermark(watermark_array, dct_array)
    coeffs_image[0] = inverse_dct(dct_array)
    image_array_H=pywt.waverec2(coeffs_image, model)
    image_array_copy = image_array_H.clip(0, 255)
    image_array_copy = image_array_copy.astype("uint8")
    return Image.fromarray(image_array_copy)

def recover_watermark(watermarked_image):
    watermarked_image = convert_image(watermarked_image, 2048)
    coeffs_image = process_coefficients(watermarked_image, model, level=level)
    image_array_H=pywt.waverec2(coeffs_image, model)
    coeffs_watermarked_image = process_coefficients(image_array_H, model, level=level)
    dct_watermarked_coeff = apply_dct(coeffs_watermarked_image[0])
    watermark_array = get_watermark(dct_watermarked_coeff, 128)
    watermark_array =  np.uint8(watermark_array)
    return Image.fromarray(watermark_array)