import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    # Private Key मधील newline character चा इश्यू फिक्स केला आहे
    private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC2S6gyyjHEFEDV\nkKyfOAWPFjDGdwCUmjz54RK5IhzfvgD08PKWmcNmHerT1q2xYimsUZqlCGV12qHp\nrgAccz7R++Ha5ob3BtCDK5tNh5nLOYN4BGjhaTfE+8bptzzjhuVGDeskOtlUWfjg\nN+q1iyHHFmHU3FtHD78Z6SVpLsr8AzlmYOThYlyu2MIu/hI3FB8RE5BYpStlcNgm\nSx3WlhtC5M4S3Sb9jcktegfDhmbabDZ+qEuznwhgCRTo6S+wIEMQGhO7grSqJBCu\n1Gr6h+dLkG7WY25hChQdVSIm5S3xCzCCZdAymldDaZqkz2//XIc4sWfoz3ipBdyE\nM3wRa+qlAgMBAAECggEAWNPz8U/KQTf3Qbm+C9WSC9+tw7+QFlkz9jUA2RpwxGvC\n7pgMNWtWpgdU+oWk3IcvNEsNVnaJbgyrkgEaB8L2bP7WVsK3KF73MruIcRZuz/LG\nB7DqZFBPfxqKmi8SKfJ8/Q5iMqTEatBur98/bNgPjQHwiPcZOT7IiXkspBzLh1G+\nVGctwDCzZYGZ5kv6Sf2GHqAXEJQoCh7PZ3ac03DUC1HWMsmYNvPWofXeoSLsbKtt\nx5A/RAxVZkPPmSEM3ZcgZXZ9CuxrFTB8NcY06ksvVVLXue8uBy+LSC7sbXNwi4B/\nhQP6uRtKPGtDJZqHbXGop8eTrB9p9yJs+UN8Ra/m/wKBgQDbH3E/HCy7UWGG21M3\nbTWNLHWmS9cPLyvvBYMAi27tochZDDUraT8ZT/Ym+kEO/BpEvvMIL05miW/bJd6E\nsU63Y6rso5Me4sb9z5eUXY5xWAmUYABp/4VU3gLJFzZSpOXnNwMFUUDD04N3uqli\nVj0Gz7Isd+gfP8vyBp2hApyzRwKBgQDU+ZHXoSPabqguQcOENSR54fhB9eqfpZUM\n7VkpN7ElDwFLG3HDhCVXd0kvakSa8OQrBKUbqCrlNh3KQhScwtkMj4guDW067pRM\nsDO43083G0hhj44X9US1TycFtzYEbyIHB94ikzjNVoPYv3bAEvR6C60Wo94JmWrx\nhwduj/jwswKBgCZi/rrYm7mBCz3NxGlMV3pQ1Jd6Z8WANQkdhRKeWqOEmQ2IhvQA\n7w3nJS803hra7VsnvHmtl+V8pDzXCIFkcm7MJhBoo4hgoA2sxVg3f5G5o4v7uXbY\nTapNbl1+FIUr4B6+U2gmENt9fWWHLM9OXkiIMCV8KAz5ZygSIqEnTP5XAoGAcD9d\nI4XVbLG3yDF3B74ujGKRwsoGr7/Ij/ikbnngzoRbDSfYzNBgEfpXwzrCD9t4lker\ncakveoEMMGalkH2NgfZAMu12rYHC/aw8hmqDyKqDeo/7txrY7KpcCcInIS0lhQkb\nhaOMY4T+loVK5C7ZVV3EC1OwmeSXHdcqDpapAMsCgYEAmMr0zkkFaPLuaZLVrWjh\naoUthIxp2mtlmK/njBTkW5hPsfFT8IaoqSQlgYeBkZlBiNemJt2IefWUAt361i58\nMrSO9CNS85CeKbbP/QKTLL5ChSfUhLByhJrWws7hSJ9kEDwVHXm3ivvMk2KzrFDv\nIH0g7FUxqgnqQljE3A+JlaA=\n-----END PRIVATE KEY-----\n".replace("\\n", "\n")

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "mandal-expense-app",
        "private_key_id": "53efc99d6c26bb94c0dcb501f777d1208b58cfc1",
        "private_key": private_key,
        "client_email": "firebase-adminsdk-fbsvc@mandal-expense-app.iam.gserviceaccount.com",
        "client_id": "101848101403749659631",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40mandal-expense-app.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    })
    firebase_admin.initialize_app(cred)

db = firestore.client()
