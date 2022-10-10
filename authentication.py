import pyrebase

firebaseConfig = {
  'apiKey': "AIzaSyD-B7yqtSByylMaf3v7QMjHD8IYu-vl7W4",
  'authDomain': "celiakia.firebaseapp.com",
  'databaseURL': "https://celiakia.firebaseio.com",
  'projectId': "celiakia",
  'storageBucket': "celiakia.appspot.com",
  'messagingSenderId': "1009814857697",
  'appId': "1:1009814857697:web:b0ab52f46bc2c17df894a0",
  'measurementId': "G-GGGN2P426M"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

