#!/usr/bin/env python3
import sys
import subprocess
import pip
import tempfile
import queue

#On installe les dépendances non-standards si ce n'est pas fait puis on les importe
bibliotheques=['numpy','soundfile as sf','sounddevice as sd', 'cv2']
importer = ['import '] * len(bibliotheques)
final=[a+str(b) for a,b in zip(importer,bibliotheques)]

for i in final:
	try:
		exec(i)
	except ImportError:
		subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python" if i.split(" ")[1]=="cv2" else i.split(" ")[1]])
		exec(i)
 
 
#queue (FIFO) pour l'audio
q = queue.Queue()


#On ajoute l'audio à la queue si pas d'erreur
def callback(indata, frames, temps, erreur):
	if erreur:
		print(erreur, file=sys.stderr)
	q.put(indata.copy())
	
	
#Boucle principale, tourne à l'infini
def boucle():
	while(1):
		print("_" * 50 + "\n1) Enregistrement audio\n2) Allumer la webcam\n3) Quitter\n");
		entree=input("Le numéro de votre option:")
		try:
			int(entree)
		except ValueError:
			print("Option inexistante\n")
			boucle()

		if(int(entree)==1):
			micro()
		elif(int(entree)==2):
			webcam()
		elif(int(entree)==3):
			exit(0)
		else:
			print("Option inexistante\n")
			boucle()

#Enregistrement, sans limite de durée grâce au callback, s'arrête grâce à Ctrl+C
def micro():
	try:
		info = sd.query_devices(None, 'input')
		freq = int(info['default_samplerate'])
		fichier = tempfile.mktemp(prefix='sortie_',suffix='.wav', dir='')
				
		with sf.SoundFile(fichier, mode='x',  channels=1, samplerate=freq) as file:
			with sd.InputStream(channels=1, callback=callback):
				print('Ctrl+C pour arrêter l\'enregistrement')
				while True:
					file.write(q.get())

	except KeyboardInterrupt:
		print('\nEnregistré sous: ' + repr(fichier) + '\n')
		boucle()
	except Exception as e:
		exit(str(e))


#Allume la webcam, jusqu'à ce que la fenêtre se ferme
def webcam():
	cv2.namedWindow("Video")
	vc = cv2.VideoCapture(0)

	if vc.isOpened():
		rval, frame = vc.read()
	else:
		rval = False

	while True:
		cv2.imshow('webcam',frame)
		rval, frame = vc.read()
		k = cv2.waitKey(20)      
		if cv2.getWindowProperty('webcam',cv2.WND_PROP_VISIBLE) < 1:        
			break 
	vc.release()       
	cv2.destroyAllWindows()

#On appelle la boucle principale
boucle()
