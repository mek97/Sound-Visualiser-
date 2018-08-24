from __future__ import print_function
import struct
import wave
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pygame,time
from math import pi
import numpy as np
import csv
import json
import requests

fname = 'TY'

def gettime(line):
  return int(line[1:3])*60 + float(line[4:9])

url = 'https://southeastasia.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment'

lyrics = []
with open(fname+'.lrc', newline='\n') as inputfile:
  for row in csv.reader(inputfile):
    lyrics.append(row)
lyrics = lyrics[2:]

documents = []
for i in range(len(lyrics)):
  d = {}
  d['language'] = 'en'
  d['id'] = i+1
  d['text'] = lyrics[i][0][10:]
  documents.append(d)

j = {}
j['documents'] = documents
data = json.dumps(j)

print(len(lyrics))

headers = {'Content-Type' : 'application/json', 'Ocp-Apim-Subscription-Key' : '22835c7c256b423580c564f2524e4910', 'Accept' : 'application/json'}

response = requests.post(url, headers=headers, data=data)
results = response.json()['documents']

print(len(results))

sentiments = []
cur = 0
t = 0
for i in range(len(results)):
  now = gettime(lyrics[i][0])
  while(t < now):
    sentiments.append(cur)
    t += 0.04
  # Update cur
    cur = results[i]['score']


print(len(sentiments))

CONST_W = 800
CONST_H = 800
BLACK = (0,  0,  0)
WHITE = (255, 255, 255)
GOLD = (255,215,0)
RED =   (232, 62,  62)
ORANGE = (237 , 140, 37)
GREEN =   (152, 224, 89)
BLUE = (91 , 192, 229)
TITLE = ''
WIDTH = 1280
HEIGHT = 720
FPS = int(25)

nFFT = 512
BUF_SIZE = 4 * nFFT
SAMPLE_SIZE = 2
CHANNELS = 2
RATE = 44100

FREQ_LIST = []
def animate(i, line, wf, MAX_y):

  N = (int((i + 1) * RATE / FPS) - wf.tell()) / nFFT
  if not N:
    return
  N *= nFFT
  data = wf.readframes(N)
  # print('{:5.1f}% - V: {:5,d} - A: {:10,d} / {:10,d}'.format(
  #   100.0 * wf.tell() / wf.getnframes(), i, wf.tell(), wf.getnframes()
  # ))

  # Unpack data, LRLRLR...
  y = np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data)) / MAX_y
  y_L = y[::2]
  y_R = y[1::2]

  Y_L = np.fft.fft(y_L, nFFT)
  Y_R = np.fft.fft(y_R, nFFT)

  # Sewing FFT of two channels together, DC part uses right channel's
  Y = abs(np.hstack((Y_L[int(-nFFT / 2):-1], Y_R[:int(nFFT / 2)])))
  
  FREQ_LIST.append(Y)


def pol2cart(x,y,rho, phi):
  phi = (pi*phi/180)
  x1 = x + rho * np.cos(phi)
  y1 = y + rho * np.sin(phi)
  return(int(x1), int(y1))    

def r_2(n1,angle1):
  return pi*(angle1%(360/n1) - (360/(2*n1)))/180


def init(line):

  # This data is a clear frame for animation
  line.set_ydata(np.zeros(nFFT - 1))
  return line,


def main():

  # Frequency range
  MAX_y = 2.0 ** (SAMPLE_SIZE * 8 - 1)
  wf = wave.open(fname+'.wav', 'rb')
  assert wf.getnchannels() == CHANNELS
  assert wf.getsampwidth() == SAMPLE_SIZE
  assert wf.getframerate() == RATE
  frames = wf.getnframes()

  for i in range(0,int((frames/RATE)*FPS) ):
    N = (int((i + 1) * RATE / FPS) - wf.tell()) / nFFT
    if not N:
      return
    N *= nFFT
    data = wf.readframes(N)
    # print('{:5.1f}% - V: {:5,d} - A: {:10,d} / {:10,d}'.format(
    #   100.0 * wf.tell() / wf.getnframes(), i, wf.tell(), wf.getnframes()
    # ))

    # Unpack data, LRLRLR...
    y = np.array(struct.unpack("%dh" % (len(data) / SAMPLE_SIZE), data)) / MAX_y
    y_L = y[::2]
    y_R = y[1::2]

    Y_L = np.fft.fft(y_L, nFFT)
    Y_R = np.fft.fft(y_R, nFFT)

    # Sewing FFT of two channels together, DC part uses right channel's
    Y = abs(np.hstack((Y_L[int(-nFFT / 2):-1], Y_R[:int(nFFT / 2)])))
    
    FREQ_LIST.append(Y)

  wf.close()

  avgfreq = []

  for i in range(0,-1+len(FREQ_LIST)):
    x = []
    for j in range(0,-1+len(FREQ_LIST[i])):
      x.append((FREQ_LIST[i][j]-FREQ_LIST[i][j+1])**2)
    avgfreq.append(np.sum(x)/len(x))


  print(len(FREQ_LIST))



  pygame.init()
  size = [CONST_W, CONST_H]
  screen = pygame.display.set_mode(size) 
  pygame.display.set_caption(fname)
  clock = pygame.time.Clock()

  def visual(t,angle,angle_e,num_dot,dest,val):
    t = t - 90
    tick = 60
    st = []
    done = False
    while not done:
      if angle>=angle_e:
        done = True
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          done=True
      clock.tick(tick)
      screen.fill(C1)
      angle += val
      for i in range(3,num_dot+1):    
        st.append(pol2cart(CONST_W/2,CONST_H/2,dest/(np.cos(r_2(i,angle*(num_dot+1-i)-180/i))*np.tan(pi/i)),angle*(num_dot+1-i)+t))
      st.append((400,400))
      pygame.draw.polygon(screen,C2,st,2)
      pygame.display.flip()
      st.clear()


  print(sentiments)
  print(len(sentiments))
  print(len(FREQ_LIST))

  pygame.mixer.init()
  pygame.mixer.music.load(fname+'.wav')
  pygame.mixer.music.play()

  start_time = time.time()
  j=0
  
  for i in range(0,(len(FREQ_LIST)-1),25):

    C1 = BLACK
    C2 = GOLD

    k = 1+avgfreq[i]
    if i >= len(sentiments):
      visual(0,j,j+k,100+int(10*abs(sentiments[i%len(sentiments)])),10+int(1/(0.0001+np.amax(FREQ_LIST[i]))),k/60)
    else:
      visual(0,j,j+k,100+int(10*abs(sentiments[i])),10+int(1/(0.0001+np.amax(FREQ_LIST[i]))),k/60)
    j+=k
  print("--- %s seconds ---" % (time.time() - start_time))

  time.sleep(7)
  pygame.quit()


if __name__ == '__main__':
  main()
