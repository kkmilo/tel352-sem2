"""
Defines networks.

@Encoder_resnet
@Encoder_resnet_v1_101
@Encoder_fc3_dropout

@Discriminator_separable_rotations

Helper:
@get_encoder_fn_separate
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import tf_slim as slim

from tensorflow.keras.initializers import VarianceScaling

def Encoder_resnet(x, is_training=True, weight_decay=0.001, reuse=False):
    """
    Resnet v2-50
    """
    from tf_slim.nets import resnet_v2
    with tf.name_scope("Encoder_resnet"):
        with slim.arg_scope(
                resnet_v2.resnet_arg_scope(weight_decay=weight_decay)):
            net, end_points = resnet_v2.resnet_v2_50(
                x,
                num_classes=None,
                is_training=is_training,
                reuse=reuse,
                scope='resnet_v2_50')
            net = tf.squeeze(net, axis=[1, 2])

    # TF2-safe replacement
    variables = tf.compat.v1.get_collection(
        tf.compat.v1.GraphKeys.GLOBAL_VARIABLES,
        scope='resnet_v2_50'
    )

    return net, variables


def Encoder_fc3_dropout(x,
                        num_output=85,
                        is_training=True,
                        reuse=False,
                        name="3D_module"):
    """
    3D inference module.
    """
    if reuse:
        print('Reuse is on!')
    with tf.variable_scope(name, reuse=reuse) as scope:
        net = slim.fully_connected(x, 1024, scope='fc1')
        net = slim.dropout(net, 0.5, is_training=is_training, scope='dropout1')
        net = slim.fully_connected(net, 1024, scope='fc2')
        net = slim.dropout(net, 0.5, is_training=is_training, scope='dropout2')
        small_xavier = VarianceScaling(
            scale=0.01,
            mode="fan_avg",
            distribution="uniform"
        )
        net = slim.fully_connected(
            net,
            num_output,
            activation_fn=None,
            weights_initializer=small_xavier,
            scope='fc3')

    # TF2-safe replacement
    variables = tf.compat.v1.get_collection(
        tf.compat.v1.GraphKeys.GLOBAL_VARIABLES,
        scope=scope.name
    )

    return net, variables


def get_encoder_fn_separate(model_type):
    """
    Retrieves diff encoder fn for image and 3D
    """
    encoder_fn = None
    threed_fn = None
    if 'resnet' in model_type:
        encoder_fn = Encoder_resnet
    else:
        print('Unknown encoder %s!' % model_type)
        exit(1)

    if 'fc3_dropout' in model_type:
        threed_fn = Encoder_fc3_dropout

    if encoder_fn is None or threed_fn is None:
        print('Dont know what encoder to use for %s' % model_type)
        import ipdb
        ipdb.set_trace()

    return encoder_fn, threed_fn


def Discriminator_separable_rotations(
        poses,
        shapes,
        weight_decay,
):
    """
    Separable rotation discriminator.
    """
    data_format = "NHWC"
    with tf.name_scope("Discriminator_sep_rotations"):
        with tf.variable_scope("D") as scope:
            with slim.arg_scope(
                [slim.conv2d, slim.fully_connected],
                    weights_regularizer=slim.l2_regularizer(weight_decay)):
                with slim.arg_scope([slim.conv2d], data_format=data_format):
                    poses = slim.conv2d(poses, 32, [1, 1], scope='D_conv1')
                    poses = slim.conv2d(poses, 32, [1, 1], scope='D_conv2')
                    theta_out = []
                    for i in range(0, 23):
                        theta_out.append(
                            slim.fully_connected(
                                poses[:, i, :, :],
                                1,
                                activation_fn=None,
                                scope="pose_out_j%d" % i))
                    theta_out_all = tf.squeeze(tf.stack(theta_out, axis=1))

                    shapes = slim.stack(
                        shapes,
                        slim.fully_connected, [10, 5],
                        scope="shape_fc1")
                    shape_out = slim.fully_connected(
                        shapes, 1, activation_fn=None, scope="shape_final")

                    nz_feat = 1024
                    poses_all = slim.flatten(poses, scope='vectorize')
                    poses_all = slim.fully_connected(
                        poses_all, nz_feat, scope="D_alljoints_fc1")
                    poses_all = slim.fully_connected(
                        poses_all, nz_feat, scope="D_alljoints_fc2")
                    poses_all_out = slim.fully_connected(
                        poses_all,
                        1,
                        activation_fn=None,
                        scope="D_alljoints_out")

                    out = tf.concat([theta_out_all,
                                     poses_all_out, shape_out], 1)

            # TF2-safe replacement
            variables = tf.compat.v1.get_collection(
                tf.compat.v1.GraphKeys.GLOBAL_VARIABLES,
                scope=scope.name
            )
            return out, variables
