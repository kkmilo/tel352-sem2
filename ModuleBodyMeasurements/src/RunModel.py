""" Evaluates a trained model using placeholders. """

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tensorflow as tf
tf.compat.v1.disable_eager_execution()
import numpy as np
from os.path import exists

from .tf_smpl import projection as proj_util
from .tf_smpl.batch_smpl import SMPL
from .models import get_encoder_fn_separate

class RunModel(object):
    def __init__(self, sess=None):
        """
        Args:
          config
        """
#        self.config = config

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.load_path = os.path.join(BASE_DIR, '..', 'models', 'model.ckpt-667589')
        self.smpl_model_path = os.path.join(BASE_DIR, '..', 'models', 'neutral_smpl_with_cocoplus_reg.pkl')

        #self.load_path = 'models/model.ckpt-667589'#config.load_path

        
        
        # Config + path
#        if not config.load_path:
#            raise Exception(
#                "[!] You need to specify `load_path` to load a pretrained model"
#            )
#        if not exists(config.load_path + '.index'):
#            print('%s doesnt exist..' % config.load_path)
#            import ipdb
#            ipdb.set_trace()

        # Data
        self.batch_size = 1#config.batch_size
        self.img_size = 224#config.img_size
 

        self.data_format = 'NHMC'
        #self.smpl_model_path = 'models/neutral_smpl_with_cocoplus_reg.pkl'#config.smpl_model_path
        
        input_size = (self.batch_size, self.img_size, self.img_size, 3)
        self.images_pl = tf.compat.v1.placeholder(tf.float32, shape=input_size)

        # Model Settings
        self.num_stage = 3#config.num_stage
        self.model_type = 'resnet_fc3_dropout'#config.model_type

        self.joint_type = 'cocoplus'#config.joint_type
 
        # Camera
        self.num_cam = 3
        self.proj_fn = proj_util.batch_orth_proj_idrot

        self.num_theta = 72        
        # Theta size: camera (3) + pose (24*3) + shape (10)
        self.total_params = self.num_cam + self.num_theta + 10

        self.smpl = SMPL(self.smpl_model_path, joint_type=self.joint_type)

        # self.theta0_pl = tf.placeholder_with_default(
        #     self.load_mean_param(), shape=[self.batch_size, self.total_params], name='theta0')
        # self.theta0_pl = tf.placeholder(tf.float32, shape=[None, self.total_params], name='theta0')

        self.build_test_model_ief()

        if sess is None:
            self.sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto())
        else:
            self.sess = sess
        
        # Load data.
        ###vars_in_ckpt = {v.name.split(':')[0]: v for v in tf.compat.v1.global_variables()
        ###                if v.name.split(':')[0] in tf.train.list_variables(self.load_path)}
        ###
        ###self.saver = tf.compat.v1.train.Saver(var_list=vars_in_ckpt)
###
        ###try:
        ###    self.saver.restore(self.sess, self.load_path)
        ###    print("Checkpoint restored partially.")
        ###except Exception as e:
        ###    print("Partial restore failed, continuing with random weights:", e)
        ###    self.sess.run(tf.compat.v1.global_variables_initializer())
        print("Initializing all variables (demo mode, checkpoint restore skipped)...")
        self.sess.run(tf.compat.v1.global_variables_initializer())

        self.prepare()        

    def build_test_model_ief(self):
        # Load mean value
        # use compat.get_variable style earlier (if you applied prior suggestion)
        self.mean_var = tf.compat.v1.get_variable(
            "mean_param",
            shape=[1, self.total_params],
            dtype=tf.float32,
            initializer=tf.zeros_initializer()
        )

        img_enc_fn, threed_enc_fn = get_encoder_fn_separate(self.model_type)
        # Extract image features.
        # NOTE: new encoder functions return (net, variables, model_instance)
        self.img_feat, self.E_var, self.img_encoder = img_enc_fn(
            self.images_pl,
            is_training=False,
            reuse=False)

        # Start loop
        self.all_verts = []
        self.all_kps = []
        self.all_cams = []
        self.all_Js = []
        self.final_thetas = []
        theta_prev = tf.tile(self.mean_var, [self.batch_size, 1])

        for i in np.arange(self.num_stage):
            print('Iteration %d' % i)
            # ---- Compute outputs
            state = tf.concat([self.img_feat, theta_prev], 1)

            if i == 0:
                # new threed_enc_fn returns (tensor, variables, model)
                delta_theta, three_vars, three_model = threed_enc_fn(
                    state,
                    num_output=self.total_params,
                    is_training=False,
                    reuse=False)
            else:
                delta_theta, three_vars, three_model = threed_enc_fn(
                    state,
                    num_output=self.total_params,
                    is_training=False,
                    reuse=True)

            # Compute new theta
            theta_here = theta_prev + delta_theta
            # cam = N x 3, pose N x self.num_theta, shape: N x 10
            cams = theta_here[:, :self.num_cam]
            poses = theta_here[:, self.num_cam:(self.num_cam + self.num_theta)]
            shapes = theta_here[:, (self.num_cam + self.num_theta):]

            verts, Js, _ = self.smpl(shapes, poses, get_skin=True)

            # Project to 2D!
            pred_kp = self.proj_fn(Js, cams, name='proj_2d_stage%d' % i)
            self.all_verts.append(verts)
            self.all_kps.append(pred_kp)
            self.all_cams.append(cams)
            self.all_Js.append(Js)
            # save each theta.
            self.final_thetas.append(theta_here)
            # Finally)update to end iteration.
            theta_prev = theta_here



    def prepare(self):
        print('Restoring checkpoint %s..' % self.load_path)
        ###self.saver.restore(self.sess, self.load_path)        
        self.mean_value = self.sess.run(self.mean_var)
            
    def predict(self, images, get_theta=False):
        """
        images: num_batch, img_size, img_size, 3
        Preprocessed to range [-1, 1]
        """
        results = self.predict_dict(images)
        if get_theta:
            return results['joints'], results['verts'], results['cams'], results[
                'joints3d'], results['theta']
        else:
            return results['joints'], results['verts'], results['cams'], results[
                'joints3d']

    def predict_dict(self, images):
        """
        images: num_batch, img_size, img_size, 3
        Preprocessed to range [-1, 1]
        Runs the model with images.
        """
        feed_dict = {
            self.images_pl: images,
            # self.theta0_pl: self.mean_var,
        }
        fetch_dict = {
            'joints': self.all_kps[-1],
            'verts': self.all_verts[-1],
            'cams': self.all_cams[-1],
            'joints3d': self.all_Js[-1],
            'theta': self.final_thetas[-1],
        }

        results = self.sess.run(fetch_dict, feed_dict)

        # Return joints in original image space.
        joints = results['joints']
        results['joints'] = ((joints + 1) * 0.5) * self.img_size

        return results
