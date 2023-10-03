from google.cloud import storage
from PIL import Image
from io import BytesIO

def download_image_as_bytes(file_name:str)->bytes:
    # サービス アカウント キーのパスを指定
    key_path = "C:\\Users\\hukur\\Downloads\\kgavengers-cca4eb0d8780.json"
    client = storage.Client.from_service_account_json(key_path)

    # バケットの取得
    bucket = client.get_bucket('routinet_media')
        
    blob = bucket.blob(file_name)
    image_bytes = blob.download_as_bytes()
    return image_bytes

def upload_image_as_bytes(file_name:str, image_bytes:bytes):
    # サービス アカウント キーのパスを指定
    key_path = "C:\\Users\\hukur\\Downloads\\kgavengers-cca4eb0d8780.json"
    client = storage.Client.from_service_account_json(key_path)

    # バケットの取得
    bucket = client.get_bucket('routinet_media')
    
    blob = bucket.blob(file_name)    
    blob.upload_from_file(image_bytes)


""" byte = download_image_as_bytes('homework.png')
# バイトストリームから Pillow の Image オブジェクトを作成
image = Image.open(BytesIO(byte))
image.show()  # 画像を表示 """

with open("c:\\Users\\hukur\\OneDrive\\デスクトップ\\Connect\\React\\src\\common\\Assets\\homework.png", "rb") as my_file:
    upload_image_as_bytes("homework.png",my_file)