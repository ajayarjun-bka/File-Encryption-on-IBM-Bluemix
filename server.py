import os,sys
#from PIL import Image
#import base64
#import transpositionEncrypt, transpositionDecrypt
import keystoneclient.v3 as keystoneclient
import swiftclient.client as swiftclient
from flask import Flask,render_template,request,make_response
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import dateutil.parser
import time
import pyDes
from cStringIO import StringIO

app = Flask(__name__)
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
port = int(os.getenv('VCAP_APP_PORT', 8000))

auth_url = 'https://identity.open.softlayer.com'+'/v3'
project_name = 'object_storage_5396a43e_8512_4746_b024_bfa34c5fd2b3'
password = '#######'
user_domain_name = '1029823'
project_id = 'a8f8e7ecef8f4c2d93eddd11fc659c58'
user_id ='dbc578008b8c46ba89edb3ba13fd6269'
region_name ='dallas'

# Get a Swift client connection object
conn = swiftclient.Connection(
        key=password,
        authurl=auth_url,
        auth_version='3',
        os_options={"project_id": project_id,
                    "user_id": user_id,
                    "region_name": region_name})

#### Variables
container_name = 'new-container'
k = pyDes.des("DESCRYPT", pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
#downloadedfile='example1_downnload.txt'
tmp="tmp.txt"
tmp1="tmp1.txt"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload',methods=['GET','POST'])
def upload():
    return render_template('upload.html')





@app.route('/upload1',methods=['GET','POST'])
def getfile():
    file = request.files['fileupload']
    blob = file.read()
    file_name = file.filename
    total_size = 0
    tmp11= open(tmp1,'w')
    tmp11.write(blob)
    tmp11.close()
    print file_name
    #en_file = os.path.splitext(file_name)[0] + '_enc.txt'
    #file_size = len(blob)
    file_size = os.path.getsize(tmp1)
    file_size = file_size / 2048
    status=0
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            # print 'object: {0}\t size: {1}\t date: {2}'.format(data['name'], data['bytes'], data['last_modified'])
            if file_name == data['name']:
                status = 4
                app.logger.warning("file exists")
            total_size = total_size + data['bytes']
    total_size = total_size / 2048
    file_size_after = file_size + total_size
    if status==0:
        if file_size < 1:
            if file_size_after < 10:
                status = 1
                app.logger.warning("road clear")
            else:
                status = 2
                app.logger.warning("too big total size goes beyond 10 MB")
        else:
            status = 3
            app.logger.warning("file greater than 1 mb")

    if status == 1:
        conn.put_container(container_name)
        print "\nContainer %s created successfully." % container_name
        # List your containers
        print ("\nContainer List:")
        for container in conn.get_account()[1]:
            print container['name']
        #gpg = gnupg.GPG(gnupghome='/gnupg')
        #gpg = gnupg.GPG(gnupghome='C:/Program Files (x86)/GNU/GnuPG')
        # print key
        f = open(tmp1,'rb')
        udata=f.read()
        ud=k.encrypt(udata)
        '''file = open(file_name,'w')
        file.write(ud)
        file.close()'''
        #contents = file.read()
        #print "Contents:"
        #print contents
        conn.put_object(container_name, file_name, contents=ud)
        #file.close()
        return "File Has been encrypted and uploaded successfully. <br><a href='/'>go back to home</a>"
    elif status == 2:
        return "If we upload the file, Total size would exceed 10 MB. <br><a href='/'>go back to home</a>"
        #exit
    elif status == 3:
        return "Upload file size is greater than 1 MB . <br><a href='/'>go back to home</a>"
        #exit
    elif status == 4:
        return "File already exists in the Server. <br><a href='/'>go back to home</a>"

@app.route('/list')
def list():
    print ("\nObject List:")
    templist=[]
    for container in conn.get_account()[1]:
        filesize=0
        for data in conn.get_container(container['name'])[1]:
            templist.append(data)
            filesize=filesize+data['bytes']
            b = 'object: {0} size: {1} date: {2}'.format(data['name'], data['bytes'], data['last_modified'])
    #print conn.get_container(container['name'])[1]
    print 'templist',templist
    return render_template('list.html',filelist=templist,totsize=filesize)

@app.route('/delete')
def delete():
    print ("\nObject List:")
    templist = []
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            templist.append(data)
            b = 'object: {0} size: {1} date: {2}'.format(data['name'], data['bytes'], data['last_modified'])
    # print conn.get_container(container['name'])[1]
    print 'templist', templist
    return render_template('delete.html', filelist=templist)


@app.route('/deletefile/<filename>',methods=['GET','POST'])
def delfile(filename):
    conn.delete_object(container_name, filename)
    return "File Deleted Successfully. <br><br><a href='/'>go back to home</a>"

@app.route('/download',methods=['GET','POST'])
def download():
    print ("\nObject List:")
    templist = []
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            templist.append(data)
            b = 'object: {0} size: {1} date: {2}'.format(data['name'], data['bytes'], data['last_modified'])
    # print conn.get_container(container['name'])[1]
    print 'templist', templist
    return render_template('download.html', filelist=templist)
@app.route('/downloadfile/<filename>',methods=['GET','POST'])
def downfile(filename):
    downloadedfile = filename
    d_file = conn.get_object(container_name, filename)
    eed=d_file[1]
    ued=k.decrypt(eed)
    #temc='down'+filename
    #dofile = open('down'+filename,'w')
    #dofile.write(ued)
    #dofile.close()
    #uedfile=open(filename,'w')
    #uedfile.write(ued)
    #uedfile.close()
    #conn.put_object(container_name, temc, contents=ued)
    #obj = conn.get_object(container_name, temc)
    #with open('down' + filename, 'w') as my_example:
    #   my_example.write(obj[1])
    responsestr="attachment; filename="+filename
    response = make_response(ued)
    response.headers["Content-Disposition"] = responsestr
    #"attachment; filename=filename"
    #conn.delete_object(container_name, temc)
    return response
    #" File has been downloaded successfully <br><br><a href='/'>go back to home</a>

@app.route('/readfile',methods=['GET','POST'])
def readfile():
    return render_template("readfile.html")

@app.route('/date',methods=['GET','POST'])
def getdate():
    return render_template("date.html")

@app.route('/datedel',methods=['GET','POST'])
def datedel():
    date=request.form['date']
    date_ob=datetime.strptime(date, '%I:%M%p')
    print (date_ob.isoformat())
    i=datetime.now()
    #i=i.replace(hour=date_ob.hour,minute=date_ob.minute)
    #print date_ob
    print(i.isoformat())
    print ("\nObject List:")
    templist = []
    for container in conn.get_account()[1]:
        for data in conn.get_container(container['name'])[1]:
            fdate= data['last_modified']
            yourdate = dateutil.parser.parse(fdate)
            subdate= i-yourdate
            conn.delete_object(container_name, filename)
            return "File Deleted Successfully. <br><br><a href='/'>go back to home</a>"
            b = 'object: {0} size: {1} date: {2}'.format(data['name'], data['bytes'], data['last_modified'])
            '''d1_ts = time.mktime(d1.timetuple())
            d2_ts = time.mktime(d2.timetuple())'''
            # they are now in seconds, subtract and then divide by 60 to get minutes.
            #print int(d2_ts - d1_ts) / 60 # much better
    # print conn.get_container(container['name'])[1]
    print 'templist', templist
    return "Check Console"

@app.route('/uploadImage',methods=['GET','POST'])
def image():
    return render_template('uploadImage.html')

@app.route('/processimg',methods=['GET','POST'])
def img():
    #file = Image.open(request.files['fileupload'])
    obj = request.files['fileupload']
    #print obj.read()
    img = obj.read();
    encimg=k.encrypt(img)
    print len(encimg)/1024
    conn.put_object(container_name, obj.filename, contents=encimg)
    return "IMAGE ENCRYPTED AND UPLOADED SUCCESSFULLY"






if __name__ == "__main__":
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    #app.run(host='0.0.0.0', port=int(port))
    app.run(debug=True)
