

def desktop_app():
    from facebook import Facebook

    # Get api_key and secret_key from a file
    fbs = open(FB_SETTINGS).readlines()
    facebook = Facebook(fbs[0].strip(), fbs[1].strip())

    facebook.auth.createToken()
    # Show login window
    facebook.login()

    # Login to the window, then press enter
    print 'After logging in, press enter...'
    raw_input()

    facebook.auth.getSession()
    info = facebook.users.getInfo([facebook.uid], ['name', 'birthday', 'affiliations', 'sex'])[0]

    for attr in info:
        print '%s: %s' % (attr, info[attr])

    friends = facebook.friends.get()
    friends = facebook.users.getInfo(friends[0:5], ['name', 'birthday', 'relationship_status'])

    for friend in friends:
        if 'birthday' in friend:
            print friend['name'], 'has a birthday on', friend['birthday'], 'and is', friend['relationship_status']
        else:
            print friend['name'], 'has no birthday and is', friend['relationship_status']

    arefriends = facebook.friends.areFriends([friends[0]['uid']], [friends[1]['uid']])

    photos = facebook.photos.getAlbums(friends[1]['uid'])
    print photos