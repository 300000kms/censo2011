# -*- coding: utf-8 -*-

'''

http://lapaginadefinitiva.com/c/exopotamia/tutorial-para-leer-con-json-las-estadisticas-del-ine/

hay que hacer un get cookie
get posible tablassss
get variables de agregacion
comunidad, municipio, distrito o uc

descarga el dato
da un listado de calidad de la info obtenida
se realizan funciones de agregacion

'''
import requests
from lxml import etree
import pprint
import re
import demjson



pp = pprint.PrettyPrinter(indent=4)

def totxt(filename, r):
    with open(filename, 'w') as f:
        f.write(r)
    return

def getCookie(lugar =''):
    #http://www.ine.es/censos2011/tablas/Inicio.do
    #http://www.ine.es/censos2011/tablas/Wizard.do#
    #url = 'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=1&reqCode=paso1'

    #1
    url = 'http://www.ine.es/censos2011/tablas/Inicio.do'
    r=requests.get(url)
    cookie = r.headers['Set-Cookie']
    print cookie

    #2
    headers = {}
    headers['Cookie'] =  cookie.replace('; Path=/censos2011/tablas','')
    url= 'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=1&reqCode=paso4'
    r = requests.get(url, headers = headers)
    print ':',r.headers.get('Set-Cookie')

    #3
    headers['Referer'] =  url
    headers['Cookie'] = cookie
    data={
        'WIZARD':1,
        'reqCode':'paso3',
        'desglose':'NO',
        'areaOrigen':'nacion',
        'elementosGeograficosOrigenSeleccionados':'[RESIDENCIA].[Todo RESIDENCIA]',
        }
    url = 'http://www.ine.es/censos2011/tablas/Wizard.do'

    r = requests.post(url, headers = headers, data = data)

    print '::', r.headers['Set-Cookie']
    print r.headers

    #4
    headers['Referer'] =  url
    headers['Cookie'] =  cookie
    headers['Content-Type'] = 'application/x-www-form-urlencoded'

    url = 'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=1&reqCode=paso2'
    r = requests.post(url,headers=headers, data=data)
    print ':::', r.headers.get()



    return r.headers['Set-Cookie']

def getDimensions(cookie):
    #http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=1&reqCode=paso2
    urls={
        'residentes_en_viviendas_principales':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=1&reqCode=paso2#',
        'ocupados_de_16_o_mas_anyos':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=2&reqCode=paso2#',
        'cursan_algun_tipo_de_estudios_y_no_trabajan':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=3&reqCode=paso2',
        'viviendas_principales_y_no_principales':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=5&reqCode=paso2',
        'viviendas_principales':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=4&reqCode=paso2',
        'hogares':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=6&reqCode=paso2',
        'parejas_y_otros_nucleos_familiares':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=7&reqCode=paso2'
        }

    headers = {}
    headers['Cookie'] = cookie
    url = 'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=1&reqCode=paso2'
    urls[urls.keys()[0]]

    #regex = re.compile(r'(?<=\{)(.*?)(?=\})')
    regex = re.compile(r'{.*?}')
    results={}
    for u in urls:
        results[u]={'variables':{}, 'unidades':{}}
        url = urls[u]
        r = requests.get(url, headers=headers)
        tree = etree.HTML(r.text)
        t = tree.xpath("//script[contains(text(),'sas_TreeView_level')]/text()")
        #(?<=\[)(.*?)(?=\])
        dics =  regex.findall(t[0])
        for d in dics:
            #print d
            obj = demjson.decode(d)
            #print obj
            results[u]['variables'][obj['text'].encode('utf-8')] = obj['value'].encode('utf-8')

        t = tree.xpath("//*[@class='combo']/option")
        for tt in t:
            if tt.xpath('./@value')[0] not in ('SI', 'NO'):
                t_name = tt.xpath('./text()')[0]
                t_value = tt.xpath('./@value')[0]
                results[u]['unidades'][t_name.encode('utf-8')] = t_value.encode('utf-8')

    pp.pprint(results)
    totxt('dimensiones.txt', str(results) )

    return


def getArea(c):

    ##
    urls ={'nacional':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=1&reqCode=paso4',
        'ccaa':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=2&reqCode=paso4',
        'provincia':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=3&reqCode=paso4',
        'municipio':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=4&reqCode=paso4',
        'inframunicipal':'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=5&reqCode=paso4'
        }

    ##
    places={}
    for u in urls:
        places[u]={}
        url = urls[u]
        headers={'Cookie': c}
        r= requests.get(url, headers=headers)
        tree = etree.HTML(r.text)
        t = tree.xpath("//*[@class='combo']/option")
        for tt in t:
            if tt.xpath('./@value')[0] not in ('SI', 'NO'):
                t_value = tt.xpath('./text()')[0]
                t_name = tt.xpath('./@value')[0]
                places[u][t_value] = t_name
    pp.pprint(places)
    totxt('areas.txt', str(places) )
    return


def get(cookie):
    url = 'http://www.ine.es/censos2011/tablas/Informe.do'
    url = 'http://www.ine.es/censos2011/tablas/Informe.do?reqCode=excel'
    url = 'http://www.ine.es/censos2011/tablas/Informe.do?reqCode=xml'

    headers = {}
    headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    headers['Accept-Encoding'] = 'gzip, deflate'
    headers['Accept-Language'] = 'es-ES,es;q=0.8,ca;q=0.6,en;q=0.4,en-US;q=0.2'
    headers['Cache-Control'] = 'max-age=0'
    headers['Connection'] = 'keep-alive'
    headers['Content-Length'] = '228'
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['Cookie'] = cookie
    headers['Host'] = 'www.ine.es'
    headers['Origin'] = 'http://www.ine.es'
    headers['Referer'] = 'http://www.ine.es/censos2011/tablas/Wizard.do?WIZARD=6&reqCode=paso2'
    headers['Upgrade-Insecure-Requests'] = '1'
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36'


    data ={}
    data['reqCode'] = 'iniciar'
    data['jerarquiasSeleccionada'] = ''
    data['WIZARD'] = '2'
    data['pagina4'] = '6'
    data['tipoInforme'] = 'LIBRE'
    #data['idFila'] = 'L_[RESIDENCIA_INFRA].[DESC_RESIDENCIA_INFRA_N1]'
    #data['idFila'] = 'L_[RESIDENCIA_INFRA].[DESC_RESIDENCIA_INFRA_N2]'
    data['idFila'] = 'L_[RESIDENCIA_INFRA].[DESC_RESIDENCIA_INFRA_N3]'
    data['idColumna'] = 'L_[N_VIAJES].[DESC_N_VIAJES]'
    data['medidas'] = '[Measures].[SPERSONASSUM]'

    #data ='reqCode:iniciar,jerarquiasSeleccionada:,WIZARD:2,pagina4:6,tipoInforme:LIBRE,idFila:L_[RESIDENCIA_INFRA].[DESC_RESIDENCIA_INFRA_N3],idColumna:L_[N_VIAJES].[DESC_N_VIAJES],medidas:[Measures].[SPERSONASSUM]'

    r = requests.post(url, data=data, headers=headers)
    print r.text
    totxt('filename.html', r.text.encode('utf-8'))
    return r.headers

#############################################################
c =getCookie()

c = 'JSESSIONID=CC22563DD29E001F97BA1B1E258F16E7.censo02'
#get(c)
c= 'JSESSIONID=E0F9C1FB199C5E74E912D657800B2257.censo02'

#getArea(c)
#getDimensions(c)