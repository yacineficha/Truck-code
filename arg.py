import argparse
import qr_extraction
#import noqr_extraction

parser = argparse.ArgumentParser()

parser.add_argument("-v", default = './', help="Videos directory path")
parser.add_argument("-o", help="Output directory", default = './')
parser.add_argument("-f", help="Format of the videos on the file, mkv, mp4, h264.. ect", default = '*.h264')
parser.add_argument("-qr", help="Use QR code algorithm", default = 1)
parser.add_argument("-c", help="Uses camera", default = 0)

args = parser.parse_args()

#both main function paramters are as follow : videos_path, formats, output_dir

if int(args.qr) :
	print('Launching the QR data extraction script')
	qr_extraction.main(args.v+'/', formats = args.f, output_dir = args.o, use_camera = args.c)
else :
	print('Launching the standard data extraction script')
	noqr_extraction.main(args.v+'/', formats = args.f, output_dir = args.o, use_camera = args.c)

