#!/bin/bash


gunicorn xadmin.wsgi:application -c gunicorn.conf.py
