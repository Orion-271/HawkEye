#grey -> red overlay version (v3 - cleaner thresholding)
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array, load_img

# Load the saved model
generator_ = tf.keras.models.load_model('model/grey.h5')

def load_and_predict(image_path, road_percentile=90):
    """
    road_percentile: only the brightest (100 - road_percentile)% of pixels
    are marked as 'road' in the overlay. Raise this (e.g. 95) for a
    stricter/cleaner mask, lower it (e.g. 80) if roads are being missed.
    """
    combined_image = tf.cast(img_to_array(load_img(image_path)), tf.float32)
    image = combined_image
    image = tf.image.rgb_to_grayscale(tf.image.resize(image, (256, 256))) / 255

    predicted = generator_.predict(tf.expand_dims(image, axis=0))[0]

    # predicted may be (256,256,1) or (256,256,3) - force to 2D
    mask = np.squeeze(predicted)
    if mask.ndim == 3:
        mask = mask[..., 0]
    mask = np.clip(mask, 0, 1)  # keep raw values, just clip to valid range - no stretching

    # Threshold based on percentile of THIS image's own distribution,
    # so we only flag genuinely bright/confident pixels as road
    cutoff = np.percentile(mask, road_percentile)
    road_pixels = mask >= cutoff
    print(f"threshold used: {cutoff:.3f} | road pixels: {road_pixels.sum()} / {mask.size}")

    gray = np.squeeze(image.numpy())
    if gray.ndim == 3:
        gray = gray[..., 0]
    base_rgb = np.stack([gray, gray, gray], axis=-1)
    overlay = base_rgb.copy()
    overlay[..., 0] = np.where(road_pixels, 1.0, overlay[..., 0])
    overlay[..., 1] = np.where(road_pixels, 0.0, overlay[..., 1])
    overlay[..., 2] = np.where(road_pixels, 0.0, overlay[..., 2])

    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.imshow(gray, cmap='gray')
    plt.title("Input Image")
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.imshow(mask, cmap='hot')  # gradient colormap - shows raw confidence, no hard cutoff
    plt.title("Raw Prediction (confidence)")
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.imshow(overlay)
    plt.title(f"Roads Highlighted (top {100-road_percentile}%)")
    plt.axis('off')

    plt.tight_layout()
    plt.show()

# Example usage - change this to your actual test image filename
image_path = "test4.jpg"

load_and_predict(image_path, road_percentile=90)

