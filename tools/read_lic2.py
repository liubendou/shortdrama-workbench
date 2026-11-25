import pathlib,sys
p=pathlib.Path("C:/Users/Administrator/Documents/shortdrama-workbench/upstream/jjyb/LICENSE")
t=p.read_bytes().decode("gbk",errors="replace")
sys.stdout.buffer.write(t.encode("utf-8"))
