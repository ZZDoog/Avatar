import os

import gradio as gr
import numpy as np

from inference import convert_video
from model import MattingNetwork
import torch

os.environ['CUDA_VISIBLE_DEVICES'] = str(0)

model_matting = MattingNetwork('mobilenetv3').eval().cuda()
model_matting.load_state_dict(torch.load('rvm_mobilenetv3.pth'))


def avatar_pro(videos, powerpoint):

    convert_video(
        model_matting,  # 模型，可以加载到任何设备（cpu 或 cuda）
        input_source=videos,  # 视频文件，或图片序列文件夹
        output_type='video',  # 可选 "video"（视频）或 "png_sequence"（PNG 序列）
        output_composition='com.mp4',  # 若导出视频，提供文件路径。若导出 PNG 序列，提供文件夹路径
        output_alpha="pha.mp4",  # [可选项] 输出透明度预测
        output_foreground="fgr.mp4",  # [可选项] 输出前景预测
        output_video_mbps=4,  # 若导出视频，提供视频码率
        downsample_ratio=None,  # 下采样比，可根据具体视频调节，或 None 选择自动
        seq_chunk=6,  # 设置多帧并行计算
    )

    return 'com.mp4'


def avatar_lite(image, text, powerpoint):
    return 0


with gr.Blocks() as demo:

    gr.Markdown('''## Avatar: Easily Show Yourself  
        Please Chose User Model: **Avatar Pro** or **Avatar Lite**  
        In Avatar Program, You can easily generate a video with your own cartoon image for powerpoint presentation  
        In **Avatar Pro** mode, You need to upload a video and a powerpoint file  
        In **Avatar Lite** mode, You need to upload a selfie, a powerpoint and a presentation text''')

    with gr.Tab("Avatar Pro"):
        with gr.Row():
            video_input_pro = gr.Video(label="Please Upload Your Representation Video")
            ppt_input_pro = gr.File(label="Please Upload your Powerpoint File")
        video_output_pro = gr.Video(label="Here is your final Video")
        pro_button = gr.Button("Generate!")

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

