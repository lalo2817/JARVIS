"""Punto de entrada: python main.py"""
import os
import warnings

os.environ["GLOG_minloglevel"] = "2"          # silencia avisos de MediaPipe/TensorFlow
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
warnings.filterwarnings("ignore")

from ui.app import JarvisApp

if __name__ == "__main__":
    JarvisApp().run()
