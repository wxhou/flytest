.PHONY: clean kill run all  
#通常，Makefile中所有不会产生与目标名称相同名称的输出文件的目标都应为PHONY。这通常包括all，install，clean，distclean，等。
.IGNORE: kill # 忽略错误


all:
run: 
	nohup ./venv/bin/gunicorn -w 4 -k eventlet -b 0.0.0.0:5000 wsgi:app --reload & 

# reload参数是gunicorn的重新加载命令
kill: 
	pkill -f "0.0.0.0:5000 wsgi:app"  

# pkill -f 查找并杀死所有相关的进程