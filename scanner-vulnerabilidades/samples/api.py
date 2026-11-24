import subprocess
def ping(request):
    host = request.args.get('host')
    subprocess.run("ping " + host, shell=True)
def lookup(cursor, request):
    uid = request.args.get('id')
    cursor.execute("SELECT * FROM users WHERE id = " + uid)
