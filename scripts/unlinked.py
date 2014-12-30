import os 
search_dir = '/media/downloads/seeding/' 
report = {} 
for i in os.listdir( search_dir ):
    full_path = os.path.join(search_dir,i)  
    if os.path.isfile(full_path) and not os.path.islink(full_path):
        report[i] = os.path.getsize(os.path.join(search_dir, i))

print "the following %d items were found" % (len(report), )

for i in report.keys():
    print "%s" % i
    print report[i] 
    gb = float(report[i])/1000/1000/1000
    print type(gb) 
    print "{0:.2f}".format(gb)
