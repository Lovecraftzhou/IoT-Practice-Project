from mqtt_pub import run
from main_picam import predict
from threading import Thread


if __name__ == '__main__':
    t1 = Thread(target=run, name="sensor")
    t2 = Thread(target=predict, name="predict")

    t1.start()
    t2.start()

