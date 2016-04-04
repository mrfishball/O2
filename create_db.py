import os, sys
sys.path.append(os.getcwd())
from run import db

if __name__ == '__main__':
    db.create_all()