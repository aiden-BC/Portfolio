import numpy as np
import cv2
import matplotlib.pyplot as plt
import glob
import imutils
import warnings
warnings.filterwarnings('ignore')

def panorama(path, nombre_jpg):
    # Cargar las imágenes 'images/*
    image_paths = glob.glob(path+'.jpg') #lee ruta de archivos
    images = []

    for image in image_paths:
        img = cv2.imread(image, cv2.IMREAD_COLOR) #lee la imagen
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #pasa a RGB
        images.append(img_rgb) #añade a la lista
        
    # Inicializamos el objeto image stitcher y luego hacemos el image stitching
    print("[INFO] stitching images...")
    stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
    (status, stitched) = stitcher.stitch(images)

    # si el status es '0', OpenCV realizó con éxito el stitching
    if status != 0:
        print("[INFO] image stitching failed ({})".format(status))
        
    # crear un borde de 10px alrededor de la imagen
    print("[INFO] cropping...")
    stitched = cv2.copyMakeBorder(stitched, 10, 10, 10, 10, cv2.BORDER_CONSTANT, (0, 0, 0))

    # convertir la imagen a escala de grises y crear el umbral
    gray = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]
    
    # extrae los contornos de la imagen umbralizada
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # encuentra el contorno mas grande, que sera el de la imagen panoramica
    c = max(cnts, key=cv2.contourArea)

    # crea la mascara que contendra la caja delimitadora de la region de la imagen panoramica
    mask = np.zeros(thresh.shape, dtype="uint8")
    (x, y, w, h) = cv2.boundingRect(c)
    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    
    # crea 2 copias de la mascara
    minRect = mask.copy() # minimum rectangular region
    sub = mask.copy() # cuantos px debemos eliminar de minRect

    # bucle hasta que no hayan pixeles distintos de 0 en sub
    while cv2.countNonZero(sub) > 0:
        minRect = cv2.erode(minRect, None) # erosiona minRect
        sub = cv2.subtract(minRect, thresh) # resta minRect y thresh: saber si quedan px distintos de 0
    
    # encuentra contornos en la mascara rectangular minima
    cnts = cv2.findContours(minRect.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)

    # extrae las coordenadas (x, y) de la caja delimitadora
    (x, y, w, h) = cv2.boundingRect(c)

    # usa las coordenadas de la caja para extraer el área de interés de la imagen
    stitched = stitched[y:y + h, x:x + w]
    print("[INFO] saving...")

    # guarda la imagen 
    plt.imsave("panoramicas/"+nombre_jpg.replace(" ","_").lower()+".jpg", stitched);