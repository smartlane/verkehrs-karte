# encoding: utf-8

from flask.ext.script import Manager

from webapp import app
from webapp import util

manager = Manager(app)

@manager.command
def sync_moers():
  util.sync_moers()

@manager.command
def sync_rostock():
  util.sync_rostock()

if __name__ == "__main__":
  manager.run()