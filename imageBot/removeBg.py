import numpy as np
from PIL import Image


def convolution(img: np.ndarray, kernal: np.ndarray) -> np.ndarray:
    if len(img.shape) == 3:
        m_i, n_i, c_i = img.shape

    elif len(img.shape) == 2:
        img = img[..., np.newaxis]
        m_i, n_i, c_i = img.shape

    else:
        raise ValueError("image foramt not recognized")

    m_k, n_k = kernal.shape

    y_strieds = m_i - m_k + 1
    x_strieds = n_i - n_k + 1

    img_ = img.copy()
    output_shape = (y_strieds, x_strieds, c_i)
    output = np.zeros(output_shape, dtype=np.float32)

    count = 0

    temp_output = output.reshape(
        (output_shape[0] * output_shape[1], output_shape[2])
    )

    for i in range(y_strieds):
        for j in range(x_strieds):
            for c in range(c_i):
                sub_matrix = img_[i:i + m_k, j:j + n_k, c]
                temp_output[count, c] = np.sum(sub_matrix * kernal)

            count += 1

    output = temp_output.reshape(output_shape)

    return output

def togray(img: np.ndarray, format: str="rgb"):
    '''
    Algorithm:
    >>> 0.2989 * R + 0.5870 * G + 0.1140 * B 

    - Returns a gray image
    '''
    if format.lower() == 'bgr':
        b, g, r = img[..., 0], img[..., 1], img[..., 2]
        return 0.2989 * r + 0.5870 * g + 0.1140 * b
    elif format.lower() == 'rgb':
        r, g, b = img[..., 0], img[..., 1], img[..., 2]
        return 0.2989 * r + 0.5870 * g + 0.1140 * b
    else:
        raise Exception('Unsupported value in parameter \'format\'')

def gaussianBlur(img: np.ndarray, sigma, filter_shape= None):
    '''
    - Returns a list that contains the filter and resultant image

    * if filter_shape is None then it calculated automatically as below,

    >>> _ = 2 * int(4 * sigma + 0.5) + 1
    >>> filter_shape = [_, _]

    ### Example:
    >>> import matplotlib.pyplot as plt
    >>> from PIL import Image
    >>> img = np.array(Image.open('../../assets/lenna.png'))
    >>> g_filter, blur_image = GuassianBlur(img, 4)
    '''

    if filter_shape == None:
        _ = 2 * int(4 * sigma + 0.5) + 1
        filter_shape = [_, _]

    gaussian_filter = np.zeros((filter_shape[0], filter_shape[1]), np.float32)
    size_y = filter_shape[0] // 2
    size_x = filter_shape[1] // 2

    x, y = np.mgrid[-size_y:size_y+1, -size_x:size_x+1]
    normal = 1 / (2.0 * np.pi * sigma**2)
    gaussian_filter = np.exp(-((x**2 + y**2) / (2.0*sigma**2))) * normal

    filtered = convolution(img, gaussian_filter)

    return gaussian_filter, filtered.astype(np.uint8)


def sobel_filter(img: np.ndarray):
    img = togray(img)
    blurred = gaussianBlur(img, 1.5, filter_shape=(10, 10))[1] / 255

    k_x = np.array(
        [[-1, 0, 1],
         [-2, 0, 2],
         [-1, 0, 1]], np.float32
    )

    k_y = np.array(
        [[1, 2, 1],
         [0, 0, 0],
         [-1, -2, -1]], np.float32
    )

    I_x = convolution(blurred, k_x)
    I_y = convolution(blurred, k_y)


    G = np.hypot(I_x, I_y)
    G = G / G.max() * 256

    theta = np.atan2(I_y, I_x)

    return np.squeeze(G), np.squeeze(theta)

def non_max_suppression(img: np.ndarray, thata: np.ndarray):
    M, N = img.shape
    Z = np.zeros((M, N), dtype=np.int32)

    angle = thata * 180 / np.pi
    angle[angle < 0] += 180

    for i in range(1, M - 1):
        for j in range(1, N - 1):
            q = r = 255
            if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                r = img[i, j - 1]
                q = img[i ,j + 1]
            elif (22.5 <= angle[i, j] < 67.5):
                r = img[i - 1, j + 1]
                q = img[i + 1,j - 1]
            elif (67.5 <= angle[i, j] < 112.5):
                r = img[i - 1, j]
                q = img[i + 1,j]
            elif (112.5 <= angle[i, j] < 157.5):
                r = img[i + 1, j + 1]
                q = img[i - 1,j - 1]

            if (img[i, j] >= q) and (img[i, j] >= r):
                Z[i, j] = img[i, j]
            else:
                Z[i, j] = 0

    return Z

def threshold_hysteresis(img: np.ndarray, lowThresholdRatio=0.05, highThresholdRatio=0.09, weak=np.int32(25)):
    high_threshold = img.max() * highThresholdRatio
    low_threshold = high_threshold * lowThresholdRatio

    M, N = img.shape
    res = np.zeros((M, N), dtype=np.int32)

    strong = np.int32(255)

    strong_i, strong_j = np.where(img >= high_threshold)
    weak_i, weak_j = np.where((img <= high_threshold) & (img >= low_threshold))

    res[strong_i, strong_j] = strong
    res[weak_i, weak_j] = weak

    for i in range(1, M - 1):
        for j in range(1, N -1):
            if res[i, j] == weak:
                if (
                    (res[i+1, j-1] == strong) or (res[i+1, j] == strong) or
                    (res[i+1, j+1] == strong) or (res[i, j-1] == strong) or
                    (res[i, j+1] == strong) or (res[i-1, j-1] == strong) or
                    (res[i-1, j] == strong) or (res[i-1, j+1] == strong)
                ):
                    res[i, j] = strong
                else:
                    res[i, j] = 0

    return res

def canny_edge_detection(img: np.ndarray):
    G, theta = sobel_filter(img)
    img = non_max_suppression(G, theta)
    img = threshold_hysteresis(img)

    return img

def remove_bg(img: Image.Image):
    img_ = np.array(img)

    img_ = canny_edge_detection(img_)

    mask = Image.fromarray((img_ > 0).astype(np.uint8) * 255)
    
    mask = mask.resize(img.size)

    mask.save("./static/uploads/removed_bg_mask.png")
    #alpha = ImageOps.invert(mask)
    
    original_rgba = img.convert("RGBA")
    
    original_rgba.show()
    #original_rgba.putalpha(mask)
    
    original_rgba.show()

    background = Image.new("RGBA", original_rgba.size, (0, 0, 0, 0))
    
    result = Image.composite(original_rgba, background, mask)

    original_rgba.close()
    mask.close()
    background.close()
    #alpha.close()
    return result

if __name__ == "__main__":
    img = Image.open("./static/uploads/uploaded_img.jpeg")

    res = remove_bg(img)


    res.show()
    res.save("./static/uploads/removed_bg.png")
    res.close()




