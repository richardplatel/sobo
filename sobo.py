from __future__ import unicode_literals
import soco
import json
from flask import Flask,jsonify,redirect,render_template

application = Flask(__name__)

class ThingyNotFoundError(Exception):
  status_code=404
  def __init__(self, message, payload=None):
        Exception.__init__(self)
        self.message = message
        self.payload = payload

  def to_dict(self):
    rv = dict(self.payload or ())
    rv['message'] = self.message
    return rv

class ZoneNotFoundError(ThingyNotFoundError): pass
class FavoriteNotFoundError(ThingyNotFoundError) : pass



@application.route('/sobo')
def idx():
  return render_template("index.html")

@application.route('/sobo/static/<path:stat>')
def stat(stat):
  return application.send_static_file(stat)

@application.route('/sobo/<where>/<what>')
def play(what='cbc', where='Bathroom'):
  whats = {
    'cbc' : 'CBC Radio One Toronto',
  }
  if what not in whats:
    raise FavoriteNotFoundError(what)

  play_fave(whats[what], where)
  return render_template("ok.html", what=what, where=where)

@application.errorhandler(ThingyNotFoundError)
def handle_nf(error):
  response = jsonify(error.to_dict())
  response.status_code = error.status_code
  return response

def get_zone_by_name(name):
  for device in soco.discover():
    if device.player_name == name:
      device.unjoin()
      return device
  raise ZoneNotFoundError(device)

def play_fave(fave, room):
  zone = get_zone_by_name(room)
  faves = zone.get_sonos_favorites()['favorites']
  for f in faves:
    if f['title'] == fave:
      zone.play_uri(f['uri'], f['meta'])
      break;

if __name__ == '__main__':
  play()


