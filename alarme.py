import json
import time
from urllib.parse import urlencode
from http import client
import urllib.request
import hashlib
import hmac
import codecs
import urllib
import urllib.parse
from datetime import datetime, timedelta

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

#suas chaves de api (geradas no site www.mercadobitcoin.com.br)
key=''
secret=''

def play(f):
    mixer.init()
    mixer.music.load("audio/"+f+".mp3")
    mixer.music.play()
    
play('refresh')

def execute(params,key,secret):
    params = urlencode(params)
    H = hmac.new(bytes(secret,encoding='utf8'),digestmod=hashlib.sha512)
    H.update(('/tapi/v3/?' + params).encode('utf-8'))
    try:
        conn = client.HTTPSConnection('www.mercadobitcoin.net')
        conn.request("POST", '/tapi/v3/', params, {
            'Content-Type': 'application/x-www-form-urlencoded',
            'TAPI-ID': key,
            'TAPI-MAC': H.hexdigest()
        })
        r=conn.getresponse().read()
        j=json.loads(r)
        return j
    finally:
        if conn:
            conn.close()

def getOrders(coin_pair):
    return execute({
        'tapi_method': 'list_orders',
        'tapi_nonce': str(int(time.time())),
        'coin_pair': coin_pair,
        'status_list': '[1, 2]',
        'has_fills': 'false',
    },key,secret)

def getHtml(u):
    try:
        return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"})).read().decode("utf8")
    except:
        return ""

line='---------------------------------------------------------------------------------------------------'

print('Bot iniciado')
print(line)

while(1):
    try:
        wallet=execute({
            'tapi_method': 'get_account_info',
            'tapi_nonce': str(int(time.time()))
        },key,secret)

        brl=float("{:.2f}".format(float(wallet['response_data']['balance']['brl']['available'])))
        sum=brl
        print(line)
        print('R$ '+str(brl))
        print(line)
        
        for coin in wallet['response_data']['balance']:
            if (coin!='brl'):
                arr=json.loads(getHtml('https://www.mercadobitcoin.net/api/'+coin+'/ticker/'))
                last=float(arr['ticker']['last'])
                low=float(arr['ticker']['low'])
                high=float(arr['ticker']['high'])

                coin_pair='BRL'+(coin.upper())
                orders=getOrders(coin_pair)                

                if len(orders['response_data']['orders'])>0:
                    print(line)
                for order in orders['response_data']['orders']:
                    pct_=float("{:.2f}".format(last*100/float(order['limit_price'])))
                    if (order['order_type']==1): #ordem de compra
                        str_=''
                        if pct_<100.5:
                            play('question')
                            str_='- SE APROXIMANDO DA ORDEM DE COMPRA'
                        if pct_>110:
                            str_='- SE DISTANCIANDO DA ORDEM DE COMPRA'
                        print(coin+' compra em '+str(order['limit_price'])+' - '+str(pct_)+'% '+str_)
                    elif (order['order_type']==2): #ordem de venda
                        str_=''
                        if pct_>99.5:
                            play('question')
                            str_='- SE APROXIMANDO DA ORDEM DE VENDA'
                        if pct_<90:
                            str_='- SE DISTANCIANDO DA ORDEM DE VENDA'
                        print(coin+' vende em '+str(order['limit_price'])+' - '+str(pct_)+'% '+str_)
                if len(orders['response_data']['orders'])>0:
                    print(line)

                printstr=(
                    coin.ljust(6)+
                    (str("{:.2f}".format(low*100/last))+'% ').ljust(9)+
                    ('low: '+str("{:.3f}".format(low))).ljust(15) +' '+
                    ('last: '+str("{:.3f}".format(last))).ljust(16) +' '+
                    ('high: '+str("{:.3f}".format(high))).ljust(16) +' '+
                    (str("{:.2f}".format(last*100/high))+'% ').ljust(9)
                )

                available=float(wallet['response_data']['balance'][coin]['available'])

                if (available>0):
                    tax=(available*last)*0.7/100
                    sum=sum+(available*last)-tax
                    print(printstr+
                          ('saldo: '+str(available)).ljust(18)+' '+
                          '(R$ '+str("{:.2f}".format((available*last)-tax))+')')
                else:
                    print(printstr)

        print(line)
        print('TOTAL R$ '+str("{:.2f}".format(sum)))
        print(line)
        time.sleep(1) #pausa de 1 segundo
    except:
        print('Erro')
        #play('lose')
