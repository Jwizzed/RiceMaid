import numpy as np
import tensorflow as tf
from PIL import Image
from PIL.ImageFile import ImageFile


def create_model(im_height: int = 300, im_width: int = 300, num_classes: int = 3) -> tf.keras.Model:
    covn_base = tf.keras.applications.EfficientNetB3(
        weights="imagenet", include_top=False, input_shape=(im_height, im_width, 3)
    )
    covn_base.trainable = False

    model = tf.keras.Sequential(
        [
            covn_base,
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(units=32, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(num_classes, activation="softmax", kernel_regularizer="l2"),
        ]
    )

    return model


def predict_image(image_path: str, weights_path: str, im_height: int = 300, im_width: int = 300) -> tuple[str, float]:
    """
    Predicts the class of the given image based on a pre-trained model.

    :param image_path: Path to the image file to be predicted.
    :param weights_path: Path to the pre-trained model weights.
    :param im_height: Height of the input image for resizing.
    :param im_width: Width of the input image for resizing.
    :return: Tuple with predicted class label and prediction probability.
    """
    # Create model and load weights
    model = create_model(im_height, im_width)
    model.load_weights(weights_path)

    # Compile model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.CategoricalCrossentropy(),
        metrics=["accuracy"],
    )

    # Process image
    img: ImageFile = Image.open(image_path)
    img = img.resize((im_width, im_height))
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = tf.keras.applications.efficientnet.preprocess_input(img_array)

    # Make prediction
    predictions = model.predict(preprocessed_img)
    predicted_class = np.argmax(predictions[0])
    probability = float(predictions[0][predicted_class])

    labels = ["BBCH11", "BBCH12", "BBCH13"]
    predicted_label = labels[predicted_class]

    return predicted_label, probability


if __name__ == "__main__":
    image_path = "path_to_your_image.jpg"
    weights_path = "path_to_your_weights.h5"

    predicted_label, probability = predict_image(image_path, weights_path)
    print(f"Predicted Label: {predicted_label}, Probability: {probability}")
