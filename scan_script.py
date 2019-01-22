import os
import sys
import time
import re
import tempfile

start=time.time()
ext_set=set()
ext_dic=dict()
ext_cnt=dict()
total_size=0
total_count=0
size_cmp=0

scriptname=sys.argv[0].split('\\')[-1]

if len(sys.argv)<2:
    print("\nThis script will scan directory contents and show capacity usage by file type.\n")
    print("Syntax for Linux:                   python",scriptname,"<path>")
    print("Usage example for Linux:            python",scriptname," /home/")
    print("\nSyntax for Windows:                 python3.exe",scriptname,"<path>")
    print("Usage example for Windows:          python3.exe",scriptname," c:\\\n")
    path=input('Enter valid scan path: (for example: C:\\Users\\)')

else: path=sys.argv[1]

f=open('tmp1.dat','w')
f.close()


if os.name=='nt':
    print('Windows detected. Running directory scan for',path)
    try:
        os.system('compact /q /c /exe lzx tmp1.dat')
        print('Temporary file is compressed.')
    except: pass
    try: os.system('dir /A-D /N /S /-C '+path+' | findstr -R "^[0-9][0-9].*$" > tmp1.dat 2>NUL')

    except:
        print("Error with listing.  Script aborted for ",path)
        exit()
else:
    print('Linux detected. Running directory scan for',path)
    os.system("ls -gGR1 --time-style=long-iso "+path+" 2>/dev/null | grep -i '^-[\S\s]*'  > tmp1.dat")

f=open('tmp1.dat')
l=f.readline()

while l:

    if os.name=='nt':
        try:
            size =int(l[21:39])
            total_count+=1
        except:
            l=f.readline()
            continue
        fname=l[39:]
        if '.' in fname[1:]:
            ext=fname[1:].split('.')[-1][:-1]
        else:
            ext='no_extnsn'

    elif os.name=='posix':
        total_count+=1
        fline=re.split('[:]\d\d\s',l)[-1][:]
        words=re.findall(r'[\S]+', l)
        size=int(words[2])
        words=re.split('[.]',fline)

        if len(words)<2:
            ext='no_extnsn'
        else:
            ext=words[-1][:-1]




    if ext in ext_set:
        ext_dic[ext]+=size
        ext_cnt[ext]+=1
        total_size+=size
    else:
       ext_set.add(ext)
       ext_dic.update({ext:size})
       ext_cnt.update({ext:1})
       total_size+=size

    l=f.readline()


f.close()
end=time.time()
print(round((end-start)/60,1),'minutes elapsed.')
print('Scan complete.')

if total_size==0:
   print('Zero total size. Exiting.')
   exit()

result=list()
for k in ext_dic.keys():
    if float(ext_dic[k])/total_size>0.01:
        use_pct=str(round(float(ext_dic[k])/total_size*100,1))
        if len(use_pct)<4: use_pct='0'+use_pct
        size_GiB=str(round(float(ext_dic[k])/1024/1024/1024,3))
        result.append(use_pct+':'+k+':'+size_GiB)

result.sort(reverse=True)

k=0




image_compressed=['jpg','jpeg','jpe','tif','tiff','gif','png']
video_compressed=['mp4','mpeg4','avi','mov','qt','flv','swf','wmv','mkv','avchd','3gp','3g2','h264','m4v','rm']
music_compressed=['mp3','mpa','wav','wma','ogg','aac','alac','flac']
office_compressed=['ost','docx','dotx','potx','pptx','ppsx','potx','potm','xlsx','xltx','xlsm','xltm','pdf']
archive=['arc','arj','as','b64','btoa','bz','cab','cpt','gz','hqx','iso','lha','lzh','mim','mme','pak','pf','rar','rpm','sea','sit','sitx','tbz','tbz2','tgz','uu','uue','z','zip','zipx','zoo','cab','7z']
compressed=image_compressed+video_compressed+music_compressed+office_compressed+archive

print("""

  SPACE CONSUMPTION BY FILE TYPE

 #       TYPE   GiB      %       QTY       COMPRESSIBLE
""")
for r in result:
    k+=1
    words=r.split(':')
    ext_type=words[1]
    ext_GiB=float(words[2])
    ext_pct=float(words[0])
    if ext_type in compressed:
        ext_cmp='No'
        size_cmp+=ext_GiB
    else: ext_cmp='.'
    print("{0:2d} {1:>10s}   {2:<5,.2f}    {3:<7.1f} {4:<6,d} {5:>9s}".format(k,ext_type,ext_GiB,ext_pct,ext_cnt[ext_type],ext_cmp))

total_size_GiB=float(total_size)/1024/1024/1024
pct_cmp=int(size_cmp*100/total_size_GiB)
print("\n\nTotal space used by all files is {0:8,.2f} GiB".format(total_size_GiB))
print("Space used by compressed files is {0:7,.2f} GiB, which is {1:3d}% of all data.".format(size_cmp,pct_cmp))
print("Total number of file types found is {0:<5,d}".format(len(ext_dic)))
print("Total number of files found is {0:<10,d}\n\n".format(total_count))
