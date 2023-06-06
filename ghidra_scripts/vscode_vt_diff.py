#vscode diff match
#@author @clearbluejar
#@category PdiffInDark
#@keybinding 
#@menupath Tools.vscode.diffmatch
#@toolbar vscode.png


import tempfile
import subprocess
import os
import difflib

def decomp_func(func):

  from ghidra.app.decompiler import DecompInterface,DecompileOptions
  

  prog = func.getProgram()
  code = ''
  error = ''

  decompiler = DecompInterface()
  decompiler.openProgram(prog)

  options = DecompileOptions()
  
  options.grabFromProgram(prog);
  decompiler.setOptions(options);

  timeout = 120  
  
  print("Decompiling {func}...".format(func=func))
  results = decompiler.decompileFunction(func, timeout, monitor)

  error = results.getErrorMessage()
  if error == '':
      code = results.getDecompiledFunction().getC()
  else:
      code = 'Error: Decompile error: {} {}. Try increasing time for decompile'.format(func,error)
      print(code)


  return code


p1 = currentProgram
print(p1)

project = currentProgram.getDomainFile().getParent().getProjectData()

vt_session_count = 0


has_vt = False
has_vt_with_p1 = False

for domain_file in project.getRootFolder().getFiles():  
  if domain_file.getContentType() == 'VersionTracking':
    has_vt = True
    vt_session = domain_file.getDomainObject(java.lang.Object() , True, False, monitor)
    vt_session_count += 1
    if vt_session.getSourceProgram() == p1 or vt_session.getDestinationProgram() == p1:
      has_vt_with_p1 = True

if not has_vt:
  print('Error: No vt sessions found %s', project.getRootFolder().getFiles())
  exit(1)

if not has_vt_with_p1:
  print('Error: No vt sessions match current prog %s', p1)
  exit(1)

if vt_session_count > 1:
  domain_file = askDomainFile("More than one vt session found. Please select vt session")
  if domain_file.getContentType() != 'VersionTracking':
    print('Error: Selected file is not a vtsession %s', domain_file)
    exit(1)    
  vt_session = domain_file.getDomainObject(java.lang.Object() , True, False, monitor)


if vt_session.getSourceProgram() != p1 and vt_session.getDestinationProgram() != p1:
  print('Error: Current session %s does not match currentProgram : %s', vt_session, p1)
  print(p1)
  exit(1)

# save selected session

source = vt_session.getSourceProgram()
dest = vt_session.getDestinationProgram()

if p1 == source:
  
  other_prog = dest
else:
  other_prog = source
  

print(p1,source,dest)

source_addr = None
dest_addr = None
current_match = None

try:
  current_address = currentLocation.getFunctionEntryPoint()
except:  
  current_address = currentLocation.getFunctionAddress()

current_func = p1.getFunctionManager().getFunctionAt(current_address)

for match_set in vt_session.getMatchSets():
  print(match_set)
  
  for match in match_set.getMatches():
    if p1 == source:
      if match.getSourceAddress() == current_address:
        print(match)
        current_match = match
        
    else:
      if match.getDestinationAddress() == current_address:
        print(match)
        current_match = match

if current_match is None:
  print('Error: no match found for {}-{}'.format(current_func,current_address))
  exit(1)

source_addr = current_match.getSourceAddress()
dest_addr = current_match.getDestinationAddress()
source_func = source.getFunctionManager().getFunctionAt(source_addr)
dest_func = dest.getFunctionManager().getFunctionAt(dest_addr)


print(vt_session)
print(source_addr)
print(source_func)
print(dest_func)

source_decomp = decomp_func(source_func)
dest_decomp = decomp_func(dest_func)

source_path = None
dest_path = None
source_name = '{}-{}-{}.c'.format('source',source_func.getName(False),source_func.getEntryPoint())
dest_name = '{}-{}-{}.c'.format('dest',dest_func.getName(False),dest_func.getEntryPoint())
temp_dir = tempfile.gettempdir()

source_path = str(os.path.join(temp_dir, source_name))
dest_path =str(os.path.join(temp_dir, dest_name))


with open(source_path,'wb') as f:
  f.write(source_decomp)

with open(dest_path,'wb') as f:
  f.write(dest_decomp)

print(source_path)
print(dest_path)

# open decomp with vscode compare
subprocess.call(['code', '-d', source_path, dest_path], shell=True)