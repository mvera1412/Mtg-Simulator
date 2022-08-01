import ast
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time
from copy import deepcopy
import pandas as pd    

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
  card=card.replace("/","")
  card=' '.join(card.split())
  try:
    numero = str(dictionary[card])
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
  def __init__(self):  
    self.deck = []
    self.hand = []
    self.play = []
    self.graveyard = []
    self.file_name = ''
    self.text = False
    self.previous_state = None

  def action(self,moving,idx=0):
    print(moving)
    if moving == 'restart':
      self.previous_state = None  
      self = restart(self.file_name)  
    elif moving == 'draw':
      self.previous_state = None   
      change(self.deck,self.hand,0)
    elif moving == 'play': 
      self.previous_state = deepcopy(self)  
      change(self.hand,self.play,idx)
    elif moving == 'discard':
      self.previous_state = deepcopy(self)
      change(self.play,self.graveyard,idx)
    elif moving == 'mulligan':
      self.previous_state = None  
      change(self.hand,self.deck,idx)
    elif moving == 'undo':
      if self.previous_state:
          self = deepcopy(self.previous_state)
      else:
          print('No se puede deshacer')
          time.sleep(0.5) 
    else:
      print('No te equivoques')
    return self


  def show(self, T=False):
    os.system('clear') # Local
    plt.close('all')
    if self.text:
      diff = len(self.hand)-len(self.play)
      aux_hand = self.hand
      aux_play = self.play
      m = max((len(self.hand),len(self.play)))
      if diff>0:
        for _ in range(diff):
          aux_play = aux_play + [" "]
      elif diff<0:
        for _ in range(-diff):
          aux_hand = aux_hand + [" "]
      l = [[aux_hand[k],aux_play[k]] for k in range(m)]
      render_mpl_table(l, ['Hand','Play'], col_width=3.5, suptitle = T+'\n Deck: '+str(len(self.deck))+', Graveyard: '+str(len(self.graveyard)))
    else:
      nhand=len(self.hand)
      nplay=len(self.play)
      maximo = max(nhand,nplay)
      fig, axs = plt.subplots(2,maximo+1,figsize=(15, 6))
      if maximo > 0:
          if T:
              fig.suptitle(T+'\n Deck: '+str(len(self.deck))+', Graveyard: '+str(len(self.graveyard)),color='red')
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
      plt.show(block=False)

def shuffle(deck):
  shuffled = np.random.permutation(len(deck))
  return [deck[i] for i in shuffled]

def change(set1,set2,idx):
  try:    
      set2.append(set1[idx])
      set1.pop(idx) 
  except:
      print('No se puede')


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
  n = len(deck)
  if n!=60:
      print(f'Your deck has {n} cards.') 
      _ = input ('Press any key to continue')
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
    time.sleep(1)  
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
    match.show('(K)eep or (M)ulligan?')
    mulligan = keep_mulligan()  
    while mulligan:
      match = match.action('restart')
      match.text = texto
      n_mul +=1
      match.show('(K)eep or (M)ulligan?')
      if n_mul>6:
          mulligan = False
      else:
          mulligan = keep_mulligan()
    while n_mul+len(match.hand)>7:
      match.show('Return a card')  
      match = return_card(match)
    return match     

def render_mpl_table(listado, titulos, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0, suptitle = False):
    newlist = deepcopy(listado)
    newlist.insert(0,titulos)
    data = pd.DataFrame(newlist)
    size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
    fig, ax = plt.subplots(figsize=size)
    if suptitle:
        fig.suptitle(suptitle,color='red')
    ax.axis('off')
    indexs = list(range(len(data)-1))
    indexs.insert(0,'')
    mpl_table = ax.table(cellText=data.values, bbox=bbox, rowLabels=indexs)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)
    for k, cell in mpl_table._cells.items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    plt.show(block=False) 

    
def elegir_archivo(listado):
    os.system('clear') # Local
    plt.close('all')
    render_mpl_table(listado, 'Choose a file', col_width=2.5)
    plt.show(block=False)
    x = input('Choose a file ')
    return x

def elegir_interfaz(filename):
    plt.close('all')
    plt.figure(figsize=[8.5,1.2])
    plt.text(0.0, 0.0,'(I)mages or (T)ext? ', fontsize = 50)
    plt.axis('off')
    plt.show(block=False)
    x = input('(I)mages or (T)ext? ')
    return (x[0]=='t') 

def menu_principal():
    x = input('(D)raw - (P)lay - (G)raveyard - (U)ndo - (R)estart - (C)hange deck - (Q)uit ')
    return x

if __name__ == '__main__':
	file_loaded = False
	quit = False
	plt.ion()
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
	    x = elegir_archivo(arr2) #l
	    if(x >= '0' and x < str(m)):
	      file_name = arr2[int(x)]
	      file_loaded = True 
	  texto = elegir_interfaz(file_name) 
	  match = start(file_name,texto)
	  playing = True
	  while playing:
	    match.show('(D)raw - (P)lay - (G)raveyard - (U)ndo - (R)estart - (C)hange deck - (Q)uit')
	    x = menu_principal()
	    if (x!='') and (x[0]=='d'):
	      match = match.action('draw')
	    elif (x!='') and (x[0]=='p'):
	      y = x[1:]
	      if(y >= '0' and y < str(len(match.hand))):
	        match = match.action('play',int(y))
	      else:
	        print('Which?')
	    elif (x!='') and (x[0]=='g'):
	      y = x[1:]
	      if(y >= '0' and y < str(len(match.play))): 
	        match = match.action('discard',int(y))
	      else:
	        print('Which?')
	    elif (x!='') and (x[0]=='u'):
	      match = match.action('undo')
	    elif (x!='') and (x[0]=='r'):
	      playing = False
	    elif (x!='') and (x[0]=='q'):
	      playing = False
	      quit=True
	    elif (x!='') and (x[0]=='c'):
	      file_loaded = False
	      playing = False
	plt.ioff()
         
