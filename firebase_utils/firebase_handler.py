def store_data(data):
    db = connect_to_firebase()
    try:
        incident_number = data['incident']['incident_number']
        report_ref = db.collection(u'reports').document(incident_number)
        report_ref.set(data)
        print("data saved successfully")
    except Exception as e:
        print(e)
        print("error storing data in firestore")


def connect_to_firebase():
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        try:
            firebase_admin.get_app()
            print('Firebase app is already initialized')
        except ValueError:
            print('Firebase app has not been initialized')

        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)

        db = firestore.client()

        if db:
            print("connected to firestore")
            return db
    except Exception as e:
        print(e)
        print("error connecting to firestore")
        return None
