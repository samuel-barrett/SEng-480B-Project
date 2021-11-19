import os

for i in range(5, 67):
    release='0.{}-stable'.format(i)
    print('Creating {}'.format(release))
    os.system('cp -r react-native {}'.format(release))
    os.system('cd {}; git checkout {}; cd ..'.format(release, release))
