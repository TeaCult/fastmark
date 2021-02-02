import os,sys,time,math,datetime,urllib.request
from subprocess import Popen
from subprocess import PIPE


if "--help" in sys.argv:
	print('It takes a fast benchmark.\n    --disable-disk-mark to skip disk cheks\n    --disable-gpu-mark to skip gpu mark')
	exit()

os.system('clear')
SYSBENCH="sysbench cpu --time=1 --threads=THREADS --cpu-max-prime=100000 run"
SYSBENCH2="sysbench memory --memory-block-size=1M --memory-total-size=8G --num-threads=1 run"
TESTS=['build','texture','loop','shading','bump','effect2d','pulsar','desktop','buffer','ideas','jellyfish','terrain','shadow','refract','contionals','function','loop']

key1="events per second:"

t1=time.time()
print('Start Time:',time.ctime())
print('**********************************************************************')
print('A Fast Benchmark designed for impatients by impatients ...')
print('**********************************************************************')

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
					arr=arr+'GPU: '+s1+' Slot: '+dev+' '+s2+'\n'
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
		out=proc.stdout.read().decode('ascii').split('\n')
		
	for i in out:
		temp='                                  glmark2 Score:'
		temp2='    GL_RENDERER:'
		if temp2 in i:
			print(i.replace(temp2,'Rendering GPU:'))
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
	with Popen("lsblk -l -o NAME,MODEL,TYPE,SERIAL,SIZE".split(' '), stdout=PIPE) as proc:
		out=proc.stdout.read().decode('ascii').split('\n')

	venlist=''
	for i in out:
		if 'disk' in i:
			venlist=venlist+i.replace('disk','')+'\n'
	print('Disks:\n'+venlist)

def testdisks():
	with Popen("lsblk -l -o NAME,MODEL,TYPE".split(' '), stdout=PIPE) as proc:
		out=proc.stdout.read().decode('ascii').split('\n')

	for i in out:
		if 'disk' in i:
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
sc=testcores(1)
print('SingleCore:',sc )#,'   passmark eq:',round(sc*kpmsc),'   userbenchmark eq:',round(sc*kubsc))
mc=testcores(128)
print('MultiCore:',mc)#,'   passmark eq:',round(mc*kpmmc),'   userbenchmark eq:',round(mc*kubmc))

ms=testmem()
print('\nMemory Speed:',ms*kmibsgbs,'GB/s\n')

print(getgpuinfo())
if '--disable-gpu-mark' in sys.argv:
	print('Skipping gpu mark...\n')
else:
	gt=gputest()
	print('GPU Score:',gt,'\n')# ,'  passmark eq:',round(gt*kpmgt),'  userbenchmark eq:',round(gt*kubgt),'\n')

listdisks()

if '--disable-disk-mark' in sys.argv:
	print('Skipping disks mark...\n')
else:
	testdisks()

print('\nEnd Time:',time.ctime())
t2=time.time()
print('Total Duration (sec):',t2-t1)

inp=input('\nDo you want to see reference score ? (yes/no)\n')
if inp.upper()=='YES':
	print('''\n\n************** REFRENCE SCORE *****************
Cpu: AMD Ryzen 9 5900X 12-Core Processor / 24 Threads :
SingleCore: 247.61
MultiCore: 2935.35

Memory Speed: 37.9355922432 GB/s

GPU: NVIDIA Corporation GP104 [GeForce GTX 1080] (rev a1) Slot: 04:00.0 driver: nvidia
GPU: NVIDIA Corporation GA104 [GeForce RTX 3070] (rev a1) Slot: 09:00.0 driver: vfio-pci

Rendering GPU:   GeForce GTX 1080/PCIe/SSE2
GPU Score: 12255.0 

Disks:
sda       WDC WD4005FZBX-0                          VBG368RR          3,7T
sdb       TOSHIBA-TR200                             Y77B62JBK46S    223,6G
nvme0n1   Samsung SSD 970 EVO Plus 1TB              S4EWNS0N701300L 931,5G

/dev/sda:  247.96 MB/sec
/dev/sdb:  426.43 MB/sec
/dev/nvme0n1:  2892.92 MB/sec
************* REFRENCE SCORE ENDS **************
''')
