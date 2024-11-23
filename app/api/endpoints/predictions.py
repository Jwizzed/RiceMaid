from typing import tuple

import numpy as np
import tensorflow as tf
from fastapi import APIRouter
from PIL import Image

from app.schemas.requests import ImagePredictionRequest
from app.schemas.responses import PredictionResponse

router = APIRouter(prefix="/predictions", tags=["predictions"])


def create_model(im_height=300, im_width=300, num_classes=3):
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
            tf.keras.layers.Dense(
                num_classes, activation="softmax", kernel_regularizer="l2"
            ),
        ]
    )

    return model


async def predict_image(
    image_path: str, weights_path: str, im_height: int = 300, im_width: int = 300
) -> tuple[str, float]:
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
    img = Image.open(image_path)
    img = img.resize((im_width, im_height))
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = tf.keras.applications.efficientnet.preprocess_input(img_array)

    # Make prediction
    predictions = model.predict(preprocessed_img)
    predicted_class = np.argmax(predictions[0])
    probability = float(predictions[0][predicted_class])  # Convert to Python float

    labels = ["BBCH11", "BBCH12", "BBCH13"]
    predicted_label = labels[predicted_class]

    return predicted_label, probability


@router.post(
    "/predict",
    response_model=PredictionResponse,
    description="Predict image class using the ML model",
)
async def predict_image_endpoint(
    prediction_request: ImagePredictionRequest,
) -> PredictionResponse:
    predicted_label, probability = await predict_image(
        image_path=prediction_request.image_path,
        weights_path=prediction_request.weights_path,
        im_height=prediction_request.im_height,
        im_width=prediction_request.im_width,
    )

    return PredictionResponse(predicted_label=predicted_label, probability=probability)
