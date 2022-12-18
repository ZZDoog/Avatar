import os

import gradio as gr
import time

from inference import convert_video
from model import MattingNetwork

import torch

import argparse

from powerpoint import cov_ppt
from videos import video_merge

from style_transfer import style_transfer




# cuda 环境配置
# os.environ['CUDA_VISIBLE_DEVICES'] = str(0)
model_matting = MattingNetwork('mobilenetv3').eval().cuda()
model_matting.load_state_dict(torch.load('rvm_mobilenetv3.pth'))


class TestOptions():
    def __init__(self):

        self.parser = argparse.ArgumentParser(description="Style Transfer")
        self.parser.add_argument("--content", type=str, default='./data/com.mp4',
                                 help="path of the content image/video")
        self.parser.add_argument("--style_id", type=int, default=26, help="the id of the style image")
        self.parser.add_argument("--style_degree", type=float, default=0.5, help="style degree for VToonify-D")
        self.parser.add_argument("--color_transfer", action="store_true", help="transfer the color of the style")
        self.parser.add_argument("--ckpt", type=str, default='./checkpoint/vtoonify_d_cartoon/vtoonify_s_d.pt',
                                 help="path of the saved model")
        self.parser.add_argument("--output_path", type=str, default='./output/', help="path of the output images")
        self.parser.add_argument("--scale_image", action="store_false",
                                 help="resize and crop the image to best fit the model")
        self.parser.add_argument("--style_encoder_path", type=str, default='./checkpoint/encoder.pt',
                                 help="path of the style encoder")
        self.parser.add_argument("--exstyle_path", type=str, default=None, help="path of the extrinsic style code")
        self.parser.add_argument("--faceparsing_path", type=str, default='./checkpoint/faceparsing.pth',
                                 help="path of the face parsing model")
        self.parser.add_argument("--video", action="store_false",
                                 help="if true, video stylization; if false, image stylization")
        self.parser.add_argument("--cpu", action="store_true", help="if true, only use cpu")
        self.parser.add_argument("--backbone", type=str, default='dualstylegan', help="dualstylegan | toonify")
        self.parser.add_argument("--padding", type=int, nargs=4, default=[200, 200, 190, 190],
                                 help="left, right, top, bottom paddings to the face center")
        self.parser.add_argument("--batch_size", type=int, default=1, help="batch size of frames when processing video")
        self.parser.add_argument("--parsing_map_path", type=str, default=None,
                                 help="path of the refined parsing map of the target video")

    def parse(self):
        self.opt = self.parser.parse_args()
        if self.opt.exstyle_path is None:
            self.opt.exstyle_path = os.path.join(os.path.dirname(self.opt.ckpt), 'exstyle_code.npy')
        args = vars(self.opt)
        print('Load options')
        for name, value in sorted(args.items()):
            print('%s: %s' % (str(name), str(value)))
        return self.opt


def avatar_pro(videos, powerpoint):

    ppt_path = powerpoint.name

    # the output path
    ppt_video_path = 'E:\\Code\\Software Engineer\\output\\ppt.mp4'
    com_video_path = 'E:\\Code\\Software Engineer\\output\\com.mp4'  # 视频去背景的视频输出路径，同时也是VToonify的视频输入路径

    # PPT to MP4
    print('Processing ppt file.......')
    cov_ppt(ppt_path, ppt_video_path)

    # Video Matting
    print('Processing video file........')
    convert_video(
        model_matting,  # 模型，可以加载到任何设备（cpu 或 cuda）
        input_source=videos,  # 视频文件，或图片序列文件夹
        output_type='video',  # 可选 "video"（视频）或 "png_sequence"（PNG 序列）
        output_composition=com_video_path,  # 若导出视频，提供文件路径。若导出 PNG 序列，提供文件夹路径
        output_video_mbps=4,  # 若导出视频，提供视频码率
        downsample_ratio=None,  # 下采样比，可根据具体视频调节，或 None 选择自动
        seq_chunk=6,  # 设置多帧并行计算
    )

    # Style Transfer
    parser = TestOptions()
    args = parser.parse()
    args.content = com_video_path
    style_transfer(args)
    time.sleep(1)

    # Merging two video
    print('Merging........')
    merge_video = video_merge(ppt_video_path, os.path.join(args.output_path, 'com_vtoonify_d.mp4'))



    # 输出格式是一个视频文件路径
    return merge_video


def avatar_lite(image, text, powerpoint):
    ppt_video = "E:\\Code\\Software Engineer\\output\\ppt.mp4"
    talk_video = "E:\\Code\\Avatar\\output\\com_vtoonify_d.mp4"
    merge_video = video_merge(ppt_video, talk_video)
    return merge_video


with gr.Blocks() as demo:

    gr.Markdown('''## Avatar: Easily Show Yourself  
        Please Chose User Model: **Avatar Pro** or **Avatar Lite**  
        In Avatar Program, You can easily generate a video with your own cartoon image for powerpoint presentation  
        In **Avatar Pro** mode, You need to upload a video and a powerpoint file  
        In **Avatar Lite** mode, You need to upload a selfie, a powerpoint and a presentation text''')

    # Avatar Pro 模式
    with gr.Tab("Avatar Pro"):
        with gr.Row():
            video_input_pro = gr.Video(label="Please Upload Your Representation Video")
            ppt_input_pro = gr.File(label="Please Upload your Powerpoint File")
        video_output_pro = gr.Video(label="Here is your final Video")
        pro_button = gr.Button("Generate!")

    # Avatar Lite 模式
    with gr.Tab("Avatar Lite"):
        text_input_lite = gr.Textbox(label="Please Enter Your Speech")
        with gr.Row():
            image_input_lite = gr.Image(label="Please Upload Your Photo")
            ppt_input_lite = gr.File(label="Please Upload your Powerpoint File")
        video_output_lite = gr.Video(label="Here is your final Video")
        lite_button = gr.Button("Generate!")

    inputs_pro = [video_input_pro, ppt_input_pro]
    inputs_lite = [image_input_lite, text_input_lite, ppt_input_lite]

    pro_button.click(avatar_pro, inputs=inputs_pro, outputs=video_output_pro)
    lite_button.click(avatar_lite, inputs=inputs_lite, outputs=video_output_lite)

demo.launch()

