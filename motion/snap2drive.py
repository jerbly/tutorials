'''
Created on Jun 7, 2015

@author: jeremyblythe
'''
import sys
#sys.path.insert(1, '/Library/Python/2.7/site-packages')

import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
from googleapiclient.http import MediaFileUpload

if __name__ == '__main__':
    file_path = sys.argv[1]
    auth_required = True
    #Have we got some credentials already?
    storage = Storage('snap2drive_credentials.txt')    
    credentials = storage.get()
    try:
        if credentials:
            # Check for expiry
            if credentials.access_token_expired:
                if credentials.refresh_token is not None:
                    credentials.refresh(httplib2.Http())
                    auth_required = False
            else:
                auth_required = False
    except:
        # Something went wrong - try manual auth
        pass
        
    if auth_required:
        flow = client.flow_from_clientsecrets(
            'client_secrets.json',
            scope='https://www.googleapis.com/auth/drive',#.metadata.readonly',
            redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    
        auth_uri = flow.step1_get_authorize_url()
        
        print 'Go to this link in your browser:'
        print auth_uri
    
        auth_code = raw_input('Enter the auth code: ')
    
        credentials = flow.step2_exchange(auth_code)
        
        storage.put(credentials)
           
    #Get the drive service
    http_auth = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v2', http_auth)
    
    #Find the 'public' folder
    files = drive_service.files().list(q="title='public' and mimeType contains 'application/vnd.google-apps.folder' and trashed=false").execute()
    if len(files['items']) == 1:
        folder_id = files['items'][0]['id']
        print folder_id
        #Delete the old lastsnap.jpg
        files = drive_service.files().list(q="title='lastsnap.jpg' and '%s' in parents and trashed=false" % folder_id).execute()
        if len(files['items']) >= 1:
            for f in files['items']:
                file_id = f['id']
                drive_service.files().delete(fileId=file_id).execute()
        #Now upload the new one
        media = MediaFileUpload(file_path, mimetype='image/jpeg')
        response = drive_service.files().insert(media_body=media, body={'title':'lastsnap.jpg', 'parents':[{u'id': folder_id}]}).execute()
        print response
    else:
        print 'Could not find public folder'
        