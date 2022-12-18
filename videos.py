# 视频融合文件

import cv2 as cv

def frame_merge(ppt_frame, talk_frame):
    merge_width = 338
    merge_height = 250
    talk_frame = cv.resize(talk_frame, (merge_width, merge_height))

    # I want to put logo on top-left corner, So I create a ROI
    # 首先获取原始图像roi
    rows, cols, channels = talk_frame.shape
    roi = ppt_frame[720-merge_height:720, 0:cols]

    # 原始图像转化为灰度值
    # Now create a mask of logo and create its inverse mask also
    img2gray = cv.cvtColor(talk_frame, cv.COLOR_BGR2GRAY)

    # cv.imshow('img2gray', img2gray)
    # cv.waitKey(0)
    '''
    将一个灰色的图片，变成要么是白色要么就是黑色。（大于规定thresh值就是设置的最大值（常为255，也就是白色））
    '''
    # 将灰度值二值化，得到ROI区域掩模
    ret, mask = cv.threshold(img2gray, 245, 255, cv.THRESH_BINARY)

    # cv.imshow('mask', mask)
    # cv.waitKey(0)

    # ROI掩模区域反向掩模
    mask_inv = cv.bitwise_not(mask)

    # cv.imshow('mask_inv', mask_inv)
    # cv.waitKey(0)

    # 掩模显示背景
    # Now black-out the area of logo in ROI
    img1_bg = cv.bitwise_and(roi, roi, mask=mask)

    # cv.imshow('img1_bg', img1_bg)
    # cv.waitKey(0)

    # 掩模显示前景
    # Take only region of logo from logo image.
    img2_fg = cv.bitwise_and(talk_frame, talk_frame, mask=mask_inv)
    # cv.imshow('img2_fg', img2_fg)
    # cv.waitKey(0)

    # 前背景图像叠加
    # Put logo in ROI and modify the main image

    dst = cv.add(img1_bg, img2_fg)
    ppt_frame[720-merge_height:720, 0:cols] = dst

    # cv.imshow('res', ppt_frame)
    # cv.waitKey(0)
    # cv.destroyAllWindows()

    return ppt_frame


def video_merge(ppt_video, talk_video):
    cap_ppt = cv.VideoCapture(ppt_video)
    cap_talk = cv.VideoCapture(talk_video)

    merge_video = 'E:\\Code\\Software Engineer\\merge.mp4'
    # fourcc = cv.VideoWriter_fourcc(*'XVID')
    fourcc = cv.VideoWriter_fourcc('H', '2', '6', '4')
    video_writer = cv.VideoWriter(merge_video, fourcc, 20.0, (1280, 720))

    while (cap_talk.isOpened()):

        ret_talk, frame_talk = cap_talk.read()
        ret_ppt, frame_ppt = cap_ppt.read()

        if (ret_ppt == True):
            if(ret_talk == True):
                merge_frame = frame_merge(frame_ppt, frame_talk)
                video_writer.write(merge_frame)
            else:
                video_writer.write(frame_ppt)

        else:
            break

    video_writer.release()
    cap_ppt.release()
    cap_talk.release()

    cv.destroyAllWindows()

    return merge_video





