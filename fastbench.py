import os,sys,time,math,datetime,urllib.request
from subprocess import Popen
from subprocess import PIPE

os.system('clear')
SYSBENCH="sysbench cpu --time=1 --threads=THREADS --cpu-max-prime=100000 run"
SYSBENCH2="sysbench memory --memory-block-size=1M --memory-total-size=8G --num-threads=1 run"
TESTS=['build','texture','loop','shading','bump','effect2d','pulsar','desktop','buffer','ideas','jellyfish','terrain','shadow','refract','contionals','function','loop']

key1="events per second:"

t1=time.time()
print('Start Time:',time.ctime())
print('*******************************************************************************************')
print('A Fast Benchmark designed for impatients by impatients ...')
print('*******************************************************************************************')

def getcpuinfo(key):
	with Popen('lscpu', stdout=PIPE) as proc:
		out=proc.stdout.read().decode('ascii').split('\n');
	for i in out:
		if key in i:
			return i.replace(key,'')        

def getgpuinfo():
	arr=''
	with Popen('lspci -qq'.split(' '), stdout=PIPE) as proc:
		out=proc.stdout.read().decode('ascii').split('\n');
	for i in out:
		if 'VGA compatible controller:' in i:
			s1=i.split('controller: ')[1]
			dev=i[:7]
			with Popen(('lspci -ks '+dev).split(' '), stdout=PIPE) as proc:
				out=proc.stdout.read().decode('ascii').split('\n');
			for j in out:
				if 'Kernel driver in use: ' in j:
					s2='driver:'+j.split('use:')[1]
					arr=arr+'GPU: '+s1+' Slot: '+dev+' '+s2
	return arr            

def testcores(corecount):
	s=SYSBENCH.replace('THREADS',str(corecount))
	args=s.split(' ')
	with Popen(args, stdout=PIPE) as proc:
		out=proc.stdout.read().decode('ascii').split('\n');
	for i in out:
		if key1 in i:
			return float(i.replace(key1,'').replace(' ',''))
def testmem():
	args=SYSBENCH2.split(' ')
	with Popen(args, stdout=PIPE) as proc:
		out=proc.stdout.read().decode('ascii').split('\n');
	for i in out:
		if 'MiB/sec' in i:
			return float(i.split('(')[1].split(' MiB')[0])

def gputest():
	gm2line='glmark2 --fullscreen --off-screen'
	for i in TESTS:
		gm2line=gm2line+' -b '+i+':duration=0.25'
	with Popen(gm2line.split(' '), stdout=PIPE) as proc:
		out=proc.stdout.read().decode('ascii').split('\n');
	for i in out:
		temp='                                  glmark2 Score:'
		if temp in i:
			return float(i.replace(temp,''))

def whichcard():
	gm2line='glmark2 --fullscreen --off-screen -b build:duration=0.05'
	with Popen(gm2line.split(' '), stdout=PIPE) as proc:
		out=proc.stdout.read().decode('ascii').split('\n');
	for i in out:
		temp='    GL_RENDERER:   '
		if temp in i:
			return i.replace(temp,'')



def listdisks():
	with Popen("lsblk -l -o NAME,MODEL,TYPE".split(' '), stdout=PIPE) as proc:
		out=proc.stdout.read().decode('ascii').split('\n')

	venlist=''
	for i in out:
		if 'disk' in i:
			venlist=venlist+i.replace('disk','')
	print('Disks:', venlist)

def testdisks():
	with Popen("lsblk -l -o NAME,MODEL,TYPE".split(' '), stdout=PIPE) as proc:
		out=proc.stdout.read().decode('ascii').split('\n')

	for i in out:
		if 'part' in i:
			target=i.split()[0]
			with Popen(("sudo hdparm -tT /dev/"+target).split(' '), stdout=PIPE) as proc:
				out2=proc.stdout.read().decode('ascii').split('\n')
			for j in out2:
				temp='/dev'
				if temp in j:
					r1=j
				temp='disk read'
				if temp in j:
					r2=j.split('seconds =')[1]
			print(r1,r2)
			
			


kpmsc=36.432
kpmmc=20.357
kubsc=2.088
kubmc=1.786
kpmgt=2.544
kubgt=0.019

kmibsgbs=0.001048576 #MiB/s to GB/s
print('Cpu:',getcpuinfo('Model name:          '),'/',getcpuinfo('CPU(s):              '),'Threads :')
print(getgpuinfo())
listdisks()
print('*******************************************************************************************')
sc=testcores(1)
print('SingleCore:',sc ,'   passmark eq:',round(sc*kpmsc),'   userbenchmark eq:',round(sc*kubsc))
mc=testcores(128)
print('MultiCore:',mc,'   passmark eq:',round(mc*kpmmc),'   userbenchmark eq:',round(mc*kubmc))
ms=testmem()
print('\nMemory Speed:',ms*kmibsgbs,'GB/s\n')
#print('Rendering On:',whichcard())
gt=gputest()
print('GPU Score:',gt,'  passmark eq:',round(gt*kpmgt),'  userbenchmark eq:',round(gt*kubgt),'\n')
testdisks()
print('*******************************************************************************************')
#print('For Extended Octane and V-Ray Benchmarks please add a switch as render-engine ieg:')
#print('"$python3 fastbench.py render-engine"\n')
print('End Time:',time.ctime())
t2=time.time()
print('Total Duration (sec):',t2-t1)
