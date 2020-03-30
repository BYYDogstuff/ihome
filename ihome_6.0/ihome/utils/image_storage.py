# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_data, etag
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
access_key = 'hnF6qcBRhaElC8HiDNMfacT-vPKenfhHUIOrUBJd'
secret_key = '-9W5PGrbg9YRnnp7R9aV-my6wnGqi1o0RV7Rt3f2'

def storage(file_data):
    """
    上传文件到七牛
    :param file_data:
    :return:
    """
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'ihome-byy'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, file_data)

    if info.status_code == 200:
        # 表示上传成功, 返回文件名
        return ret.get("key")
    else:
        # 上传失败
        raise Exception("上传七牛失败")


if __name__ == '__main__':
    with open("D:\图片\logo.png", "rb") as f:
        file_data = f.read()
        storage(file_data)
