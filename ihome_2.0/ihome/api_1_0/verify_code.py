from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants
from flask import current_app, jsonify, make_response, request
from ihome.utils.response_code import RET
from ihome.models import User
from ihome.libs.yuntongxun.sms import CCP
import random


@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """
    获取验证码图片
    :param image_code_id: 图片验证码编号
    :return: 如果出现异常，返回异常信息，否则，返回验证码图片
    """
    # 生成验证码图片
    # 名字，真是文本，图片数据
    name, text, image_code = captcha.generate_captcha()

    # 将编号以及验证码的真实值保存到redis（选择字符串）中，并设置有效期（自定义有效期为180秒，设置成了常量，在constants中）
    # redis_store.set('iamge_code_%s' % image_code_id, text)
    # redis_store.expire('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)
    # 将以上合并写
    try:
        redis_store.setex('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        # return jsonify(errno=RET.DBERR, errmsg="save image code failed")
        # 出现异常，返回json格式的提示
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    # 没有异常 返回验证码图片，并指定一下Content-Type(默认为test/html)类型为image,不改不认识图片
    resp = make_response(image_code)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp



# GET api/v1.0/sms_codes/<mobile>?image_code=xxx&image_code_id=xxx
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    # 获取参数
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')

    # 检验参数
    if not all([image_code, image_code_id]):
        # 参数不完整
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 逻辑处理
    # 从redis中取出验证码图片的真实值
    try:
        real_image_code = redis_store.get('image_code_%s' % image_code_id)
        print(real_image_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    # 判断真实值是否过期,redis中如果过期则返回None
    if real_image_code is None:
        return jsonify(errno=RET.NODATA, errmsg='验证码失效')

    # 删除redis中的图片验证码，防止用户使用同一个图片验证码验证多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        print(real_image_code.decode('utf-8').lower())
        print(image_code.lower())

    # 验证用户填写的验证码与redis中的真实值是否相等
    if real_image_code.decode('utf-8').lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmssg='图片验证码错误')

    # 判断对于这个手机号的操作，在60秒内有没有之前的记录，如果有，则认为用户操作频繁，不接受处理
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            # 表示在60秒内之前有过发送的记录
            return jsonify(errno=RET.REQERR, errmsg="请求过于频繁，请60秒后重试")

    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已注册')

    # 生成短信验证码 6 位
    # import random
    sms_code = "%06d" % random.randint(0, 999999)  # %06d  表示生成6位整数，不够的前边补0 ，如029541

    # 保存真实的短信验证码
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送给这个手机号的记录，防止用户在60s内再次出发发送短信的操作
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")

    # 发送短信
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")

    # 返回值
    if result == 0:
        # 发送成功
        return jsonify(errno=RET.OK, errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')








