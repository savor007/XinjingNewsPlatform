from flask import current_app
from qiniu import Auth, put_data


ACESS_KEY="y3xgn1BSoI1CQVMGla64Ko-cg9qNqYBSHbZP4Dho"
SECRET_KEY="fSvypAozMBeBWDO3hHYHg3b8tdzHz0BQ30e3MQJs"
STORAGE_NAME="parttimedevelopment"

def StorageFile2RemoteServer(data):
    if not data:
        return None
    try:
        # 构建鉴权对象
        q = Auth(ACESS_KEY, SECRET_KEY)

        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(STORAGE_NAME)

        # 上传文件
        ret, info = put_data(token, None, data)

    except Exception as e:
        current_app.logger.error(e)
        raise e

    if info and info.status_code != 200:
        raise Exception("上传文件到七牛失败")

        # 返回七牛中保存的图片名，这个图片名也是访问七牛获取图片的路径
    return ret["key"]


if __name__ == '__main__':
    file_name = input("输入上传的文件")
    with open(file_name, "rb") as f:
        StorageFile2RemoteServer(f.read())