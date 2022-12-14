import filetype
import argparse
import os
import re

rot_value = 0 #Default value



def modify_file(offset1, offset2, filename,output, width=None, height=None):
	bin_arr = [] 
	with open(filename,'rb') as f:
		arr = f.read()
	for b in arr:
		bin_arr.append(bytes([b]))
		
	org_width = hex(int(bin_arr[offset1].hex() + bin_arr[offset1+1].hex(),16))
	org_height = hex(int(bin_arr[offset2].hex() + bin_arr[offset2+1].hex(),16))

	print("Detected width: %d px" % int(org_width,16))
	print("Detected height: %d px" % int(org_height,16))

	if width == None and height == None:
		print("Nothing todo. Set width/height?")
		exit()

	if width == None:
		width = int(org_width, 16) 
	if height == None:
		height = int(org_height,16)
	
	new_width=str(hex(width))[2:].zfill(4) #Width bad adaptive filter value :(/
	new_height=str(hex(height))[2:].zfill(4)

	if str(org_width)[2:] != new_width:
		print("New width: %d px" % int(new_width,16))
	if str(org_height)[2:] != new_height:
		print("New height: %d px" % int(new_height,16))
	

	#Set width
	bin_arr[offset1]=bytes.fromhex(str(new_width)[:2])
	bin_arr[offset1+1]=bytes.fromhex(str(new_width)[2:])
	#set height
	bin_arr[offset2]=bytes.fromhex(str(new_height)[:2])
	bin_arr[offset2+1]=bytes.fromhex(str(new_height)[2:])

	with open(output, "wb") as binary_file:
		binary_file.write(b"".join(bin_arr))
	print("Image saved!")
	
	
def modify_png(filename,output,width,height):
	modify_file(18,22, filename,output,width,height)
	os.remove("%s" % output)
	os.rename("%snew" % output, output)


def modify_jpg(filename,output,width,height):
	with open(filename,'rb') as f:
		arr = f.read()
	prev = ""
	i = 0
	for b in arr:
		b = bytes([b])
		if re.match("ffc[0-3]", prev + b.hex()):
			break
		i+=1
		prev = b.hex()
	print("Found magic bytes on offset %d " % i)
	modify_file(i+6,i+4,filename,output,width,height)

	
def process_file(filename,output,width,height):
	kind = filetype.guess(filename)
	if kind is None:
		print('Filetype not supported!')
		return
	if kind.mime == "image/png":
		print("Detected: png")
		modify_png(filename,output,width,height)
	elif kind.mime == "image/jpeg":
		print("Detected: jpg/jpeg")
		modify_jpg(filename,output,width,height)
	else:
		print("Filetype not supported")

if __name__ = "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("file", help="Filepath to image")
	parser.add_argument("output", help="Filepath to image")
	parser.add_argument("--width", "-sw", type=int, help="New width of image")
	parser.add_argument("--height", "-sh", type=int, help="New height of image")
	args = parser.parse_args()
	
	process_file(args.file, args.output, args.width, args.height)
