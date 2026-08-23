import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    # Key मधील newline format फिक्स केला आहे
    raw_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDJiGUeITyRNw+Q\n9iHTM2uO1E1ym+O8kU2C2LKuuOjWqK+ZwfONgFo7OWd5lqV1sSgwnM/bw31SXi4f\nML4Kd2keSbyog1flALgrdfdi7O2PPX+3GMmtB/D4k8ZI1NfwaKbxsgBHAG5euyJN\nduG0HMiIn2A+6hkmii9oTQhYyDcadYC7+9FY/hCMV5QmuhneJv5Tb72MxKQT9c9u\nQBP0H8x2WOsWgy5iXXLAQvUoGlRyeYz/4DY6W8+tYbaxDG2gtWXPMXls4EhKmLdn\nCZipEMkR7fqoaAsDZRhlpDweOE6iC0KgkiFwQhWXxA+/gGEW0l0mrJAq54H7yDp3\nQpAAx5sVAgMBAAECggEAMSnEXSbHgzdW5Uqd8stK9FNnN0u/MSuTKJXbdRMnveH1\nwIEXfI/wsxzsWLV+1KisgLtoW5ijdFoET1iRK7V4n8pmKwerg/J6eyOyf2AEDdr3\nUn/KBxt2VfWau/6sVPn6q+B7/9Yjlpl5I0OaiNkytF2I2aA7FXNFYGDWZe4lvx63\nJ9LHpufxsJDKMnsKmMEBAo91kd1mIICLsok5k5M/WAtZ+Q+iRt1mpfprLuOlz0sA\ndGAh9O7FUfj1LlCqVO9tLtV/pOfAdlh4EDLXQh3Wr4ZLUvUixwEau+QtrW3Wp3WW\noyTVR3aXd8jF6KKPQdnWCucxOnpf07lS/1gWZTcXkQKBgQDsvNqhWg/LTH2MD/3U\ngnBB7ZViXzN7v7oNp4n7cCAdxq7KY7bzDfeY0ttIJDiaGxOIDisn1lTecyQlblC8\ni8vD9AdRhfgXyMduJUWn01YeEwe3oR4wQgOEs1/zypggdAnyWV0NwV7OSNh+EpHG\nbS+aN41KpL2KyYLfvnqbyIwSqQKBgQDZ7jzLHz4RO416xion0YY0rsxmMH1j5awb\nAztZniBAy7D7FiEyXNmAXQLXrPHNIAGZ1JhZNUhv+ofAPKzGEo39ornFvSPYoP63\nEWi+APxEMIfSjXU8lOJgtF+v1G4ZlTW6nxvFNYfzyf0NNqf5ha2eoT/jD3g0suet\netG95n80jQKBgGuQD0I6mmyDj5Og/HKe5YR+/13X5Zt3bIChu+bbdiwxRt+8WLas\nhPAR9gIcOv+CB+jMjz0lfCAqbqT3L4XLesTIzr5ywVuFJV/dXX24XyuA+AOuF/pT\nNCgKHDG3vlEYiCBuDAKg9oOBw6PcqhFfML7AONlOarRxhJ5GfIzlnQcpAoGBAIgZ\n+guc4mVevNfdJHyjpN4IAI0dYWHfEOH53bn1QA1XaJsW0fqi9A7vh5PsZUKG55kL\npW2pEikk3FzZR8mX0ueBFeYBXn6u5QStsa1f7iwj5t8/CuWf0dU1MMEduPjvL5Py\nRCSgbtx43DnBVZxGuQxlhgGnKpo21OuJ1a10YyMNAoGAPnBSu1SRbNzoB31Eczxo\nD3N0KnELB36aCDGaOchNiKV4R7khUcL/OkwLqKfW0jrHfUllGVLIDNpcMOQQo79A\nNZ4GPmCUwFmruE2ulk5j2Vgqw2q3S9ZdCyAjUSAAiHEHPZGQ5eq/rjUc2hgX0qia\nP04fbVsPDx7S1k58zxGkPyU=\n-----END PRIVATE KEY-----\n"

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "mandal-expense-app",
        "private_key_id": "4cc162c3984ac144de1109d2c7926449bbe04f5f",
        "private_key": raw_key.replace("\\n", "\n"),
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
