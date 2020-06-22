import os
from subprocess import Popen, PIPE
from flask import Flask, request, render_template


app = Flask(__name__)


pop = dict()


# frp批处理启动
def nginx():
    os.chdir("www/")
    command = 'nginx.exe'
    return Popen(command, stdout=PIPE, shell=False)


# ffmpeg推流
def ffmpeg(chn, url):
    os.chdir("../ffmpeg/")
    command = '''ffmpeg -i "%s" -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -r 25 -b:v 500k -s 640*480 -f flv "%s"''' % (chn, url)
    pop[url] = Popen(command, stdout=PIPE, shell=False, close_fds=True).pid
    print(pop)
    return


# 开启推流服务
@app.route('/rtmp/start', methods=['POST'])
def start_view():
    if request.method == "POST":
        chn = request.form['channel']
        url = request.form["rtmp"]
        if not chn:
            return "please input channel"
        if not url:
            return "please input rtsp"
        # 开始启动推流
        ffmpeg(chn, url)
        return "ok"
    return "please Use a POST request"


# 关闭推流服务
@app.route('/rtmp/stop', methods=['POST'])
def stop_view():
    if request.method == "POST":
        url = request.form["rtmp"]
        if not url:
            return "please input rtsp"
        # 关闭推流
        os.kill(pop[url], 9)
        del pop[url]
        return "ok"
    return "please Use a POST request"


@app.route('/rtmp', methods=["GET"])
def rtmp_view():
    return render_template("rtmp.html")


if __name__ == "__main__":
    nginx()
    app.run(host="127.0.0.1", port=6001, threaded=True)