import subprocess

def start_stream(cam,channel):
    proc = subprocess.Popen('cmd /k "ffmpeg -i {}\
        -vcodec copy -acodec aac \
            -f flv {}"'.format(cam,channel), shell=False)
    print ('proc = '), proc.pid
    return(proc)


def stop_stream(id):

    id.terminate
    
    return("OK")
