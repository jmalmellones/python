"""
    RSS Downloader. Automatically download rss linked pages' torrents.
    Copyright (C) 2016 Jose Miguel Almellones Cabello

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import re
import subprocess
import json

config_file = 'quitar_elitetorrent.json'
config = json.load(open(config_file))

raices = config['raices']
# raices = ['y:\pelis', 'y:\series']
re1 = re.compile('[ ]*[\(]?elitetorrent\.net[\)]?', re.IGNORECASE)
re2 = re.compile('[ \.]*[\[]?www\.newpct[1]?\.com[\]]?', re.IGNORECASE)
punto_montaje = config['punto_montaje']


def asegurar_video():
    if not os.path.exists(punto_montaje):
        os.makedirs(punto_montaje)
    subprocess.call(['mount_afp', 'afp://' + config['usuario'] + ':' + config['password'] + '@' + config['ip_synology'] + '/' + config['carpeta_compartida'], punto_montaje])


def tratar_fichero(fichero):
    path, filename = os.path.split(fichero)
    nombre, extension = os.path.splitext(filename)
    nombre_tratado = re1.sub('', nombre).strip()
    nombre_tratado = re2.sub('', nombre_tratado).strip()
    if nombre != nombre_tratado:
        nuevo = os.path.join(path, nombre_tratado + extension)
        print 'renombrando ', fichero
        print 'a           ', nuevo
        try:
            os.rename(fichero, nuevo)
        except Exception as excp:
            print 'error renombrando ', fichero, ' a ', nuevo, ': ', excp


def tratar_directorio(directorio):
    for f in os.listdir(directorio):
        fichero = os.path.join(directorio, f)
        if os.path.isfile(fichero):
            tratar_fichero(fichero)
        else:
            print 'tratando directorio ', fichero
            tratar_directorio(fichero)


def quitar_elitetorrent():
    asegurar_video()
    for raiz in raices:
        print "tratando raiz ", raiz
        tratar_directorio(raiz)


if __name__ == '__main__':
    quitar_elitetorrent()
