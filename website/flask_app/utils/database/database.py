import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow
import time
import csv
import os

def load_csv(filename):
    base = os.path.dirname(__file__)
    # Go up TWO levels: from utils/database/ to flask_app/
    path = os.path.join(base, '..', '..', 'database', 'create_tables', filename)
    path = os.path.abspath(path)
    with open(path, newline='', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))

def get_resume_data():
    institutions = load_csv('institutions.csv')
    positions = load_csv('positions.csv')
    experiences = load_csv('experiences.csv')
    skills = load_csv('skills.csv')
    # Optionally, build a nested structure here if your template expects it
    return {
        "institutions": institutions,
        "positions": positions,
        "experiences": experiences,
        "skills": skills,
    }

