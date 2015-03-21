# encoding: utf-8

from flask.ext.script import Manager

from webapp import app
from webapp import util

manager = Manager(app)

@manager.command
def sync_moers():
  util.sync_moers()

if __name__ == "__main__":
  manager.run()