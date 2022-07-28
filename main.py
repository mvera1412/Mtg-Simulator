import ast
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import numpy as np
from prettytable import PrettyTable
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def save_dict(dict):
  f = open("dict","w")
  f.write( str(dict) )
  f.close()

def load_dict():
  with open('dict') as f:
    data = f.read()
  return ast.literal_eval(data)
  
def card2image(card):
  dictionary = load_dict()
  card=card.replace("\'","")
  try:
    numero = dictionary[card]
    arr = os.listdir('./images/')
    if not(numero + '.jpg' in arr):
      imagen = 'https://gatherer.wizards.com/Handlers/Image.ashx?multiverseid='+ numero +'&type=card'
      img_data = requests.get(imagen,verify = False).content
      with open('./images/' + numero + '.jpg', 'wb') as handler:
        handler.write(img_data)
    return numero
  except:
    name = ''
    for word in card.split():
      name += '+['
      name += word
      name += ']'
    web = 'https://gatherer.wizards.com/Pages/Search/Default.aspx?name=' + name
    response = requests.get(web,verify = False)
    texto_web = response.text
    wh = texto_web.find('multiverseid')
    texto_web = texto_web[wh+13:]
    wh = texto_web.find('"')
    numero = texto_web[:wh]
    if numero.isnumeric():
      arr = os.listdir()
      dictionary[card] = numero
      save_dict(dictionary)   
      if numero + '.jpg' in arr:
        return numero
      else:
        imagen = 'https://gatherer.wizards.com/Handlers/Image.ashx?multiverseid='+ numero +'&type=card'
        img_data = requests.get(imagen,verify = False).content
        with open('./images/' + numero + '.jpg', 'wb') as handler:
          handler.write(img_data)
        return numero
    else:
      return None
      
class Match:
  deck = []
  hand = []
  play = []
  graveyard = []
  file_name = ''
  text = False

  def action(self,moving,idx=0):
    print(moving)
    if moving == 'restart':
      self = restart(self.file_name)  
    elif moving == 'draw':
      change(self.deck,self.hand,0)
    elif moving == 'play':
      change(self.hand,self.play,idx)
    elif moving == 'discard':
      change(self.play,self.graveyard,idx)
    elif moving == 'mulligan':
      change(self.hand,self.deck,idx)
    else:
      print('No te equivoques')
    return self


  def show(self):
    os.system('clear') # Local
    if self.text:
      diff = len(self.hand)-len(self.play)
      aux_hand = self.hand
      aux_play = self.play
      m = max((len(self.hand),len(self.play)))
      idxs = list(range(m))
      if diff>0:
        for _ in range(diff):
          aux_play = aux_play + [" "]
      elif diff<0:
        for _ in range(-diff):
          aux_hand = aux_hand + [" "]
      l = [[idxs[k],aux_hand[k],aux_play[k]] for k in range(m)]
      table = PrettyTable(['Idx', 'Hand', 'Play'])
      for rec in l:
        table.add_row(rec)
      print(table)
    else:
      nhand=len(self.hand)
      nplay=len(self.play)
      maximo = max(nhand,nplay)
      fig, axs = plt.subplots(2,maximo+1,figsize=(15, 6))
      if maximo > 0:
          axs[1,0].text(0.3, 0.5, 'Hand')
          axs[1,0].axis('off')
          for idx, card in enumerate(self.hand):
            num = card2image(card)
            if not num:  
              raise ValueError("No encuentro {}".format(card))
            v = mpimg.imread('./images/' + num + '.jpg')
            axs[1,idx+1].imshow(v)
            axs[1,idx+1].axis('off')
            axs[1,idx+1].set_title(str(idx),y=-0.5)
          axs[0,0].text(0.3, 0.5, 'Play')
          axs[0,0].axis('off')
          for idx, card in enumerate(self.play):
            num = card2image(card)
            v = mpimg.imread('./images/' + num + '.jpg')
            axs[0,idx+1].imshow(v)
            axs[0,idx+1].axis('off')
          if nhand>nplay:
            for idx in range(nhand-nplay):
              axs[0,nplay+idx+1].axis('off')
          else:
            for idx in range(nplay-nhand):
              axs[1,nhand+idx+1].axis('off') 
              axs[1,nhand+idx+1].set_title(str(nhand+idx),y=-0.5)
      else:
          axs[1].text(0.3, 0.5, 'Hand')
          axs[1].axis('off')
          axs[0].text(0.3, 0.5, 'Play')
          axs[0].axis('off')
      plt.show()

def shuffle(deck):
  shuffled = np.random.permutation(len(deck))
  return [deck[i] for i in shuffled]

def change(set1,set2,idx):
  set2.append(set1[idx])
  set1.pop(idx) 


def restart(file_name):
  f = open('./decks/' + file_name, "r")
  linea = f.readline()
  num=[]
  nom=[] 
  while (linea!="\n") and linea:
    v=linea.split(" ", 1)
    num.append(int(v[0]))
    nom.append(v[1].rstrip())
    linea = f.readline()
  deck=[[nom[k]] * num[k] for k in range(len(num))]
  deck = [x for xs in deck for x in xs]
  deck = shuffle(deck)
  hand = []
  for _ in range(7):
    change(deck,hand,0)
  match = Match()
  match.deck = deck
  match.hand = hand
  match.play = []
  match.graveyard = []
  match.file_name = file_name
  return match
  
def keep_mulligan():
  while 1:
    x = input('(K)eep or (M)ulligan? ')
    if x=='k':
      mulligan = False
      break
    elif x=='m':
      mulligan = True
      break
  return mulligan    

def return_card(match):
  while 1:
    x = input('Return a card ')
    if(x >= '0' and x <= str(len(match.hand))):
      idx = int(x)
      match = match.action('mulligan',idx)
      break
  return match 

def start(file_name,texto):
    n_mul = 0
    match = Match()
    match.file_name = file_name
    match = match.action('restart')
    match.text = texto
    match.show()
    mulligan = keep_mulligan()  
    while mulligan:
      match = match.action('restart')
      match.text = texto
      n_mul +=1
      match.show()
      if n_mul>6:
          mulligan = False
      else:
          mulligan = keep_mulligan()
    while n_mul+len(match.hand)>7:
      match = return_card(match)
      match.show()
    return match     
    
    
if __name__ == '__main__':
	file_loaded = False
	quit = False
	while not quit:
	  while not file_loaded:
	    arr = os.listdir('./decks/')   
	    arr2 = []
	    for k in range(len(arr)):
	      s = arr[k]
	      if s[-4:]=='.txt':
	        arr2.append(arr[k])
	    m = len(arr2)
	    l = [[k,arr2[k]] for k in range(m)]
	    table = PrettyTable(['Idx', 'File name'])
	    for rec in l:
	      table.add_row(rec)
	    os.system('clear') # Local
	    print(table)
	    x = input('Choose a file ')
	    if(x >= '0' and x < str(m)):
	      file_name = arr2[int(x)]
	      file_loaded = True 
	  x = input('(I)mages or (T)ext? ')
	  texto = (x[0]=='t')  
	  match = start(file_name,texto)
	  playing = True
	  while playing:
	    x = input('(D)raw - (P)lay - (G)raveyard - (R)estart - (C)hange deck - (Q)uit ')
	    if (x!='') and (x[0]=='d'):
	      match = match.action('draw',match)
	      match.show()
	    elif (x!='') and (x[0]=='p'):
	      y = x[1:]
	      if(y >= '0' and y < str(len(match.hand))):
	        match = match.action('play',int(y))
	        match.show()
	      else:
	        print('Which?')
	    elif (x!='') and (x[0]=='g'):
	      y = x[1:]
	      if(y >= '0' and y < str(len(match.play))):
	        match = match.action('discard',int(y))
	        match.show()
	      else:
	        print('Which?')
	    elif (x!='') and (x[0]=='r'):
	      playing = False
	    elif (x!='') and (x[0]=='q'):
	      playing = False
	      quit=True
	    elif (x!='') and (x[0]=='c'):
	      file_loaded = False
	      playing = False
    
         
