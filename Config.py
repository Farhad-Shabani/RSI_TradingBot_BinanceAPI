def api_keys(key):
    keys = {'test': {'key': 'Insert the key here',
                     'secret': 'Insert the secret here'},
            }
    try:
        return keys[key]
    except:
        return print('There is no such a key! Please enter again...')


def dat_secrets():
    return {'host': 'Your host name',
            'database': 'Your database Name',
            'user': 'Your username',
            'password': 'Your Password'}
