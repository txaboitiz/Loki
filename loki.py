#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 09:59:18 2020

@author: txominaboitiz
"""

# loki

import os
import pyAesCrypt as pc
import pickle
from getpass import getpass
import string
import random
import sys

def setup():
    user = str(input('Username: '))
    confirmed = False
    masterki = getpass('Master key: ')
    while not confirmed:
        confirm = getpass('Confirm Master key: ')
        if masterki == confirm:
            confirmed = True
    dir_setup(user, masterki)

def dir_setup(user, masterki):
    if not os.path.isdir('.loki'):
        os.mkdir('.loki')
    os.chdir('.loki')
    location = f'.{user}'
    os.mkdir(location)
    os.chdir(location)
    file = f'{user}_ki.pkl'
    with open(file, 'wb') as f:
        pickle.dump({}, f)
    pc.encryptFile(file, f'{file}.aes', masterki, 64 * 1024)
    os.remove(file)
    os.chdir('../..')

def login():
    confirmed = False
    user = str(input('Username: '))
    location = os.path.join('.loki', f'.{user}')
    if os.path.isdir(location):
        file = f'{user}_ki.pkl.aes'
        openfile = f'{user}_ki.pkl'
        while not confirmed:
            masterki = getpass('Master key: ')
            try:
                pc.decryptFile(os.path.join(location, file), os.path.join(location, openfile), masterki, 64 * 1024)
                os.chdir(location)
                confirmed = True
            except ValueError:
                print('Invalid master key, try again')
    return openfile, masterki

def read(openfile):
    with open(openfile, 'rb') as f:
        keys = pickle.load(f)
    return keys

def write(openfile, keys):
    with open(openfile, 'wb') as f:
        pickle.dump(keys, f)

def sort_dict(d):
    return {i[0]: i[1] for i in sorted(d.items())}

def new(openfile, g = False, account = None):
    keys = read(openfile)
    if not account:
        account = str(input('New account: '))
    if account in keys.keys():
        print(f'The account "{account}" is already registered. Operation aborted')
        return
    if not g:
        password = str(input('Password: '))
    else:
        password = generate_pass()
    keys[account.capitalize()] = password
    keys = sort_dict(keys)
    write(openfile, keys)
    print('New password saved')

def request(openfile, account = None):
    keys = read(openfile)
    if not account:
        account = str(input('Account: '))
    print('{:40s}| {:40s}'.format('Account','Password'))
    print('-' * 80)
    for key in keys:
        if account.capitalize() in key:
            print('{:40s}| {:40s}'.format(f'{key}', f'{keys[key]}'))
    
def list_all(openfile):
    keys = read(openfile)
    print('{:40s}| {:40s}'.format('Account','Password'))
    print('-' * 80)
    for account in keys.keys():
        print('{:40s}| {:40s}'.format(f'{account}', f'{keys[account]}'))

def change_master(g = False):
    global masterki
    validated = False
    while not validated:
        current = getpass('Current master key: ')
        if current != masterki:
            print('Invalid master key. Try again.')
        else:
            validated = True
    if not g:
        new = getpass('New master key: ')
        confirmed = False
        while not confirmed:
            confirm = getpass('Confirm master key: ')
            if new == confirm:
                print('Master key has been changed')
                confirmed = True
                masterki = new
    else:
        masterki = generate_pass()
        print('Master key has been generated and changed')
        print(f'New master key: {new}')


def change_password(openfile, g = False, account = None):
    if not account:
        account = str(input('Account: '))
    keys = read(openfile)
    account = account.capitalize()
    if account in keys.keys():
        if not g:
            keys[account] = str(input('New password: '))
            print('Password changed')
        else:
            keys[account] = generate_pass()
            print('Password generated and changed')
        write(openfile, keys)
    else:
        print(f'"{account}" is not a registered account. Try again')
        change_password(openfile)

def generate_pass():
    digits = [str(i) for i in range(10)]
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    lists = [digits, lower, upper]
    password = ''
    for i in range(8):
        l = random.choice(lists)
        c = random.choice(l)
        password += c
    return password

def print_gen_pass():
    print(generate_pass())

def remove_account(openfile, account = None):
    keys = read(openfile)
    if not account:
        account = str(input('Select account to remove: '))
    account = account.capitalize()
    if account in keys.keys():
        confirm = str(input(f'Are you sure you wish to remove the account "{account}"? (y/n): '))
        if confirm == 'y':
            keys.pop(account)
            write(openfile, keys)
            print(f'The account "{account}" has been removed.')
        else:
            print('Operation aborted')
            return
    else:
        print(f'"{account}" is not a registered account. Try again')
        remove_account(openfile)

def remove_all(openfile):
    confirm = str(input('Are you sure you want to remove all your accounts? (y/n)'))
    if confirm == 'y':
        write(openfile, {})
        print('All the accounts have been removed.')
    else:
        print('Operation aborted')
        return

def show_codes():
    print('--------------------- FUNCTION CODES (cmd: codes) ---------------------')
    print('n: add new password   | r: request password      | l: list all')
    print('-----------------------------------------------------------------------')
    print('cm: change master key | cp: change password      | g: generate password')
    print('-----------------------------------------------------------------------')
    print('To modify or add a new password with an randomly generated password,\n insert: [function code] + [space] + "g"')
    print('-----------------------------------------------------------------------')
    print('rm: remove account    | rm a: remove all accounts |                exit')
    print('-----------------------------------------------------------------------')


def logout(openfile, masterki):
    pc.encryptFile(openfile, f'{openfile}.aes', masterki, 64 * 1024)
    os.remove(openfile)
    os.chdir('../..')
    sys.exit()

def outer_prompt():
    while True:
        f = str(input('Prompt: '))
        if f == 'exit':
            sys.exit()
        elif f == 's':
            setup()
        elif f == 'l':
            openfile, masterki = login()
            return openfile, masterki
        else:
            print('Invalid function code. Try again')

def inner_prompt(openfile, masterki):
    while True:
        g = False
        prompt = str(input('Prompt: '))
        prompt = prompt.split()
        f, args = prompt[0], prompt[1:]
        if args:
            if args[0] == 'g':
                g = True
                args = args[1:]
        functions = {'n': [new, (openfile, g)],
                 'r': [request, (openfile,)],
                 'l': [list_all, (openfile,)],
                 'cm': [change_master, (masterki, g)],
                 'cp': [change_password, (openfile, g)],
                 'g': [print_gen_pass, ()],
                 'rm': [remove_account, (openfile,)],
                 'ra': [remove_all, (openfile,)],
                 'codes': [show_codes, ()],
                 'exit': [logout, (openfile, masterki)]}
        if f in functions.keys():
            func = functions[f][0]
            args = functions[f][1] + tuple(args)
            print('')
            func(*args)
            print('')
        else:
            print('Invalid function code. Try again.')

def main():
    print('--------------FUNCTION CODES----------')
    print('l: login | s: setup new account | exit')
    print('--------------------------------------')
    logged = False
    openfile, masterki = outer_prompt()
    logged = True
    if logged:
        show_codes()
        inner_prompt(openfile, masterki)



#%%

if __name__ == '__main__':
    main()
