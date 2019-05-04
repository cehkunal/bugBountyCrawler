import cPickle
x={'ab','cd','e'}
def dump_dump(filename):
    with open(filename,'wb') as f:
        cPickle.dump(x,f)
    f.close()

def dump_load(filename):
    with open(filename,'rb') as f:
        data=cPickle.load(f)
        print data,type(data)
    f.close()


dump_dump('mypick')

dump_load('mypick')
