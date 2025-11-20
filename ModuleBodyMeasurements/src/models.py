"""
TF2-compatible replacement for models.py
Uses tf.keras.layers / Models instead of tf_slim and tf.compat.v1.
Each encoder fn returns: (net_tensor, variables_list, model_instance)
"""

from __future__ import absolute_import, division, print_function

import tensorflow as tf
from tensorflow.keras import layers, Model, Sequential
from tensorflow.keras.initializers import VarianceScaling

# ---------- Encoder: ResNet50V2 backbone ----------
def Encoder_resnet(x, is_training=True, weight_decay=0.001, reuse=False):
    """
    ResNetV2-50 encoder. Accepts an input tensor `x` and returns:
      net, variables, model
    where `net` is a 2D feature vector (batch, features).
    """
    # Build a small wrapper model around Keras ResNet50V2
    # We expect x to be a 4D tensor: [B, H, W, C]
    backbone = tf.keras.applications.ResNet50V2(
        include_top=False, weights=None, pooling='avg'
    )

    # Run the backbone on x
    net = backbone(x, training=is_training)  # (B, feature_dim)
    # Collect variables
    variables = backbone.trainable_variables
    return net, variables, backbone


# ---------- 3D regression head (fc3 + dropout) ----------
def Encoder_fc3_dropout(x, num_output=85, is_training=True, reuse=False, name="3D_module"):
    """
    Fully-connected 3D head as Keras Sequential module.
    Returns: output_tensor, variables_list, model
    """
    small_xavier = VarianceScaling(
        scale=0.01,
        mode="fan_avg",
        distribution="uniform"
    )

    # Define a small Sequential model for the head
    head = Sequential(name=name)
    head.add(layers.Dense(1024, activation='relu', name='fc1'))
    # dropout rate is 0.5; use training flag when calling
    head.add(layers.Dropout(0.5, name='dropout1'))
    head.add(layers.Dense(1024, activation='relu', name='fc2'))
    head.add(layers.Dropout(0.5, name='dropout2'))
    head.add(layers.Dense(num_output, activation=None, kernel_initializer=small_xavier, name='fc3'))

    out = head(x, training=is_training)
    variables = head.trainable_variables
    return out, variables, head


# ---------- Factory to get encoder functions ----------
def get_encoder_fn_separate(model_type):
    """
    Returns (image_encoder_fn, threed_head_fn)
    Each function has signature: (x, is_training, **kwargs) -> (tensor, variables, model)
    """
    encoder_fn = None
    threed_fn = None

    if 'resnet' in model_type:
        encoder_fn = Encoder_resnet
    else:
        raise ValueError(f"Unknown encoder type: {model_type}")

    if 'fc3_dropout' in model_type:
        threed_fn = Encoder_fc3_dropout
    else:
        raise ValueError(f"Unknown 3D head for: {model_type}")

    return encoder_fn, threed_fn


# ---------- Discriminator (converted to TF2/Keras) ----------
def Discriminator_separable_rotations(weight_decay=0.001):
    """
    Returns (model_instance, variables_list)
    Later you call it: model([poses, shapes], training=True)
    """
    poses_in = layers.Input(shape=(23, None, None, ), name='poses_in')
    shapes_in = layers.Input(shape=(shapes_dim,), name='shapes_in')  
    # you need to define shapes_dim = shapes.shape[-1]

    # Conv stack
    p = layers.Conv2D(32, (1, 1), padding='same', activation='relu', name='D_conv1')(poses_in)
    p = layers.Conv2D(32, (1, 1), padding='same', activation='relu', name='D_conv2')(p)

    # Per-joint predictions
    p_flat = layers.TimeDistributed(layers.Flatten(), name="p_flat")(p)
    theta_raw = layers.TimeDistributed(layers.Dense(1), name="pose_out_td")(p_flat)
    theta_out_all = layers.Lambda(lambda x: tf.squeeze(x, -1), name='theta_out_squeeze')(theta_raw)

    # Shape branch
    s = layers.Dense(10, activation='relu', name='shape_fc1')(shapes_in)
    s = layers.Dense(5, activation='relu', name='shape_fc2')(s)
    shape_out = layers.Dense(1, name='shape_final')(s)

    # Global joint branch
    poses_all = layers.Flatten(name='vectorize')(p)
    poses_all = layers.Dense(1024, activation='relu', name='D_alljoints_fc1')(poses_all)
    poses_all = layers.Dense(1024, activation='relu', name='D_alljoints_fc2')(poses_all)
    poses_all_out = layers.Dense(1, name='D_alljoints_out')(poses_all)

    out = layers.Concatenate(axis=1, name='D_concat')([
        theta_out_all, poses_all_out, shape_out
    ])

    model = Model(inputs=[poses_in, shapes_in], outputs=out, name='Discriminator_sep_rot')
    variables = model.trainable_variables
    return model, variables

