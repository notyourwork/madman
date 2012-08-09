import os 
search_dir = '/media/downloads/seeding/' 
report = [] 
for i in os.listdir( search_dir ):
    full_path = os.path.join(search_dir,i)  
    if os.path.isfile(full_path) and not os.path.islink(full_path):
        report.append(i) 

print "the following %d items were found" % (len(report), )
for i in report:
    print "--%s" % i 
    
